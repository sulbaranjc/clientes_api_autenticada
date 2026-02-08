#!/usr/bin/env python3
"""
Script de Gestión de Usuarios
Proyecto: Clientes API Autenticada

Funcionalidades:
1. Cambiar contraseña de un usuario
2. Crear nuevo usuario
3. Forzar cambio de contraseña (admin)
4. Listar usuarios con estado de seguridad
5. Activar/Desactivar usuarios

Uso:
    python scripts/manage_users.py [comando] [opciones]

Ejemplos:
    # Cambiar contraseña
    python scripts/manage_users.py change-password usuario@example.com
    python scripts/manage_users.py change-password admin@test.com
    

    # Crear usuario
    python scripts/manage_users.py create-user nuevo@example.com --rol admin
    
    # Forzar cambio de contraseña
    python scripts/manage_users.py force-change usuario@example.com
    
    # Listar usuarios
    python scripts/manage_users.py list
    
    # Ver ayuda
    python scripts/manage_users.py --help
"""

import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import getpass

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from passlib.context import CryptContext
from app.core.database import get_connection
from app.repository.users_repo import (
    get_user_by_username,
    change_user_password as repo_change_password,
    force_password_change_by_admin as repo_force_password_change,
    check_password_expiration
)

# Configuración
load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Imprime encabezado formateado."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_success(text: str):
    """Mensaje de éxito."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Mensaje de error."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Mensaje de advertencia."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Mensaje informativo."""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida la fortaleza de una contraseña.
    
    Returns:
        (es_valida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    
    return True, "Contraseña válida"


def get_user_by_email(email: str):
    """Obtiene usuario por email."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT u.*, r.nombre as rol
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.email = %s
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return user
    except Exception as e:
        print_error(f"Error al consultar usuario: {str(e)}")
        return None


def change_user_password(email: str, new_password: Optional[str] = None, interactive: bool = True):
    """
    Cambia la contraseña de un usuario.
    
    Args:
        email: Email del usuario
        new_password: Nueva contraseña (si no se provee, se solicita interactivamente)
        interactive: Si es True, solicita confirmación
    """
    print_header(f"CAMBIAR CONTRASEÑA - {email}")
    
    # Verificar que el usuario existe
    user = get_user_by_email(email)
    if not user:
        print_error(f"Usuario '{email}' no encontrado")
        return False
    
    print_info(f"Usuario encontrado: {user['username']} ({user['rol']})")
    
    # Solicitar nueva contraseña si no se proveyó
    if not new_password:
        if not interactive:
            print_error("Debe proporcionar una contraseña en modo no interactivo")
            return False
        
        print(f"\n{Colors.YELLOW}Ingrese la nueva contraseña:{Colors.END}")
        new_password = getpass.getpass("Nueva contraseña: ")
        confirm_password = getpass.getpass("Confirmar contraseña: ")
        
        if new_password != confirm_password:
            print_error("Las contraseñas no coinciden")
            return False
    
    # Validar fortaleza de contraseña
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        print_error(message)
        return False
    
    print_success(message)
    
    # Confirmar cambio
    if interactive:
        confirm = input(f"\n{Colors.YELLOW}¿Confirmar cambio de contraseña para '{email}'? (s/N): {Colors.END}")
        if confirm.lower() != 's':
            print_warning("Operación cancelada")
            return False
    
    # Cambiar contraseña
    try:
        # Hashear la contraseña
        password_hash = pwd_context.hash(new_password)
        
        success = repo_change_password(
            user_id=user['id'],
            new_password_hash=password_hash,
            is_first_login=False,
            client_ip="CLI"
        )
        
        if success:
            print_success("Contraseña actualizada exitosamente")
            print_info(f"Fecha de cambio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print_info(f"Expira en: 90 días")
            return True
        else:
            print_error("No se pudo actualizar la contraseña")
            return False
            
    except Exception as e:
        print_error(f"Error al cambiar contraseña: {str(e)}")
        return False


def create_user(
    email: str,
    username: str,
    rol: str = "user",
    password: Optional[str] = None,
    interactive: bool = True
):
    """
    Crea un nuevo usuario.
    
    Args:
        email: Email del usuario
        username: Nombre de usuario
        rol: Rol (admin, user, guest)
        password: Contraseña inicial (si no se provee, se genera temporal)
        interactive: Modo interactivo
    """
    print_header(f"CREAR NUEVO USUARIO - {email}")
    
    # Verificar que no exista
    existing = get_user_by_email(email)
    if existing:
        print_error(f"Ya existe un usuario con el email '{email}'")
        return False
    
    # Validar rol
    valid_roles = ['admin', 'user', 'guest']
    if rol not in valid_roles:
        print_error(f"Rol inválido. Debe ser uno de: {', '.join(valid_roles)}")
        return False
    
    # Generar contraseña temporal si no se provee
    if not password:
        password = f"Temp{datetime.now().strftime('%Y%m')}!"
        print_info(f"Contraseña temporal generada: {password}")
        print_warning("El usuario deberá cambiarla en el primer login")
    
    # Validar contraseña
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        print_error(message)
        return False
    
    # Mostrar resumen
    print(f"\n{Colors.BOLD}Datos del nuevo usuario:{Colors.END}")
    print(f"  Email:    {email}")
    print(f"  Username: {username}")
    print(f"  Rol:      {rol}")
    print(f"  Password: {'***' if interactive else password}")
    print(f"  Estado:   Activo")
    print(f"  First Login: True (debe cambiar contraseña)\n")
    
    # Confirmar
    if interactive:
        confirm = input(f"{Colors.YELLOW}¿Confirmar creación? (s/N): {Colors.END}")
        if confirm.lower() != 's':
            print_warning("Operación cancelada")
            return False
    
    # Crear usuario
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener ID del rol
        cursor.execute("SELECT id FROM roles WHERE nombre = %s", (rol,))
        rol_row = cursor.fetchone()
        if not rol_row:
            print_error(f"Rol '{rol}' no encontrado en la base de datos")
            return False
        
        rol_id = rol_row[0]
        
        # Hash de la contraseña
        password_hash = pwd_context.hash(password)
        
        # Insertar usuario
        query = """
            INSERT INTO usuarios (
                username, email, password_hash, rol_id, activo,
                first_login, password_expires_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        expires_at = datetime.now() + timedelta(days=90)
        
        cursor.execute(query, (
            username, email, password_hash, rol_id, True,
            True, expires_at
        ))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        print_success(f"Usuario creado exitosamente (ID: {user_id})")
        print_info(f"Contraseña temporal: {password}")
        print_warning("Guarde esta contraseña de forma segura")
        
        return True
        
    except Exception as e:
        print_error(f"Error al crear usuario: {str(e)}")
        return False


def force_password_change(email: str, interactive: bool = True):
    """
    Fuerza a un usuario a cambiar su contraseña en el próximo login.
    """
    print_header(f"FORZAR CAMBIO DE CONTRASEÑA - {email}")
    
    # Verificar usuario
    user = get_user_by_email(email)
    if not user:
        print_error(f"Usuario '{email}' no encontrado")
        return False
    
    print_info(f"Usuario: {user['username']}")
    print_info(f"Rol: {user['rol']}")
    
    # Confirmar
    if interactive:
        confirm = input(f"\n{Colors.YELLOW}¿Forzar cambio de contraseña? (s/N): {Colors.END}")
        if confirm.lower() != 's':
            print_warning("Operación cancelada")
            return False
    
    # Forzar cambio
    try:
        success = repo_force_password_change(user['id'])
        
        if success:
            print_success("Usuario marcado para cambio obligatorio de contraseña")
            print_info("En el próximo login deberá cambiar su contraseña")
            return True
        else:
            print_error("No se pudo actualizar el usuario")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def list_users():
    """
    Lista todos los usuarios con su estado de seguridad.
    """
    print_header("LISTA DE USUARIOS")
    
    try:
        conn = get_connection()
        if not conn:
            print_error("No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                u.id,
                u.email,
                u.username,
                r.nombre as rol,
                u.activo,
                u.first_login,
                u.force_password_change,
                u.password_expires_at,
                u.password_changed_at,
                u.creado_en,
                CASE 
                    WHEN u.first_login = TRUE THEN 'PRIMER_LOGIN'
                    WHEN u.force_password_change = TRUE THEN 'CAMBIO_FORZADO'
                    WHEN u.password_expires_at < NOW() THEN 'EXPIRADA'
                    WHEN u.password_expires_at IS NULL THEN 'SIN_EXPIRACION'
                    WHEN DATEDIFF(u.password_expires_at, NOW()) <= 7 THEN 'POR_EXPIRAR'
                    ELSE 'OK'
                END AS estado_password,
                CASE
                    WHEN u.password_expires_at IS NULL THEN NULL
                    ELSE DATEDIFF(u.password_expires_at, NOW())
                END AS dias_expiracion
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            ORDER BY u.creado_en DESC
        """
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        if not users:
            print_warning("No hay usuarios en la base de datos")
            return True
        
        print(f"\n{Colors.BOLD}Total de usuarios: {len(users)}{Colors.END}\n")
        
        # Encabezado de tabla
        header = f"{'ID':<5} {'EMAIL':<30} {'USERNAME':<20} {'ROL':<10} {'ACTIVO':<8} {'ESTADO PASSWORD':<25}"
        print(f"{Colors.BOLD}{header}{Colors.END}")
        print("-" * 110)
        
        # Filas
        for user in users:
            estado = user['estado_password']
            
            # Color según estado
            if estado in ['PRIMER_LOGIN', 'CAMBIO_FORZADO', 'EXPIRADA']:
                color = Colors.RED
            elif estado == 'POR_EXPIRAR':
                color = Colors.YELLOW
            else:
                color = Colors.GREEN
            
            activo_str = "Sí" if user['activo'] else "No"
            
            # Estado detallado
            if estado == 'PRIMER_LOGIN':
                estado_str = "⚠️  Primer login"
            elif estado == 'CAMBIO_FORZADO':
                estado_str = "🔒 Cambio forzado"
            elif estado == 'EXPIRADA':
                estado_str = "❌ Expirada"
            elif estado == 'POR_EXPIRAR':
                dias = user['dias_expiracion']
                estado_str = f"⏰ {dias} días restantes"
            elif estado == 'SIN_EXPIRACION':
                estado_str = "➖ Sin expiración"
            else:
                dias = user['dias_expiracion']
                estado_str = f"✅ OK ({dias} días)"
            
            row = f"{user['id']:<5} {user['email']:<30} {user['username']:<20} {user['rol']:<10} {activo_str:<8} {color}{estado_str}{Colors.END}"
            print(row)
        
        # Resumen
        print("\n" + "-" * 110)
        activos = sum(1 for u in users if u['activo'])
        requieren_cambio = sum(1 for u in users if u['estado_password'] in ['PRIMER_LOGIN', 'CAMBIO_FORZADO', 'EXPIRADA'])
        
        print(f"\n{Colors.BOLD}Resumen:{Colors.END}")
        print(f"  Usuarios activos: {activos}/{len(users)}")
        print(f"  Requieren cambio de contraseña: {requieren_cambio}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print_error(f"Error al listar usuarios: {str(e)}")
        return False


def toggle_user_status(email: str, activate: bool, interactive: bool = True):
    """
    Activa o desactiva un usuario.
    """
    action = "ACTIVAR" if activate else "DESACTIVAR"
    print_header(f"{action} USUARIO - {email}")
    
    # Verificar usuario
    user = get_user_by_email(email)
    if not user:
        print_error(f"Usuario '{email}' no encontrado")
        return False
    
    current_status = "Activo" if user['activo'] else "Inactivo"
    print_info(f"Estado actual: {current_status}")
    
    if user['activo'] == activate:
        print_warning(f"El usuario ya está {current_status.lower()}")
        return True
    
    # Confirmar
    if interactive:
        confirm = input(f"\n{Colors.YELLOW}¿Confirmar operación? (s/N): {Colors.END}")
        if confirm.lower() != 's':
            print_warning("Operación cancelada")
            return False
    
    # Actualizar estado
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE usuarios SET activo = %s WHERE id = %s",
            (activate, user['id'])
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        new_status = "activado" if activate else "desactivado"
        print_success(f"Usuario {new_status} exitosamente")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def show_help():
    """Muestra la ayuda del script."""
    help_text = f"""
{Colors.BOLD}GESTIÓN DE USUARIOS - Clientes API Autenticada{Colors.END}

{Colors.CYAN}USO:{Colors.END}
    python scripts/manage_users.py [comando] [argumentos]

{Colors.CYAN}COMANDOS DISPONIBLES:{Colors.END}

    {Colors.GREEN}change-password{Colors.END} <email> [--password PASS]
        Cambia la contraseña de un usuario
        
        Ejemplos:
            python scripts/manage_users.py change-password usuario@example.com
            python scripts/manage_users.py change-password usuario@example.com --password NuevaPass123!

    {Colors.GREEN}create-user{Colors.END} <email> <username> [--rol ROLE] [--password PASS]
        Crea un nuevo usuario
        
        Ejemplos:
            python scripts/manage_users.py create-user nuevo@example.com nuevouser
            python scripts/manage_users.py create-user admin@example.com adminuser --rol admin

    {Colors.GREEN}force-change{Colors.END} <email>
        Fuerza a un usuario a cambiar su contraseña en el próximo login
        
        Ejemplo:
            python scripts/manage_users.py force-change usuario@example.com

    {Colors.GREEN}list{Colors.END}
        Lista todos los usuarios con su estado de seguridad
        
        Ejemplo:
            python scripts/manage_users.py list

    {Colors.GREEN}activate{Colors.END} <email>
        Activa un usuario desactivado
        
        Ejemplo:
            python scripts/manage_users.py activate usuario@example.com

    {Colors.GREEN}deactivate{Colors.END} <email>
        Desactiva un usuario
        
        Ejemplo:
            python scripts/manage_users.py deactivate usuario@example.com

{Colors.CYAN}OPCIONES:{Colors.END}
    --help, -h          Muestra esta ayuda
    --password PASS     Especifica contraseña (evita prompt interactivo)
    --rol ROLE          Rol del usuario (admin, user, guest)

{Colors.YELLOW}EJEMPLOS DE USO:{Colors.END}
    # Cambiar contraseña interactivamente
    python scripts/manage_users.py change-password usuario@example.com

    # Crear admin con contraseña específica
    python scripts/manage_users.py create-user admin@empresa.com adminuser \\
        --rol admin --password AdminPass123!

    # Listar todos los usuarios
    python scripts/manage_users.py list

    # Forzar cambio de contraseña inmediato
    python scripts/manage_users.py force-change comprometido@example.com
"""
    print(help_text)


def main():
    """Función principal - maneja argumentos de línea de comandos."""
    
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        return 0
    
    command = sys.argv[1]
    
    try:
        if command == "change-password":
            if len(sys.argv) < 3:
                print_error("Debe especificar un email")
                print_info("Uso: python scripts/manage_users.py change-password <email> [--password PASS]")
                return 1
            
            email = sys.argv[2]
            password = None
            
            if '--password' in sys.argv:
                idx = sys.argv.index('--password')
                if idx + 1 < len(sys.argv):
                    password = sys.argv[idx + 1]
            
            success = change_user_password(email, password)
            return 0 if success else 1
        
        elif command == "create-user":
            if len(sys.argv) < 4:
                print_error("Faltan argumentos")
                print_info("Uso: python scripts/manage_users.py create-user <email> <username> [--rol ROLE] [--password PASS]")
                return 1
            
            email = sys.argv[2]
            username = sys.argv[3]
            rol = "user"
            password = None
            
            if '--rol' in sys.argv:
                idx = sys.argv.index('--rol')
                if idx + 1 < len(sys.argv):
                    rol = sys.argv[idx + 1]
            
            if '--password' in sys.argv:
                idx = sys.argv.index('--password')
                if idx + 1 < len(sys.argv):
                    password = sys.argv[idx + 1]
            
            success = create_user(email, username, rol, password)
            return 0 if success else 1
        
        elif command == "force-change":
            if len(sys.argv) < 3:
                print_error("Debe especificar un email")
                print_info("Uso: python scripts/manage_users.py force-change <email>")
                return 1
            
            email = sys.argv[2]
            success = force_password_change(email)
            return 0 if success else 1
        
        elif command == "list":
            success = list_users()
            return 0 if success else 1
        
        elif command == "activate":
            if len(sys.argv) < 3:
                print_error("Debe especificar un email")
                print_info("Uso: python scripts/manage_users.py activate <email>")
                return 1
            
            email = sys.argv[2]
            success = toggle_user_status(email, True)
            return 0 if success else 1
        
        elif command == "deactivate":
            if len(sys.argv) < 3:
                print_error("Debe especificar un email")
                print_info("Uso: python scripts/manage_users.py deactivate <email>")
                return 1
            
            email = sys.argv[2]
            success = toggle_user_status(email, False)
            return 0 if success else 1
        
        else:
            print_error(f"Comando desconocido: {command}")
            print_info("Ejecute 'python scripts/manage_users.py --help' para ver los comandos disponibles")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operación cancelada por el usuario{Colors.END}")
        return 130
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
