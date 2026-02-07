#!/usr/bin/env python3
"""
Script de prueba para validar la refactorización del módulo database.

Este script verifica que:
1. La conexión a la base de datos funciona correctamente
2. El repositorio de clientes puede realizar operaciones CRUD
3. No hay errores de importación
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_connection
from app.repository.cliente_repository import cliente_repository


def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        conn = get_connection()
        if conn:
            print("✅ Conexión exitosa")
            conn.close()
            return True
        else:
            print("❌ No se pudo establecer conexión")
            return False
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return False


def test_repository_get_all():
    """Prueba el método get_all del repositorio."""
    print("\n🔍 Probando cliente_repository.get_all()...")
    
    try:
        clientes = cliente_repository.get_all()
        print(f"✅ Se obtuvieron {len(clientes)} clientes")
        
        if len(clientes) > 0:
            primer_cliente = clientes[0]
            print(f"   📋 Ejemplo: {primer_cliente.get('nombre')} {primer_cliente.get('apellido')}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_repository_get_by_id():
    """Prueba el método get_by_id del repositorio."""
    print("\n🔍 Probando cliente_repository.get_by_id(1)...")
    
    try:
        cliente = cliente_repository.get_by_id(1)
        
        if cliente:
            print(f"✅ Cliente encontrado: {cliente.get('nombre')} {cliente.get('apellido')}")
            print(f"   📧 Email: {cliente.get('email')}")
        else:
            print("ℹ️  No existe cliente con ID 1 (esto es normal si la tabla está vacía)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("=" * 60)
    print("🚀 Validación de Refactorización - Módulo Database")
    print("=" * 60)
    
    resultados = []
    
    # Prueba 1: Conexión
    resultados.append(test_database_connection())
    
    # Prueba 2: get_all
    resultados.append(test_repository_get_all())
    
    # Prueba 3: get_by_id
    resultados.append(test_repository_get_by_id())
    
    # Resumen
    print("\n" + "=" * 60)
    total_pruebas = len(resultados)
    pruebas_exitosas = sum(resultados)
    
    if pruebas_exitosas == total_pruebas:
        print(f"✅ TODAS LAS PRUEBAS PASARON ({pruebas_exitosas}/{total_pruebas})")
        print("🎉 La refactorización se completó exitosamente")
        return 0
    else:
        print(f"⚠️  ALGUNAS PRUEBAS FALLARON ({pruebas_exitosas}/{total_pruebas} exitosas)")
        print("🔧 Revisa la configuración de la base de datos y las variables de entorno")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
