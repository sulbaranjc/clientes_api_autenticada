from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    """
    Respuesta del endpoint de login con información de sesión
    y estado de seguridad del usuario.
    """
    access_token: str
    token_type: str = "bearer"
    username: str
    rol: str
    
    # 🔐 Nuevos campos de política de contraseñas
    requires_password_change: bool = False
    password_expired: bool = False
    days_until_expiration: Optional[int] = None
    is_first_login: bool = False


class ChangePasswordRequest(BaseModel):
    """
    Schema para cambiar la contraseña del usuario autenticado.
    
    El usuario solo puede cambiar su propia contraseña.
    - En primer login: password_actual es OPCIONAL
    - En cambio normal: password_actual es OBLIGATORIO
    """
    password_actual: Optional[str] = Field(
        None,
        description="Contraseña actual del usuario (opcional en primer login)",
        min_length=6
    )
    password_nueva: str = Field(
        ...,
        description="Nueva contraseña (mínimo 6 caracteres)",
        min_length=6
    )
    password_confirmacion: str = Field(
        ...,
        description="Confirmación de la nueva contraseña",
        min_length=6
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "password_actual": "admin123",
                "password_nueva": "nuevaPassword456",
                "password_confirmacion": "nuevaPassword456"
            }
        }


class ChangePasswordResponse(BaseModel):
    """Respuesta después de cambiar contraseña."""
    mensaje: str = "Contraseña actualizada exitosamente"
    username: str
    password_changed_at: datetime
