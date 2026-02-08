# 🔧 Guía: Gestión de Usuarios desde CLI

## 📋 Descripción General

El script `manage_users.py` es una **herramienta de línea de comandos** para administrar usuarios de forma eficiente y segura. Integra todas las funcionalidades de gestión de usuarios con políticas de contraseñas.

### ✨ Funcionalidades

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `list` | Lista todos los usuarios con estado de seguridad | Ver tabla con colores y emojis |
| `change-password` | Cambia contraseña de un usuario | Interactivo o con parámetro |
| `create-user` | Crea un nuevo usuario | Con rol y contraseña opcionales |
| `force-change` | Fuerza cambio de contraseña en próximo login | Admin puede resetear contraseñas |
| `activate` | Activa un usuario desactivado | Restaurar acceso |
| `deactivate` | Desactiva un usuario | Bloquear acceso temporalmente |

### 🎯 Ventajas vs Scripts Antiguos

| Script Antiguo | Script Nuevo | Mejora |
|----------------|--------------|--------|
| `crear_usuario.py` | `manage_users.py create-user` | ✅ Más opciones y validaciones |
| Múltiples scripts | Un solo script CLI | ✅ Centralizado y consistente |
| Sin estado visual | Colores y emojis | ✅ Mejor UX en terminal |
| Sin políticas | Integrado con password policy | ✅ Seguridad automática |

---

## 🚀 Inicio Rápido

### Listar Todos los Usuarios

```bash
python scripts/manage_users.py list
```

**Salida esperada:**

```
======================================================================
                          LISTA DE USUARIOS                           
======================================================================

Total de usuarios: 4

ID    EMAIL                          USERNAME             ROL        ACTIVO   ESTADO PASSWORD          
--------------------------------------------------------------------------------------------------------------
4     test@example.com               test                 admin      Sí       🔒 Cambio forzado
3     prueba@example.com             prueba               admin      Sí       ➖ Sin expiración
1     admin@test.com                 admin                admin      Sí       ➖ Sin expiración
2     lector@test.com                lector               lector     Sí       ➖ Sin expiración

Resumen:
  Usuarios activos: 4/4
  Requieren cambio de contraseña: 1
```

### Ver Ayuda Completa

```bash
python scripts/manage_users.py --help
```

---

## 📖 Comandos Detallados

### 1. `list` - Listar Usuarios

**Descripción:** Muestra tabla con todos los usuarios y su estado de seguridad.

**Uso:**
```bash
python scripts/manage_users.py list
```

**Información mostrada:**
- ✅ ID, email, username, rol
- ✅ Estado activo/inactivo
- ✅ Estado de contraseña con indicadores visuales:
  - 🔒 **Cambio forzado** - Admin requirió cambio
  - ⚠️ **Primer login** - Usuario nuevo debe cambiar contraseña
  - ❌ **Expirada** - Contraseña venció (>90 días)
  - ⏰ **Por expirar** - Quedan ≤7 días
  - ✅ **OK** - Contraseña válida (muestra días restantes)
  - ➖ **Sin expiración** - No tiene política configurada

**Resumen incluido:**
- Total de usuarios activos
- Cantidad que requieren cambio de contraseña

---

### 2. `change-password` - Cambiar Contraseña

**Descripción:** Actualiza la contraseña de un usuario con validaciones de fortaleza.

#### Modo Interactivo (Recomendado)

```bash
python scripts/manage_users.py change-password usuario@example.com
```

**Proceso:**
1. Solicita nueva contraseña (no visible al escribir)
2. Solicita confirmación
3. Valida fortaleza
4. Confirma cambio
5. Actualiza en BD

#### Modo Directo

```bash
python scripts/manage_users.py change-password usuario@example.com --password NuevaPass123!
```

**Validaciones automáticas:**
- ✅ Mínimo 8 caracteres
- ✅ Al menos 1 mayúscula
- ✅ Al menos 1 minúscula
- ✅ Al menos 1 número

**Actualizaciones automáticas en BD:**
- `password_hash` → Hash bcrypt de la nueva contraseña
- `first_login` → FALSE (ya no es primer login)
- `force_password_change` → FALSE (cambio completado)
- `password_changed_at` → Timestamp actual
- `password_expires_at` → Ahora + 90 días
- `last_password_change_ip` → "CLI"

**Ejemplo completo:**

