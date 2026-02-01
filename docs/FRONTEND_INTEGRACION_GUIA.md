# 📱 Guía de Integración para Desarrolladores Frontend

## 🎯 Resumen Ejecutivo

Esta guía contiene **toda la información técnica** que el equipo de Frontend necesita para integrar la autenticación JWT y consumir los endpoints de la API.

**Backend URL:** `http://localhost:8000`

---

## 📋 Tabla de Contenidos

1. [Endpoints Disponibles](#endpoints-disponibles)
2. [Autenticación JWT](#autenticación-jwt)
3. [Almacenamiento del Token](#almacenamiento-del-token)
4. [Ejemplos de Implementación](#ejemplos-de-implementación)
5. [Variables de Entorno](#variables-de-entorno)
6. [Credenciales de Prueba](#credenciales-de-prueba)
7. [Manejo de Errores](#manejo-de-errores)
8. [Checklist de Desarrollo](#checklist-de-desarrollo)

---

## 🔌 Endpoints Disponibles

### **1. POST /auth/login** - Iniciar Sesión

Obtiene el JWT Token para acceder a endpoints protegidos.

**URL:** `POST http://localhost:8000/auth/login`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body (form-data):**
```
username=admin
password=admin123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcwMDAwMDAwMH0.abc123...",
  "token_type": "bearer",
  "username": "admin",
  "rol": "admin"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Credenciales inválidas"
}
```

**Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### **2. POST /auth/cambiar-password** - Cambiar Contraseña

Permite al usuario autenticado cambiar su propia contraseña.

**URL:** `POST http://localhost:8000/auth/cambiar-password`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "password_actual": "admin123",
  "password_nueva": "nuevoPassword2024",
  "password_confirmacion": "nuevoPassword2024"
}
```

**Response (200 OK):**
```json
{
  "mensaje": "Contraseña actualizada exitosamente",
  "username": "admin"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Las nuevas contraseñas no coinciden"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Contraseña actual incorrecta"
}
```

---

### **3. GET /clientes/** - Listar Todos los Clientes

Obtiene lista de todos los clientes registrados.

**URL:** `GET http://localhost:8000/clientes/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
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
  {
    "id": 2,
    "nombre": "María",
    "apellido": "García",
    "email": "maria.garcia@example.com",
    "telefono": "555-0102",
    "direccion": "Avenida 456, Ciudad"
  }
]
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Token inválido o expirado"
}
```

---

### **4. GET /clientes/{id}** - Obtener Cliente Específico

Obtiene los datos de un cliente específico por ID.

**URL:** `GET http://localhost:8000/clientes/1`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
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

**Response (404 Not Found):**
```json
{
  "detail": "Cliente no encontrado"
}
```

---

### **5. POST /clientes/** - Crear Nuevo Cliente

Crea un nuevo cliente en la BD. **Requiere rol admin.**

**URL:** `POST http://localhost:8000/clientes/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "nombre": "Carlos",
  "apellido": "Rodríguez",
  "email": "carlos.rodriguez@example.com",
  "telefono": "555-0103",
  "direccion": "Plaza 789, Ciudad"
}
```

**Response (200 OK):**
```json
{
  "id": 6,
  "nombre": "Carlos",
  "apellido": "Rodríguez",
  "email": "carlos.rodriguez@example.com",
  "telefono": "555-0103",
  "direccion": "Plaza 789, Ciudad"
}
```

**Response (403 Forbidden - si es lector):**
```json
{
  "detail": "Permisos insuficientes"
}
```

**Response (422 Validation Error - email duplicado):**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Email already registered"
    }
  ]
}
```

---

### **6. PUT /clientes/{id}** - Actualizar Cliente

Actualiza los datos de un cliente existente. **Requiere rol admin.**

**URL:** `PUT http://localhost:8000/clientes/1`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez López",
  "email": "juan.perez.lopez@example.com",
  "telefono": "555-0100",
  "direccion": "Calle 123 Apt 2, Ciudad"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "nombre": "Juan",
  "apellido": "Pérez López",
  "email": "juan.perez.lopez@example.com",
  "telefono": "555-0100",
  "direccion": "Calle 123 Apt 2, Ciudad"
}
```

---

### **7. DELETE /clientes/{id}** - Eliminar Cliente

Elimina un cliente de la BD. **Requiere rol admin.**

**URL:** `DELETE http://localhost:8000/clientes/1`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "mensaje": "Cliente eliminado correctamente",
  "id": 1
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Cliente no encontrado"
}
```

---

## 🔐 Autenticación JWT

### Flujo de Autenticación

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  1. Usuario ingresa credenciales (username + password)     │
│                         ↓                                   │
│  2. Frontend hace POST /auth/login                         │
│                         ↓                                   │
│  3. Backend verifica credenciales                          │
│     - Busca usuario en BD                                  │
│     - Compara contraseña con hash bcrypt                   │
│                         ↓                                   │
│  4. Backend genera JWT Token                               │
│     - Incluye: username, role, expiración                  │
│     - Firma: HS256 (HMAC SHA-256)                         │
│                         ↓                                   │
│  5. Frontend recibe token y lo almacena                    │
│     (localStorage, sessionStorage o Cookie)               │
│                         ↓                                   │
│  6. Frontend incluye token en header                       │
│     Authorization: Bearer {token}                         │
│                         ↓                                   │
│  7. Backend verifica firma del token                       │
│     - Token válido → Procesa request                       │
│     - Token expirado → Responde 401                        │
│     - Token inválido → Responde 401                        │
│                         ↓                                   │
│  8. Si 401 → Frontend pide re-login                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Configuración de Seguridad

```
Algorithm:        HS256 (HMAC-SHA256)
Expiración:       60 minutos
Secret Key:       super-secret-key-cambiar-en-produccion
Hash Contraseña:  bcrypt 12 iteraciones
```

### Estructura del JWT Token

Un JWT contiene 3 partes separadas por puntos:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcwMDAwMDAwMH0.
abc123...

┌─────────────────────┐
│      HEADER         │ Base64({"alg":"HS256","typ":"JWT"})
├─────────────────────┤
│      PAYLOAD        │ Base64({"sub":"admin","role":"admin","exp":1700000000})
├─────────────────────┤
│      SIGNATURE      │ HMAC-SHA256(header.payload, SECRET_KEY)
└─────────────────────┘
```

