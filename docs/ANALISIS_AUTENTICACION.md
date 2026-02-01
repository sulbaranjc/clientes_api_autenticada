# 🔐 ANÁLISIS COMPLETO DEL PROBLEMA DE AUTENTICACIÓN

**Fecha:** 1 de febrero de 2026  
**Autor:** Análisis automático  
**Estado:** ✅ PROBLEMA IDENTIFICADO Y RESUELTO

---

## 📌 RESUMEN EJECUTIVO

### Problema
El usuario `admin` con contraseña `admin123` **no autenticaba correctamente** aunque el usuario estaba creado en la BD.

### Causa Raíz
El hash bcrypt almacenado en `init_db.sql` **NO correspondía** a la contraseña "admin123".

### Solución
Reemplazar los hashes bcrypt inválidos por los correctos generados con bcrypt.

---

## 🔍 ANÁLISIS DETALLADO DEL WORKFLOW DE AUTENTICACIÓN

### 1️⃣ **FLUJO DE AUTENTICACIÓN** (End-to-End)

```
┌─────────────────────────────────────────┐
│ Cliente: POST /auth/login               │
│ Body: {                                 │
│   "username": "admin",                  │
│   "password": "admin123"                │
│ }                                       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ app/routers/auth.py - login()           │
│ 1. Obtiene form_data (username, pwd)   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ app/repository/users_repo.py            │
│ get_user_by_username("admin")          │
│                                         │
│ Query:                                  │
│ SELECT u.username, u.password_hash,    │
│        r.nombre AS role                │
│ FROM usuarios u                         │
│ JOIN roles r ON u.rol_id = r.id        │
│ WHERE u.username = "admin" AND          │
│       u.activo = 1                      │
│                                         │
│ Resultado de BD:                        │
│ {                                       │
│   "username": "admin",                  │
│   "password_hash": "$2b$12$...",       │
│   "role": "admin"                       │
│ }                                       │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ app/auth/passwords.py - verify_password│
│                                         │
│ verify_password(                        │
│   plain_password="admin123",           │
│   hashed_password="$2b$12$..." (BD)   │
│ )                                       │
│                                         │
│ Bcrypt.verify():                        │
│  ❌ FALLA: El hash no coincide         │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ Response: HTTP 401                      │
│ {                                       │
│   "detail": "Credenciales inválidas"   │
│ }                                       │
└─────────────────────────────────────────┘
```

---

## 🔴 PROBLEMA ESPECÍFICO

### En `docs/init_db.sql`

**❌ HASH INVÁLIDO:**
```sql
INSERT INTO usuarios (username, email, password_hash, rol_id)
VALUES ('admin', 'admin@test.com', 
        '$2b$12$1FERac3oRY3l2090Xl7EGuDzO4zUe9Nyowy3XLaZ2t6znkmwB9I76', 
        1);
```

**¿Por qué falla?**
- El hash `$2b$12$1FERac3oRY3l2090Xl7EGuDzO4zUe9Nyowy3XLaZ2t6znkmwB9I76` fue generado para una contraseña diferente a "admin123"
- Bcrypt es unidireccional: no se puede "deshashar"
- La verificación: `verify("admin123", hash_incorrecto)` = **FALSE**
- Resultado: 401 Unauthorized

---

## ✅ SOLUCIÓN APLICADA

### Generación de Hashes Correctos

Se generaron nuevos hashes bcrypt válidos para las contraseñas:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Para admin123
hash_admin = pwd_context.hash("admin123")
# Resultado: $2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlLAe

# Para lector123
hash_lector = pwd_context.hash("lector123")
# Resultado: $2b$12$IYBfsBcTC4ZM74Oeez98EemoXhThcPWJCd7DBpQcVIItA1uem4wVm
```

### Archivo Actualizado: `docs/init_db.sql`

```sql
-- admin (password: admin123)
INSERT INTO usuarios (username, email, password_hash, rol_id)
VALUES ('admin', 'admin@test.com', 
        '$2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlLAe', 
        1);

-- lector (password: lector123)
INSERT INTO usuarios (username, email, password_hash, rol_id)
VALUES ('lector', 'lector@test.com', 
        '$2b$12$IYBfsBcTC4ZM74Oeez98EemoXhThcPWJCd7DBpQcVIItA1uem4wVm', 
        2);
