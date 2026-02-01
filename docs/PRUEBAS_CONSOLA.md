# 🧪 PRUEBAS DE CONSOLA - VALIDACIÓN MANUAL

**Guía práctica para validar la autenticación JWT desde la terminal**

---

## 📌 Descripción

Estos 3 comandos te permiten verificar que:
1. ✅ Los usuarios existen en la BD con hashes correctos
2. ✅ El login funciona y devuelve un token válido
3. ✅ El token autoriza el acceso a recursos protegidos

**Perfecto para aprender cómo funciona la autenticación JWT en FastAPI**

---

## 🧪 PRUEBA 1: Verificar usuarios en la Base de Datos

### Comando:
```bash
mysql -u profesor -p4688 clientes_autenticado_db \
  -e "SELECT username, email, password_hash, activo FROM usuarios;"
```

### ¿Qué hace?
Conecta a MySQL y muestra todos los usuarios con:
- `username`: Nombre de usuario
- `email`: Email del usuario
- `password_hash`: Hash bcrypt almacenado (NO la contraseña plana)
- `activo`: 1=activo, 0=inactivo

### Respuesta esperada:
```
+----------+-----------------+--------------------------------------------------------------+--------+
| username | email           | password_hash                                                | activo |
+----------+-----------------+--------------------------------------------------------------+--------+
| admin    | admin@test.com  | $2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlL |      1 |
| lector   | lector@test.com | $2b$12$IYBfsBcTC4ZM74Oeez98EemoXhThcPWJCd7DBpQcVIItA1uem |      1 |
+----------+-----------------+--------------------------------------------------------------+--------+
```

### Información que ves:
- ✅ Usuario `admin` existe y está activo (activo=1)
- ✅ Usuario `lector` existe y está activo (activo=1)
- ✅ Ambos tienen hashes bcrypt válidos
- ⚠️ NUNCA vemos la contraseña plana (está hasheada)

---

## 🧪 PRUEBA 2: Hacer Login y Obtener Token JWT

### Comando:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" 2>/dev/null | python3 -m json.tool
```

### ¿Qué hace?
1. Hace POST a `/auth/login` con credenciales
2. El servidor verifica la contraseña contra el hash
3. Si es correcta, devuelve un JWT (token de acceso)
4. `python3 -m json.tool` formatea la respuesta JSON

### Respuesta esperada:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2OTk0NzY1N30.dYqfQVdoTU84JVr9SLTHu2cYeHfQDaxnpJgdb0Xlh_Q",
    "token_type": "bearer"
}
```

### Información que ves:
- ✅ `access_token`: JWT válido firmado con la SECRET_KEY
- ✅ `token_type`: "bearer" (tipo de autenticación OAuth2)
- 🔒 El token es unidireccional: contiene info pero no se puede modificar sin la SECRET_KEY

### ¿Qué contiene el token?
Aunque parece aleatorio, el JWT contiene información (codificada en Base64):
```
Header:     {"alg": "HS256", "typ": "JWT"}
Payload:    {"sub": "admin", "role": "admin", "exp": 1769947657}
Signature:  HMAC-SHA256(header + payload, SECRET_KEY)
```

### Prueba con credenciales incorrectas:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=PASSWORD_INCORRECTA" 2>/dev/null | python3 -m json.tool
```

**Respuesta (❌ Error):**
```json
{
    "detail": "Credenciales inválidas"
}
```

---

## 🧪 PRUEBA 3: Usar Token para Acceder a Recurso Protegido

### Comando:
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])") && \
echo "✅ Token obtenido: $TOKEN" && \
curl -s -X GET "http://localhost:8000/clientes/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30
```

### ¿Qué hace?
1. **Línea 1-3:** Obtiene el token del login
2. **Línea 4:** Imprime el token (verificación)
3. **Línea 5-7:** Usa el token en un GET a `/clientes/` (recurso protegido)

### Respuesta esperada:
```
✅ Token obtenido: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2OTk0NzY3NH0.8qLfRu2G4QI6KlxW9QeyVadobg2Ftpehgd3Vax8XAq4
[
    {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan.perez@example.com",
        "telefono": "555-0101",
        "direccion": "Calle 123, Ciudad",
        "id": 1
    },
    {
        "nombre": "María",
        "apellido": "García",
        "email": "maria.garcia@example.com",
        "telefono": "555-0102",
        "direccion": "Avenida 456, Ciudad",
        "id": 2
    },
    ...
]
```