---

## 💾 Almacenamiento del Token

### Opción 1: localStorage (Recomendado para SPAs)

**Ventajas:**
- ✅ Persiste después de cerrar el navegador
- ✅ Accesible desde cualquier pestaña
- ❌ Vulnerable a XSS (inyección de código)

**Implementación:**
```javascript
// Guardar token después del login
const response = await fetch('http://localhost:8000/auth/login', {...});
const data = await response.json();
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('token_type', data.token_type);
localStorage.setItem('username', data.username);
localStorage.setItem('rol', data.rol);

// Obtener token antes de cada request
const token = localStorage.getItem('access_token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

// Limpiar token al logout
localStorage.removeItem('access_token');
localStorage.removeItem('token_type');
localStorage.removeItem('username');
localStorage.removeItem('rol');
```

### Opción 2: sessionStorage (Más seguro)

**Ventajas:**
- ✅ Se borra automáticamente al cerrar el navegador
- ✅ No se comparte entre pestañas
- ✅ Menos vulnerable a XSS prolongado

**Implementación:**
```javascript
// Guardar
sessionStorage.setItem('access_token', data.access_token);

// Obtener
const token = sessionStorage.getItem('access_token');

// Limpiar (automático al cerrar navegador)
```

### Opción 3: Cookie Segura (Más seguro, automático)

