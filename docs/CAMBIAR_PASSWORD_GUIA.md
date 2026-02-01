# 📚 Guía: Cambiar Contraseña de Usuario

## Descripción General

Esta guía explica cómo **cambiar la contraseña de un usuario autenticado** en la API FastAPI.

El endpoint `/auth/cambiar-password` permite que:
- ✅ El usuario autenticado cambie **su propia contraseña**
- ✅ Valide su contraseña actual antes de hacer cambios
- ✅ Confirme que las nuevas contraseñas coincidan
- ❌ **No** permita que un usuario cambie la contraseña de otro

## Ubicación del Código

```
proyecto/
├── app/
│   ├── routers/
│   │   └── auth.py                    ← Endpoint POST /auth/cambiar-password
│   ├── schemas/
│   │   └── auth.py                    ← ChangePasswordRequest, ChangePasswordResponse
│   ├── repository/
│   │   └── users_repo.py              ← update_user_password()
│   └── auth/
│       ├── deps.py                    ← get_current_user() (validación JWT)
│       ├── passwords.py               ← hash_password(), verify_password()
│       └── jwt.py                     ← decode_access_token()
└── docs/
    └── CAMBIAR_PASSWORD_GUIA.md       ← Esta guía
```

## Arquitectura del Flujo

```
Cliente (Postman/curl)
    ↓
    POST /auth/cambiar-password
    Header: Authorization: Bearer {TOKEN}
    Body: { password_actual, password_nueva, password_confirmacion }
    ↓
get_current_user(token)  ← Valida JWT, obtiene username
    ↓
get_user_by_username()   ← Obtiene usuario actual de BD
    ↓
verify_password()        ← Valida contraseña actual contra hash
    ↓
hash_password()          ← Hashea la nueva contraseña con bcrypt
    ↓
update_user_password()   ← Actualiza en BD
    ↓
Return 200 + mensaje     ← Confirmación de éxito
```

## Arquitectura de Seguridad

### 🔐 Validaciones Incluidas

1. **Autenticación JWT:** Usuario debe estar logueado (Bearer Token válido)
2. **Identidad Confirmada:** Solo puede cambiar su propia contraseña
3. **Contraseña Actual Validada:** Debe proporcionar contraseña actual correcta
4. **Coincidencia de Contraseña:** Las nuevas contraseñas deben ser idénticas
5. **Hash Seguro:** Usa bcrypt con 12 iteraciones
6. **Timestamp:** Se registra la hora de actualización en BD

### 📊 Validaciones de Entrada

| Campo | Validación |
|-------|-----------|
| `password_actual` | Mínimo 6 caracteres, debe ser correcta |
| `password_nueva` | Mínimo 6 caracteres, diferente a actual |
| `password_confirmacion` | Debe coincidir exactamente con password_nueva |
| `Authorization Header` | Token JWT válido y no expirado |

## Schema del Endpoint

### 📥 Request (ChangePasswordRequest)

```json
{
  "password_actual": "admin123",
  "password_nueva": "nuevaPassword456",
  "password_confirmacion": "nuevaPassword456"
}
```

### 📤 Response (ChangePasswordResponse)

**Éxito (200 OK):**
```json
{
  "mensaje": "Contraseña actualizada exitosamente",
  "username": "admin"
}
```

**Error: Contraseñas no coinciden (400):**
```json
{
  "detail": "Las nuevas contraseñas no coinciden"
}
```

**Error: Contraseña actual incorrecta (401):**
```json
{
  "detail": "Contraseña actual incorrecta"
}
```

**Error: Token inválido (401):**
```json
{
  "detail": "Token inválido o expirado"
}
```

**Error: Error en BD (500):**
```json
{
  "detail": "Error al actualizar la contraseña"
}
```

## Cómo Usar desde Consola (curl)

### Paso 1: Obtener Token JWT

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### Paso 2: Cambiar Contraseña

```bash
curl -X POST "http://localhost:8000/auth/cambiar-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password_actual": "admin123",
    "password_nueva": "miNuevaPassword2024",
    "password_confirmacion": "miNuevaPassword2024"
  }' | python3 -m json.tool
```

**Respuesta esperada:**
```json
{
  "mensaje": "Contraseña actualizada exitosamente",
  "username": "admin"
}
```