```bash
$ python scripts/manage_users.py change-password test@example.com

======================================================================
                CAMBIAR CONTRASEÑA - test@example.com                 
======================================================================

ℹ️  Usuario encontrado: test (admin)

Ingrese la nueva contraseña:
Nueva contraseña: ********
Confirmar contraseña: ********

✅ Contraseña válida

¿Confirmar cambio de contraseña para 'test@example.com'? (s/N): s

✅ Contraseña actualizada exitosamente
ℹ️  Fecha de cambio: 2026-02-07 17:07:45
ℹ️  Expira en: 90 días
```

---

### 3. `create-user` - Crear Usuario

**Descripción:** Crea un nuevo usuario con rol y contraseña opcionales.

#### Sintaxis

```bash
python scripts/manage_users.py create-user <email> <username> [--rol ROLE] [--password PASS]
```

#### Ejemplos

**Usuario básico:**
```bash
python scripts/manage_users.py create-user nuevo@example.com nuevouser
```
- Rol por defecto: `user`
- Contraseña temporal generada automáticamente

**Administrador con contraseña específica:**
```bash
python scripts/manage_users.py create-user admin@empresa.com adminuser \
  --rol admin --password AdminPass123!
```

**Usuario invitado:**
```bash
python scripts/manage_users.py create-user invitado@example.com guestuser \
  --rol guest
```

#### Roles Válidos

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| `admin` | Administrador | Acceso completo |
| `user` | Usuario estándar | Acceso limitado |
| `guest` | Invitado | Solo lectura |

#### Contraseña Temporal

Si no especificas `--password`, se genera automáticamente:

**Formato:** `TempYYYYMM!`

**Ejemplo:** `Temp202602!` (febrero 2026)

**Configuración automática:**
- `first_login` → TRUE (debe cambiar en primer login)
- `activo` → TRUE (usuario activo)
- `password_expires_at` → Ahora + 90 días

#### Ejemplo Completo

```bash
$ python scripts/manage_users.py create-user nuevo@example.com nuevouser --rol user

======================================================================
                CREAR NUEVO USUARIO - nuevo@example.com               
======================================================================

ℹ️  Contraseña temporal generada: Temp202602!
⚠️  El usuario deberá cambiarla en el primer login

Datos del nuevo usuario:
  Email:    nuevo@example.com
  Username: nuevouser
  Rol:      user
  Password: ***
  Estado:   Activo
  First Login: True (debe cambiar contraseña)

¿Confirmar creación? (s/N): s

✅ Usuario creado exitosamente (ID: 5)
ℹ️  Contraseña temporal: Temp202602!
⚠️  Guarde esta contraseña de forma segura
```

---

### 4. `force-change` - Forzar Cambio de Contraseña

**Descripción:** Marca un usuario para que DEBA cambiar su contraseña en el próximo login.

**Uso típico:**
- Sospecha de compromiso de seguridad
- Reset administrativo
- Política de seguridad corporativa

#### Sintaxis

```bash
python scripts/manage_users.py force-change <email>
```

#### Ejemplo

```bash
$ python scripts/manage_users.py force-change usuario@example.com

======================================================================
            FORZAR CAMBIO DE CONTRASEÑA - usuario@example.com        
======================================================================

ℹ️  Usuario: usuario_test
ℹ️  Rol: user

¿Forzar cambio de contraseña? (s/N): s

✅ Usuario marcado para cambio obligatorio de contraseña
ℹ️  En el próximo login deberá cambiar su contraseña
```

**Actualización en BD:**
- `force_password_change` → TRUE

**Comportamiento en login:**
El endpoint `/auth/login` retornará:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "requires_password_change": true,
  "is_first_login": false,
  "password_expired": false
}
```

El frontend debe redirigir a `/change-password?reason=forced`

---

### 5. `activate` / `deactivate` - Activar/Desactivar Usuario

**Descripción:** Controla el acceso de usuarios sin eliminarlos.

#### Desactivar Usuario

```bash
python scripts/manage_users.py deactivate usuario@example.com
```

**Efecto:**
- `activo` → FALSE
- Usuario NO puede hacer login
- Datos permanecen en BD
- Reversible

#### Activar Usuario

```bash
python scripts/manage_users.py activate usuario@example.com
```

**Efecto:**
- `activo` → TRUE
- Usuario puede hacer login nuevamente

#### Ejemplo Completo

```bash
# Desactivar
$ python scripts/manage_users.py deactivate usuario@example.com

======================================================================
                DESACTIVAR USUARIO - usuario@example.com              
======================================================================

ℹ️  Estado actual: Activo

¿Confirmar operación? (s/N): s

✅ Usuario desactivado exitosamente

# Verificar en lista
$ python scripts/manage_users.py list
ID    EMAIL                   USERNAME    ROL    ACTIVO   ESTADO PASSWORD
5     usuario@example.com     usuario     user   No       ✅ OK (85 días)