**Ventajas:**
- ✅ Automáticamente incluido en todos los requests
- ✅ Puede tener flag HttpOnly (no accesible desde JS)
- ✅ Puede tener flag Secure (solo HTTPS)

**Nota:** Requiere cambios en backend para soportar cookies.

**Recomendación:** Usa **localStorage** para desarrollo y **Cookie segura** para producción.

---

## 📡 Ejemplos de Implementación

### Ejemplo 1: React (Fetch API)

```javascript
// context/AuthContext.js
import React, { createContext, useState } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `username=${username}&password=${password}`
      });

      if (!response.ok) {
        throw new Error('Credenciales inválidas');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('username', data.username);
      localStorage.setItem('rol', data.rol);
      setToken(data.access_token);
      setUser({ username: data.username, rol: data.rol });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    localStorage.removeItem('rol');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

```javascript
// hooks/useAPI.js
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export function useAPI() {
  const { token } = useContext(AuthContext);

  const request = async (url, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`http://localhost:8000${url}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Token expirado
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      return;
    }

    return response.json();
  };

  return { request };
}
```

```javascript
// components/ClientesList.js
import { useEffect, useState } from 'react';
import { useAPI } from '../hooks/useAPI';

export function ClientesList() {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const { request } = useAPI();

  useEffect(() => {
    const getClientes = async () => {
      const data = await request('/clientes/');
      setClientes(data);
      setLoading(false);
    };

    getClientes();
  }, []);

  if (loading) return <div>Cargando...</div>;

  return (
    <table>
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Email</th>
          <th>Teléfono</th>
        </tr>
      </thead>
      <tbody>
        {clientes.map(cliente => (
          <tr key={cliente.id}>
            <td>{cliente.nombre} {cliente.apellido}</td>
            <td>{cliente.email}</td>
            <td>{cliente.telefono}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### Ejemplo 2: Vue.js 3 (Composables)

```javascript
// composables/useAuth.js
import { ref } from 'vue';

export const useAuth = () => {
  const token = ref(localStorage.getItem('access_token'));
  const user = ref(null);

  const login = async (username, password) => {
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `username=${username}&password=${password}`
    });

    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('username', data.username);
    localStorage.setItem('rol', data.rol);
    token.value = data.access_token;
    user.value = { username: data.username, rol: data.rol };
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    localStorage.removeItem('rol');
    token.value = null;
    user.value = null;
  };

  const getAuthHeader = () => ({
    'Authorization': `Bearer ${token.value}`,
    'Content-Type': 'application/json'
  });

  return { token, user, login, logout, getAuthHeader };
};
```

```javascript
// composables/useAPI.js
import { useAuth } from './useAuth';

export const useAPI = () => {
  const { getAuthHeader, token } = useAuth();

  const request = async (url, options = {}) => {
    const response = await fetch(`http://localhost:8000${url}`, {
      ...options,
      headers: getAuthHeader()
    });

    if (response.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }

    return response.json();
  };

  return { request };
};
```

### Ejemplo 3: Angular

```typescript
// services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = 'http://localhost:8000/auth';
  public token$ = new BehaviorSubject<string | null>(
    localStorage.getItem('access_token')
  );

  constructor(private http: HttpClient) {}

  login(username: string, password: string) {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    return this.http.post<any>(`${this.apiUrl}/login`, body)
      .pipe(
        tap(response => {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('username', response.username);
          localStorage.setItem('rol', response.rol);
          this.token$.next(response.access_token);
        })
      );
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    localStorage.removeItem('rol');
    this.token$.next(null);
  }

  getToken() {
    return this.token$.value;
  }
}
```

```typescript
// interceptors/auth.interceptor.ts
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = this.authService.getToken();

    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          this.authService.logout();
          this.router.navigate(['/login']);
        }
        return throwError(() => error);
      })
    );
  }
}
```

---

## � Control de Permisos por Rol en el Frontend

### Uso del Campo `rol` en la UI

Ahora que el endpoint `/auth/login` devuelve el campo `rol`, puedes usar esta información para:

#### 1. Mostrar/Ocultar Botones según Permisos

```javascript
// Después del login
const rol = localStorage.getItem('rol');
const isAdmin = rol === 'admin';