### Información que ves:
- ✅ Token obtenido correctamente
- ✅ Token autoriza acceso al endpoint protegido `/clientes/`
- ✅ Se devuelven todos los clientes (200 OK)

### Prueba SIN token (❌ Sin autorización):
```bash
curl -X GET "http://localhost:8000/clientes/" \
  -H "Content-Type: application/json" 2>/dev/null | python3 -m json.tool
```

**Respuesta (❌ Error 403):**
```json
{
    "detail": "Not authenticated"
}
```

---

## 🎓 EXPLICACIÓN DEL FLUJO COMPLETO

```
┌──────────────────────────────────────┐
│ USUARIO: admin / PASSWORD: admin123  │
└────────────────────┬─────────────────┘
                     │
        ┌────────────▼────────────┐
        │  PRUEBA 1: BD           │
        │ Verificar que usuario   │
        │ existe con hash ok      │
        └────────────┬────────────┘
                     │
        ┌────────────▼──────────────────┐
        │  PRUEBA 2: LOGIN              │
        │ POST /auth/login              │
        │ Enviar: username + password   │
        │ Recibir: JWT token            │
        └────────────┬──────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │  PRUEBA 3: PROTEGIDO          │
        │ GET /clientes/                │
        │ Header: Authorization: Bearer │
        │ Respuesta: Datos con 200 OK   │
        └───────────────────────────────┘
```

---

## 📋 RESUMEN DE PRUEBAS

| # | Comando | Propósito | Verificar |
|---|---------|-----------|-----------|
| 1 | MySQL | BD | Usuario existe + hash correcto |
| 2 | curl login | JWT | Token generado correctamente |
| 3 | curl token | Autorización | Token accede a recurso |

---

## 🔒 SEGURIDAD - Puntos Clave

### Contraseñas:
- ✅ NUNCA se almacenan en texto plano
- ✅ Se hashean con bcrypt (unidireccional)
- ✅ Cada login verifica: `bcrypt.verify(password_plana, hash_bd)`

### Tokens JWT:
- ✅ Se generan con la `SECRET_KEY`
- ✅ Se validan en cada request a recurso protegido
- ✅ Expiran después de 60 minutos (configurable)
- ✅ NO se pueden falsificar sin la `SECRET_KEY`

### Headers HTTP:
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded
─────────────────────────────────────────────────
username=admin&password=admin123

────────────────────────────────────────────────

GET /clientes/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 💡 TRUCOS ÚTILES

### Extraer solo el token:
```bash
curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token'
```

### Decodificar el JWT (solo header y payload):
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2OTk0NzY3NH0.8qLfRu2G4QI6KlxW9QeyVadobg2Ftpehgd3Vax8XAq4"

# Ver header
echo $TOKEN | cut -d'.' -f1 | base64 -d | python3 -m json.tool

# Ver payload (claims)
echo $TOKEN | cut -d'.' -f2 | base64 -d | python3 -m json.tool
```

### Guardar token en variable para reutilizarlo:
```bash
# Obtener token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Usar múltiples veces
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/clientes/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/clientes/1
```

---

## ✅ CHECKLIST DE VALIDACIÓN

Al ejecutar las 3 pruebas, verifica:

- [ ] **Prueba 1:** Usuarios en BD tienen `activo=1`
- [ ] **Prueba 1:** Hashes comienzan con `$2b$12$`
- [ ] **Prueba 2:** Respuesta contiene `access_token`
- [ ] **Prueba 2:** `token_type` es `"bearer"`
- [ ] **Prueba 2:** El token es un string largo (JWT)
- [ ] **Prueba 3:** Token obtiene lista de clientes (200 OK)
- [ ] **Prueba 3:** Sin token devuelve 401/403 error

---

## 🚀 ¡Listo para Aprender!

Ahora puedes:
1. Entender cómo funciona la autenticación
2. Ver exactamente qué datos se envían/reciben
3. Verificar que el servidor está funcionando
4. Experimentar cambiando credenciales

**¡Adelante con las pruebas!** 🧪

---

**Última actualización:** 1 de febrero de 2026  
**Versión:** 1.0
