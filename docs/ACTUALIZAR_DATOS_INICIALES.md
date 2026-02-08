# Guía: Actualizar Datos Iniciales de Base de Datos

## 📋 Descripción General

Este documento explica cómo modificar y actualizar los datos iniciales (clientes, usuarios, etc.) que se cargan automáticamente cuando se inicializa la base de datos en el contenedor Docker.

---

## 🎯 Concepto Clave: Init Scripts en MariaDB/MySQL

El contenedor de MariaDB ejecuta **automáticamente** todos los scripts SQL ubicados en `/docker-entrypoint-initdb.d/` cuando:

1. ✅ El contenedor se inicia **por primera vez**
2. ✅ El volumen de datos (`db_data`) está **vacío** o **no existe**

**Configuración en docker-compose.yml:**
```yaml
db:
  image: mariadb:10.6
  volumes:
    - db_data:/var/lib/mysql
    - ./docs/init_db.sql:/docker-entrypoint-initdb.d/01_init.sql:ro
```

---

## 📁 Archivos de Inicialización

### Ubicaciones de init_db.sql

El proyecto mantiene **dos copias** del archivo de inicialización:

| Archivo | Propósito | Uso |
|---------|-----------|-----|
| `docs/init_db.sql` | **PRODUCCIÓN** | Montado en el contenedor Docker (docker-compose.yml) |
| `scripts/init_db.sql` | Documentación/Referencia | Copia para desarrollo local y consulta |

⚠️ **IMPORTANTE:** Cualquier cambio debe aplicarse en **AMBOS** archivos para mantener consistencia.

---

## 🔧 Procedimiento: Modificar Datos Iniciales

### Paso 1: Modificar los Archivos SQL

1. **Editar ambos archivos:**
   - `docs/init_db.sql`
   - `scripts/init_db.sql`

2. **Ejemplo: Agregar más clientes**

```sql
-- Clientes de Prueba (30 registros)
INSERT INTO clientes (nombre, apellido, email, telefono, direccion) VALUES
    -- Colombia
    ('Juan', 'Pérez', 'juan.perez@email.com', '+57 310 1234567', 'Calle 123 #45-67, Bogotá'),
    ('María', 'González', 'maria.gonzalez@email.com', '+57 320 7654321', 'Carrera 45 #12-34, Medellín'),
    
    -- México
    ('Sofía', 'García', 'sofia.garcia@email.com', '+52 55 1234 5678', 'Avenida Insurgentes 1502, CDMX'),
    
    -- ... más registros ...
    
    -- Uruguay
    ('Emilia', 'Vega', 'emilia.vega@email.com', '+598 2 345 6789', 'Avenida 18 de Julio 1234, Montevideo')
ON DUPLICATE KEY UPDATE email = email;
```

### Paso 2: Commit y Push (Desarrollo Local)

```bash
# Agregar cambios al staging
git add docs/init_db.sql scripts/init_db.sql

# Commit con mensaje descriptivo
git commit -m "feat: agregar 30 clientes de prueba de países hispanohablantes"

# Push a la rama actual
git push

# Ejecutar deploy (si tienes script personalizado)
deployIT
```

---

## 🚀 Aplicar Cambios en Producción

### Opción 1: Destruir y Recrear (RECOMENDADO para desarrollo/testing)

Esta opción **elimina todos los datos existentes** y recrea la base de datos desde cero.

#### Cuándo usar:
- ✅ Ambiente de desarrollo/testing
- ✅ Los datos actuales NO son importantes
- ✅ Quieres una base de datos completamente limpia
- ✅ Primera vez que aplicas cambios estructurales

#### Comandos:

```bash
# 1. Conectar al servidor
ssh sulbaranjc@docker.sulbaranjc.com

# 2. Navegar al directorio del proyecto
cd ~/apps/clientes_api_autenticada/

# 3. Traer los últimos cambios del repositorio
git pull

# 4. Verificar que los cambios están en el archivo
grep -c "INSERT INTO clientes" docs/init_db.sql
# Debería mostrar: 1

grep "Colombia\|México\|España" docs/init_db.sql | head -3
# Debería mostrar los comentarios de países

# 5. Destruir contenedores y ELIMINAR volúmenes (-v)
docker compose down -v

# 6. Recrear contenedores (ejecutará init_db.sql automáticamente)
docker compose up -d

# 7. Esperar ~10 segundos para que MariaDB se inicialice
sleep 10

# 8. Verificar que los contenedores están corriendo
docker ps | grep clientes-api-autenticado

# 9. Verificar el total de registros
docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT COUNT(*) as total FROM clientes_autenticado_db.clientes;"

# 10. Ver algunos registros de ejemplo
docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT id, nombre, apellido, email FROM clientes_autenticado_db.clientes LIMIT 10;"
```

#### Output Esperado:

