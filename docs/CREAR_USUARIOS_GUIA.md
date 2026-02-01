# 📚 Guía: Crear Usuarios desde Consola

## Descripción General

Esta guía explica cómo usar el **script interactivo para crear usuarios** en la base de datos MySQL de forma segura desde la consola.

El script automatiza el proceso de:
- 📝 Capturar nombre de usuario
- 🔑 Solicitar contraseña de forma segura
- 🔐 Hashear automáticamente con bcrypt
- 💾 Insertar en la base de datos MySQL (vinculando con tabla de roles)
- ✅ Confirmar la creación exitosa

## Ubicación del Código

```
proyecto/
├── scripts/
│   └── crear_usuario.py          ← Script principal
├── app/
│   └── auth/
│       └── passwords.py           ← Módulo de hashing
└── docs/
    ├── CREAR_USUARIOS_GUIA.md     ← Esta guía
    └── init_db.sql                ← Script de inicialización BD
```

### Archivos Relacionados

| Archivo | Propósito |
|---------|-----------|
| `scripts/crear_usuario.py` | Script interactivo para crear usuarios |
| `app/auth/passwords.py` | Funciones de hashing bcrypt |
| `app/database.py` | Conexión a MySQL |
| `app/core/config.py` | Configuración de variables de entorno |

## Requisitos Previos

### 1. **Variables de Entorno (.env)**

Asegúrate de tener configuradas en `.env`:

```bash
DB_HOST=localhost
DB_USER=profesor
DB_PASSWORD=4688
DB_NAME=clientes_autenticado_db
SECRET_KEY=tu-clave-secreta
```

### 2. **Base de Datos Existente**

La tabla `usuarios` debe existir. Si no la tienes, ejecuta primero:

```bash
mysql -u profesor -p4688 clientes_autenticado_db < docs/init_db.sql
```

### 3. **Dependencias Python Instaladas**

```bash
pip install -r requirements.txt
```

Las librerías necesarias son:
- `mysql-connector-python` - Conexión a MySQL
- `passlib` - Hashing de contraseñas
- `python-dotenv` - Manejo de variables de entorno

## Cómo Usar el Script

### Opción 1: Ejecución Interactiva

**Paso 1:** Navega al directorio del proyecto

```bash
cd /home/sulbaranjc/proyectos/python/backend/fastapi/api/clientes_api_autenticada
```

**Paso 2:** Ejecuta el script

```bash
python3 scripts/crear_usuario.py
```

**Paso 3:** Sigue las instrucciones:

```
============================================================
  🔐 CREADOR DE USUARIOS - FastAPI Clientes API
============================================================

📝 Ingrese el nombre de usuario: admin
```

El script te pedirá:
1. **Nombre de usuario** (mínimo 3 caracteres)
2. **Contraseña** (mínimo 6 caracteres, no se muestra)
3. **Confirmación de contraseña** (debe coincidir)
4. **Rol del usuario** (admin o lector)

### Opción 2: Ejecución con Permisos de Ejecución

Si quieres hacer el script ejecutable:

```bash
chmod +x scripts/crear_usuario.py
./scripts/crear_usuario.py
```

## Ejemplo de Uso Completo

```bash
$ python3 scripts/crear_usuario.py

============================================================
  🔐 CREADOR DE USUARIOS - FastAPI Clientes API
============================================================

📝 Ingrese el nombre de usuario: juan_perez

🔑 Ingrese la contraseña (no se mostrará mientras escribe):
   Contraseña: 
   Confirme la contraseña: 

👤 Seleccione el rol del usuario:
   1. admin   (acceso total)
   2. lector  (solo lectura)

   Opción (1-2): 2

⏳ Creando usuario 'juan_perez' con rol 'lector'...

✅ Usuario 'juan_perez' creado exitosamente
   Rol: lector
   Hash: $2b$12$o00cK68S.E1NdDf5.tAhd.FeZF...

✨ Usuario creado exitosamente

   Datos de acceso:
   • Usuario: juan_perez
   • Contraseña: (la que ingresó)
   • Rol: lector

============================================================
```

## Validación: Verificar que el Usuario fue Creado

Después de crear un usuario, verifica que se insertó correctamente:

```bash
mysql -u profesor -p4688 clientes_autenticado_db -e "SELECT id, username, email, role, activo FROM usuarios WHERE username='juan_perez';"
```

**Salida esperada:**

```
+----+------------+---------------------+--------+--------+
| id | username   | email               | role   | activo |
+----+------------+---------------------+--------+--------+
|  5 | juan_perez | juan_perez@example.com | lector |      1 |
+----+------------+---------------------+--------+--------+
```

## Funcionalidades del Script

### ✅ Validaciones Incluidas

