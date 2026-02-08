# 🚀 API REST de Gestión de Clientes con Autenticación JWT by JC

> **Proyecto Educativo** - FastAPI + MySQL + JWT Authentication by JC
> 
> Última actualización: 6 de enero de 2026

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características Principales](#-características-principales)
3. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
4. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Requisitos Previos](#-requisitos-previos)
7. [Instalación y Configuración](#-instalación-y-configuración)
8. [Ejecución del Proyecto](#-ejecución-del-proyecto)
9. [API Endpoints](#-api-endpoints)
10. [Sistema de Autenticación](#-sistema-de-autenticación)
11. [Control de Acceso Basado en Roles](#-control-de-acceso-basado-en-roles)
12. [Validaciones y Schemas](#-validaciones-y-schemas)
13. [Base de Datos](#-base-de-datos)
14. [Documentación Interactiva](#-documentación-interactiva)
15. [Buenas Prácticas Implementadas](#-buenas-prácticas-implementadas)
16. [Herramientas de Gestión](#-herramientas-de-gestión)
17. [Solución de Problemas](#-solución-de-problemas)

---

## 📖 Descripción General

Este proyecto es una **API REST profesional** desarrollada con **FastAPI** que implementa un sistema completo de gestión de clientes con autenticación JWT y control de acceso basado en roles. 

### 🎯 Finalidad Educativa

Diseñado específicamente para estudiantes de **Desarrollo de Aplicaciones Web** y **Desarrollo de Aplicaciones Multiplataforma**, este proyecto demuestra:

✅ **Arquitectura moderna de APIs REST**
- Separación completa Backend/Frontend
- Arquitectura en capas (Layered Architecture)
- Diseño modular y escalable

✅ **Seguridad implementada profesionalmente**
- Autenticación OAuth2 con JWT
- Hash de contraseñas con bcrypt
- Control de acceso basado en roles (RBAC)
- Protección de endpoints sensibles

✅ **Mejores prácticas de desarrollo**
- Validación robusta de datos con Pydantic
- Manejo apropiado de errores HTTP
- Documentación automática con OpenAPI/Swagger
- Variables de entorno para configuración

---

## ✨ Características Principales

### 🔐 Autenticación y Autorización
- **Login con JWT**: Sistema OAuth2 Password Flow compatible con Swagger UI
- **Tokens de acceso**: JWT firmados con expiración configurable
- **Dos roles de usuario**: 
  - `admin`: CRUD completo sobre clientes
  - `lector`: Solo lectura de clientes
- **Protección de endpoints**: Middleware de autenticación y autorización

### 📊 Gestión de Clientes
- **CRUD completo**: Crear, leer, actualizar y eliminar clientes
- **Validaciones exhaustivas**: Email, teléfono, nombres con regex
- **Endpoints públicos**: Lectura de clientes sin autenticación
- **Endpoints protegidos**: Escritura/modificación requiere rol admin

### 🛠️ Características Técnicas
- **CORS configurado**: Listo para integración con frontends
- **Manejo de errores**: Respuestas HTTP apropiadas para cada situación
- **Documentación interactiva**: Swagger UI y ReDoc automáticos
- **Base de datos MySQL**: Con índices y restricciones apropiadas

---

## 🏗️ Arquitectura del Proyecto

```
┌──────────────────────────────────────────────┐
│         CLIENTE (Frontend)                   │
│    React / Vue / Angular / Mobile            │
└────────────────┬─────────────────────────────┘
                 │ HTTP/JSON + JWT Bearer
                 ↓
┌──────────────────────────────────────────────┐
│    CAPA DE PRESENTACIÓN (Routers)            │
│  ┌─────────────┐      ┌──────────────┐      │
│  │ Auth Router │      │ Clientes     │      │
│  │ /auth/login │      │ Router       │      │
│  └─────────────┘      │ /clientes    │      │
│                       └──────────────┘      │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│    CAPA DE SEGURIDAD (Auth)                  │
│  ┌──────────────┐  ┌────────────────┐       │
│  │ JWT Handler  │  │ Dependencies   │       │
│  │ • create     │  │ • require_admin│       │
│  │ • decode     │  │ • get_current  │       │
│  └──────────────┘  └────────────────┘       │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│    CAPA DE VALIDACIÓN (Schemas)              │
│  • ClienteCreate    • ClienteUpdate          │
│  • ClienteResponse  • EmailStr               │
│  • Field validators con regex                │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│    CAPA DE LÓGICA (Database + Repository)    │
│  ┌────────────────┐  ┌──────────────┐       │
│  │ database.py    │  │ users_repo   │       │
│  │ • CRUD clientes│  │ • get_user   │       │
│  └────────────────┘  └──────────────┘       │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────┴─────────────────────────────┐
│    CAPA DE DATOS (MySQL)                     │
│  • clientes    • usuarios    • roles         │
└──────────────────────────────────────────────┘
```

### Ventajas de esta Arquitectura:

- ✅ **Separación de responsabilidades**: Cada capa tiene una función específica
- ✅ **Mantenibilidad**: Fácil de modificar y extender
- ✅ **Reutilización**: El backend puede servir múltiples frontends
- ✅ **Escalabilidad**: Se puede escalar cada capa independientemente
- ✅ **Testabilidad**: Cada capa se puede probar de forma aislada

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| **Python** | 3.12+ | Lenguaje de programación principal |
| **FastAPI** | 0.128.0 | Framework web moderno y de alto rendimiento |
| **Pydantic** | 2.12.5 | Validación de datos y serialización |
| **MySQL Connector** | 9.5.0 | Driver para conexión con MySQL |
| **Uvicorn** | 0.40.0 | Servidor ASGI para ejecutar FastAPI |
| **Python-dotenv** | 1.2.1 | Gestión de variables de entorno |
| **Email-validator** | 2.3.0 | Validación de direcciones de email |
| **Python-Jose** | 3.5.0 | Generación y verificación de JWT |
| **Passlib** | 1.7.4 | Hash seguro de contraseñas |
| **Bcrypt** | 3.2.2 | Algoritmo de hashing para passwords |
| **Python-multipart** | 0.0.21 | Procesamiento de datos de formulario |

### Dependencias de Desarrollo
- **Black** | 25.12.0 | Formateador de código Python

---

## 📁 Estructura del Proyecto

```
clientes_api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   │
│   ├── core/
│   │   └── config.py           # Configuración centralizada (SECRET_KEY, JWT)
│   │
│   ├── auth/
│   │   ├── jwt.py              # Creación y decodificación de JWT
│   │   ├── passwords.py        # Hash y verificación de contraseñas
│   │   └── deps.py             # Dependencias de autenticación/autorización
│   │
│   ├── routers/
│   │   ├── auth.py             # Endpoint de login OAuth2
│   │   └── clientes.py         # CRUD de clientes (público + protegido)
│   │
│   ├── schemas/
│   │   ├── auth.py             # Schemas de autenticación
│   │   └── cliente.py          # Schemas de validación de clientes
│   │
│   ├── repository/
│   │   └── users_repo.py       # Consultas de usuarios para auth
│   │
│   └── database.py             # Funciones CRUD y conexión MySQL
│
├── docs/
│   └── init_db.sql             # Script de inicialización de BD
│
├── .env                        # Variables de entorno (NO INCLUIR EN GIT)
├── .env.example                # Plantilla de variables de entorno
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Este archivo

```

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- ✅ **Python 3.12 o superior**
  ```bash
  python --version
  ```

- ✅ **MySQL Server 8.0 o superior**
  ```bash
  mysql --version
  ```

- ✅ **pip** (gestor de paquetes de Python)
  ```bash
  pip --version
  ```

- ✅ **Git** (opcional, para clonar el repositorio)

---

## ⚙️ Instalación y Configuración

### 1️⃣ Clonar o Descargar el Proyecto

```bash
git clone <url-del-repositorio>
cd clientes_api
```

### 2️⃣ Crear y Activar Entorno Virtual

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Base de Datos MySQL

**a) Crear la base de datos:**
```bash
mysql -u root -p < docs/init_db.sql
```

**b) Verificar que se crearon las tablas:**
```bash
mysql -u root -p
```
```sql
USE clientes_db;
SHOW TABLES;
-- Debe mostrar: clientes, roles, usuarios
```

### 5️⃣ Configurar Variables de Entorno

**a) Crear archivo `.env` en la raíz del proyecto:**
```bash
cp .env.example .env
```

**b) Editar `.env` con tus credenciales:**
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password_mysql
DB_NAME=clientes_db

# JWT Configuration
SECRET_KEY=tu_clave_secreta_super_segura_aqui_cambiala
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ **IMPORTANTE**: Genera una SECRET_KEY única usando:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## 🚀 Ejecución del Proyecto

### Modo Desarrollo (con auto-reload)

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: **http://127.0.0.1:8000**

### Configurar Alias (Opcional)

Si usas Linux/Mac, puedes crear un alias en tu shell:

**Bash (~/.bashrc):**
```bash
alias py-uvi-app="uvicorn app.main:app --reload"
```

**Luego simplemente ejecuta:**
```bash
py-uvi-app
```

---

## 📍 API Endpoints

### 🔐 Autenticación

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| `POST` | `/auth/login` | Login y generación de JWT | No | - |

**Request (Form Data):**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 👥 Gestión de Clientes

| Método | Endpoint | Descripción | Auth | Rol |
|--------|----------|-------------|------|-----|
| `GET` | `/clientes/` | Listar todos los clientes | No | - |
| `GET` | `/clientes/{id}` | Obtener cliente por ID | No | - |
| `POST` | `/clientes/` | Crear nuevo cliente | Sí | Admin |
| `PUT` | `/clientes/{id}` | Actualizar cliente | Sí | Admin |
| `DELETE` | `/clientes/{id}` | Eliminar cliente | Sí | Admin |

### Ejemplos de Uso

**1. Listar clientes (público):**
```bash
curl http://127.0.0.1:8000/clientes/
```

**2. Login:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**3. Crear cliente (requiere token):**
```bash
curl -X POST "http://127.0.0.1:8000/clientes/" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Pedro",
    "apellido": "González",
    "email": "pedro@example.com",
    "telefono": "+34612345678",
    "direccion": "Calle Principal 123"
  }'
```

---

## 🔐 Sistema de Autenticación

### Flujo de Autenticación

1. **Login**: Usuario envía `username` y `password` a `/auth/login`
2. **Verificación**: Sistema verifica credenciales contra la BD (hash bcrypt)
3. **Generación JWT**: Se crea un token firmado con información del usuario
4. **Respuesta**: Cliente recibe el token
5. **Uso**: Cliente incluye token en header `Authorization: Bearer <token>`
6. **Validación**: Cada request protegido verifica y decodifica el JWT

### Estructura del JWT

```json
{
  "sub": "admin",           // username
  "role": "admin",          // rol del usuario
  "exp": 1704585600         // timestamp de expiración
}
```

### Implementación de Seguridad

**Hash de contraseñas:**
```python
# app/auth/passwords.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**Creación de JWT:**
```python
# app/auth/jwt.py
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

---

## 🛡️ Control de Acceso Basado en Roles

### Roles Disponibles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **admin** | Administrador | CRUD completo de clientes |
| **lector** | Solo lectura | Solo GET endpoints |

### Usuarios de Prueba

| Username | Password | Rol |
|----------|----------|-----|
| `admin` | `admin123` | admin |
| `lector` | `lector123` | lector |

### Implementación de Autorización

**Dependencia `require_admin`:**
```python
# app/auth/deps.py
def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Permisos insuficientes"
        )
    return user
```

**Uso en endpoints protegidos:**
```python
# app/routers/clientes.py
@router.post("/", dependencies=[Depends(require_admin)])
def crear_cliente(cliente: ClienteCreate):
    # Solo usuarios admin pueden ejecutar esto
    pass
```

---

## ✅ Validaciones y Schemas

### Schema de Cliente

```python
# app/schemas/cliente.py
class ClienteCreate(BaseModel):
    nombre: str          # 2-50 caracteres, solo letras
    apellido: str        # 2-50 caracteres, solo letras
    email: EmailStr      # Validación automática de email
    telefono: str | None # Formato internacional (7-15 dígitos)
    direccion: str | None
```

### Validaciones Implementadas

**1. Nombres y Apellidos:**
- Mínimo 2 caracteres, máximo 50
- Solo letras, espacios, tildes y caracteres españoles (ñ, ü)
- Auto-capitalización (Title Case)
- Regex: `^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$`

**2. Email:**
- Validación completa con `EmailStr` de Pydantic
- Verifica formato y dominio válido

**3. Teléfono:**
- Formato internacional permitido
- 7-15 dígitos (puede incluir +, espacios, guiones, paréntesis)
- Se limpia automáticamente antes de validar

**4. Dirección:**
- Opcional
- Máximo 255 caracteres

### Ejemplo de Validación Exitosa

```json
{
  "nombre": "María José",
  "apellido": "García López",
  "email": "maria.garcia@example.com",
  "telefono": "+34 612 345 678",
  "direccion": "Av. Principal 123, Madrid"
}
```

### Ejemplo de Error de Validación

```json
{
  "nombre": "M",  // ❌ Menos de 2 caracteres
  "apellido": "García123",  // ❌ Contiene números
  "email": "no-es-email",  // ❌ Email inválido
  "telefono": "123"  // ❌ Menos de 7 dígitos
}
```

**Respuesta HTTP 422:**
```json
{
  "detail": [
    {
      "loc": ["body", "nombre"],
      "msg": "Debe tener al menos 2 caracteres",
      "type": "value_error"
    }
  ]
}
```

---

## 🗄️ Base de Datos

### Esquema de Tablas

**Tabla `clientes`:**
```sql
CREATE TABLE clientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  telefono VARCHAR(50),
  direccion VARCHAR(255)
);
```

**Tabla `roles`:**
```sql
CREATE TABLE roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(150)
);
```

**Tabla `usuarios`:**
```sql
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol_id INT NOT NULL,
  activo TINYINT NOT NULL DEFAULT 1,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  actualizado_en TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (rol_id) REFERENCES roles(id)
);
```

### Datos Iniciales

El script `docs/init_db.sql` incluye:
- ✅ 5 clientes de ejemplo
- ✅ 2 roles (admin, lector)
- ✅ 2 usuarios de prueba con contraseñas hasheadas

---

## 📚 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

### Swagger UI (OpenAPI)
**URL:** http://127.0.0.1:8000/docs

Características:
- ✅ Interfaz visual para probar endpoints
- ✅ Botón "Authorize" para login con JWT
- ✅ Generación automática de requests
- ✅ Visualización de respuestas en tiempo real

### ReDoc
**URL:** http://127.0.0.1:8000/redoc

Características:
- ✅ Documentación clara y organizada
- ✅ Exportación a PDF
- ✅ Búsqueda de endpoints

### Cómo Usar Swagger UI con Autenticación

1. Abrir http://127.0.0.1:8000/docs
2. Expandir endpoint `POST /auth/login`
3. Click en "Try it out"
4. Ingresar credenciales (`admin` / `admin123`)
5. Click "Execute"
6. Copiar el `access_token` de la respuesta
7. Click en botón "Authorize" (🔒 arriba a la derecha)
8. Pegar token en el campo y click "Authorize"
9. Ahora puedes probar endpoints protegidos

---

## ✨ Buenas Prácticas Implementadas

### 1. Arquitectura en Capas
- Separación clara de responsabilidades
- Código modular y reutilizable
- Fácil de testear y mantener

### 2. Validación de Datos
- Uso de Pydantic para validación automática
- Validators personalizados con regex
- Mensajes de error claros y específicos

### 3. Seguridad
- ✅ Contraseñas hasheadas con bcrypt (nunca en texto plano)
- ✅ JWT firmados con SECRET_KEY segura
- ✅ Tokens con expiración configurable
- ✅ Control de acceso basado en roles
- ✅ Variables sensibles en `.env` (excluidas de git)

### 4. Manejo de Errores
- Códigos HTTP apropiados (200, 201, 401, 403, 404, 409, 422, 500)
- Mensajes descriptivos para el cliente
- Captura de errores específicos de MySQL

### 5. CORS Configurado
- Preparado para integración con frontends
- Configurable para producción

### 6. Documentación
- Código autodocumentado con docstrings
- OpenAPI/Swagger automático
- README completo y actualizado

### 7. Variables de Entorno
- Configuración centralizada en `config.py`
- Uso de `.env` para secretos
- `.env.example` como plantilla

---

## 🔧 Solución de Problemas

### Error: "python-multipart" requerido

**Problema:**
```
RuntimeError: Form data requires "python-multipart" to be installed
```

**Solución:**
```bash
pip install python-multipart
```

### Error: Conexión a MySQL rechazada

**Problema:**
```
Error al conectar a MySQL: Access denied
```

**Solución:

## 📁 Estructura del Proyecto

```
clientes_api/
│
├── app/                          # Paquete principal de la aplicación
│   ├── __init__.py              # Inicializa el paquete
│   ├── main.py                  # Punto de entrada de la aplicación
│   ├── database.py              # Funciones de acceso a datos
│   │
│   ├── routers/                 # Módulo de rutas/endpoints
│   │   ├── __init__.py
│   │   └── clientes.py          # Endpoints de gestión de clientes
│   │
│   └── schemas/                 # Módulo de modelos de datos
│       ├── __init__.py
│       └── cliente.py           # Modelos Pydantic para clientes
│
├── docs/                         # Documentación y scripts SQL
│   └── init_db.sql              # Script de inicialización de BD
│
├── .env                         # Variables de entorno (NO versionar)
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Este archivo
```

### Descripción de Archivos Clave:

#### 📄 `app/main.py`
Archivo principal que:
- Inicializa la aplicación FastAPI
- Configura CORS para permitir peticiones desde el frontend
- Registra los routers (endpoints)
- Define el endpoint raíz

#### 📄 `app/database.py`
Contiene las funciones de acceso a datos:
- `get_connection()`: Establece conexión con MySQL
- `get_all_clientes()`: Obtiene todos los clientes
- `get_cliente_by_id()`: Obtiene un cliente por ID
- `create_cliente()`: Inserta un nuevo cliente
- `update_cliente()`: Actualiza un cliente existente
- `delete_cliente()`: Elimina un cliente

#### 📄 `app/routers/clientes.py`
Define los endpoints de la API:
- `GET /clientes`: Listar todos los clientes
- `GET /clientes/{id}`: Obtener un cliente específico
- `POST /clientes`: Crear un nuevo cliente
- `PUT /clientes/{id}`: Actualizar un cliente
- `DELETE /clientes/{id}`: Eliminar un cliente

#### 📄 `app/schemas/cliente.py`
Define los modelos de datos con Pydantic:
- `ClienteBase`: Modelo base con validaciones comunes
- `ClienteCreate`: Para crear nuevos clientes
- `ClienteUpdate`: Para actualizar clientes existentes
- `ClienteResponse`: Para las respuestas de la API
- `ClienteDB`: Representa los datos almacenados en BD

---

## 💡 Conceptos Clave

### 1️⃣ API REST
**REST** (Representational State Transfer) es un estilo de arquitectura que utiliza HTTP para la comunicación entre cliente y servidor.

**Características:**
- Usa métodos HTTP estándar (GET, POST, PUT, DELETE)
- Recursos identificados por URLs
- Sin estado (stateless)
- Formato JSON para intercambio de datos

### 2️⃣ CRUD Operations
**CRUD** = Create, Read, Update, Delete

| Operación | Método HTTP | Endpoint | Descripción |
|-----------|-------------|----------|-------------|
| **Create** | POST | `/clientes` | Crear nuevo cliente |
| **Read** | GET | `/clientes` | Listar todos los clientes |
| **Read** | GET | `/clientes/{id}` | Obtener un cliente |
| **Update** | PUT | `/clientes/{id}` | Actualizar cliente |
| **Delete** | DELETE | `/clientes/{id}` | Eliminar cliente |

### 3️⃣ Códigos de Estado HTTP

| Código | Significado | Uso en el Proyecto |
|--------|-------------|-------------------|
| **200** | OK | Respuesta exitosa (GET, PUT) |
| **201** | Created | Cliente creado exitosamente |
| **204** | No Content | Cliente eliminado (sin contenido) |
| **404** | Not Found | Cliente no encontrado |
| **409** | Conflict | Email duplicado |
| **422** | Unprocessable Entity | Error de validación |
| **500** | Internal Server Error | Error del servidor |

### 4️⃣ Pydantic Models
Pydantic es una librería para validación de datos usando type hints de Python.

**Ventajas:**
- Validación automática de tipos
- Mensajes de error descriptivos
- Conversión automática de datos
- Documentación automática en Swagger

### 5️⃣ Dependency Injection

**Solución:**
1. Verificar credenciales en el archivo `.env`
2. Verificar que MySQL esté corriendo:
   ```bash
   sudo systemctl status mysql
   ```
3. Verificar que la base de datos `clientes_db` existe:
   ```bash
   mysql -u root -p -e "SHOW DATABASES;"
   ```

### Error: SECRET_KEY no definida

**Problema:**
```
RuntimeError: SECRET_KEY no está definida en el archivo .env
```

**Solución:**
1. Crear archivo `.env` si no existe
2. Agregar la línea:
   ```env
   SECRET_KEY=tu_clave_generada_con_secrets
   ```
3. Generar clave segura:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### Error: Token inválido o expirado

**Problema:**
```
401 Unauthorized: Token inválido o expirado
```

**Solución:**
1. Verificar que el token se está enviando correctamente en el header:
   ```
   Authorization: Bearer <token>
   ```
2. El token expira según `ACCESS_TOKEN_EXPIRE_MINUTES` en `.env`
3. Hacer login nuevamente para obtener un nuevo token

### Error: Permisos insuficientes (403)

**Problema:**
```
403 Forbidden: Permisos insuficientes
```

**Solución:**
- El usuario `lector` solo puede hacer GET
- Usa el usuario `admin` para operaciones de escritura (POST, PUT, DELETE)

### El servidor no se levanta

**Problema:** El comando `uvicorn` no funciona

**Solución:**
```bash
# Asegúrate de estar en el entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Reinstalar uvicorn
pip install uvicorn --force-reinstall

# Ejecutar desde la raíz del proyecto
uvicorn app.main:app --reload
```

---

## 🎯 Casos de Uso y Ejemplos

### Caso 1: Sistema de Registro de Clientes para Tienda

**Escenario:** Una tienda quiere digitalizar el registro de sus clientes.

**Flujo:**
1. Empleado inicia sesión con `admin` / `admin123`
2. Obtiene token JWT
3. Registra nuevo cliente con POST `/clientes/`
4. Consulta lista de clientes con GET `/clientes/`
5. Actualiza información si hay cambios

### Caso 2: Portal de Consulta para Vendedores

**Escenario:** Vendedores necesitan consultar información de clientes pero no modificarla.

**Flujo:**
1. Vendedor inicia sesión con `lector` / `lector123`
2. Obtiene token JWT (con rol `lector`)
3. Consulta clientes (GET permitido)
4. Si intenta crear/modificar → Error 403 Forbidden

---

## 📖 Ejercicios Propuestos

### Nivel Básico

1. **Agregar campo "activo"** a la tabla clientes
   - Modificar base de datos
   - Actualizar schemas
   - Implementar endpoint para activar/desactivar

2. **Endpoint de búsqueda** por email
   - Crear `GET /clientes/search?email=...`
   - Implementar función en database.py

3. **Paginación** en listado de clientes
   - Agregar parámetros `skip` y `limit`
   - `GET /clientes?skip=0&limit=10`

### Nivel Intermedio

4. **Implementar búsqueda avanzada**
   - Buscar por nombre, apellido o email
   - Soporte de filtros múltiples

5. **Agregar timestamps** a clientes
   - `created_at` y `updated_at`
   - Actualizar automáticamente

6. **Soft delete**
   - No eliminar físicamente
   - Marcar como inactivo

### Nivel Avanzado

7. **Implementar refresh tokens**
   - Token de acceso corto (15 min)
   - Refresh token largo (7 días)

8. **Rate limiting**
   - Limitar requests por IP
   - Prevenir abuso de la API

9. **Logging completo**
   - Registrar todas las operaciones
   - Logs estructurados con timestamps

---

## 🚀 Próximos Pasos

### Mejoras Sugeridas

- [ ] **Testing**: Agregar tests unitarios con pytest
- [ ] **Migraciones**: Usar Alembic para gestionar cambios en BD
- [ ] **ORM**: Migrar a SQLAlchemy para mejor abstracción
- [ ] **Cache**: Implementar Redis para mejorar performance
- [ ] **Async**: Usar driver async de MySQL
- [ ] **Docker**: Containerizar la aplicación
- [ ] **CI/CD**: Automatizar despliegue con GitHub Actions
- [ ] **Monitoring**: Agregar métricas y observabilidad

### Integración con Frontend

Este backend está listo para conectarse con:
- **React**: Usando axios o fetch
- **Vue.js**: Usando axios o Vue Resource
- **Angular**: Usando HttpClient
- **Flutter/React Native**: Para apps móviles

**Ejemplo de consumo desde JavaScript:**
```javascript
// Login
const response = await fetch('http://127.0.0.1:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=admin&password=admin123'
});
const { access_token } = await response.json();

// Obtener clientes con autenticación
const clientes = await fetch('http://127.0.0.1:8000/clientes/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **MySQL Connector**: https://dev.mysql.com/doc/connector-python/en/
- **JWT (Python-Jose)**: https://python-jose.readthedocs.io/
- **Passlib**: https://passlib.readthedocs.io/

### Tutoriales Recomendados

- [FastAPI Tutorial Oficial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic Field Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [JWT Authentication en FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [SQL con Python](https://realpython.com/python-sql-libraries/)

### Videos Educativos

- FastAPI - A Python Framework Full Course (freeCodeCamp)
- Building REST APIs with FastAPI (TechWithTim)
- JWT Authentication Tutorial (Pretty Printed)

---

## 📝 Notas Finales

### Seguridad en Producción

⚠️ **IMPORTANTE**: Este proyecto es educativo. Para producción considera:

1. **Variables de entorno seguras**: No usar valores por defecto
2. **HTTPS**: Siempre usar SSL/TLS
3. **CORS específico**: No usar `allow_origins=["*"]`
4. **Rate limiting**: Limitar requests por IP
5. **Logging y monitoring**: Implementar observabilidad
6. **Validación adicional**: Sanitización de inputs
7. **Secretos seguros**: Usar gestores de secretos (AWS Secrets Manager, HashiCorp Vault)

### Licencia

Este proyecto es de código abierto con fines educativos.

### Contribuciones

Las contribuciones son bienvenidas:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 👨‍💻 Autor

**Juan Carlos Sulbarán González**

---

## 🙏 Agradecimientos

- Comunidad de FastAPI
- Documentación de Pydantic
- Estudiantes que han probado y mejorado este proyecto

---

<div align="center">

**¿Preguntas o sugerencias?**

Abre un issue en el repositorio o contacta al autor.

⭐ Si este proyecto te fue útil, dale una estrella ⭐

**Última actualización:** 6 de enero de 2026

</div>

DB_PASSWORD=tu_contraseña_mysql
DB_NAME=clientes_db
```

⚠️ **IMPORTANTE**: Nunca subir el archivo `.env` a repositorios públicos (agregar a `.gitignore`)

### Paso 5: Verificar Instalación

```bash
# Ver paquetes instalados
pip list

# Verificar conexión a la BD (opcional)
python -c "from app.database import get_connection; print('OK' if get_connection() else 'ERROR')"
```

---

## ▶️ Ejecución del Proyecto

### Modo Desarrollo

```bash
# Asegúrate de estar en el directorio del proyecto
# y tener el entorno virtual activado

uvicorn app.main:app --reload
```

**Parámetros:**
- `app.main:app`: Indica el módulo y la instancia de FastAPI
- `--reload`: Recarga automáticamente al detectar cambios (solo desarrollo)

### Salida Esperada:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Acceder a la Aplicación:

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000 | Endpoint raíz |
| http://127.0.0.1:8000/docs | **Swagger UI** - Documentación interactiva |
| http://127.0.0.1:8000/redoc | **ReDoc** - Documentación alternativa |

### Modo Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Parámetros adicionales:**
- `--host 0.0.0.0`: Acepta conexiones externas
- `--port 8000`: Puerto de escucha
- `--workers 4`: Número de procesos worker

---

## 🌐 API Endpoints

### 1️⃣ Listar Todos los Clientes

```http
GET /clientes
```

**Respuesta Exitosa (200):**
```json
[
  {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan.perez@example.com",
    "telefono": "555-0101",
    "direccion": "Calle 123, Ciudad"
  },
  ...
]
```

### 2️⃣ Obtener Un Cliente Específico

```http
GET /clientes/{id}
```

**Parámetros:**
- `id` (path): ID del cliente

**Respuesta Exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan.perez@example.com",
  "telefono": "555-0101",
  "direccion": "Calle 123, Ciudad"
}
```

**Respuesta Error (404):**
```json
{
  "detail": "Cliente no encontrado"
}
```

### 3️⃣ Crear Nuevo Cliente

```http
POST /clientes
Content-Type: application/json
```

**Cuerpo de la Petición:**
```json
{
  "nombre": "Pedro",
  "apellido": "González",
  "email": "pedro.gonzalez@example.com",
  "telefono": "+34 612345678",
  "direccion": "Av. Principal 456"
}
```

**Campos Obligatorios:**
- `nombre` ✅
- `apellido` ✅
- `email` ✅

**Campos Opcionales:**
- `telefono` (puede ser `null` o vacío)
- `direccion` (puede ser `null` o vacío)

**Respuesta Exitosa (201):**
```json
{
  "id": 6,
  "nombre": "Pedro",
  "apellido": "González",
  "email": "pedro.gonzalez@example.com",
  "telefono": "+34 612345678",
  "direccion": "Av. Principal 456"
}
```

**Respuesta Error - Email Duplicado (409):**
```json
{
  "detail": "Ya existe un cliente con ese email"
}
```

**Respuesta Error - Validación (422):**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "nombre"],
      "msg": "Debe tener al menos 2 caracteres"
    }
  ]
}
```

### 4️⃣ Actualizar Cliente

```http
PUT /clientes/{id}
Content-Type: application/json
```

**Parámetros:**
- `id` (path): ID del cliente a actualizar

**Cuerpo de la Petición:**
```json
{
  "nombre": "Pedro",
  "apellido": "González Sánchez",
  "email": "pedro.gonzalez@example.com",
  "telefono": "+34 687654321",
  "direccion": "Nueva Dirección 789"
}
```

**Respuesta Exitosa (200):**
```json
{
  "id": 6,
  "nombre": "Pedro",
  "apellido": "González Sánchez",
  "email": "pedro.gonzalez@example.com",
  "telefono": "+34 687654321",
  "direccion": "Nueva Dirección 789"
}
```

### 5️⃣ Eliminar Cliente

```http
DELETE /clientes/{id}
```

**Parámetros:**
- `id` (path): ID del cliente a eliminar

**Respuesta Exitosa (204):**
Sin contenido

**Respuesta Error (404):**
```json
{
  "detail": "Cliente no encontrado"
}
```

---

## ✅ Validaciones Implementadas

### Campo: `nombre` y `apellido`

| Regla | Descripción | Ejemplo Válido | Ejemplo Inválido |
|-------|-------------|----------------|------------------|
| **No vacío** | No puede estar vacío | "Juan" | "" o "   " |
| **Longitud mínima** | Al menos 2 caracteres | "Li" | "J" |
| **Longitud máxima** | Máximo 50 caracteres | "Juan Carlos" | (Cadena > 50) |
| **Solo letras** | Letras, espacios y acentos | "José María" | "Juan123" |
| **Capitalización** | Convierte a Title Case | "JUAN" → "Juan" | - |

### Campo: `email`

| Regla | Descripción | Ejemplo Válido | Ejemplo Inválido |
|-------|-------------|----------------|------------------|
| **Formato válido** | Email bien formado | "user@example.com" | "user@" o "user.com" |
| **Único en BD** | No puede repetirse | "nuevo@example.com" | (Email existente) |

### Campo: `telefono` (opcional)

| Regla | Descripción | Ejemplo Válido | Ejemplo Inválido |
|-------|-------------|----------------|------------------|
| **Formato** | 7-15 dígitos | "+34 612345678" | "123" |
| **Caracteres permitidos** | Números, +, -, (), espacios | "555-0101" | "abc123" |
| **Limpieza** | Elimina espacios y guiones | "555 - 0101" → validado | - |

### Campo: `direccion` (opcional)

| Regla | Descripción | Ejemplo Válido | Ejemplo Inválido |
|-------|-------------|----------------|------------------|
| **Longitud máxima** | Máximo 200 caracteres | "Calle 123, Piso 4" | (Cadena > 200) |

### Validaciones a Nivel de Base de Datos

```sql
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,           -- No nulo
    apellido VARCHAR(100) NOT NULL,         -- No nulo
    email VARCHAR(150) NOT NULL UNIQUE,     -- No nulo y único
    telefono VARCHAR(50),                   -- Opcional
    direccion VARCHAR(255)                  -- Opcional
);
```

---

## 🚨 Manejo de Errores

### Estrategia de Manejo de Errores

El proyecto implementa un manejo robusto de errores en múltiples niveles:

#### 1️⃣ Errores de Validación (422)

FastAPI + Pydantic validan automáticamente:
- Tipos de datos incorrectos
- Campos requeridos faltantes
- Formatos inválidos

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "nombre"],
      "msg": "Debe tener al menos 2 caracteres",
      "input": "J"
    }
  ]
}
```

#### 2️⃣ Errores de Negocio

**Cliente no encontrado (404):**
```python
if not cliente:
    raise HTTPException(
        status_code=404,
        detail="Cliente no encontrado"
    )
```

**Email duplicado (409):**
```python
if e.errno == 1062:  # MySQL duplicate entry
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ya existe un cliente con ese email"
    )
```

#### 3️⃣ Errores de Conexión (500)

```python
def get_connection():
    try:
        connection = mysql.connector.connect(...)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
```

### Tabla de Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| **ConnectionError** | No se puede conectar a MySQL | Verificar servicio MySQL, credenciales en `.env` |
| **404 Not Found** | ID de cliente inexistente | Verificar que el ID existe en la BD |
| **409 Conflict** | Email ya registrado | Usar un email diferente |
| **422 Validation Error** | Datos inválidos en el body | Revisar formato y campos requeridos |
| **500 Internal Server** | Error en el servidor | Revisar logs de Uvicorn |

---

## 🏆 Buenas Prácticas Aplicadas

### 1️⃣ Organización del Código

✅ **Separación por responsabilidades:**
- Routers → Endpoints
- Schemas → Validaciones
- Database → Acceso a datos

### 2️⃣ Nomenclatura

✅ **Convenciones Python (PEP 8):**
- `snake_case` para funciones y variables
- `PascalCase` para clases
- Nombres descriptivos

```python
# ✅ Correcto
def get_cliente_by_id(cliente_id: int):
    ...

# ❌ Incorrecto
def getClient(id):
    ...
```

### 3️⃣ Type Hints

✅ **Uso de anotaciones de tipo:**

```python
def create_cliente(data: dict) -> int:
    ...
```

### 4️⃣ Validación de Datos

✅ **Validaciones exhaustivas con Pydantic**
✅ **Mensajes de error descriptivos**

### 5️⃣ Seguridad

✅ **Variables de entorno** para credenciales
✅ **Prepared statements** (protección contra SQL injection)
✅ **Validación de email único**

```python
# ✅ Prepared statement
cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))

