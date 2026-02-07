"""
Módulo de repositorios de acceso a datos.

Contiene las clases Repository que encapsulan las operaciones
de base de datos para cada entidad del dominio.
"""

from app.repository.cliente_repository import cliente_repository, ClienteRepository

__all__ = [
    "cliente_repository",
    "ClienteRepository"
]
