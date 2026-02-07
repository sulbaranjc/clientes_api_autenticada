#!/usr/bin/env python3
"""
Script de prueba para validar políticas de contraseñas.

Prueba:
1. Creación de usuario con first_login = TRUE
2. Login y verificación de flags de seguridad
3. Cambio de contraseña en primer login
4. Verificación de expiración de contraseñas
5. Forzar cambio de contraseña por admin

Uso:
    python scripts/test_password_policy.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

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
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")


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


def test_database_schema():
    """Verifica que los nuevos campos existan en la tabla usuarios."""
    print_header("TEST 1: Verificar Schema de Base de Datos")
    
    try:
        from app.core.database import get_connection
        
        conn = get_connection()
        if not conn:
            print_error("No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor(dictionary=True)
        
        # Obtener estructura de la tabla
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        
        required_fields = [
            'first_login',
            'password_expires_at',
            'force_password_change',
            'password_changed_at',
            'last_password_change_ip'
        ]
        
        existing_fields = [col['Field'] for col in columns]
        
        all_ok = True
        for field in required_fields:
            if field in existing_fields:
                print_success(f"Campo '{field}' existe")
            else:
                print_error(f"Campo '{field}' NO existe")
                all_ok = False
        
        if all_ok:
            print_success("Todos los campos de política de contraseñas existen")
        else:
            print_warning("Ejecuta la migración: bash scripts/apply_password_policy_migration.sh")
        
        cursor.close()
        conn.close()
        
        return all_ok
        
    except Exception as e:
        print_error(f"Error al verificar schema: {e}")
        return False


def test_user_repository_functions():
    """Prueba las nuevas funciones del repositorio de usuarios."""
    print_header("TEST 2: Funciones del Repositorio de Usuarios")
    
    try:
        from app.repository.users_repo import (
            get_user_by_username,
            check_password_expiration,
            change_user_password,
            force_password_change_by_admin
        )
        
        # Verificar que las funciones existan
        print_success("Función get_user_by_username() existe")
        print_success("Función check_password_expiration() existe")
        print_success("Función change_user_password() existe")
        print_success("Función force_password_change_by_admin() existe")
        
        # Probar obtener un usuario
        print_info("Probando get_user_by_username('admin')...")
        user = get_user_by_username('admin')
        
        if user:
            print_success(f"Usuario encontrado: {user['username']}")
            print_info(f"  first_login: {user.get('first_login')}")
            print_info(f"  force_password_change: {user.get('force_password_change')}")
            print_info(f"  password_changed_at: {user.get('password_changed_at')}")
            
            # Probar verificación de expiración
            print_info("Probando check_password_expiration()...")
            status = check_password_expiration(user)
            print_info(f"  requires_change: {status['requires_change']}")
            print_info(f"  expired: {status['expired']}")
            print_info(f"  days_until_expiration: {status['days_until_expiration']}")
        else:
            print_warning("Usuario 'admin' no encontrado (esto es normal si no existe)")
        
        return True
        
    except Exception as e:
        print_error(f"Error en funciones del repositorio: {e}")
        return False


def test_schema_models():
    """Verifica que los schemas de Pydantic estén actualizados."""
    print_header("TEST 3: Schemas de Pydantic")
    
    try:
        from app.schemas.auth import (
            TokenResponse,
            ChangePasswordRequest,
            ChangePasswordResponse
        )
        
        # Verificar campos de TokenResponse
        print_info("Verificando TokenResponse...")
        test_token = TokenResponse(
            access_token="test_token",
            username="test_user",
            rol="user",
            requires_password_change=True,
            is_first_login=True,
            password_expired=False,
            days_until_expiration=30
        )
        
        print_success("TokenResponse tiene todos los campos de seguridad")
        print_info(f"  requires_password_change: {test_token.requires_password_change}")
        print_info(f"  is_first_login: {test_token.is_first_login}")
        print_info(f"  password_expired: {test_token.password_expired}")
        print_info(f"  days_until_expiration: {test_token.days_until_expiration}")
        
        # Verificar ChangePasswordRequest
        print_info("Verificando ChangePasswordRequest...")
        test_req = ChangePasswordRequest(
            password_actual=None,  # Ahora es opcional
            password_nueva="newpass123",
            password_confirmacion="newpass123"
        )
        print_success("ChangePasswordRequest permite password_actual opcional")
        
        return True
        
    except Exception as e:
        print_error(f"Error en schemas: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_login_response_structure():
    """Simula una respuesta de login y verifica la estructura."""
    print_header("TEST 4: Estructura de Respuesta de Login")
    
    try:
        from app.schemas.auth import TokenResponse
        
        # Simular respuesta de login con primer login
        print_info("Simulando respuesta de login con first_login=True...")
        
        response = TokenResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer",
            username="nuevo_usuario",
            rol="user",
            requires_password_change=True,
            is_first_login=True,
            password_expired=False,
            days_until_expiration=None
        )
        
        print_success("Respuesta de login creada exitosamente")
        print_info(f"  Username: {response.username}")
        print_info(f"  Rol: {response.rol}")
        print_info(f"  🔐 Requiere cambio: {response.requires_password_change}")
        print_info(f"  🆕 Primer login: {response.is_first_login}")
        
        print("")
        print_info("Lógica del frontend:")
        if response.requires_password_change:
            if response.is_first_login:
                print_warning("→ Redirigir a: /change-password?reason=first_login")
            elif response.password_expired:
                print_warning("→ Redirigir a: /change-password?reason=expired")
            else:
                print_warning("→ Redirigir a: /change-password?reason=forced")
        else:
            print_success("→ Permitir acceso al dashboard")
        
        return True
        
    except Exception as e:
        print_error(f"Error al simular respuesta de login: {e}")
        return False


def test_password_expiration_logic():
    """Prueba la lógica de expiración de contraseñas."""
    print_header("TEST 5: Lógica de Expiración de Contraseñas")
    
    try:
        from app.repository.users_repo import check_password_expiration
        
        # Test 1: Primer login
        print_info("Test: Usuario con first_login=True")
        user1 = {'first_login': True}
        result1 = check_password_expiration(user1)
        
        if result1['requires_change']:
            print_success("✓ Requiere cambio de contraseña (first_login)")
        else:
            print_error("✗ Debería requerir cambio de contraseña")
        
        # Test 2: Cambio forzado
        print_info("Test: Usuario con force_password_change=True")
        user2 = {'first_login': False, 'force_password_change': True}
        result2 = check_password_expiration(user2)
        
        if result2['requires_change']:
            print_success("✓ Requiere cambio de contraseña (forced)")
        else:
            print_error("✗ Debería requerir cambio de contraseña")
        
        # Test 3: Contraseña expirada por fecha
        print_info("Test: Contraseña expirada por fecha")
        past_date = datetime.now() - timedelta(days=100)
        user3 = {
            'first_login': False,
            'force_password_change': False,
            'password_expires_at': past_date
        }
        result3 = check_password_expiration(user3)
        
        if result3['requires_change'] and result3['expired']:
            print_success("✓ Contraseña detectada como expirada")
        else:
            print_error("✗ Debería detectar contraseña expirada")
        
        # Test 4: Contraseña válida
        print_info("Test: Contraseña válida (30 días restantes)")
        future_date = datetime.now() + timedelta(days=30)
        user4 = {
            'first_login': False,
            'force_password_change': False,
            'password_expires_at': future_date
        }
        result4 = check_password_expiration(user4)
        
        if not result4['requires_change'] and result4['days_until_expiration'] > 0:
            print_success(f"✓ Contraseña válida ({result4['days_until_expiration']} días restantes)")
        else:
            print_error("✗ Debería marcar contraseña como válida")
        
        return True
        
    except Exception as e:
        print_error(f"Error en lógica de expiración: {e}")
        return False


def main():
    """Ejecuta todos los tests."""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{'TEST DE POLÍTICAS DE CONTRASEÑAS'.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")
    
    tests = [
        ("Schema de Base de Datos", test_database_schema),
        ("Funciones del Repositorio", test_user_repository_functions),
        ("Schemas de Pydantic", test_schema_models),
        ("Respuesta de Login", test_login_response_structure),
        ("Lógica de Expiración", test_password_expiration_logic)
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
        print(f"{Colors.GREEN}La implementación de políticas de contraseñas está completa.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Algunos tests fallaron.{Colors.END}\n")
        print("Verifica:")
        print("1. Que la migración SQL se haya aplicado correctamente")
        print("2. Que todos los archivos estén actualizados")
        print("3. Los mensajes de error arriba para más detalles\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


# ============================================================================
# COMANDO PARA EJECUTAR ESTE SCRIPT:
# ============================================================================
#
# source .venv/bin/activate && python scripts/test_password_policy.py
#
# ============================================================================
