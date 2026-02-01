# 🔐 GUÍA TÉCNICA DE AUTENTICACIÓN DEL PROYECTO

## 📖 Tabla de Contenidos
1. [Arquitectura](#arquitectura)
2. [Flujo de Autenticación](#flujo)
3. [Hashing de Contraseñas](#hashing)
4. [JWT (Token)](#jwt)
5. [Estructura de Datos](#datos)
6. [Endpoints Disponibles](#endpoints)

---

## <a name="arquitectura"></a>🏗️ ARQUITECTURA

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENTE (Navegador/API)            │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │  FastAPI Application             │
        │  (app/main.py)                   │
        └──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌──────────────────────┐          ┌──────────────────────┐
│  Router: /auth       │          │  Router: /clientes   │
│  (app/routers/auth)  │          │  (app/routers/...)   │
└──────────────────────┘          └──────────────────────┘
        │                                     │
        ▼                                     ▼
    ┌───────────────────────────────────────────────┐
    │         Dependencias (Dependencies)           │
    │  • auth.deps (Validar JWT)                   │
    │  • auth.jwt (Generar/Decodificar)            │
    │  • auth.passwords (Hash/Verify)              │
    └───────────────────────────────────────────────┘
        │
        ▼
    ┌───────────────────────────────────────────────┐
    │           Base de Datos (MySQL)               │
    │  • Tabla usuarios (username, password_hash)   │
    │  • Tabla roles (admin, lector)                │
    └───────────────────────────────────────────────┘
```

---

## <a name="flujo"></a>🔄 FLUJO DE AUTENTICACIÓN

### 1. LOGIN (Obtener Token)

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123

                    │
                    ▼
        ┌──────────────────────────────────┐
        │  app/routers/auth.py :: login()  │
        └──────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    ┌───────────────────┐  ┌──────────────────────┐
    │ Buscar usuario en │  │ Verificar contraseña │
    │ BD por username   │  │ con bcrypt           │
    └─────────┬─────────┘  └──────────┬───────────┘
              │                       │
              ▼                       ▼
    ┌──────────────────────────────────────┐
    │ create_access_token()                │
    │ Genera JWT con claims:               │
    │  • sub: username                     │
    │  • role: rol del usuario             │
    │  • exp: fecha expiración             │
    └──────────────┬───────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────┐
        │  Response 200 OK                 │
        │  {                               │
        │    "access_token": "eyJ...",    │
        │    "token_type": "bearer"        │
        │  }                               │
        └──────────────────────────────────┘
```

### 2. USAR TOKEN (Acceder a Recursos Protegidos)

```
GET /clientes/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

                    │
                    ▼
        ┌──────────────────────────────────┐
        │  app/auth/deps.py                │
        │  get_current_user()              │
        └──────────────────────────────────┘
                    │
                    ├─ Extrae token del header
                    │
                    ▼
        ┌──────────────────────────────────┐
        │  decode_access_token()           │
        │  Valida JWT y extrae claims      │
        └──────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    ✅ Token válido       ❌ Token inválido
       │                      │
       ▼                      ▼
   Procesa request      Response 401
   ✓ Permite acceso     (Unauthorized)
```

---

## <a name="hashing"></a>🔒 HASHING DE CONTRASEÑAS

### Algoritmo: BCrypt

**¿Qué es BCrypt?**
- Algoritmo de hashing criptográfico unidireccional
- Incluye "salt" aleatorio (protección contra rainbow tables)
- Adaptativo: se vuelve más lento con el tiempo (CPU improvements)
- Estándar de la industria para contraseñas

### Estructura del Hash BCrypt

```
$2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlLAe
├─┘ ├┘├─────────────────┬──────────────────────────────────────┤
│   │ │                 │                                       │
│   │ │                 └─ Hash (salted)                       │
│   │ └─ Costo: 2^12 = 4096 iteraciones
│   └─ Algoritmo: 2b = bcrypt
└─ Versión: $
```

### Proceso de Verificación

```
┌──────────────────────────────────────────────┐
│ verify_password("admin123", hash_from_db)    │
└──────────────────┬───────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
    ▼                             ▼
Hash("admin123")              Hash_BD
con salt del hash_BD          (extraído)
    │                             │
    └─────────────┬───────────────┘
                  │
                  ▼
            ¿Coinciden?
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
      ✅ TRUE            ❌ FALSE
    Credenciales OK    Credenciales inválidas
```

### Código en `app/auth/passwords.py`

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],     # Usa solo bcrypt
    deprecated="auto"       # Reconoce hashes viejos pero crea nuevos con bcrypt
)

def hash_password(password: str) -> str:
    """Convierte contraseña plana en hash bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara contraseña plana con hash almacenado"""
    return pwd_context.verify(plain_password, hashed_password)
```

---

## <a name="jwt"></a>🎫 JWT (JSON Web Token)

### Estructura de un JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcwMzAwMDAwMH0.
o3FvzAeL9p8R4-Kxq1N2M6Q5T7U8V9W0X1Y2Z3A4B5C
├─ HEADER ────────────────────┤ PAYLOAD ────────────────────┤ SIGNATURE ────┤

Header (Base64):
{
  "alg": "HS256",    // Algoritmo de firma
  "typ": "JWT"       // Tipo de token
}

Payload (Base64):
{
  "sub": "admin",           // Subject (username)
  "role": "admin",          // Rol del usuario
  "exp": 1703000000         // Expiración (timestamp)
}

Signature (HMAC-SHA256):
HMAC_SHA256(
  base64(header) + "." + base64(payload),
  SECRET_KEY
)
```

### Ventajas de JWT

✅ **Stateless:** No requiere almacenamiento en servidor  
✅ **Seguro:** Firmado criptográficamente  
✅ **Portable:** Se envía en cada request  
✅ **Escalable:** Ideal para APIs distribuidas  

### Configuración en `app/core/config.py`

```python
class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"                        # HMAC-SHA256
    ACCESS_TOKEN_EXPIRE_MINUTES = 60           # Expira en 1 hora
```

---

## <a name="datos"></a>📊 ESTRUCTURA DE DATOS

### Tabla: `usuarios`

```sql
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,           -- Identificador único
  email VARCHAR(150) NOT NULL UNIQUE,             -- Email único
  password_hash VARCHAR(255) NOT NULL,            -- Hash bcrypt (NO contraseña plana)
  rol_id INT NOT NULL,                            -- Foreign key a roles
  activo TINYINT NOT NULL DEFAULT 1,              -- 1=activo, 0=inactivo
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha creación
  actualizado_en TIMESTAMP NULL,                  -- Fecha actualización
  CONSTRAINT fk_usuarios_roles 
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);
```

### Tabla: `roles`

```sql
CREATE TABLE roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE,    -- 'admin' o 'lector'
  descripcion VARCHAR(150)                -- Descripción del rol
);
```

### Datos Iniciales

```sql
-- Roles
INSERT INTO roles (nombre, descripcion) VALUES
  ('admin', 'Puede crear, modificar y eliminar clientes'),
  ('lector', 'Solo puede consultar y filtrar clientes');

-- Usuarios
-- admin (contraseña: admin123)
INSERT INTO usuarios (username, email, password_hash, rol_id) VALUES
  ('admin', 'admin@test.com', 
   '$2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlLAe', 1);

-- lector (contraseña: lector123)
INSERT INTO usuarios (username, email, password_hash, rol_id) VALUES
  ('lector', 'lector@test.com', 
   '$2b$12$IYBfsBcTC4ZM74Oeez98EemoXhThcPWJCd7DBpQcVIItA1uem4wVm', 2);
```

### Objeto Usuario en Python (Dictado desde BD)

```python
{
    "username": "admin",
    "email": "admin@test.com",
    "password_hash": "$2b$12$o00cK68S.E1NdDf5...",
    "role": "admin"
}
```

---

## <a name="endpoints"></a>🌐 ENDPOINTS DISPONIBLES

### 1. Login - Obtener Token

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

Response 401:
{
  "detail": "Credenciales inválidas"
}
```

### 2. Obtener Clientes (Requiere Token)

```
GET /clientes/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response 200:
[
  {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan.perez@example.com",
    ...
  },
  ...
]

Response 401:
{
  "detail": "No autorizado"
}
```

---

## 🛡️ SEGURIDAD

### ✅ Lo que está bien
- ✅ Contraseñas hasheadas con bcrypt (unidireccional)
- ✅ JWT con firma criptográfica
- ✅ Token con expiración
- ✅ Salt automático en bcrypt
- ✅ SECRET_KEY desde variables de entorno

### ⚠️ Lo que se debe mejorar en PRODUCCIÓN
- ⚠️ HTTPS obligatorio (no HTTP)
- ⚠️ CORS más restrictivo (no allow_origins=["*"])
- ⚠️ Rate limiting en /auth/login
- ⚠️ Refresh tokens además de access tokens
- ⚠️ Auditoría de intentos fallidos
- ⚠️ Password requirements más fuertes
- ⚠️ 2FA (Two-Factor Authentication)

---

## 🧪 TROUBLESHOOTING

### Problema: "Credenciales inválidas" pero el usuario existe

**Causas posibles:**
1. Hash bcrypt incorrecto en BD
2. Contraseña no corresponde al hash
3. Usuario no está `activo` (activo=0)

**Solución:**
- Regenerar hash: `pwd_context.hash("contraseña")`
- Verificar que `activo=1` en BD
- Ejecutar init_db.sql nuevamente

### Problema: "Token inválido o expirado"

**Causas posibles:**
1. Token expiró (>60 minutos por defecto)
2. SECRET_KEY cambió
3. Token malformado

**Solución:**
- Hacer login nuevamente para obtener token fresco
- Verificar SECRET_KEY en `.env`

### Problema: No se puede conectar a BD

**Causas posibles:**
1. Credenciales MySQL incorrectas
2. MySQL no está ejecutándose
3. Base de datos no existe

**Solución:**
```bash
mysql -u profesor -p4688 -e "SELECT * FROM clientes_autenticado_db.usuarios"
```

---

## 📚 REFERENCIAS

- [Passlib Documentation](https://passlib.readthedocs.io/)
- [JWT Introduction](https://jwt.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [BCrypt Explained](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Última actualización:** 1 de febrero de 2026  
**Versión:** 1.0
