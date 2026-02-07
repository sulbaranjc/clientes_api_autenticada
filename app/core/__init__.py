"""
Módulo core - Configuraciones y utilidades centrales.

Contiene componentes fundamentales de infraestructura como:
- Configuración de la aplicación
- Gestión de conexiones a base de datos
"""

from app.core.database import get_connection, get_db_cursor

__all__ = [
    "get_connection",
    "get_db_cursor"
]
