from typing import Optional, Dict, Any, cast
from app.core.database import get_connection


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    assert conn is not None, "No se pudo obtener conexión a la base de datos"

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT u.username, u.password_hash, r.nombre AS role
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE u.username = %s AND u.activo = 1
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
    Actualiza la contraseña de un usuario.
    
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
