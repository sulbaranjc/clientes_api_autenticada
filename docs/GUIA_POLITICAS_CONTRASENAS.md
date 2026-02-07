# 🔐 Guía de Implementación: Políticas de Contraseñas

## 📋 Resumen

Esta implementación agrega un sistema completo de políticas de contraseñas que incluye:

- ✅ **Cambio obligatorio en el primer login**
- ✅ **Expiración automática de contraseñas** (90 días por defecto)
- ✅ **Cambio forzado por administradores**
- ✅ **Auditoría de cambios** (IP, timestamp)
- ✅ **Validaciones de seguridad**
- ✅ **Alertas tempranas de expiración**

---

## 🏗️ Arquitectura de la Solución

### 1. Base de Datos (Nuevos campos en `usuarios`)

```sql
ALTER TABLE usuarios
ADD COLUMN first_login BOOLEAN DEFAULT TRUE,
ADD COLUMN password_expires_at DATETIME NULL,
ADD COLUMN force_password_change BOOLEAN DEFAULT FALSE,
ADD COLUMN password_changed_at DATETIME NULL,
ADD COLUMN last_password_change_ip VARCHAR(45) NULL;
```

### 2. Repositorio (`app/repository/users_repo.py`)

**Nuevas funciones:**

- `check_password_expiration(user)` - Evalúa si la contraseña requiere cambio
- `change_user_password(user_id, ...)` - Cambia la contraseña con políticas
- `force_password_change_by_admin(user_id)` - Fuerza cambio administrativo

### 3. Schemas (`app/schemas/auth.py`)

**TokenResponse actualizado:**
```python
class TokenResponse(BaseModel):
    access_token: str
    username: str
    rol: str
    # 🔐 Nuevos campos
    requires_password_change: bool = False
    is_first_login: bool = False
    password_expired: bool = False
    days_until_expiration: Optional[int] = None
```

### 4. Router (`app/routers/auth.py`)

**Endpoints modificados:**

- `POST /auth/login` - Incluye verificación de políticas
- `POST /auth/cambiar-password` - Maneja primer login y expiración

**Nuevo endpoint:**

- `POST /auth/admin/force-password-change/{user_id}` - Para administradores

---

## 🚀 Instalación

### Paso 1: Aplicar Migración SQL

```bash
# Opción 1: Usando el script automatizado
chmod +x scripts/apply_password_policy_migration.sh
./scripts/apply_password_policy_migration.sh

# Opción 2: Manualmente desde MySQL
mysql -u profesor -p clientes_autenticado_db < docs/migrations/001_add_password_policy_fields.sql
```

### Paso 2: Validar la Implementación

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar tests
python scripts/test_password_policy.py
```

### Paso 3: Reiniciar la Aplicación

```bash
# Detener si está corriendo
# ...

# Iniciar de nuevo
uvicorn app.main:app --reload
```

---

## 📖 Guía de Uso

### Flujo: Creación de Usuario

```python
# Cuando se crea un usuario nuevo:
# - first_login se establece automáticamente en TRUE
# - force_password_change = FALSE
# - password_changed_at = NULL
# - password_expires_at = NULL
```

### Flujo: Primer Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=nuevo_usuario&password=TempPassword123
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "username": "nuevo_usuario",
  "rol": "user",
  "requires_password_change": true,   // ⚠️ TRUE
  "is_first_login": true,              // ⚠️ TRUE
  "password_expired": false,
  "days_until_expiration": null
}
```

**Lógica del Frontend:**
```javascript
if (response.requires_password_change) {
  if (response.is_first_login) {
    router.push('/change-password?reason=first_login');
    showMessage('Por favor, cambia tu contraseña temporal');
  }
}
```

### Flujo: Cambio de Contraseña (Primer Login)

```http
POST /auth/cambiar-password
Authorization: Bearer eyJhbGci...
Content-Type: application/json

{
  "password_actual": null,               // ⚠️ OPCIONAL en primer login
  "password_nueva": "MiNuevaPass123!",
  "password_confirmacion": "MiNuevaPass123!"
}
```

**Respuesta:**
```json
{
  "mensaje": "Contraseña actualizada exitosamente",
  "username": "nuevo_usuario",
  "password_changed_at": "2026-02-07T16:30:00"
}
```

**Qué ocurre internamente:**
1. `first_login` se marca como `FALSE`
2. `password_changed_at` se establece en NOW()
3. `password_expires_at` se calcula como NOW() + 90 días
4. `last_password_change_ip` guarda la IP del cliente

