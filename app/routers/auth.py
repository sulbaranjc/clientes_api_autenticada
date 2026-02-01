# app/routers/auth.py
"""
Router de autenticación.

Implementa login mediante OAuth2 Password Flow
compatible con Swagger UI y JWT.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.passwords import verify_password, hash_password
from app.auth.jwt import create_access_token
from app.auth.deps import get_current_user
from app.repository.users_repo import get_user_by_username, update_user_password
from app.schemas.auth import ChangePasswordRequest, ChangePasswordResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# ======================================================
# POST /auth/login
# ======================================================
@router.post(
    "/login",
    summary="Login y generación de JWT",
    description="""
    Autenticación de usuario usando **OAuth2 Password Flow**.

    - Compatible con Swagger UI (Authorize)
    - Devuelve un JWT Bearer
    - Usa username y password
    """,
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica un usuario y devuelve un access_token JWT.
    """

    # 1️⃣ Buscar usuario
    user = get_user_by_username(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2️⃣ Verificar password
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3️⃣ Crear token
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"]
        }
    )

    # 4️⃣ Respuesta estándar OAuth2
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ======================================================
# POST /auth/cambiar-password
# ======================================================
@router.post(
    "/cambiar-password",
    response_model=ChangePasswordResponse,
    summary="Cambiar contraseña del usuario autenticado",
    description="""
    Permite que el usuario autenticado cambie su propia contraseña.

    - **Requiere autenticación:** Bearer Token JWT válido
    - **Seguridad:** Valida contraseña actual antes de actualizar
    - **Validación:** Las nuevas contraseñas deben coincidir
    - **Restricción:** Solo el usuario puede cambiar su propia contraseña
    """,
    status_code=status.HTTP_200_OK
)
def cambiar_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
) -> ChangePasswordResponse:
    """
    Cambia la contraseña del usuario actual.
    
    El usuario debe proporcionar:
    1. Su contraseña actual (para validación)
    2. La nueva contraseña (mínimo 6 caracteres)
    3. Confirmación de la nueva contraseña (debe coincidir)
    
    Returns:
        ChangePasswordResponse con mensaje de confirmación
    
    Raises:
        HTTPException 400: Si las nuevas contraseñas no coinciden
        HTTPException 401: Si la contraseña actual es incorrecta
        HTTPException 500: Si hay error al actualizar la BD
    """
    
    # 1️⃣ Obtener usuario actual desde el token
    username = current_user["username"]
    
    # 2️⃣ Validar que las nuevas contraseñas coincidan
    if payload.password_nueva != payload.password_confirmacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las nuevas contraseñas no coinciden"
        )
    
    # 3️⃣ Obtener usuario de la BD para validar contraseña actual
    user = get_user_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    # 4️⃣ Validar que la contraseña actual sea correcta
    if not verify_password(payload.password_actual, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # 5️⃣ Hashear la nueva contraseña
    new_password_hash = hash_password(payload.password_nueva)
    
    # 6️⃣ Actualizar en la BD
    success = update_user_password(username, new_password_hash)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la contraseña"
        )
    
    # 7️⃣ Respuesta exitosa
    return ChangePasswordResponse(username=username)