# ❌ Concatenación (vulnerable a SQL injection)
cursor.execute(f"SELECT * FROM clientes WHERE id = {cliente_id}")
```

### 6️⃣ Documentación

✅ **Comentarios explicativos**
✅ **Docstrings** (cuando es necesario)
✅ **Documentación automática** (Swagger/OpenAPI)

### 7️⃣ Manejo de Recursos

✅ **Cerrar conexiones:**

```python
cursor.close()
conn.close()
```

### 8️⃣ Códigos HTTP Apropiados

✅ **200** para GET/PUT exitosos
✅ **201** para POST exitosos
✅ **204** para DELETE exitosos
✅ **404** para recursos no encontrados
✅ **409** para conflictos

---

## 🎯 Ejercicios Propuestos

### Nivel Básico

1. **Agregar un nuevo campo:**
   - Añadir campo `fecha_nacimiento` a la tabla y modelo
   - Implementar validación (mayor de 18 años)

2. **Endpoint de búsqueda:**
   - Crear `GET /clientes/buscar?email=...`
   - Buscar cliente por email

3. **Paginación:**
   - Modificar `GET /clientes` para aceptar parámetros `limit` y `offset`
   - Implementar paginación en la consulta SQL

### Nivel Intermedio

4. **Endpoint de estadísticas:**
   - Crear `GET /clientes/estadisticas`
   - Retornar: total de clientes, clientes por dominio de email, etc.

5. **Soft Delete:**
   - Agregar campo `activo` (boolean)
   - Modificar DELETE para marcar como inactivo en vez de eliminar
   - Filtrar clientes inactivos en GET

6. **Logging:**
   - Implementar logging con el módulo `logging`
   - Registrar todas las operaciones CRUD

### Nivel Avanzado

7. **Autenticación:**
   - Agregar JWT authentication
   - Proteger endpoints (excepto GET)

8. **Testing:**
   - Escribir tests unitarios con `pytest`
   - Tests de integración para los endpoints

9. **Segunda entidad:**
   - Crear entidad `Pedidos`
   - Relación: Un cliente tiene muchos pedidos
   - Implementar CRUD completo

10. **Migraciones:**
    - Usar `Alembic` para gestionar cambios en la BD
    - Crear script de migración para agregar nuevo campo

---

## �️ Herramientas de Gestión

### Script CLI de Gestión de Usuarios

El proyecto incluye **`manage_users.py`**, una herramienta completa de línea de comandos para administrar usuarios y sus contraseñas desde la terminal.

**Ubicación:** `scripts/manage_users.py`

#### Comandos Disponibles

```bash
# Listar usuarios con estado de seguridad
python scripts/manage_users.py list

