# app/database.py

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def get_all_clientes():
    conn = get_connection()
    if not conn:
        raise Exception("No se pudo conectar a la base de datos")
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clientes")
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()
    return resultados


def get_cliente_by_id(cliente_id: int):
    conn = get_connection()
    if not conn:
        raise Exception("No se pudo conectar a la base de datos")
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()
    return resultado


def create_cliente(data: dict):
    conn = get_connection()
    if not conn:
        raise Exception("No se pudo conectar a la base de datos")
    
    cursor = conn.cursor()

    query = """
        INSERT INTO clientes (nombre, apellido, email, telefono, direccion)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        data["nombre"],
        data["apellido"],
        data["email"],
        data.get("telefono"),
        data.get("direccion")
    )

    cursor.execute(query, values)
    conn.commit()

    new_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return new_id


def update_cliente(cliente_id: int, data: dict) -> bool:
    conn = get_connection()
    if not conn:
        raise Exception("No se pudo conectar a la base de datos")
    
    cursor = conn.cursor()

    query = """
        UPDATE clientes
        SET nombre=%s, apellido=%s, email=%s, telefono=%s, direccion=%s
        WHERE id=%s
    """

    values = (
        data["nombre"],
        data["apellido"],
        data["email"],
        data.get("telefono") if data.get("telefono") else None,
        data.get("direccion") if data.get("direccion") else None,
        cliente_id
    )

    cursor.execute(query, values)
    conn.commit()

    actualizado = cursor.rowcount > 0

    cursor.close()
    conn.close()

    return actualizado


def delete_cliente(cliente_id: int):
    conn = get_connection()
    if not conn:
        raise Exception("No se pudo conectar a la base de datos")
    
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
    conn.commit()

    affected = cursor.rowcount

    cursor.close()
    conn.close()
    return affected
