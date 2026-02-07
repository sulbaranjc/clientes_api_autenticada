"""
Módulo de gestión de conexiones a la base de datos.
Proporciona funciones para obtener conexiones MySQL configuradas.
"""

import mysql.connector
from mysql.connector import Error
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
from typing import Optional, Union
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()


def get_connection() -> Optional[Union[PooledMySQLConnection, MySQLConnectionAbstract]]:
    """
    Establece y retorna una conexión a MySQL.
    
    Returns:
        Conexión activa o None si falla.
        
    Raises:
        Exception: Si las variables de entorno no están configuradas.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            # Configuraciones adicionales recomendadas
            autocommit=False  # Control explícito de transacciones
        )
        return connection
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return None


@contextmanager
def get_db_cursor(dictionary: bool = True):
    """
    Context manager para manejo automático de conexión y cursor.
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM clientes")
            results = cursor.fetchall()
    
    Args:
        dictionary: Si True, retorna resultados como diccionarios.
        
    Yields:
        Cursor de MySQL configurado.
        
    Raises:
        Exception: Si no se puede establecer conexión.
    """
    conn = get_connection()
    if not conn:
        raise Exception("No se pudo establecer conexión con la base de datos")
    
    cursor = conn.cursor(dictionary=dictionary)
    
    try:
        yield cursor
        conn.commit()  # Auto-commit si todo salió bien
    except Exception as e:
        conn.rollback()  # Rollback automático en caso de error
        raise e
    finally:
        cursor.close()
        conn.close()