### Flujo: Login Normal (Después del Primer Login)

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=nuevo_usuario&password=MiNuevaPass123!
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "username": "nuevo_usuario",
  "rol": "user",
  "requires_password_change": false,   // ✅ FALSE
  "is_first_login": false,             // ✅ FALSE
  "password_expired": false,
  "days_until_expiration": 90          // Días restantes
}
```

**Lógica del Frontend:**
```javascript
if (!response.requires_password_change) {
  // Acceso permitido
  router.push('/dashboard');
  
  // Advertencia si está por expirar
  if (response.days_until_expiration <= 7) {
    showWarning(`Tu contraseña expira en ${response.days_until_expiration} días`);
  }
}
```

### Flujo: Contraseña Expirada

**Cuando pasan 90 días desde el último cambio:**

```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "username": "usuario",
  "rol": "user",
  "requires_password_change": true,     // ⚠️ TRUE
  "is_first_login": false,
  "password_expired": true,              // ⚠️ TRUE
  "days_until_expiration": null
}
```

**Frontend debe redirigir:**
```javascript
router.push('/change-password?reason=expired');
showMessage('Tu contraseña ha expirado. Por seguridad, debes cambiarla.');
```

### Flujo: Cambio Forzado por Admin

**1. Admin fuerza cambio:**

```http
POST /auth/admin/force-password-change/5
Authorization: Bearer {admin_token}
```

**Respuesta:**
```json
{
  "mensaje": "El usuario con ID 5 deberá cambiar su contraseña...",
  "user_id": 5,
  "forced_by": "admin"
}
```

**2. Usuario afectado hace login:**

```json
{
  "access_token": "eyJhbGci...",
  "username": "usuario_afectado",
  "requires_password_change": true,     // ⚠️ Forzado
  "is_first_login": false,
  "password_expired": false,
  "days_until_expiration": 45
}
```

---

## 🛠️ Configuración

### Variables de Política (Configurable)

En `app/repository/users_repo.py`:

```python
# Días antes de que la contraseña expire
PASSWORD_EXPIRATION_DAYS = 90  # Cambiar según necesidad
```

### Validación de Contraseñas (Futuro)

Puedes agregar validaciones adicionales en `app/auth/passwords.py`:

```python
import re

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida la fortaleza de una contraseña.
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Debe incluir al menos una mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "Debe incluir al menos una minúscula"
    
    if not re.search(r'\d', password):
        return False, "Debe incluir al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Debe incluir al menos un carácter especial"
    
    return True, "Contraseña válida"
```

---

## 🎨 Ejemplo de Integración Frontend (React)

```typescript
// services/auth.service.ts

interface LoginResponse {
  access_token: string;
  token_type: string;
  username: string;
  rol: string;
  requires_password_change: boolean;
  is_first_login: boolean;
  password_expired: boolean;
  days_until_expiration: number | null;
}

export async function login(username: string, password: string): Promise<void> {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username, password })
  });
  
  const data: LoginResponse = await response.json();
  
  // Guardar token
  localStorage.setItem('token', data.access_token);
  
  // 🔐 Verificar políticas de contraseñas
  if (data.requires_password_change) {
    if (data.is_first_login) {
      router.push('/change-password?reason=first_login');
      toast.info('Por favor, cambia tu contraseña temporal');
    } else if (data.password_expired) {
      router.push('/change-password?reason=expired');
      toast.warning('Tu contraseña ha expirado');
    } else {
      router.push('/change-password?reason=forced');
      toast.warning('El administrador ha solicitado que cambies tu contraseña');
    }
  } else {
    // Login exitoso - continuar al dashboard
    router.push('/dashboard');
    
    // Advertencia si la contraseña está por expirar
    if (data.days_until_expiration && data.days_until_expiration <= 7) {
      toast.warning(
        `Tu contraseña expira en ${data.days_until_expiration} días. Te recomendamos cambiarla pronto.`
      );
    }
  }
}