# Reactivar
$ python scripts/manage_users.py activate usuario@example.com

✅ Usuario activado exitosamente
```

---

## 🎨 Códigos de Color en Terminal

El script usa colores para facilitar la lectura:

| Color | Significado | Ejemplos |
|-------|-------------|----------|
| 🔴 Rojo | Error o atención urgente | Contraseña expirada, cambio forzado |
| 🟡 Amarillo | Advertencia | Por expirar (≤7 días) |
| 🟢 Verde | Éxito | Contraseña OK, operación exitosa |
| 🔵 Azul | Información | Encabezados, datos |
| 🟠 Cian | Detalles informativos | Mensajes ℹ️ |

---

## 🔐 Integración con Políticas de Contraseñas

El script está **100% integrado** con el sistema de políticas:

### Al Cambiar Contraseña

✅ Valida fortaleza (8+ chars, mayúscula, minúscula, número)  
✅ Hashea con bcrypt  
✅ Actualiza `password_changed_at`  
✅ Calcula `password_expires_at` (90 días)  
✅ Resetea `first_login` y `force_password_change`  
✅ Registra IP (como "CLI")  

### Al Crear Usuario

✅ Marca `first_login = TRUE`  
✅ Configura expiración automática  
✅ Genera contraseña temporal segura  

### Estados Visibles

El comando `list` muestra el estado calculado según lógica de negocio:

```python
if first_login:
    return "PRIMER_LOGIN"
elif force_password_change:
    return "CAMBIO_FORZADO"
elif password_expires_at < NOW:
    return "EXPIRADA"
elif days_until_expiration <= 7:
    return "POR_EXPIRAR"
else:
    return "OK"
```

---

## 📂 Ubicación de Archivos

```
proyecto/
├── scripts/
│   ├── manage_users.py          ← Script principal (NUEVO)
│   ├── crear_usuario.py         ← Script antiguo (deprecado)
│   └── test_password_policy.py  ← Tests de políticas
├── app/
│   ├── repository/
│   │   └── users_repo.py        ← Funciones de BD usadas
│   └── core/
│       └── database.py          ← Conexión MySQL
└── docs/
    ├── GESTION_USUARIOS_CLI.md  ← Esta guía
    └── GUIA_POLITICAS_CONTRASENAS.md
```

---

## ⚙️ Requisitos Previos

### 1. Entorno Virtual Activado

```bash
source .venv/bin/activate
```

### 2. Variables de Entorno (.env)

```env
DB_HOST=localhost
DB_USER=profesor
DB_PASSWORD=4688
DB_NAME=clientes_autenticado_db
```

### 3. Base de Datos Inicializada

```bash
mysql -u profesor -p4688 < docs/init_db.sql
```

### 4. Dependencias Instaladas

```bash
pip install -r requirements.txt
```

Necesarias:
- `mysql-connector-python`
- `passlib`
- `python-dotenv`

---

## 🛠️ Casos de Uso Prácticos

### Escenario 1: Onboarding de Empleado Nuevo

```bash
# 1. Crear usuario
python scripts/manage_users.py create-user \
  juan.perez@empresa.com jperez --rol user

# Salida: Contraseña temporal: Temp202602!

# 2. Enviar credenciales por email seguro

# 3. Usuario hace login → debe cambiar contraseña
# (automático por first_login=TRUE)
```

### Escenario 2: Contraseña Comprometida

```bash
# 1. Desactivar inmediatamente
python scripts/manage_users.py deactivate usuario@empresa.com

# 2. Cambiar contraseña
python scripts/manage_users.py change-password usuario@empresa.com \
  --password NuevaSegura123!

# 3. Reactivar
python scripts/manage_users.py activate usuario@empresa.com

# 4. Notificar al usuario
```

### Escenario 3: Auditoría de Seguridad

```bash
# Ver todos los usuarios y sus estados
python scripts/manage_users.py list

# Identificar contraseñas por expirar
# (buscar en salida: ⏰ o ❌)

# Forzar cambio a usuarios críticos
python scripts/manage_users.py force-change admin@empresa.com
python scripts/manage_users.py force-change finanzas@empresa.com
```

### Escenario 4: Empleado Sale de la Empresa

```bash
# Opción 1: Desactivar (reversible, mantiene datos)
python scripts/manage_users.py deactivate exempleado@empresa.com

# Opción 2: Dejar inactivo para auditoría
# (no requiere acción, solo verificar en lista)

# Opción 3: Eliminar desde MySQL (irreversible)
# (no implementado en script por seguridad)
```

### Escenario 5: Reset Masivo de Contraseñas

```bash
#!/bin/bash
# Script batch para forzar cambio a múltiples usuarios