| Validación | Descripción |
|-----------|-------------|
| **Nombre duplicado** | ❌ No permite crear usuarios que ya existen |
| **Nombre vacío** | ❌ Requiere al menos 3 caracteres |
| **Contraseña vacía** | ❌ Requiere al menos 6 caracteres |
| **Contraseñas coinciden** | ✅ Verifica que ambas contraseñas sean iguales |
| **Rol válido** | ✅ Solo acepta admin, lector o usuario |

### 🔐 Seguridad

- **Contraseña no mostrada:** Usa `getpass.getpass()` para entrada segura
- **Hashing automático:** bcrypt con 12 iteraciones (costo 12)
- **Email generado:** Crea automáticamente email basado en username
- **Usuario activo:** Se crea con `activo=1` para que pueda usar la API inmediatamente

### 📊 Información Mostrada

Al crear el usuario, el script muestra:
- ✅ Confirmación de éxito
- 📝 Nombre de usuario creado
- 👤 Rol asignado
- 🔐 Primeros 40 caracteres del hash (sin mostrar la contraseña)

## Estructura del Script

```python
get_connection()          # Conecta a MySQL
├── Lee variables de .env
└── Retorna conexión

username_exists()         # Verifica duplicados
├── Consulta BD
└── Retorna True/False

create_user()            # Crea el usuario
├── Verifica username
├── Hashea contraseña
├── Inserta en BD
└── Confirma operación

main()                   # Interfaz interactiva
├── Solicita username
├── Solicita contraseña
├── Solicita rol
└── Llama a create_user()
```

## Casos de Uso

### 📚 Para Estudiantes - Crear BD desde Cero

```bash
# 1. Crear tablas
mysql -u profesor -p4688 < docs/init_db.sql

# 2. Crear usuario admin
python3 scripts/crear_usuario.py
   Usuario: admin
   Contraseña: MiPassword123
   Rol: 1 (admin)

# ✅ BD lista para usar la API
```

### 👨‍🏫 Para Docentes - Crear Múltiples Usuarios

```bash
# Crear admin
python3 scripts/crear_usuario.py

# Crear lector
python3 scripts/crear_usuario.py
```

### 🧪 Para Testing - Usuarios de Prueba

```bash
# Usuario para probar login
python3 scripts/crear_usuario.py
   Usuario: test_user
   Contraseña: test123456
   Rol: 2 (lector)

# Usuario admin para probar permisos
python3 scripts/crear_usuario.py
   Usuario: test_admin
   Contraseña: admin123456
   Rol: 1 (admin)
```

## Archivos Relacionados

### 📖 Documentación

- [ANALISIS_AUTENTICACION.md](./ANALISIS_AUTENTICACION.md) - Análisis técnico de la autenticación
- [GUIA_TECNICA_AUTENTICACION.md](./GUIA_TECNICA_AUTENTICACION.md) - Arquitectura y diseño JWT
- [PRUEBAS_CONSOLA.md](./PRUEBAS_CONSOLA.md) - Pruebas de API desde consola
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Referencia rápida

### 💻 Código Fuente

```python
# app/auth/passwords.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

## Solución de Problemas

### ❌ "Error al conectar a MySQL"

**Causa:** Variables de entorno no configuradas o BD no disponible

**Solución:**
```bash
# Verifica variables de entorno
cat .env

# Verifica que MySQL está corriendo
mysql -u profesor -p4688 -e "SELECT 1;"
```

### ❌ "El usuario 'xxx' ya existe"

**Causa:** Ya hay un usuario con ese nombre

**Solución:** Usa un nombre diferente o consulta usuarios existentes:
```bash
mysql -u profesor -p4688 clientes_autenticado_db -e "SELECT username FROM usuarios;"
```

### ❌ "ModuleNotFoundError: No module named 'mysql'"

**Causa:** Dependencias no instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

### ❌ "Operación cancelada por el usuario" (Ctrl+C)

**Causa:** Presionaste Ctrl+C durante la ejecución

**Solución:** Vuelve a ejecutar el script:
```bash
python3 scripts/crear_usuario.py
```

## Integración con la API

Una vez creado el usuario, puedes probarlo con la API:

### 1. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=MiPassword123"
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Usar el Token

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET "http://localhost:8000/clientes/" \
  -H "Authorization: Bearer $TOKEN"
```

## Resumen

| Aspecto | Descripción |
|--------|------------|
| **Ubicación** | `scripts/crear_usuario.py` |
| **Ejecución** | `python3 scripts/crear_usuario.py` |
| **Entrada** | Interactiva (username, password, rol) |
| **Proceso** | Hashea y inserta en BD MySQL |
| **Salida** | Confirmación de éxito o error |
| **Seguridad** | bcrypt con costo 12, sin mostrar contraseña |
| **Validaciones** | Username único, longitud mínima, coincidencia de contraseña |

---

**Última actualización:** 1 de febrero de 2026  
**Para:** Estudiantes de FastAPI y APIs REST seguras  
**Docente:** [Tu nombre]
