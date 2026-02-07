from typing import Optional, Dict, Any, cast
from datetime import datetime, timedelta
from app.core.database import get_connection

# Política de expiración de contraseñas (en días)
PASSWORD_EXPIRATION_DAYS = 90


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un usuario por username con todos los campos de seguridad.
    
    Returns:
        Dict con datos del usuario incluyendo campos de política de contraseñas,
        o None si no existe.
    """
    conn = get_connection()
    assert conn is not None, "No se pudo obtener conexión a la base de datos"

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            u.id,
            u.username, 
            u.email,
            u.password_hash, 
            r.nombre AS role,
            u.activo,
            u.creado_en,
            u.actualizado_en,
            u.first_login,
            u.force_password_change,
            u.password_expires_at,
            u.password_changed_at,
            u.last_password_change_ip
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE u.username = %s
    """

    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:
        return None

    # Normalizamos el tipo para el resto de la aplicación
    return cast(Dict[str, Any], user)


def update_user_password(username: str, new_password_hash: str) -> bool:
    """
    Actualiza la contraseña de un usuario (función legacy).
    
    NOTA: Para nuevos desarrollos, usar change_user_password()
    que incluye gestión de políticas de contraseñas.
    
    Args:
        username: Nombre de usuario
        new_password_hash: Hash bcrypt de la nueva contraseña
    
    Returns:
        True si la actualización fue exitosa, False en caso contrario
    """
    conn = get_connection()
    assert conn is not None, "No se pudo obtener conexión a la base de datos"
    
    try:
        cursor = conn.cursor()
        
        query = """
            UPDATE usuarios 
            SET password_hash = %s, actualizado_en = NOW()
            WHERE username = %s AND activo = 1
        """
        
        cursor.execute(query, (new_password_hash, username))
        conn.commit()
        
        # Verificar si se actualizó alguna fila
        updated_rows = cursor.rowcount
        cursor.close()
        conn.close()
        
        return updated_rows > 0
    
    except Exception as e:
        print(f"Error al actualizar contraseña: {e}")
        conn.close()
        return False


def check_password_expiration(user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifica el estado de expiración de la contraseña de un usuario.
    
    Evalúa múltiples condiciones:
    1. Primer login (first_login = TRUE)
    2. Cambio forzado (force_password_change = TRUE)
    3. Expiración por fecha (password_expires_at < NOW)
    4. Expiración por tiempo desde último cambio
    
    Args:
        user: Diccionario con datos del usuario
    
    Returns:
        {
            'expired': bool,  # Contraseña expirada
            'days_until_expiration': int | None,  # Días restantes
            'requires_change': bool  # Requiere cambio obligatorio
        }
    """
    result = {
        'expired': False,
        'days_until_expiration': None,
        'requires_change': False
    }
    
    # Caso 1: Primer login - siempre requiere cambio
    if user.get('first_login'):
        result['requires_change'] = True
        return result
    
    # Caso 2: Cambio forzado manualmente (ej: reset de admin)
    if user.get('force_password_change'):
        result['requires_change'] = True
        return result
    
    # Caso 3: Verificar expiración por fecha explícita
    if user.get('password_expires_at'):
        now = datetime.now()
        expires_at = user['password_expires_at']
        
        if now > expires_at:
            result['expired'] = True
            result['requires_change'] = True
        else:
            delta = expires_at - now
            result['days_until_expiration'] = delta.days
    
    # Caso 4: Verificar por tiempo desde último cambio
    elif user.get('password_changed_at'):
        now = datetime.now()
        last_change = user['password_changed_at']
        delta = now - last_change
        
        if delta.days >= PASSWORD_EXPIRATION_DAYS:
            result['expired'] = True
            result['requires_change'] = True
        else:
            result['days_until_expiration'] = PASSWORD_EXPIRATION_DAYS - delta.days
    
    return result


def change_user_password(
    user_id: int,
    new_password_hash: str,
    is_first_login: bool = False,
    client_ip: str = None
) -> bool:
    """
    Cambia la contraseña de un usuario y actualiza los flags de seguridad.
    
    Actualiza:
    - password_hash: Nueva contraseña hasheada
    - first_login: FALSE (ya no es primer login)
    - force_password_change: FALSE (se completó el cambio)
    - password_changed_at: Timestamp actual
    - password_expires_at: NOW + PASSWORD_EXPIRATION_DAYS
    - last_password_change_ip: IP del cliente
    
    Args:
        user_id: ID del usuario
        new_password_hash: Hash bcrypt de la nueva contraseña
        is_first_login: Si es el primer login del usuario
        client_ip: Dirección IP del cliente
    
    Returns:
        True si se actualizó correctamente, False en caso contrario
    """
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    now = datetime.now()
    
    # Calcular fecha de expiración
    expires_at = now + timedelta(days=PASSWORD_EXPIRATION_DAYS)
    
    try:
        query = """
            UPDATE usuarios
            SET 
                password_hash = %s,
                first_login = FALSE,
                force_password_change = FALSE,
                password_changed_at = %s,
                password_expires_at = %s,
                last_password_change_ip = %s,
                actualizado_en = %s
            WHERE id = %s
        """
        
        values = (
            new_password_hash,
            now,
            expires_at,
            client_ip,
            now,
            user_id
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        success = cursor.rowcount > 0
        
        cursor.close()
        conn.close()
        
        return success
        
    except Exception as e:
        print(f"Error al cambiar contraseña: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def force_password_change_by_admin(user_id: int) -> bool:
    """
    Marca a un usuario para que deba cambiar su contraseña en el próximo login.
    
    Útil para:
    - Resets de seguridad
    - Sospecha de compromiso de cuenta
    - Políticas de seguridad corporativas
    
    Args:
        user_id: ID del usuario
    
    Returns:
        True si se marcó correctamente, False en caso contrario
    """
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        query = """
            UPDATE usuarios
            SET force_password_change = TRUE,
                actualizado_en = NOW()
            WHERE id = %s
        """
        
        cursor.execute(query, (user_id,))
        conn.commit()
        
        success = cursor.rowcount > 0
        
        cursor.close()
        conn.close()
        
        return success
        
    except Exception as e:
        print(f"Error al forzar cambio de contraseña: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False