### Paso 3: Verificar - Login con Nueva Contraseña

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=miNuevaPassword2024" | python3 -m json.tool
```

**Debe devolver un nuevo token JWT ✅**

## Ejemplo Completo de Prueba

Copia y pega este script para probar el flujo completo:

### Script: `test_cambiar_password.sh`

```bash
#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"
USERNAME="admin"
PASSWORD_ACTUAL="admin123"
PASSWORD_NUEVA="nuevoAdmin2024"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TEST: Cambiar Contraseña de Usuario${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Paso 1: Login inicial
echo -e "${BLUE}1️⃣ Obtener token inicial...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD_ACTUAL")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Error: No se pudo obtener el token${NC}"
    echo "Respuesta: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Token obtenido${NC}"
echo -e "   Token: ${TOKEN:0:50}...\n"

# Paso 2: Cambiar contraseña
echo -e "${BLUE}2️⃣ Cambiar contraseña...${NC}"
CHANGE_RESPONSE=$(curl -s -X POST "$API_URL/auth/cambiar-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"password_actual\": \"$PASSWORD_ACTUAL\",
    \"password_nueva\": \"$PASSWORD_NUEVA\",
    \"password_confirmacion\": \"$PASSWORD_NUEVA\"
  }")

echo -e "   Respuesta:"
echo "$CHANGE_RESPONSE" | python3 -m json.tool

# Verificar éxito
if echo "$CHANGE_RESPONSE" | grep -q "Contraseña actualizada"; then
    echo -e "${GREEN}✅ Contraseña cambiada exitosamente${NC}\n"
else
    echo -e "${RED}❌ Error al cambiar contraseña${NC}\n"
    exit 1
fi

# Paso 3: Intentar login con contraseña antigua (debe fallar)
echo -e "${BLUE}3️⃣ Verificar: Login con contraseña antigua (debe fallar)...${NC}"
OLD_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD_ACTUAL")

if echo "$OLD_LOGIN" | grep -q "Credenciales inválidas"; then
    echo -e "${GREEN}✅ Correcto: Contraseña antigua rechazada${NC}\n"
else
    echo -e "${RED}❌ Error: Contraseña antigua aún funciona${NC}\n"
    exit 1
fi

# Paso 4: Login con contraseña nueva (debe funcionar)
echo -e "${BLUE}4️⃣ Verificar: Login con contraseña nueva...${NC}"
NEW_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD_NUEVA")