// Habilitar/deshabilitar botones
document.getElementById('btn-crear-cliente').style.display = isAdmin ? 'block' : 'none';
document.getElementById('btn-editar-cliente').disabled = !isAdmin;
document.getElementById('btn-eliminar-cliente').disabled = !isAdmin;
```

#### 2. Mostrar Rol en la Interfaz

```javascript
// Mostrar información del usuario en la navbar
const username = localStorage.getItem('username');
const rol = localStorage.getItem('rol');

document.getElementById('user-info').innerHTML = `
  <span>${username}</span>
  <span class="badge ${rol === 'admin' ? 'badge-danger' : 'badge-info'}">
    ${rol.toUpperCase()}
  </span>
`;
```

#### 3. Validación antes de Acciones

```javascript
async function eliminarCliente(id) {
  const rol = localStorage.getItem('rol');
  
  if (rol !== 'admin') {
    alert('Solo los administradores pueden eliminar clientes');
    return;
  }
  
  // Proceder con eliminación
  const response = await fetch(`http://localhost:8000/clientes/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });
  
  if (response.status === 403) {
    alert('No tienes permisos para esta acción');
  }
}
```

#### 4. React - Componente Condicional

```jsx
function ClientesActions({ clienteId }) {
  const rol = localStorage.getItem('rol');
  const isAdmin = rol === 'admin';
  
  return (
    <div>
      <button onClick={() => verCliente(clienteId)}>Ver</button>
      
      {isAdmin && (
        <>
          <button onClick={() => editarCliente(clienteId)}>Editar</button>
          <button onClick={() => eliminarCliente(clienteId)}>Eliminar</button>
        </>
      )}
    </div>
  );
}
```

#### 5. Vue.js - Directivas Condicionales

```vue
<template>
  <div>
    <h2>Bienvenido, {{ username }} <span class="badge">{{ rol }}</span></h2>
    
    <button @click="verClientes">Ver Clientes</button>
    
    <!-- Solo visible para administradores -->
    <button v-if="isAdmin" @click="crearCliente">Crear Cliente</button>
    <button v-if="isAdmin" @click="editarCliente">Editar</button>
    <button v-if="isAdmin" @click="eliminarCliente">Eliminar</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: localStorage.getItem('username'),
      rol: localStorage.getItem('rol')
    };
  },
  computed: {
    isAdmin() {
      return this.rol === 'admin';
    }
  }
};
</script>
```

#### 6. Tabla de Permisos por Rol

| Acción | Admin | Lector |
|--------|-------|--------|
| Ver clientes (GET) | ✅ | ✅ |
| Ver detalle (GET) | ✅ | ✅ |
| Crear cliente (POST) | ✅ | ❌ 403 |
| Editar cliente (PUT) | ✅ | ❌ 403 |
| Eliminar cliente (DELETE) | ✅ | ❌ 403 |
| Cambiar password (POST) | ✅ | ✅ |

**Nota:** El backend siempre valida los permisos, el frontend solo mejora la UX ocultando opciones no permitidas.

---

## �🛠️ Variables de Entorno

### Para Desarrollo (Frontend)

```bash
# .env.local (React/Vue/Angular)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
REACT_APP_TOKEN_STORAGE=localStorage
REACT_APP_TOKEN_EXPIRY_MINUTES=60

# En código
const API_URL = process.env.REACT_APP_API_URL;
```

### Para Producción

```bash
# .env.production
REACT_APP_API_URL=https://api.tudominio.com
REACT_APP_API_TIMEOUT=30000
REACT_APP_TOKEN_STORAGE=sessionStorage
REACT_APP_TOKEN_EXPIRY_MINUTES=60
```

---

## 👤 Credenciales de Prueba

### Usuario 1: Admin (Acceso Total)

```
Username: admin
Password: admin123
Rol:     admin

Permisos:
✅ Ver clientes        (GET /clientes/)
✅ Ver cliente         (GET /clientes/{id})
✅ Crear cliente       (POST /clientes/)
✅ Editar cliente      (PUT /clientes/{id})
✅ Eliminar cliente    (DELETE /clientes/{id})
✅ Cambiar contraseña  (POST /auth/cambiar-password)
```

### Usuario 2: Lector (Solo Lectura)

```
Username: lector
Password: lector123
Rol:     lector

Permisos:
✅ Ver clientes        (GET /clientes/)
✅ Ver cliente         (GET /clientes/{id})
❌ Crear cliente       (POST /clientes/)      → 403 Forbidden
❌ Editar cliente      (PUT /clientes/{id})   → 403 Forbidden
❌ Eliminar cliente    (DELETE /clientes/{id}) → 403 Forbidden
✅ Cambiar contraseña  (POST /auth/cambiar-password)
```

### Crear Más Usuarios

```bash
python3 scripts/crear_usuario.py
```

Sigue las instrucciones para crear usuarios adicionales.

---

## ⚠️ Manejo de Errores

### Error 401: Unauthorized

**Causas:**
- Token expirado (más de 60 minutos)
- Token inválido o corrupto
- Usuario desactivado
- No se incluyó el header Authorization

**Manejo:**
```javascript
if (response.status === 401) {
  // Limpiar token
  localStorage.removeItem('access_token');
  
  // Redirigir a login
  window.location.href = '/login';
  
  // Mostrar mensaje
  alert('Sesión expirada. Por favor inicia sesión nuevamente.');
}
```

### Error 403: Forbidden

**Causas:**
- Usuario sin permisos (rol lector intentando crear/editar/eliminar)
- Token válido pero sin permisos para esta acción

**Manejo:**
```javascript
if (response.status === 403) {
  alert('No tienes permisos para realizar esta acción');
  
  // Deshabilitar botones según rol
  const isAdmin = user.role === 'admin';
  document.getElementById('btn-crear').disabled = !isAdmin;
  document.getElementById('btn-editar').disabled = !isAdmin;
  document.getElementById('btn-eliminar').disabled = !isAdmin;
}
```

### Error 422: Validation Error

**Causas:**
- Datos inválidos en el request
- Email duplicado
- Campos requeridos faltantes
- Formato incorrecto

**Ejemplo:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

**Manejo:**
```javascript
if (response.status === 422) {
  const errors = response.detail;
  errors.forEach(error => {
    const field = error.loc[1];
    const message = error.msg;
    console.error(`Campo ${field}: ${message}`);
  });
}
```

### Error 500: Internal Server Error

**Causas:**
- Error en la base de datos
- Error en el servidor
- Código no manejado

**Manejo:**
```javascript
if (response.status === 500) {
  alert('Error en el servidor. Por favor contacta al administrador.');
  console.error('Server error:', response.statusText);
}
```

---

## ✅ Checklist de Desarrollo

### Configuración Inicial
- [ ] Clonar repositorio del backend
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Configurar `.env` con valores correctos
- [ ] Crear base de datos: `mysql ... < docs/init_db.sql`
- [ ] Ejecutar backend: `uvicorn app.main:app --reload`
- [ ] Verificar Swagger: `http://localhost:8000/docs`

### Autenticación
- [ ] Implementar formulario de login
- [ ] Conectar POST /auth/login
- [ ] Guardar token en localStorage/sessionStorage
- [ ] Implementar logout (limpiar token)
- [ ] Interceptar errores 401 (token expirado)
- [ ] Redirigir a login si token inválido
- [ ] Mostrar usuario autenticado en navbar

### Endpoints de Clientes
- [ ] GET /clientes/ - Listar clientes
- [ ] GET /clientes/{id} - Ver cliente específico
- [ ] POST /clientes/ - Crear cliente (solo admin)
- [ ] PUT /clientes/{id} - Editar cliente (solo admin)
- [ ] DELETE /clientes/{id} - Eliminar cliente (solo admin)

### Validaciones
- [ ] Validar datos antes de enviar
- [ ] Mostrar errores de validación (422)
- [ ] Validar longitud de campos
- [ ] Validar formato de email
- [ ] Validar que emails sean únicos

### Seguridad
- [ ] Incluir Authorization header en todos los requests
- [ ] No almacenar contraseñas en localStorage
- [ ] Usar HTTPS en producción
- [ ] Validar CORS (Cross-Origin)
- [ ] Limpiar datos sensibles al logout

### UI/UX
- [ ] Mostrar spinner/loading mientras se carga
- [ ] Mostrar errores al usuario (toasts, alerts)
- [ ] Deshabilitar botones según permisos
- [ ] Mostrar rol del usuario
- [ ] Implementar cambio de contraseña

### Testing
- [ ] Probar login con credenciales correctas
- [ ] Probar login con credenciales incorrectas
- [ ] Probar endpoints con token válido
- [ ] Probar endpoints con token expirado
- [ ] Probar endpoints sin token (401)
- [ ] Probar acciones sin permisos (403)

---

## 🔗 URLs Útiles

**API:**
- Base: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Documentación:**
- Login: [Guía de Autenticación](./ANALISIS_AUTENTICACION.md)
- Cambiar Contraseña: [Guía Detallada](./CAMBIAR_PASSWORD_GUIA.md)
- Crear Usuarios: [Guía de Usuarios](./CREAR_USUARIOS_GUIA.md)

---

## 📞 FAQ - Preguntas Frecuentes

### P: ¿Cuánto tiempo dura el token?
**R:** 60 minutos. Después de expirar, el usuario debe hacer login nuevamente.

### P: ¿Dónde guardo el token?
**R:** localStorage (desarrollo) o Cookie segura (producción).

### P: ¿Puedo cambiar la expiración del token?
**R:** Sí, modifica `ACCESS_TOKEN_EXPIRE_MINUTES` en `.env`.

### P: ¿Cómo sé qué rol tiene el usuario?
**R:** El endpoint `/auth/login` devuelve el campo `rol` directamente en la respuesta. También puedes decodificar el JWT si lo necesitas.

### P: ¿Qué es CORS?
**R:** Mecanismo de seguridad del navegador. Backend debe permitir requests desde tu frontend.

### P: ¿Cómo agrego más usuarios?
**R:** Ejecuta `python3 scripts/crear_usuario.py`.

### P: ¿Puedo usar Axios en lugar de Fetch?
**R:** Sí, ambos funcionan igual. Solo cambia sintaxis.

### P: ¿Qué pasa si olvido incluir el Authorization header?
**R:** Recibirás 401 Unauthorized.

### P: ¿Puedo cambiar el email del usuario?
**R:** No hay endpoint para eso actualmente. Contáctame para agregar.

---

## 🚀 Próximos Pasos

1. **Clonar este repositorio**
2. **Leer esta guía completamente**
3. **Probar endpoints en Swagger UI**
4. **Implementar login en Frontend**
5. **Conectar endpoints de clientes**
6. **Probar con usuarios admin y lector**
7. **Implementar manejo de errores**
8. **Desplegar en producción**

---

## 📧 Soporte Técnico

Para preguntas o problemas:

1. Revisa la [Guía Técnica de Autenticación](./GUIA_TECNICA_AUTENTICACION.md)
2. Revisa los ejemplos en esta guía
3. Prueba en [Swagger UI](http://localhost:8000/docs)
4. Contacta al equipo de backend

---

**Última actualización:** 1 de febrero de 2026  
**Para:** Desarrolladores Frontend  
**Backend:** FastAPI + JWT + MySQL  
**Versión:** 1.0