export async function changePassword(
  currentPassword: string | null,
  newPassword: string,
  confirmPassword: string
): Promise<void> {
  const token = localStorage.getItem('token');
  
  const response = await fetch('/auth/cambiar-password', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      password_actual: currentPassword,
      password_nueva: newPassword,
      password_confirmacion: confirmPassword
    })
  });
  
  if (response.ok) {
    toast.success('Contraseña actualizada exitosamente');
    router.push('/dashboard');
  }
}
```

---

## 📊 Casos de Uso Cubiertos

| Caso | `first_login` | `force_password_change` | `password_expired` | Acción |
|------|---------------|-------------------------|--------------------| -------|
| Usuario nuevo | ✅ TRUE | ❌ FALSE | ❌ FALSE | Cambiar contraseña obligatorio |
| Usuario normal | ❌ FALSE | ❌ FALSE | ❌ FALSE | Acceso permitido |
| Contraseña expirada | ❌ FALSE | ❌ FALSE | ✅ TRUE | Cambiar contraseña obligatorio |
| Reset por admin | ❌ FALSE | ✅ TRUE | ❌ FALSE | Cambiar contraseña obligatorio |
| Próximo a expirar (7 días) | ❌ FALSE | ❌ FALSE | ❌ FALSE | Advertencia + acceso |

---

## 🔒 Seguridad

### Mejores Prácticas Implementadas

1. ✅ **No se permite reutilizar la contraseña anterior**
2. ✅ **Auditoría de cambios** (IP, timestamp)
3. ✅ **Expiración automática** (90 días)
4. ✅ **Contraseñas hasheadas con bcrypt**
5. ✅ **Validación en backend** (no solo frontend)

### Recomendaciones Adicionales

- 📧 **Enviar email** cuando se cambie la contraseña
- 📊 **Log de seguridad** para auditorías
- 🔐 **Rate limiting** en endpoints de cambio de contraseña
- ⏱️ **Sesión única** (invalidar tokens anteriores al cambiar contraseña)

---

## 🧪 Testing

### Tests Automatizados

```bash
# Test de funcionalidad completa
python scripts/test_password_policy.py

# Test de conexión a BD
python scripts/test_conexion.py
```

### Tests Manuales con Swagger UI

1. Ir a `http://localhost:8000/docs`
2. Crear un usuario nuevo (automáticamente `first_login = TRUE`)
3. Hacer login y verificar `requires_password_change: true`
4. Cambiar contraseña con `password_actual: null`
5. Hacer login nuevamente y verificar `requires_password_change: false`

---

## 📝 Logs y Auditoría

### Consultas Útiles

```sql
-- Ver usuarios que requieren cambio de contraseña
SELECT username, first_login, force_password_change, password_expires_at
FROM usuarios
WHERE first_login = TRUE OR force_password_change = TRUE 
   OR password_expires_at < NOW();

-- Ver historial de cambios de contraseña
SELECT username, password_changed_at, last_password_change_ip
FROM usuarios
WHERE password_changed_at IS NOT NULL
ORDER BY password_changed_at DESC;

-- Ver contraseñas que expiran pronto (próximos 7 días)
SELECT username, password_expires_at,
       DATEDIFF(password_expires_at, NOW()) as dias_restantes
FROM usuarios
WHERE password_expires_at BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY);
```

---

## 🚨 Troubleshooting

### Problema: Los nuevos campos no existen

**Solución:**
```bash
# Verificar que la migración se aplicó
mysql -u profesor -p clientes_autenticado_db -e "DESCRIBE usuarios;"

# Si no están, aplicar migración
./scripts/apply_password_policy_migration.sh
```

### Problema: Login no retorna los nuevos campos

**Solución:**
- Verificar que `app/schemas/auth.py` tenga los campos actualizados
- Reiniciar la aplicación FastAPI
- Limpiar cache del navegador

### Problema: Error al cambiar contraseña en primer login

**Solución:**
- Verificar que `password_actual` sea `null` u optional
- Revisar los logs del servidor
- Verificar que el usuario tenga `first_login = TRUE`

---

## 📚 Referencias

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)

---

## ✅ Checklist de Implementación

- [x] Migración SQL creada y documentada
- [x] Campos agregados a la tabla `usuarios`
- [x] Repositorio actualizado con nuevas funciones
- [x] Schemas de Pydantic actualizados
- [x] Endpoint `/auth/login` actualizado
- [x] Endpoint `/auth/cambiar-password` actualizado
- [x] Endpoint admin agregado
- [x] Scripts de test creados
- [x] Documentación completa
- [ ] Tests unitarios (opcional)
- [ ] Integración con frontend
- [ ] Envío de emails (opcional)
- [ ] Logs de auditoría (opcional)

---

**Fecha de implementación:** 7 de febrero de 2026  
**Versión:** 1.0.0  
**Autor:** Sistema de IA - GitHub Copilot
