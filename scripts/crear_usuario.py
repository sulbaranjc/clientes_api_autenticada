#!/usr/bin/env python3
"""
Script para crear usuarios de forma interactiva.

Permite crear nuevos usuarios desde consola con:
- Nombre de usuario (username)
- Contraseña (en texto plano, se hashea automáticamente)
- Rol del usuario (admin, lector, etc.)

El script:
1. Pide los datos al usuario
2. Hashea la contraseña usando bcrypt
3. Inserta el usuario en la base de datos
4. Confirma la creación exitosa

Uso:
    python3 scripts/crear_usuario.py

Requisitos:
    - Variables de entorno configuradas en .env
    - Base de datos MySQL disponible
"""

import os
import sys
import getpass
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from passlib.context import CryptContext

# Cargar variables de entorno
load_dotenv()

# Configurar contexto de hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_connection():
    """Establece conexión con la base de datos MySQL."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "profesor"),
            password=os.getenv("DB_PASSWORD", "4688"),
            database=os.getenv("DB_NAME", "clientes_autenticado_db")
        )
        return connection
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return None


def username_exists(conn, username: str) -> bool:
    """Verifica si el nombre de usuario ya existe."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None


def get_role_id(conn, role_name: str) -> int:
    """
    Obtiene el ID del rol por su nombre.
    
    Args:
        conn: Conexión a la base de datos
        role_name: Nombre del rol (admin, lector, usuario)
    
    Returns:
        ID del rol, o None si no existe
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM roles WHERE nombre = %s", (role_name,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def create_user(username: str, password: str, role: str = "usuario") -> bool:
    """
    Crea un nuevo usuario en la base de datos.
    
    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
        role: Rol del usuario (admin, lector, usuario)
    
    Returns:
        True si se creó exitosamente, False en caso contrario
    """
    conn = get_connection()
    if not conn:
        return False
    
    # Verificar si el usuario ya existe
    if username_exists(conn, username):
        print(f"❌ El usuario '{username}' ya existe en la base de datos")
        conn.close()
        return False
    
    # Obtener el ID del rol
    role_id = get_role_id(conn, role)
    if not role_id:
        print(f"❌ El rol '{role}' no existe en la base de datos")
        print(f"   Roles disponibles: admin, lector")
        conn.close()
        return False
    
    # Hashear la contraseña
    hashed_password = pwd_context.hash(password)
    
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO usuarios (username, email, password_hash, rol_id, activo)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            username,
            f"{username}@example.com",
            hashed_password,
            role_id,  # ID del rol, no el nombre
            1  # activo = 1
        ))
        conn.commit()
        cursor.close()
        
        print(f"✅ Usuario '{username}' creado exitosamente")
        print(f"   Rol: {role}")
        print(f"   Hash: {hashed_password[:40]}...")
        return True
        
    except Error as e:
        print(f"❌ Error al insertar usuario: {e}")
        conn.close()
        return False
    finally:
        conn.close()


def main():
    """Función principal con interfaz interactiva."""
    print("\n" + "="*60)
    print("  🔐 CREADOR DE USUARIOS - FastAPI Clientes API")
    print("="*60 + "\n")
    
    # Pedir nombre de usuario
    while True:
        username = input("📝 Ingrese el nombre de usuario: ").strip()
        if not username:
            print("⚠️  El nombre de usuario no puede estar vacío")
            continue
        if len(username) < 3:
            print("⚠️  El nombre de usuario debe tener al menos 3 caracteres")
            continue
        break
    
    # Pedir contraseña
    print("\n🔑 Ingrese la contraseña (no se mostrará mientras escribe):")
    while True:
        password = getpass.getpass("   Contraseña: ")
        if not password:
            print("⚠️  La contraseña no puede estar vacía")
            continue
        if len(password) < 6:
            print("⚠️  La contraseña debe tener al menos 6 caracteres")
            continue
        
        # Confirmación
        password_confirm = getpass.getpass("   Confirme la contraseña: ")
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden, intente nuevamente\n")
            continue
        break
    
    # Pedir rol
    print("\n👤 Seleccione el rol del usuario:")
    print("   1. admin   (acceso total)")
    print("   2. lector  (solo lectura)")
    
    while True:
        rol_option = input("\n   Opción (1-2): ").strip()
        if rol_option == "1":
            role = "admin"
            break
        elif rol_option == "2":
            role = "lector"
            break
        else:
            print("⚠️  Opción inválida, intente nuevamente")
    
    # Crear el usuario
    print(f"\n⏳ Creando usuario '{username}' con rol '{role}'...\n")
    success = create_user(username, password, role)
    
    if success:
        print("\n✨ Usuario creado exitosamente")
        print(f"\n   Datos de acceso:")
        print(f"   • Usuario: {username}")
        print(f"   • Contraseña: (la que ingresó)")
        print(f"   • Rol: {role}")
    else:
        print("\n❌ No se pudo crear el usuario")
        sys.exit(1)
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
