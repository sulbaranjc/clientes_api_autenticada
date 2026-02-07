# app/routers/clientes.py

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, cast
from mysql.connector import Error

from app.auth.deps import require_admin
from app.schemas.cliente import (
    ClienteResponse,
    ClienteCreate,
    ClienteUpdate
)
from app.repository.cliente_repository import cliente_repository

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

# =========================
# GET /clientes (PÚBLICO)
# =========================
@router.get("/", response_model=List[ClienteResponse])
def listar_clientes():
    return cliente_repository.get_all()


# =========================
# GET /clientes/{id} (PÚBLICO)
# =========================
@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int):
    cliente = cliente_repository.get_by_id(cliente_id)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    return cliente


# =========================
# POST /clientes (ADMIN)
# =========================
@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_cliente(
    cliente: ClienteCreate,
    _: dict = Depends(require_admin)
):
    try:
        nuevo_id = cliente_repository.create(cliente.model_dump())

        # Cast explícito para el tipador (create devuelve el id)
        return cliente_repository.get_by_id(cast(int, nuevo_id))

    except Error as e:
        # MySQL error code 1062 = Duplicate entry (email UNIQUE)
        if e.errno == 1062:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un cliente con ese email"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el cliente"
        )


# =========================
# PUT /clientes/{id} (ADMIN)
# =========================
@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK
)
def actualizar_cliente(
    cliente_id: int,
    cliente: ClienteUpdate,
    _: dict = Depends(require_admin)
):
    existente = cliente_repository.get_by_id(cliente_id)
    if not existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    try:
        actualizado = cliente_repository.update(cliente_id, cliente.model_dump())

        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

        return cliente_repository.get_by_id(cliente_id)

    except Error as e:
        if e.errno == 1062:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe otro cliente con ese email"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el cliente"
        )


# =========================
# DELETE /clientes/{id} (ADMIN)
# =========================
@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_cliente(
    cliente_id: int,
    _: dict = Depends(require_admin)
):
    existente = cliente_repository.get_by_id(cliente_id)
    if not existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    try:
        eliminado = cliente_repository.delete(cliente_id)

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

        return None

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el cliente"
        )
