# 🐳 Gestión de Usuarios en Servidor Docker - Guía Completa

**Versión:** 1.0  
**Fecha:** 8 de febrero de 2026  
**Estado:** ✅ Validado en producción  

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Conexión al Servidor](#conexión-al-servidor)
3. [Comandos Esenciales](#comandos-esenciales)
4. [Casos de Uso Validados](#casos-de-uso-validados)
5. [Troubleshooting](#troubleshooting)
6. [Seguridad](#seguridad)

---

## 🎯 Introducción

Esta guía documenta cómo gestionar usuarios del sistema **Clientes API Autenticada** directamente desde el servidor de producción utilizando Docker.

### Arquitectura

```
Servidor (docker.sulbaranjc.com)
  └── Directorio: ~/apps/clientes_api_autenticada/
      └── Contenedor Docker: clientes-api-autenticado
          └── Scripts: /app/scripts/manage_users.py
```

### Requisitos

- ✅ Acceso SSH al servidor
- ✅ Contenedor Docker `clientes-api-autenticado` en ejecución
- ✅ Scripts sincronizados desde el repositorio

---

## 🔐 Conexión al Servidor

### Paso 1: Conectarse por SSH

```bash
ssh sulbaranjc@docker.sulbaranjc.com
```

### Paso 2: Navegar al directorio del proyecto

```bash
cd ~/apps/clientes_api_autenticada
```

### Paso 3: Verificar que el contenedor esté corriendo

```bash
docker ps | grep clientes-api-autenticado
```

**Salida esperada:**
```
clientes-api-autenticado   "uvicorn app.main:ap…"   Up X hours   8000/tcp
```

---

## 🛠️ Comandos Esenciales

### Formato General

```bash
docker exec clientes-api-autenticado python /app/scripts/manage_users.py [COMANDO] [ARGUMENTOS]
```

### Comandos Disponibles

| Comando | Descripción | Requiere Interacción |
|---------|-------------|---------------------|
| `list` | Lista todos los usuarios | ❌ No |
| `force-change <email>` | Fuerza cambio de contraseña | ✅ Sí |
| `change-password <email>` | Cambia contraseña | ✅ Sí |
| `create-user <email> <username>` | Crea nuevo usuario | ✅ Sí |
| `activate <email>` | Activa usuario | ✅ Sí |
| `deactivate <email>` | Desactiva usuario | ✅ Sí |

---

## ✅ Casos de Uso Validados

### 1. Listar Usuarios (No Interactivo)

**Comando:**
```bash
docker exec clientes-api-autenticado python /app/scripts/manage_users.py list
```

**Salida Validada:**
```
======================================================================
                          LISTA DE USUARIOS                           
======================================================================

Total de usuarios: 2

ID    EMAIL                          USERNAME             ROL        ACTIVO   ESTADO PASSWORD       
----------------------------------------------------------------------------------------------------
1     admin@example.com              admin                admin      Sí       🔒 Cambio forzado
2     usuario@example.com            usuario_prueba       user       Sí       ⚠️  Primer login

----------------------------------------------------------------------------------------------------

Resumen:
  Usuarios activos: 2/2
  Requieren cambio de contraseña: 2
```

**Cuándo usar:**
- Auditoría diaria de usuarios
- Verificar estado de seguridad
- Identificar contraseñas próximas a expirar

---

### 2. Forzar Cambio de Contraseña (Interactivo)

**Comando:**
```bash
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py force-change admin@example.com
```

**Flujo Interactivo:**
```
======================================================================
           FORZAR CAMBIO DE CONTRASEÑA - admin@example.com            
======================================================================

ℹ️  Usuario: admin
ℹ️  Rol: admin

¿Forzar cambio de contraseña? (s/N): s

✅ Usuario marcado para cambio obligatorio de contraseña
ℹ️  En el próximo login deberá cambiar su contraseña
```

**Cuándo usar:**
- Cuenta comprometida
- Reset de seguridad
- Cumplimiento de políticas
- Auditorías de seguridad

**Efecto:**
- Se activa `force_password_change = TRUE`
- En el próximo login, el API responderá con `requires_password_change: true`
- El usuario no podrá acceder hasta cambiar su contraseña

---

### 3. Cambiar Contraseña (Interactivo)

**Comando:**
```bash
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py change-password admin@example.com
```

**Flujo:**
```
======================================================================
              CAMBIAR CONTRASEÑA - admin@example.com                    
======================================================================

ℹ️  Usuario encontrado: admin (admin)

Ingrese la nueva contraseña:
Nueva contraseña: ********
Confirmar contraseña: ********

✅ Contraseña válida

¿Confirmar cambio de contraseña para 'admin@example.com'? (s/N): s

✅ Contraseña actualizada exitosamente
ℹ️  Fecha de cambio: 2026-02-08 09:35:12
ℹ️  Expira en: 90 días
```

**Cuándo usar:**
- Usuario olvidó su contraseña
- Reset administrativo
- Cumplir política de rotación

---

### 4. Cambiar Contraseña (No Interactivo - Automatizado)

**Comando:**
```bash
docker exec clientes-api-autenticado python /app/scripts/manage_users.py change-password admin@example.com --password NuevaPass123!
```

**Cuándo usar:**
- Scripts automatizados
- Deployments
- CI/CD pipelines

⚠️ **ADVERTENCIA:** Evitar contraseñas en logs. Usar con precaución.

---

### 5. Crear Nuevo Usuario (Interactivo)

**Comando:**
```bash
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py create-user nuevo@empresa.com nuevouser --rol admin
```

**Flujo:**
```
======================================================================
              CREAR NUEVO USUARIO - nuevo@empresa.com                    
======================================================================

ℹ️  Contraseña temporal generada: Temp202602!
⚠️  El usuario deberá cambiarla en el primer login

Datos del nuevo usuario:
  Email:    nuevo@empresa.com
  Username: nuevouser
  Rol:      admin
  Password: ***
  Estado:   Activo
  First Login: True (debe cambiar contraseña)

¿Confirmar creación? (s/N): s

✅ Usuario creado exitosamente (ID: 3)
ℹ️  Contraseña temporal: Temp202602!
⚠️  Guarde esta contraseña de forma segura
```

**Cuándo usar:**
- Onboarding de nuevos empleados
- Crear usuarios de emergencia
- Configuración inicial

---

### 6. Activar/Desactivar Usuario

**Desactivar:**
```bash
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py deactivate usuario@example.com
```

**Activar:**
```bash
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py activate usuario@example.com
```

**Cuándo usar:**
- Offboarding de empleados
- Suspensión temporal
- Reactivación de cuentas

---

## 🚨 Escenarios de Producción

### Escenario 1: Cuenta Comprometida - Acción Inmediata

```bash
# 1. Conectar al servidor
ssh sulbaranjc@docker.sulbaranjc.com

# 2. Forzar cambio de contraseña
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py force-change comprometido@empresa.com

# 3. Verificar el cambio
docker exec clientes-api-autenticado python /app/scripts/manage_users.py list | grep comprometido
```

---

### Escenario 2: Usuario Olvidó su Contraseña

```bash
# 1. Conectar al servidor
ssh sulbaranjc@docker.sulbaranjc.com

# 2. Cambiar contraseña (modo interactivo seguro)
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py change-password usuario@empresa.com

# 3. Comunicar nueva contraseña por canal seguro (no por email)
```

---

### Escenario 3: Auditoría de Seguridad Semanal

```bash
# 1. Conectar al servidor
ssh sulbaranjc@docker.sulbaranjc.com

# 2. Generar reporte de usuarios
docker exec clientes-api-autenticado python /app/scripts/manage_users.py list > ~/security_audit_$(date +%Y%m%d).txt

# 3. Revisar usuarios que requieren atención
cat ~/security_audit_$(date +%Y%m%d).txt

# 4. Descargar reporte a local (desde tu máquina local)
scp sulbaranjc@docker.sulbaranjc.com:~/security_audit_*.txt ./
```

---

### Escenario 4: Crear Usuario de Emergencia

```bash
# 1. Conectar al servidor
ssh sulbaranjc@docker.sulbaranjc.com

# 2. Crear admin temporal
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py create-user emergency@admin.com emergadmin --rol admin --password EmergAdmin2026!

# 3. Verificar creación
docker exec clientes-api-autenticado python /app/scripts/manage_users.py list | grep emergency
```

---

## 📊 Estados de Contraseña

| Estado | Emoji | Descripción | Acción Frontend |
|--------|-------|-------------|-----------------|
| ✅ OK | - | Contraseña válida y activa | Permitir acceso normal |
| ⏰ POR_EXPIRAR | - | Expira en ≤7 días | Mostrar advertencia |
| ❌ EXPIRADA | - | Más de 90 días | Forzar cambio |
| ⚠️ PRIMER_LOGIN | - | Primera sesión | Forzar cambio |
| 🔒 CAMBIO_FORZADO | - | Administrador forzó cambio | Forzar cambio |
| ➖ SIN_EXPIRACION | - | Sin política aplicada | Permitir (legacy) |

---

## 🐛 Troubleshooting

### Problema 1: Script no encontrado

**Error:**
```
python: can't open file '/app/scripts/manage_users.py': [Errno 2] No such file or directory
```

**Solución:**
```bash
# 1. Ir al directorio del proyecto
cd ~/apps/clientes_api_autenticada

# 2. Hacer pull del repositorio
git stash
git pull

# 3. Reconstruir la imagen
docker compose down
docker compose up -d --build

# 4. Verificar que esté el archivo
docker exec clientes-api-autenticado ls -la /app/scripts/ | grep manage
```

---

### Problema 2: Error EOFError en modo interactivo

**Error:**
```
EOFError: EOF when reading a line
```

**Causa:** Falta la flag `-it` para modo interactivo

**Solución:**
```bash
# ❌ Incorrecto
docker exec clientes-api-autenticado python /app/scripts/manage_users.py force-change user@test.com

# ✅ Correcto
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py force-change user@test.com
```

---

### Problema 3: Contenedor no está corriendo

**Verificar:**
```bash
docker ps | grep clientes-api-autenticado
```

**Si no aparece:**
```bash
cd ~/apps/clientes_api_autenticada
docker compose up -d
```

---

### Problema 4: Error de conexión a base de datos

**Verificar variables de entorno:**
```bash
docker exec clientes-api-autenticado env | grep DB
```

**Verificar que el contenedor de BD esté corriendo:**
```bash
docker ps | grep clientes-api-autenticado-db
```

---

### Problema 5: Python no encuentra módulos

**Solución:**
```bash
# Reconstruir contenedor asegurando dependencias
cd ~/apps/clientes_api_autenticada
docker compose down
docker compose up -d --build --force-recreate
```

---

## 🔒 Seguridad

### Mejores Prácticas

#### 1. Gestión de Contraseñas Temporales

✅ **Correcto:**
```bash
# Generar contraseña temporal
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py create-user nuevo@empresa.com nuevouser

# Copiar contraseña mostrada
# Enviar por canal seguro (Signal, WhatsApp, etc.)
# NO por email sin cifrar
```

❌ **Incorrecto:**
```bash
# Evitar contraseñas en historial de bash
docker exec clientes-api-autenticado python /app/scripts/manage_users.py change-password user@test.com --password Admin123!
```

---

#### 2. Auditoría y Logs

**Crear log de acciones:**
```bash
# Redirigir salida a archivo de log
docker exec clientes-api-autenticado python /app/scripts/manage_users.py list >> ~/user_management_log_$(date +%Y%m%d_%H%M%S).log
```

**Limpiar historial sensible:**
```bash
# Limpiar historial de bash después de operaciones sensibles
history -c
```

---

#### 3. Validación de Fortaleza de Contraseña

El script valida automáticamente:
- ✅ Mínimo 8 caracteres
- ✅ Al menos 1 mayúscula
- ✅ Al menos 1 minúscula
- ✅ Al menos 1 número

**Ejemplos válidos:**
- `Password123`
- `Admin$ecure1`
- `MiClave2026!`

**Ejemplos inválidos:**
- `password` (sin mayúscula ni número)
- `ADMIN123` (sin minúscula)
- `Password` (sin número)
- `Pass1` (muy corta)

---

#### 4. Rotación de Contraseñas

**Política implementada:**
- Expiración: **90 días**
- Advertencia: **7 días** antes
- First login: **Cambio obligatorio**

**Implementar rotación periódica:**
```bash
# Listar usuarios próximos a expirar
docker exec clientes-api-autenticado python /app/scripts/manage_users.py list | grep "POR_EXPIRAR"

# Forzar cambio si es necesario
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py force-change usuario@empresa.com
```

---

## 📚 Comandos de Referencia Rápida

```bash
# ==========================================
# LISTAR USUARIOS
# ==========================================
docker exec clientes-api-autenticado python /app/scripts/manage_users.py list

# ==========================================
# FORZAR CAMBIO DE CONTRASEÑA
# ==========================================
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py force-change admin@example.com

# ==========================================
# CAMBIAR CONTRASEÑA (INTERACTIVO)
# ==========================================
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py change-password admin@example.com

# ==========================================
# CAMBIAR CONTRASEÑA (NO INTERACTIVO)
# ==========================================
docker exec clientes-api-autenticado python /app/scripts/manage_users.py change-password admin@example.com --password NuevaPass123!

# ==========================================
# CREAR USUARIO
# ==========================================
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py create-user nuevo@empresa.com nuevouser --rol admin

# ==========================================
# DESACTIVAR USUARIO
# ==========================================
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py deactivate usuario@empresa.com

# ==========================================
# ACTIVAR USUARIO
# ==========================================
docker exec -it clientes-api-autenticado python /app/scripts/manage_users.py activate usuario@empresa.com

# ==========================================
# VER AYUDA
# ==========================================
docker exec clientes-api-autenticado python /app/scripts/manage_users.py --help
```

---

## 📝 Checklist de Operaciones

### Onboarding de Nuevo Empleado

- [ ] Crear usuario con rol apropiado
- [ ] Generar contraseña temporal segura
- [ ] Enviar credenciales por canal seguro
- [ ] Verificar que `first_login = true`
- [ ] Confirmar que el usuario cambió la contraseña

### Offboarding de Empleado

- [ ] Desactivar usuario inmediatamente
- [ ] Auditar sesiones activas
- [ ] Revisar logs de actividad reciente
- [ ] Documentar fecha de desactivación
- [ ] Backup de datos si es necesario

### Rotación Periódica de Contraseñas

- [ ] Listar usuarios con contraseñas próximas a expirar
- [ ] Notificar a usuarios afectados
- [ ] Forzar cambio en cuentas críticas
- [ ] Verificar compliance
- [ ] Documentar acciones

---

## 🔗 Referencias

- [API Contract de Autenticación](./API_CONTRACT_AUTH.md)
- [Guía de Políticas de Contraseñas](./GUIA_POLITICAS_CONTRASENAS.md)
- [Gestión de Usuarios CLI](./GESTION_USUARIOS_CLI.md)
- [Quick Reference](./QUICK_REFERENCE.md)

---

## 📞 Soporte

**En caso de problemas:**
1. Revisar esta documentación
2. Consultar logs: `docker logs clientes-api-autenticado`
3. Verificar conexión a BD: `docker logs clientes-api-autenticado-db`
4. Contactar al equipo de backend

---

**Última actualización:** 8 de febrero de 2026  
**Validado en:** Servidor de producción (docker.sulbaranjc.com)  
**Estado:** ✅ Operativo y probado
