# 🚀 QUICK START - Políticas de Contraseñas

## Aplicar la Implementación (3 pasos)

### 1️⃣ Aplicar Migración SQL

```bash
./scripts/apply_password_policy_migration.sh
```

### 2️⃣ Validar con Tests

```bash
source .venv/bin/activate
python scripts/test_password_policy.py
```

**Resultado esperado:** `5/5 tests PASARON` 🎉

### 3️⃣ Reiniciar la Aplicación

```bash
uvicorn app.main:app --reload
```

---

## Prueba Rápida en Swagger

1. Ir a: `http://localhost:8000/docs`
2. Probar endpoint `POST /auth/login`
3. Ver respuesta con campos nuevos:
   - `requires_password_change`
   - `is_first_login`
   - `password_expired`
   - `days_until_expiration`

---

## Documentación Completa

- 📘 **Guía Completa:** [docs/GUIA_POLITICAS_CONTRASENAS.md](docs/GUIA_POLITICAS_CONTRASENAS.md)
- 📊 **Resumen de Implementación:** [docs/RESUMEN_IMPLEMENTACION_PASSWORD_POLICY.md](docs/RESUMEN_IMPLEMENTACION_PASSWORD_POLICY.md)

---

## Archivos Clave

```
✅ app/repository/users_repo.py       - Funciones de políticas
✅ app/routers/auth.py                - Endpoints actualizados
✅ app/schemas/auth.py                - Schemas con campos nuevos
✅ docs/migrations/001_*.sql          - Migración SQL
✅ scripts/test_password_policy.py    - Tests automatizados
```

---

**Estado:** ✅ Código completo - ⏳ Aplicar migración SQL