# Cambiar contraseña (interactivo)
python scripts/manage_users.py change-password usuario@example.com

# Cambiar contraseña (directo)
python scripts/manage_users.py change-password usuario@example.com --password Nueva123!

# Crear usuario nuevo
python scripts/manage_users.py create-user nuevo@example.com nuevouser --rol user

# Forzar cambio de contraseña en próximo login
python scripts/manage_users.py force-change usuario@example.com

# Activar/Desactivar usuario
python scripts/manage_users.py activate usuario@example.com
python scripts/manage_users.py deactivate usuario@example.com

# Ver ayuda completa
python scripts/manage_users.py --help
```

#### Características

- ✅ **Validación de contraseñas** (mínimo 8 caracteres, mayúscula, minúscula, número)
- ✅ **Estados visuales** con colores y emojis en terminal
- ✅ **Integración completa** con políticas de contraseñas (expiración 90 días)
- ✅ **Modo interactivo** seguro (contraseñas no visibles)
- ✅ **Confirmaciones** antes de ejecutar cambios
- ✅ **Auditoría** de cambios de contraseñas

#### Documentación Completa

📖 **Guía detallada:** [docs/GESTION_USUARIOS_CLI.md](docs/GESTION_USUARIOS_CLI.md)

---

## �📚 Recursos Adicionales

### Documentación Oficial

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

### Tutoriales y Guías

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Real Python - FastAPI](https://realpython.com/fastapi-python-web-apis/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [REST API Design](https://restfulapi.net/)

### Herramientas Recomendadas

- **Postman**: Testing de APIs
- **DBeaver**: Cliente de bases de datos
- **VS Code Extensions**:
  - Python
  - Pylance
  - Thunder Client
  - MySQL

### Videos Educativos

- [Curso FastAPI (YouTube)](https://www.youtube.com/results?search_query=fastapi+tutorial+español)
- [REST API Concepts](https://www.youtube.com/results?search_query=rest+api+concepts)

---

## 🤝 Contribuciones

Este proyecto es educativo. Se anima a los estudiantes a:

- Reportar bugs
- Proponer mejoras
- Hacer fork y experimentar
- Compartir aprendizajes

---

## 📝 Licencia

Este proyecto es de uso educativo y libre distribución.

---

## ✉️ Contacto

**Autor:** Juan Carlos Sulbarán González  
**Propósito:** Material educativo para DAW/DAM  
**Fecha:** 2025

---

## 🙏 Agradecimientos

A todos los estudiantes que utilicen este proyecto como recurso de aprendizaje. ¡Mucho éxito en su formación como desarrolladores!

---

**¡Happy Coding! 🚀**
