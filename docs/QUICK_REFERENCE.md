# 🚀 QUICK START - VALIDACIÓN RÁPIDA

## En 3 Pasos

### 1️⃣ Ejecutar el Script SQL

```bash
mysql -u profesor -p4688 < docs/init_db.sql
```

### 2️⃣ Probar Login con curl

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Resultado esperado:**
```json
{"access_token":"eyJ...","token_type":"bearer"}
```

### 3️⃣ ¡Listo! ✅

Si aparece el token, todo funciona.

---

## Credenciales para Prueba

```
admin    : admin123
lector   : lector123
```

---

## Si No Funciona...

| Problema | Solución |
|----------|----------|
| `Connection refused` | ¿MySQL está corriendo? Verificar: `mysql -u profesor -p4688 -e "SELECT 1"` |
| `Access denied` | Verificar credenciales MySQL (usuario: profesor, pwd: 4688) |
| `Unknown database` | Ejecutar: `mysql -u profesor -p4688 < docs/init_db.sql` |
| `401 Unauthorized` | Hash incorrecto. Verificar que se ejecutó el SQL correctamente |

---

## 🔧 Gestión de Usuarios desde CLI

**Script:** `manage_users.py` - Herramienta completa de administración

```bash
# Listar usuarios
python scripts/manage_users.py list

# Cambiar contraseña
python scripts/manage_users.py change-password usuario@example.com

# Crear usuario
python scripts/manage_users.py create-user nuevo@example.com nuevouser --rol user

# Forzar cambio
python scripts/manage_users.py force-change usuario@example.com

# Ayuda
python scripts/manage_users.py --help
```

📖 **Guía completa:** [GESTION_USUARIOS_CLI.md](GESTION_USUARIOS_CLI.md)

---

## Archivos de Referencia

- 🔧 `GESTION_USUARIOS_CLI.md` - Gestión de usuarios CLI (NUEVO)
- 🔐 `GUIA_POLITICAS_CONTRASENAS.md` - Políticas de contraseñas
- 📄 `CAMBIOS_RESUMEN.md` - ¿Qué cambió?
- 📊 `ANALISIS_AUTENTICACION.md` - Análisis técnico
- 📖 `GUIA_TECNICA_AUTENTICACION.md` - Documentación completa
- ✅ `STATUS_VALIDACION.md` - Estado actual

---

## El Cambio

**Archivo:** `docs/init_db.sql`

**Cambio:** 2 lineas con hashes bcrypt actualizados

```diff
- VALUES ('admin', 'admin@test.com', '$2b$12$1FERac3oRY3l2090Xl7EGuDzO4zUe9Nyowy3XLaZ2t6znkmwB9I76', 1);
+ VALUES ('admin', 'admin@test.com', '$2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlLAe', 1);

- VALUES ('lector', 'lector@test.com', '$2b$12$IBWpsxUBSMIhWALA3L3Fk.97qcrHZ7xEpbkyFmaBmBtn1hca/j3Em', 2);
+ VALUES ('lector', 'lector@test.com', '$2b$12$IYBfsBcTC4ZM74Oeez98EemoXhThcPWJCd7DBpQcVIItA1uem4wVm', 2);
```

---

Más detalles en los documentos anteriores.