```

---

## 📋 COMPONENTES DEL PROYECTO ANALIZADOS

### 1. **app/routers/auth.py** ✅
- Router de autenticación OAuth2 Password Flow
- Endpoint: `POST /auth/login`
- Flujo correcto:
  1. Obtiene `form_data` (username, password)
  2. Busca usuario en BD
  3. Verifica contraseña con bcrypt
  4. Genera JWT si es válido
  5. Devuelve token o error 401

### 2. **app/auth/passwords.py** ✅
- Funciones de hashing y verificación
- `hash_password()`: Genera hash bcrypt seguro
- `verify_password()`: Compara contraseña plana con hash
- Usa: `passlib.context.CryptContext` con bcrypt

### 3. **app/repository/users_repo.py** ✅
- `get_user_by_username()`: Obtiene usuario de BD
- Query SQL:
  ```sql
  SELECT u.username, u.password_hash, r.nombre AS role
  FROM usuarios u
  JOIN roles r ON u.rol_id = r.id
  WHERE u.username = ? AND u.activo = 1
  ```
- Retorna: `{username, password_hash, role}`

### 4. **app/database.py** ✅
- `get_connection()`: Conexión a MySQL con variables de entorno
- Variables esperadas: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

### 5. **app/auth/jwt.py** ✅
- `create_access_token()`: Genera JWT con claim "sub" (username) y "role"
- `decode_access_token()`: Decodifica y valida JWT
- Configuración: `SECRET_KEY`, `ALGORITHM` (HS256), `ACCESS_TOKEN_EXPIRE_MINUTES`

### 6. **app/core/config.py** ✅
- Clase `Settings` que carga variables de entorno
- Requiere: `SECRET_KEY` en `.env`

### 7. **docs/init_db.sql** ❌ → ✅ (CORREGIDO)
- Estructura de tablas: `usuarios`, `roles`, `clientes`
- **PROBLEMA:** Hashes bcrypt incorrectos
- **SOLUCIÓN:** Reemplazados con hashes válidos

### 8. **app/main.py** ✅
- Aplicación FastAPI
- Routers: `clientes`, `auth`
- CORS habilitado para desarrollo

---

## 🧪 VERIFICACIÓN

### Nuevo Workflow Después de la Corrección

```
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}

↓

verify_password(
  "admin123",
  "$2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlLAe"
)

↓ ✅ BCRYPT.VERIFY() = TRUE

Genera JWT

↓

Response 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 📝 PASOS PARA APLICAR LA SOLUCIÓN

### 1. Respaldrar BD Actual (OPCIONAL pero recomendado)
```bash
mysqldump -u profesor -p4688 clientes_autenticado_db > backup.sql
```

### 2. Ejecutar Script Actualizado
```bash
mysql -u profesor -p4688 < docs/init_db.sql
```

### 3. Probar Autenticación
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 4. Verificar en Swagger
- Ir a: `http://localhost:8000/docs`
- Click en "Authorize"
- Username: `admin`
- Password: `admin123`
- ✅ Debe aceptar y generar token

---

## 🎯 CREDENCIALES DE PRUEBA (DESPUÉS DE LA CORRECCIÓN)

| Usuario | Contraseña | Rol   | Email            |
|---------|-----------|-------|------------------|
| admin   | admin123  | admin | admin@test.com   |
| lector  | lector123 | lector| lector@test.com  |

---

## 📚 REFERENCIA TÉCNICA

### Bcrypt Hash Format
```
$2b$12$rounds$salt$hash
│  │  │
│  │  └─ Cost factor (12 iteraciones)
│  └──── Algoritmo (2b = bcrypt)
└─────── Versión
```

### Ventajas de la Solución
1. ✅ Hashes bcrypt válidos generados con mismo `CryptContext`
2. ✅ Compatibles con `passlib.verify_password()`
3. ✅ Contraseñas visibles solo en este documento para referencia
4. ✅ Hashes unidireccionales (seguro)
5. ✅ Costo: 12 iteraciones (seguro y rápido)

---

## ❓ NOTAS IMPORTANTES

1. **No cambiar contraseñas sin regenerar hashes**: Si cambias contraseña, necesitas nuevo hash bcrypt
2. **Las contraseñas en este documento son SOLO para prueba**: En producción usar contraseñas seguras
3. **Secret Key del JWT**: Verificar que `.env` tenga `SECRET_KEY` válida
4. **Base de datos**: Verificar conexión MySQL con credenciales correctas

---

**Estado:** ✅ LISTO PARA PRUEBA  
**Cambios:** Archivo `docs/init_db.sql` actualizado  
**Pendiente de usuario:** Validar funcionamiento en BD y Swagger UI