```
# Paso 5:
[+] down 4/4
 ✔ Container clientes-api-autenticado        Removed
 ✔ Container clientes-api-autenticado-db     Removed
 ✔ Volume clientes_api_autenticada_db_data   Removed  ← IMPORTANTE: Volumen eliminado
 ✔ Network clientes_api_autenticada_internal Removed

# Paso 6:
[+] up 4/4
 ✔ Network clientes_api_autenticada_internal Created
 ✔ Volume clientes_api_autenticada_db_data   Created  ← Volumen nuevo y vacío
 ✔ Container clientes-api-autenticado-db     Created
 ✔ Container clientes-api-autenticado        Created

# Paso 8:
clientes-api-autenticado                           Up 15 seconds
clientes-api-autenticado-db                        Up 15 seconds

# Paso 9:
total
30

# Paso 10:
id      nombre  apellido        email
1       Juan    Pérez           juan.perez@email.com
2       María   González        maria.gonzalez@email.com
3       Carlos  Rodríguez       carlos.rodriguez@email.com
...
```

---

### Opción 2: Insertar Datos Manualmente (Conservar datos existentes)

Esta opción **preserva** los datos actuales y solo agrega nuevos registros.

#### Cuándo usar:
- ✅ Ambiente de producción con datos reales
- ✅ Solo quieres AGREGAR nuevos registros
- ✅ NO quieres perder datos existentes

#### Comandos:

```bash
# 1. Crear archivo temporal solo con los nuevos registros
cat > nuevos_clientes.sql << 'EOF'
USE clientes_autenticado_db;
INSERT INTO clientes (nombre, apellido, email, telefono, direccion) VALUES
    ('Nuevo', 'Cliente', 'nuevo.cliente@email.com', '+57 300 1111111', 'Nueva Dirección 123');
-- Agregar más registros según necesites
EOF

# 2. Ejecutar el script en el contenedor
docker exec -i clientes-api-autenticado-db mysql -uprofesor -p4688 < nuevos_clientes.sql

# 3. Verificar que se agregaron
docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT * FROM clientes_autenticado_db.clientes WHERE email = 'nuevo.cliente@email.com';"

# 4. Limpiar archivo temporal
rm nuevos_clientes.sql
```

---

## 🔍 Verificación Post-Deployment

### Checklist de Verificación:

```bash
# ✅ Contenedores corriendo
docker ps | grep clientes-api-autenticado
# Deberías ver: clientes-api-autenticado y clientes-api-autenticado-db con estado "Up"

# ✅ Total de clientes correcto
docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT COUNT(*) FROM clientes_autenticado_db.clientes;"
# Debería mostrar: 30 (o el número esperado)

# ✅ Total de usuarios correcto
docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT COUNT(*) FROM clientes_autenticado_db.usuarios;"
# Debería mostrar: 2 (admin y usuario)

# ✅ Verificar usuarios específicos
docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT email, rol_id, activo, first_login FROM clientes_autenticado_db.usuarios;"
# Debería mostrar:
# admin@example.com    | 1 | 1 | 0
# usuario@example.com  | 2 | 1 | 1

# ✅ Verificar logs del contenedor (buscar errores)
docker logs clientes-api-autenticado-db --tail 50

# ✅ Probar endpoint de la API
curl -X GET https://clientes-api-autenticado.docker.sulbaranjc.com/docs
# Debería abrir la documentación Swagger
```

---

## ⚠️ Troubleshooting

### Problema 1: Los datos nuevos no aparecen

**Causa:** El volumen `db_data` ya existe y tiene datos previos.

**Solución:**
```bash
# VOLVER A HACER down con -v para eliminar el volumen
docker compose down -v && docker compose up -d
```

---

### Problema 2: Error "Table already exists"

**Causa:** El script init_db.sql se está ejecutando en una base de datos que ya tiene las tablas.

**Solución:** El script ya tiene `DROP TABLE IF EXISTS`, pero si persiste:
```bash
# Entrar al contenedor y eliminar la base de datos manualmente
docker exec -it clientes-api-autenticado-db mysql -uroot -proot4688

# Dentro del MySQL shell:
DROP DATABASE IF EXISTS clientes_autenticado_db;
CREATE DATABASE clientes_autenticado_db;
exit;

# Luego recrear el contenedor
docker compose restart db
```

---

### Problema 3: El contenedor no inicia

**Causa:** Error de sintaxis en init_db.sql

**Diagnóstico:**
```bash
# Ver logs del contenedor
docker logs clientes-api-autenticado-db

# Buscar errores SQL
docker logs clientes-api-autenticado-db 2>&1 | grep -i error
```

**Solución:**
1. Corregir el error en `docs/init_db.sql`
2. Hacer `git pull` en el servidor
3. Recrear: `docker compose down -v && docker compose up -d`

---

### Problema 4: Diferencias entre scripts/init_db.sql y docs/init_db.sql

**Causa:** Se modificó solo uno de los archivos.

