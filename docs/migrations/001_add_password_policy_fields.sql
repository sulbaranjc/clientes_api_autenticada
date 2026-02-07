-- ============================================================================
-- MIGRACIÓN: Agregar campos de política de contraseñas
-- ============================================================================
-- Fecha: 7 de febrero de 2026
-- Descripción: Agrega campos para implementar cambio de contraseña obligatorio
--              en el primer login y políticas de expiración de contraseñas.
--
-- EJECUTAR:
--   mysql -u profesor -p clientes_autenticado_db < docs/migrations/001_add_password_policy_fields.sql
-- 
-- O desde MySQL Workbench/phpMyAdmin copiar y pegar este contenido
-- ============================================================================

USE clientes_autenticado_db;

-- Agregar campos de políticas de contraseña
ALTER TABLE usuarios
ADD COLUMN first_login BOOLEAN DEFAULT TRUE 
    COMMENT 'Indica si es el primer inicio de sesión del usuario',
ADD COLUMN password_expires_at DATETIME NULL 
    COMMENT 'Fecha de expiración de la contraseña',
ADD COLUMN force_password_change BOOLEAN DEFAULT FALSE 
    COMMENT 'Fuerza al usuario a cambiar contraseña en el próximo login',
ADD COLUMN password_changed_at DATETIME NULL 
    COMMENT 'Última fecha en que el usuario cambió su contraseña',
ADD COLUMN last_password_change_ip VARCHAR(45) NULL 
    COMMENT 'Dirección IP desde donde se realizó el último cambio de contraseña';

-- Actualizar usuarios existentes: marcar que NO es primer login
-- (asumimos que usuarios existentes ya tienen contraseñas válidas)
UPDATE usuarios 
SET first_login = FALSE,
    password_changed_at = creado_en
WHERE creado_en IS NOT NULL;

-- Crear índice para mejorar consultas de expiración
CREATE INDEX idx_password_expires ON usuarios(password_expires_at);

-- ============================================================================
-- Verificar cambios
-- ============================================================================
-- Ejecutar para ver la estructura actualizada:
-- DESCRIBE usuarios;

-- Ejecutar para ver usuarios con primer login pendiente:
-- SELECT username, first_login, force_password_change FROM usuarios;

-- ============================================================================
-- ROLLBACK (en caso de error)
-- ============================================================================
-- Si necesitas revertir los cambios:
-- 
-- ALTER TABLE usuarios
-- DROP COLUMN first_login,
-- DROP COLUMN password_expires_at,
-- DROP COLUMN force_password_change,
-- DROP COLUMN password_changed_at,
-- DROP COLUMN last_password_change_ip;
-- 
-- DROP INDEX idx_password_expires ON usuarios;
-- ============================================================================