USUARIOS=(
  "user1@example.com"
  "user2@example.com"
  "user3@example.com"
)

for email in "${USUARIOS[@]}"; do
  echo "s" | python scripts/manage_users.py force-change "$email"
done

echo "✅ Reset masivo completado"
python scripts/manage_users.py list
```

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError: No module named 'dotenv'

**Causa:** Entorno virtual no activado o dependencias no instaladas

**Solución:**
```bash
source .venv/bin/activate
pip install python-dotenv
```

### Error: cannot import name 'user_repository'

**Causa:** Versión antigua del código

**Solución:**
El script usa funciones directas, no singletons:
```python
from app.repository.users_repo import (
    get_user_by_username,
    change_user_password,
    # ...
)
```

### Error: Connection refused

**Causa:** MySQL no está corriendo

**Solución:**
```bash
# Ubuntu/Debian
sudo systemctl start mysql

# Verificar
mysql -u profesor -p4688 -e "SELECT 1"
```

### Error: Unknown database 'clientes_autenticado_db'

**Causa:** Base de datos no inicializada

**Solución:**
```bash
mysql -u profesor -p4688 < docs/init_db.sql
```

### Error: La contraseña debe tener al menos una mayúscula"

**Causa:** Contraseña débil

**Solución:**
Usar contraseña que cumpla:
- ✅ Mínimo 8 caracteres
- ✅ Al menos 1 mayúscula
- ✅ Al menos 1 minúscula  
- ✅ Al menos 1 número

Ejemplo válido: `MiPass123`

### Advertencia: Operación cancelada

**Causa:** Se presionó 'N' en la confirmación

**Solución:**
Ejecutar nuevamente y presionar 's' para confirmar

---

## 🔗 Referencias Relacionadas

| Documento | Contenido |
|-----------|-----------|
| [GUIA_POLITICAS_CONTRASENAS.md](GUIA_POLITICAS_CONTRASENAS.md) | Sistema de políticas de contraseñas |
| [QUICK_START_PASSWORD_POLICY.md](QUICK_START_PASSWORD_POLICY.md) | Inicio rápido con políticas |
| [CREAR_USUARIOS_GUIA.md](CREAR_USUARIOS_GUIA.md) | Script antiguo `crear_usuario.py` |
| [CAMBIAR_PASSWORD_GUIA.md](CAMBIAR_PASSWORD_GUIA.md) | Cambio de contraseñas vía API |

---

## 📝 Migración desde Scripts Antiguos

### De `crear_usuario.py` a `manage_users.py`

**Antes:**
```bash
python scripts/crear_usuario.py
# (proceso interactivo paso a paso)
```

**Ahora:**
```bash
# Modo interactivo similar
python scripts/manage_users.py create-user nuevo@example.com nuevouser

# O modo directo con flags
python scripts/manage_users.py create-user nuevo@example.com nuevouser \
  --rol admin --password Admin123!
```

**Ventajas adicionales:**
- ✅ Validación de contraseña
- ✅ Integración con políticas
- ✅ Confirmación antes de crear
- ✅ Generación automática de contraseña temporal

---

## 🎯 Resumen de Comandos

```bash
# Listar usuarios con estado de seguridad
python scripts/manage_users.py list

# Cambiar contraseña (interactivo)
python scripts/manage_users.py change-password usuario@example.com

# Cambiar contraseña (directo)
python scripts/manage_users.py change-password usuario@example.com --password Nueva123!

# Crear usuario básico
python scripts/manage_users.py create-user nuevo@example.com nuevouser

# Crear admin con contraseña
python scripts/manage_users.py create-user admin@example.com adminuser \
  --rol admin --password AdminPass123!

# Forzar cambio de contraseña
python scripts/manage_users.py force-change usuario@example.com

# Desactivar usuario
python scripts/manage_users.py deactivate usuario@example.com

# Activar usuario
python scripts/manage_users.py activate usuario@example.com

# Ayuda
python scripts/manage_users.py --help
```

---

## ✅ Checklist de Validación

Después de usar el script, verifica:

- [ ] Usuario aparece en `python scripts/manage_users.py list`
- [ ] Estado de contraseña es correcto
- [ ] Usuario puede hacer login (si está activo)
- [ ] Si `first_login=TRUE`, se requiere cambio de contraseña
- [ ] Fecha de expiración es correcta (90 días desde cambio)

---

**Última actualización:** 7 de febrero de 2026  
**Versión:** 1.0  
**Autor:** Sistema de Gestión de Usuarios