**Verificación:**
```bash
# En local
diff scripts/init_db.sql docs/init_db.sql

# No debería mostrar diferencias
```

**Solución:**
```bash
# Copiar el contenido correcto al otro archivo
cp docs/init_db.sql scripts/init_db.sql
# O viceversa si scripts/ está correcto
```

---

## 📊 Datos Actuales del Sistema

### Clientes Iniciales: 30 Registros

Distribución por país:
- 🇨🇴 **Colombia:** 5 clientes (Bogotá, Medellín, Cali, Barranquilla)
- 🇲🇽 **México:** 5 clientes (CDMX, Guadalajara, Monterrey)
- 🇪🇸 **España:** 5 clientes (Madrid, Barcelona, Málaga, Valencia)
- 🇦🇷 **Argentina:** 4 clientes (Buenos Aires, Córdoba, Mendoza)
- 🇨🇱 **Chile:** 3 clientes (Santiago, Viña del Mar)
- 🇵🇪 **Perú:** 3 clientes (Lima, Arequipa)
- 🇪🇨 **Ecuador:** 2 clientes (Quito, Guayaquil)
- 🇻🇪 **Venezuela:** 2 clientes (Caracas, Valencia)
- 🇺🇾 **Uruguay:** 1 cliente (Montevideo)

### Usuarios Iniciales: 2 Registros

| Email | Password | Rol | Estado | First Login |
|-------|----------|-----|--------|-------------|
| admin@example.com | admin123 | Administrador (1) | Activo | No |
| usuario@example.com | user123 | Usuario (2) | Activo | **Sí** (forzar cambio) |

---

## 🎓 Mejores Prácticas

### ✅ DO (Hacer):

1. **Siempre modifica ambos archivos** (docs/ y scripts/)
2. **Haz commit descriptivos** con el número de registros agregados/modificados
3. **Verifica ANTES de hacer push** que la sintaxis SQL es correcta
4. **Usa comentarios** para organizar los datos por categoría/país
5. **Documenta los cambios** en el mensaje de commit
6. **Prueba localmente** antes de aplicar en producción (si es posible)

### ❌ DON'T (No hacer):

1. ❌ Modificar solo uno de los dos archivos init_db.sql
2. ❌ Usar `docker compose up -d` sin `-v` esperando que los datos cambien
3. ❌ Hacer cambios directamente en producción sin git
4. ❌ Olvidar verificar después de aplicar cambios
5. ❌ Poner contraseñas reales en los datos de prueba
6. ❌ Usar emails reales de personas en datos ficticios

---

## 📝 Ejemplo Completo: Agregar 10 Clientes Más

```bash
# 1. Local: Editar los archivos
vim docs/init_db.sql
vim scripts/init_db.sql

# Agregar nuevos registros al INSERT INTO clientes...

# 2. Commit y push
git add docs/init_db.sql scripts/init_db.sql
git commit -m "feat: agregar 10 clientes más de Costa Rica y Panamá"
git push
deployIT

# 3. Producción: SSH al servidor
ssh sulbaranjc@docker.sulbaranjc.com
cd ~/apps/clientes_api_autenticada/

# 4. Pull y verificar
git pull
grep -A 5 "Costa Rica\|Panamá" docs/init_db.sql

# 5. Recrear con datos limpios
docker compose down -v && docker compose up -d

# 6. Esperar inicialización
sleep 10

# 7. Verificar
docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT COUNT(*) FROM clientes_autenticado_db.clientes;"
# Debería mostrar: 40

docker exec clientes-api-autenticado-db mysql -uprofesor -p4688 \
  -e "SELECT nombre, apellido, direccion FROM clientes_autenticado_db.clientes \
      WHERE direccion LIKE '%Costa Rica%' OR direccion LIKE '%Panamá%';"
# Debería mostrar los nuevos clientes
```

---

## 🔗 Documentos Relacionados

- [SERVER_USER_MANAGEMENT.md](./SERVER_USER_MANAGEMENT.md) - Gestión de usuarios vía CLI
- [GESTION_USUARIOS_CLI.md](./GESTION_USUARIOS_CLI.md) - Comandos manage_users.py
- [GUIA_POLITICAS_CONTRASENAS.md](./GUIA_POLITICAS_CONTRASENAS.md) - Políticas de contraseñas
- [QUICK_START_PASSWORD_POLICY.md](./QUICK_START_PASSWORD_POLICY.md) - Inicio rápido

---

## 📅 Historial de Cambios

| Fecha | Cambio | Registros | Autor |
|-------|--------|-----------|-------|
| 2026-02-08 | Expandir de 3 a 30 clientes iniciales | 30 clientes | sulbaranjc |
| (Fecha anterior) | Creación inicial del proyecto | 3 clientes, 2 usuarios | sulbaranjc |

---

**Última actualización:** 8 de febrero de 2026  
**Versión:** 1.0  
**Mantenedor:** sulbaranjc
