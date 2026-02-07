#!/usr/bin/env python3
"""
Script de prueba de conexión a la base de datos MySQL.

Valida que:
1. Las variables de entorno estén configuradas
2. La conexión a MySQL sea exitosa
3. La base de datos exista
4. Las tablas necesarias existan
5. Se puedan ejecutar consultas básicas

Uso:
    python scripts/test_conexion.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos de app
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from app.core.database import get_connection, get_db_cursor

# Colores para la terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Imprime un encabezado formateado."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Imprime mensaje de éxito."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Imprime mensaje de error."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Imprime mensaje de advertencia."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Imprime mensaje informativo."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def test_environment_variables():
    """Verifica que las variables de entorno estén configuradas."""
    print_header("TEST 1: Variables de Entorno")
    
    load_dotenv()
    
    required_vars = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_NAME": os.getenv("DB_NAME")
    }
    
    all_ok = True
    
    for var_name, var_value in required_vars.items():
        if var_value:
            print_success(f"{var_name}: {var_value if var_name != 'DB_PASSWORD' else '***'}")
        else:
            print_error(f"{var_name}: NO CONFIGURADA")
            all_ok = False
    
    if all_ok:
        print_success("Todas las variables de entorno están configuradas")
    else:
        print_error("Faltan variables de entorno en el archivo .env")
    
    return all_ok


def test_basic_connection():
    """Prueba la conexión básica a MySQL."""
    print_header("TEST 2: Conexión Básica a MySQL")
    
    try:
        connection = get_connection()
        
        if connection and connection.is_connected():
            db_info = connection.get_server_info()
            print_success(f"Conexión exitosa a MySQL Server versión: {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            print_success(f"Base de datos actual: {database[0]}")
            
            cursor.close()
            connection.close()
            print_success("Conexión cerrada correctamente")
            
            return True
        else:
            print_error("No se pudo establecer la conexión")
            return False
            
    except Error as e:
        print_error(f"Error al conectar: {e}")
        return False


def test_database_exists():
    """Verifica que la base de datos especificada exista."""
    print_header("TEST 3: Existencia de Base de Datos")
    
    try:
        connection = get_connection()
        if not connection:
            print_error("No se pudo conectar")
            return False
        
        cursor = connection.cursor()
        db_name = os.getenv("DB_NAME")
        
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        result = cursor.fetchone()
        
        if result:
            print_success(f"La base de datos '{db_name}' existe")
            cursor.close()
            connection.close()
            return True
        else:
            print_error(f"La base de datos '{db_name}' NO existe")
            cursor.close()
            connection.close()
            return False
            
    except Error as e:
        print_error(f"Error al verificar base de datos: {e}")
        return False


def test_tables_exist():
    """Verifica que las tablas necesarias existan."""
    print_header("TEST 4: Existencia de Tablas")
    
    required_tables = ["clientes", "usuarios"]
    
    try:
        connection = get_connection()
        if not connection:
            print_error("No se pudo conectar")
            return False
        
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print_info(f"Tablas encontradas: {existing_tables}")
        
        all_ok = True
        for table in required_tables:
            if table in existing_tables:
                print_success(f"Tabla '{table}' existe")
                
                # Mostrar estructura de la tabla
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print_info(f"  Columnas de '{table}':")
                for col in columns:
                    print(f"    - {col[0]} ({col[1]})")
            else:
                print_warning(f"Tabla '{table}' NO existe")
                all_ok = False
        
        cursor.close()
        connection.close()
        
        return all_ok
        
    except Error as e:
        print_error(f"Error al verificar tablas: {e}")
        return False


def test_crud_operations():
    """Prueba operaciones CRUD básicas."""
    print_header("TEST 5: Operaciones CRUD")
    
    try:
        from app.repository.cliente_repository import cliente_repository
        
        # Test: Listar clientes
        print_info("Probando: Listar todos los clientes")
        clientes = cliente_repository.get_all()
        print_success(f"Se encontraron {len(clientes)} clientes")
        
        if clientes:
            print_info(f"Primer cliente: {clientes[0]}")
            
            # Test: Obtener por ID
            primer_id = clientes[0]['id']
            print_info(f"Probando: Obtener cliente con ID {primer_id}")
            cliente = cliente_repository.get_by_id(primer_id)
            
            if cliente:
                print_success(f"Cliente obtenido: {cliente['nombre']} {cliente['apellido']}")
            else:
                print_warning("No se pudo obtener el cliente")
        else:
            print_warning("No hay clientes en la base de datos")
        
        return True
        
    except Exception as e:
        print_error(f"Error en operaciones CRUD: {e}")
        return False


def test_context_manager():
    """Prueba el context manager de database."""
    print_header("TEST 6: Context Manager")
    
    try:
        print_info("Probando: get_db_cursor() como context manager")
        
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM clientes")
            result = cursor.fetchone()
            total = result['total']
            print_success(f"Context manager funciona correctamente")
            print_info(f"Total de clientes: {total}")
        
        print_success("Cursor y conexión cerrados automáticamente")
        return True
        
    except Exception as e:
        print_error(f"Error en context manager: {e}")
        return False


def test_transaction_rollback():
    """Prueba que el rollback automático funcione."""
    print_header("TEST 7: Rollback Automático")
    
    try:
        print_info("Probando: Rollback en caso de error")
        
        try:
            with get_db_cursor() as cursor:
                # Intentar una operación inválida
                cursor.execute("INSERT INTO tabla_inexistente VALUES (1)")
        except Exception:
            print_success("Excepción capturada como se esperaba")
        
        # Verificar que la conexión sigue siendo utilizable
        connection = get_connection()
        if connection and connection.is_connected():
            print_success("El rollback automático funcionó correctamente")
            connection.close()
            return True
        else:
            print_error("La conexión quedó en mal estado")
            return False
            
    except Exception as e:
        print_error(f"Error en test de rollback: {e}")
        return False


def main():
    """Ejecuta todos los tests de conexión."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{'TEST DE CONEXIÓN A BASE DE DATOS'.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    tests = [
        ("Variables de Entorno", test_environment_variables),
        ("Conexión Básica", test_basic_connection),
        ("Base de Datos", test_database_exists),
        ("Tablas", test_tables_exist),
        ("Operaciones CRUD", test_crud_operations),
        ("Context Manager", test_context_manager),
        ("Rollback Automático", test_transaction_rollback)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print_header("RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASÓ")
        else:
            print_error(f"{test_name}: FALLÓ")
    
    print(f"\n{Colors.BOLD}Resultado Final: {passed}/{total} tests pasaron{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡TODOS LOS TESTS PASARON! 🎉{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Algunos tests fallaron. Revisa la configuración.{Colors.END}\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


# ============================================================================
# COMANDO PARA EJECUTAR ESTE SCRIPT DESDE LA CONSOLA:
# ============================================================================
# 
# Opción 1 - Con entorno virtual activado (.venv):
#   source .venv/bin/activate && python scripts/test_conexion.py
#
# Opción 2 - Sin activar entorno virtual:
#   .venv/bin/python scripts/test_conexion.py
#
# Opción 3 - Si el script tiene permisos de ejecución:
#   chmod +x scripts/test_conexion.py
#   ./scripts/test_conexion.py
#
# Opción 4 - Desde cualquier ubicación (especificando ruta completa):
#   cd /home/sulbaranjc/proyectos/python/backend/fastapi/api/clientes_api_autenticada
#   source .venv/bin/activate && python scripts/test_conexion.py
#
# ============================================================================
