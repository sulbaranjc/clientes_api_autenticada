# app/routers/auth.py
"""
Router de autenticación.

Implementa login mediante OAuth2 Password Flow
compatible con Swagger UI y JWT.

NUEVAS CARACTERÍSTICAS:
- Detección de primer login
- Políticas de expiración de contraseñas
- Cambio de contraseña obligatorio
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.passwords import verify_password, hash_password
from app.auth.jwt import create_access_token
from app.auth.deps import get_current_user
from app.repository.users_repo import (
    get_user_by_username,
    update_user_password,
    check_password_expiration,
    change_user_password,
    force_password_change_by_admin
)
from app.schemas.auth import ChangePasswordRequest, ChangePasswordResponse, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


def get_client_ip(request: Request) -> str:
    """
    Obtiene la dirección IP del cliente.
    Maneja proxies y headers de forwarding.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


# ======================================================
# POST /auth/login
# ======================================================
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login y generación de JWT",
    description="""
    Autenticación de usuario usando **OAuth2 Password Flow**.

    - Compatible con Swagger UI (Authorize)
    - Devuelve un JWT Bearer con información del usuario
    - Usa username y password
    - Incluye username y rol en la respuesta para el frontend
    
    🔐 **IMPORTANTE - Políticas de Contraseñas:**
    
    El response incluye flags de seguridad que el frontend DEBE verificar:
    - `requires_password_change`: true si debe cambiar contraseña
    - `is_first_login`: true si es el primer inicio de sesión
    - `password_expired`: true si la contraseña expiró
    - `days_until_expiration`: días restantes antes de expirar
    
    Si `requires_password_change` es true, el frontend DEBE:
    1. Redirigir a la pantalla de cambio de contraseña
    2. Bloquear acceso a otras funcionalidades hasta cambiar la contraseña
    3. Mostrar mensaje apropiado según el motivo (primer login vs expiración)
    """,
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica un usuario y devuelve un access_token JWT.
    
    Incluye validación de políticas de contraseñas y
    retorna información de estado de seguridad.
    """

    # 1️⃣ Buscar usuario
    user = get_user_by_username(form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si el usuario está activo
    if not user.get("activo", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador"
        )

    # 2️⃣ Verificar password
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3️⃣ Verificar política de contraseñas
    password_status = check_password_expiration(user)

    # 4️⃣ Crear token
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "user_id": user["id"]
        }
    )

    # 5️⃣ Respuesta con información completa para el frontend
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=user["username"],
        rol=user["role"],
        requires_password_change=password_status['requires_change'],
        is_first_login=user.get('first_login', False),
        password_expired=password_status['expired'],
        days_until_expiration=password_status['days_until_expiration']
    )

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
    - **Seguridad:** Valida contraseña actual antes de actualizar (excepto en primer login)
    - **Validación:** Las nuevas contraseñas deben coincidir
    - **Restricción:** Solo el usuario puede cambiar su propia contraseña
    
    🔐 **Casos de Uso:**
    
    1. **Primer Login** (`first_login = true`):
       - `password_actual` es OPCIONAL
       - El usuario puede omitir la contraseña actual
       - Después del cambio, `first_login` se marca como FALSE
    
    2. **Cambio Normal**:
       - `password_actual` es OBLIGATORIO
       - Se valida la contraseña actual antes del cambio
    
    3. **Cambio Forzado** (`force_password_change = true`):
       - `password_actual` es OBLIGATORIO
       - Después del cambio, `force_password_change` se marca como FALSE
    
    📅 **Política de Expiración:**
    - La nueva contraseña expirará en 90 días
    - Se registra la IP desde donde se realizó el cambio
    - Se actualiza `password_changed_at` con el timestamp actual
    """,
    status_code=status.HTTP_200_OK
)
def cambiar_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
) -> ChangePasswordResponse:
    """
    Cambia la contraseña del usuario actual.
    
    Maneja diferentes escenarios:
    - Primer login: No requiere contraseña actual
    - Cambio normal: Requiere contraseña actual
    - Contraseña expirada: Requiere contraseña actual
    
    El usuario debe proporcionar:
    1. Su contraseña actual (excepto en primer login)
    2. La nueva contraseña (mínimo 6 caracteres)
    3. Confirmación de la nueva contraseña (debe coincidir)
    
    Returns:
        ChangePasswordResponse con mensaje de confirmación y timestamp
    
    Raises:
        HTTPException 400: Si las nuevas contraseñas no coinciden o validación falla
        HTTPException 401: Si la contraseña actual es incorrecta
        HTTPException 404: Si el usuario no existe
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # 4️⃣ Determinar si es primer login
    is_first_login = user.get('first_login', False)
    
    # 5️⃣ Validar contraseña actual (excepto en primer login)
    if is_first_login:
        # En primer login, password_actual es opcional
        # Si se proporciona, la validamos por seguridad
        if payload.password_actual:
            if not verify_password(payload.password_actual, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Contraseña actual incorrecta"
                )
    else:
        # En cambio normal, password_actual es OBLIGATORIO
        if not payload.password_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es requerida"
            )
        
        if not verify_password(payload.password_actual, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña actual incorrecta"
            )
    
    # 6️⃣ Validar que la nueva contraseña no sea igual a la anterior
    if payload.password_actual and verify_password(payload.password_nueva, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la anterior"
        )
    
    # 7️⃣ Hashear la nueva contraseña
    new_password_hash = hash_password(payload.password_nueva)
    
    # 8️⃣ Obtener IP del cliente
    client_ip = get_client_ip(request)
    
    # 9️⃣ Actualizar contraseña con nuevo método (incluye políticas)
    from datetime import datetime
    
    success = change_user_password(
        user_id=user["id"],
        new_password_hash=new_password_hash,
        is_first_login=is_first_login,
        client_ip=client_ip
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la contraseña"
        )
    
    # 🔟 Respuesta exitosa
    return ChangePasswordResponse(
        username=username,
        password_changed_at=datetime.now()
    )


# ======================================================
# POST /auth/admin/force-password-change/{user_id}
# ======================================================
@router.post(
    "/admin/force-password-change/{user_id}",
    summary="[ADMIN] Forzar cambio de contraseña a un usuario",
    description="""
    **[Solo Administradores]**
    
    Marca a un usuario para que deba cambiar su contraseña obligatoriamente
    en el próximo inicio de sesión.
    
    **Casos de uso:**
    - Resets de seguridad
    - Sospecha de compromiso de cuenta
    - Políticas de seguridad corporativas
    - Auditorías de seguridad
    
    **Efecto:**
    - Se activa la flag `force_password_change = TRUE`
    - En el próximo login, el usuario verá `requires_password_change: true`
    - El usuario no podrá acceder al sistema hasta cambiar su contraseña
    
    **Nota:** Este endpoint requiere rol de administrador.
    """,
    status_code=status.HTTP_200_OK,
    tags=["Auth", "Admin"]
)
def admin_force_password_change(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Fuerza a un usuario a cambiar su contraseña en el próximo login.
    
    Args:
        user_id: ID del usuario al que se le forzará el cambio de contraseña
        current_user: Usuario autenticado (debe ser admin)
    
    Returns:
        Mensaje de confirmación
    
    Raises:
        HTTPException 403: Si el usuario no es administrador
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si hay error al actualizar
    """
    
    # Verificar que el usuario actual sea admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden forzar cambios de contraseña"
        )
    
    # Forzar cambio de contraseña
    success = force_password_change_by_admin(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado"
        )
    
    return {
        "mensaje": f"El usuario con ID {user_id} deberá cambiar su contraseña en el próximo inicio de sesión",
        "user_id": user_id,
        "forced_by": current_user["username"]
    }