NEW_TOKEN=$(echo $NEW_LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$NEW_TOKEN" ]; then
    echo -e "${GREEN}✅ Correcto: Login exitoso con nueva contraseña${NC}\n"
else
    echo -e "${RED}❌ Error: No se puede login con nueva contraseña${NC}\n"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✨ TODAS LAS PRUEBAS PASARON ✨${NC}"
echo -e "${GREEN}========================================\n${NC}"

# Mostrar resumen
echo "Resumen:"
echo "  • Usuario: $USERNAME"
echo "  • Contraseña anterior: $PASSWORD_ACTUAL ❌"
echo "  • Contraseña nueva: $PASSWORD_NUEVA ✅"
echo "  • Token inicial: ${TOKEN:0:50}..."
echo "  • Token nuevo: ${NEW_TOKEN:0:50}..."
echo ""
```

### Ejecutar el Script

```bash
chmod +x test_cambiar_password.sh
./test_cambiar_password.sh
```

## Cómo Usar desde Postman

### 1. **Login para Obtener Token**

- Método: `POST`
- URL: `http://localhost:8000/auth/login`
- Body (form-data):
  ```
  username: admin
  password: admin123
  ```
- Click **Send**
- Copiar el valor de `access_token` de la respuesta

### 2. **Cambiar Contraseña**

- Método: `POST`
- URL: `http://localhost:8000/auth/cambiar-password`
- **Authorization:**
  - Type: `Bearer Token`
  - Token: (pega el token del paso anterior)
  
- **Body (raw, JSON):**
  ```json
  {
    "password_actual": "admin123",
    "password_nueva": "miNuevaPassword2024",
    "password_confirmacion": "miNuevaPassword2024"
  }
  ```
- Click **Send**

**Respuesta esperada:**
```json
{
  "mensaje": "Contraseña actualizada exitosamente",
  "username": "admin"
}
```

## Acceso desde Swagger UI

### 1. **Abrir Swagger**
Navega a: `http://localhost:8000/docs`

### 2. **Login (GET TOKEN)**
- Haz click en `POST /auth/login`
- Click **Try it out**
- Ingresa username y password
- Click **Execute**
- Copia el `access_token`

### 3. **Autorizar Swagger**
- Click en el botón **Authorize** (arriba a la derecha)
- Pega: `Bearer {tu_token}`
- Click **Authorize**

### 4. **Cambiar Contraseña**
- Haz click en `POST /auth/cambiar-password`
- Click **Try it out**
- Ingresa los datos:
  ```json
  {
    "password_actual": "admin123",
    "password_nueva": "nuevaPassword123",
    "password_confirmacion": "nuevaPassword123"
  }
  ```
- Click **Execute**

## Flujo de Seguridad Detallado

```
┌─────────────────────────────────────────────────────────┐
│ 1. Cliente envía solicitud                              │
│    POST /auth/cambiar-password                          │
│    Authorization: Bearer {JWT_TOKEN}                    │
│    Body: { password_actual, password_nueva, ... }       │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 2. get_current_user(token) - Validar JWT               │
│    • Decodifica JWT                                     │
│    • Valida que no esté expirado                       │
│    • Extrae username y role                            │
│    • Retorna { username, role }                        │
└──────────────────┬──────────────────────────────────────┘
                   ↓ (❌ Si JWT inválido → 401)
┌─────────────────────────────────────────────────────────┐
│ 3. Validar coincidencia de nuevas contraseñas           │
│    password_nueva == password_confirmacion?             │
└──────────────────┬──────────────────────────────────────┘
                   ↓ (❌ Si no coinciden → 400)
┌─────────────────────────────────────────────────────────┐
│ 4. get_user_by_username(username)                       │
│    • Consulta BD: SELECT ... FROM usuarios              │
│    • Obtiene usuario actual con hash actual             │
└──────────────────┬──────────────────────────────────────┘
                   ↓ (❌ Si no existe → 401)
┌─────────────────────────────────────────────────────────┐
│ 5. verify_password(password_actual, hash_en_bd)         │
│    • Compara contraseña actual con hash almacenado      │
│    • Usa bcrypt.verify()                               │
└──────────────────┬──────────────────────────────────────┘
                   ↓ (❌ Si no coincide → 401)
┌─────────────────────────────────────────────────────────┐
│ 6. hash_password(password_nueva)                        │
│    • Hashea nueva contraseña con bcrypt                │
│    • Costo 12, 60+ caracteres resultado                │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 7. update_user_password(username, new_hash)             │
│    • UPDATE usuarios SET password_hash = ...             │
│    • UPDATE actualizado_en = NOW()                      │
│    • WHERE username = ... AND activo = 1                │
└──────────────────┬──────────────────────────────────────┘
                   ↓ (❌ Si error BD → 500)
┌─────────────────────────────────────────────────────────┐
│ 8. ✅ Retornar 200 OK                                  │
│    {                                                    │
│      "mensaje": "Contraseña actualizada...",           │
│      "username": "admin"                               │
│    }                                                    │
└─────────────────────────────────────────────────────────┘
```

## Casos de Uso

### 📌 Caso 1: Usuario Cambio Contraseña Exitosamente

```bash
# Admin con token válido cambia su contraseña
curl -X POST "http://localhost:8000/auth/cambiar-password" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "password_actual": "admin123",
    "password_nueva": "admin2024",
    "password_confirmacion": "admin2024"
  }'

# Respuesta:
# { "mensaje": "Contraseña actualizada exitosamente", "username": "admin" }
```

### 📌 Caso 2: Error - Contraseña Actual Incorrecta

```bash
curl -X POST "http://localhost:8000/auth/cambiar-password" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "password_actual": "wrongPassword",  # ❌ Incorrecta
    "password_nueva": "admin2024",
    "password_confirmacion": "admin2024"
  }'

# Respuesta 401:
# { "detail": "Contraseña actual incorrecta" }
```

### 📌 Caso 3: Error - Nuevas Contraseñas No Coinciden

```bash
curl -X POST "http://localhost:8000/auth/cambiar-password" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "password_actual": "admin123",
    "password_nueva": "admin2024",
    "password_confirmacion": "admin2025"  # ❌ No coincide
  }'

# Respuesta 400:
# { "detail": "Las nuevas contraseñas no coinciden" }
```

### 📌 Caso 4: Error - Token Expirado

```bash
curl -X POST "http://localhost:8000/auth/cambiar-password" \
  -H "Authorization: Bearer expiredToken..." \
  -H "Content-Type: application/json" \
  -d '{...}'

# Respuesta 401:
# { "detail": "Token inválido o expirado" }
```

## Archivos del Sistema

### 📄 app/routers/auth.py
- Define endpoint `POST /auth/cambiar-password`
- Orquesta las validaciones
- 73 líneas de código bien documentado

### 📄 app/schemas/auth.py
- `ChangePasswordRequest` - Schema para validar entrada
- `ChangePasswordResponse` - Schema para respuesta
- Incluye ejemplos y validaciones de campo

### 📄 app/repository/users_repo.py
- `update_user_password()` - Actualiza hash en BD
- Retorna True/False para éxito/fallo

### 📄 app/auth/passwords.py
- `hash_password()` - Hashea con bcrypt
- `verify_password()` - Verifica contraseña

### 📄 app/auth/deps.py
- `get_current_user()` - Valida JWT del request
- Retorna { username, role }

## Base de Datos

### Tabla usuarios

```sql
CREATE TABLE usuarios (
  id INT PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  email VARCHAR(150) UNIQUE,
  password_hash VARCHAR(255),      ← Se actualiza aquí
  rol_id INT,
  activo TINYINT,
  creado_en TIMESTAMP,
  actualizado_en TIMESTAMP         ← Se actualiza con NOW()
);
```

### SQL Ejecutado Internamente

```sql
UPDATE usuarios 
SET password_hash = '$2b$12$...' ,
    actualizado_en = NOW()
WHERE username = 'admin' AND activo = 1;
```

## Restricciones y Limitaciones

| Restricción | Descripción |
|------------|------------|
| **Token Requerido** | Debe estar autenticado (Bearer Token) |
| **Solo Automodificación** | No puede cambiar contraseña de otros usuarios |
| **Longitud Mínima** | Todas las contraseñas deben tener 6+ caracteres |
| **Contraseña Actual Requerida** | Debe validar que conoce su contraseña actual |
| **Expiración de Token** | Si token expira (60 min default), debe re-login |
| **Usuario Activo** | Solo usuarios con `activo=1` pueden cambiar password |

## Integración con Otros Endpoints

Este endpoint es complementario a:

- `POST /auth/login` - Para obtener el token JWT inicial
- `GET /clientes/` - Endpoint protegido que usa el mismo JWT
- Script `scripts/crear_usuario.py` - Para crear usuarios inicialmente

## Testing Automatizado

Puedes integrar el test en un pipeline CI/CD:

### GitHub Actions Ejemplo

```yaml
- name: Test cambiar contraseña
  run: |
    chmod +x docs/test_cambiar_password.sh
    ./docs/test_cambiar_password.sh
  env:
    API_URL: http://localhost:8000
```

## Resumen

| Aspecto | Descripción |
|--------|------------|
| **Endpoint** | `POST /auth/cambiar-password` |
| **Autenticación** | Bearer Token JWT (obligatorio) |
| **Request** | ChangePasswordRequest (3 campos) |
| **Response** | ChangePasswordResponse (2 campos) |
| **Validaciones** | 4 validaciones de seguridad |
| **Status 200** | Cambio exitoso |
| **Status 400** | Nuevas contraseñas no coinciden |
| **Status 401** | Token inválido o contraseña actual incorrecta |
| **Status 500** | Error en la base de datos |
| **Base de Datos** | Actualiza password_hash y actualizado_en |
| **Seguridad** | bcrypt 12 iteraciones, no muestra contraseñas |

---

**Última actualización:** 1 de febrero de 2026  
**Para:** Estudiantes de FastAPI y APIs REST seguras  
**Docente:** [Tu nombre]
