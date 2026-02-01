from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    """
    Schema para cambiar la contraseña del usuario autenticado.
    
    El usuario solo puede cambiar su propia contraseña.
    """
    password_actual: str = Field(
        ...,
        description="Contraseña actual del usuario",
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
