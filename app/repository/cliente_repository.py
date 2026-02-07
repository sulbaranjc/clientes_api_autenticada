"""
Repositorio de datos para la entidad Cliente.
Contiene todas las operaciones CRUD sobre la tabla 'clientes'.
"""

from typing import Optional, List, Dict, Any, cast
from mysql.connector import Error
from app.core.database import get_connection


class ClienteRepository:
    """
    Clase que encapsula las operaciones de base de datos
    para la tabla 'clientes'.
    
    Implementa el patrón Repository para separar la lógica de acceso
    a datos de la lógica de negocio.
    """
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        Obtiene todos los clientes de la base de datos.
        
        Returns:
            Lista de diccionarios con datos de clientes ordenados por ID descendente.
            
        Raises:
            Exception: Si no se puede conectar a la BD.
        """
        conn = get_connection()
        if not conn:
            raise Exception("No se pudo conectar a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
            resultados = cursor.fetchall()
            return cast(List[Dict[str, Any]], resultados)
        finally:
            cursor.close()
            conn.close()
    
    
    @staticmethod
    def get_by_id(cliente_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca un cliente por su ID.
        
        Args:
            cliente_id: ID del cliente a buscar.
            
        Returns:
            Diccionario con datos del cliente o None si no existe.
            
        Raises:
            Exception: Si no se puede conectar a la BD.
        """
        conn = get_connection()
        if not conn:
            raise Exception("No se pudo conectar a la base de datos")
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(
                "SELECT * FROM clientes WHERE id = %s", 
                (cliente_id,)
            )
            resultado = cursor.fetchone()
            return cast(Optional[Dict[str, Any]], resultado)
        finally:
            cursor.close()
            conn.close()
    
    
    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """
        Inserta un nuevo cliente en la base de datos.
        
        Args:
            data: Diccionario con datos del cliente (nombre, apellido, email, etc).
            
        Returns:
            ID del cliente recién creado.
            
        Raises:
            Exception: Si no se puede conectar a la BD.
            Error: Si hay error de MySQL (ej: email duplicado - código 1062).
        """
        conn = get_connection()
        if not conn:
            raise Exception("No se pudo conectar a la base de datos")
        
        cursor = conn.cursor()
        
        try:
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
            if new_id is None:
                raise Exception("No se pudo obtener el ID del registro insertado")
            
            return new_id
            
        except Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    
    @staticmethod
    def update(cliente_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza un cliente existente.
        
        Args:
            cliente_id: ID del cliente a actualizar.
            data: Diccionario con nuevos datos del cliente.
            
        Returns:
            True si se actualizó al menos un registro, False si no existe.
            
        Raises:
            Exception: Si no se puede conectar a la BD.
            Error: Si hay error de MySQL (ej: email duplicado - código 1062).
        """
        conn = get_connection()
        if not conn:
            raise Exception("No se pudo conectar a la base de datos")
        
        cursor = conn.cursor()
        
        try:
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
            
            return cursor.rowcount > 0
            
        except Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    
    @staticmethod
    def delete(cliente_id: int) -> int:
        """
        Elimina un cliente de la base de datos.
        
        Args:
            cliente_id: ID del cliente a eliminar.
            
        Returns:
            Número de registros eliminados (1 si existía, 0 si no).
            
        Raises:
            Exception: Si no se puede conectar a la BD.
        """
        conn = get_connection()
        if not conn:
            raise Exception("No se pudo conectar a la base de datos")
        
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM clientes WHERE id=%s", 
                (cliente_id,)
            )
            conn.commit()
            
            return cursor.rowcount
            
        finally:
            cursor.close()
            conn.close()


# Instancia única del repositorio (Singleton pattern)
# Puede importarse directamente: from app.repository.cliente_repository import cliente_repository
cliente_repository = ClienteRepository()
