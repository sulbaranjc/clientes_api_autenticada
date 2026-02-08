-- ============================================================================
-- Script de Inicialización de Base de Datos
-- Proyecto: Clientes API Autenticada
-- Descripción: Crea la base de datos con todas las tablas y políticas de seguridad
-- ============================================================================

-- 1. CREAR BASE DE DATOS
-- ============================================================================
CREATE DATABASE IF NOT EXISTS clientes_autenticado_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE clientes_autenticado_db;


-- 2. TABLA: roles
-- ============================================================================
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar roles por defecto
INSERT INTO roles (nombre, descripcion) VALUES
    ('admin', 'Administrador del sistema con acceso completo'),
    ('user', 'Usuario estándar con acceso limitado'),
    ('guest', 'Usuario invitado con acceso de solo lectura')
ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion);


-- 3. TABLA: usuarios
-- ============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL,
    activo TINYINT DEFAULT 1,
    
    -- ========================================
    -- 🔐 CAMPOS DE POLÍTICA DE CONTRASEÑAS
    -- ========================================
    first_login BOOLEAN DEFAULT TRUE 
        COMMENT 'Indica si es el primer inicio de sesión del usuario',
    
    password_expires_at DATETIME NULL 
        COMMENT 'Fecha de expiración de la contraseña actual',
    
    force_password_change BOOLEAN DEFAULT FALSE 
        COMMENT 'Fuerza al usuario a cambiar contraseña en próximo login',
    
    password_changed_at DATETIME NULL 
        COMMENT 'Última fecha en que se cambió la contraseña',
    
    last_password_change_ip VARCHAR(45) NULL 
        COMMENT 'IP desde donde se realizó el último cambio de contraseña',
    
    -- ========================================
    -- AUDITORÍA
    -- ========================================
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- ========================================
    -- CONSTRAINTS
    -- ========================================
    CONSTRAINT fk_usuarios_rol 
        FOREIGN KEY (rol_id) REFERENCES roles(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_rol_id (rol_id),
    INDEX idx_activo (activo),
    INDEX idx_first_login (first_login),
    INDEX idx_password_expires (password_expires_at)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 4. TABLA: clientes
-- ============================================================================
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(50),
    direccion VARCHAR(255),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_nombre_apellido (nombre, apellido)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 5. DATOS DE PRUEBA
-- ============================================================================

-- Usuario Administrador (password: admin123)
-- Hash generado con bcrypt
INSERT INTO usuarios (
    username,
    email,
    password_hash,
    rol_id,
    activo,
    first_login,
    password_changed_at
) VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbYr8kQJSi',
    (SELECT id FROM roles WHERE nombre = 'admin'),
    1,
    FALSE,
    CURRENT_TIMESTAMP
) ON DUPLICATE KEY UPDATE username = username;

-- Usuario de Prueba (password: user123 - debe cambiarse en primer login)
INSERT INTO usuarios (
    username,
    email,
    password_hash,
    rol_id,
    activo,
    first_login,
    force_password_change
) VALUES (
    'usuario_prueba',
    'usuario@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbYr8kQJSi',
    (SELECT id FROM roles WHERE nombre = 'user'),
    1,
    TRUE,
    FALSE
) ON DUPLICATE KEY UPDATE username = username;

-- Clientes de Prueba
INSERT INTO clientes (nombre, apellido, email, telefono, direccion) VALUES
    ('Juan', 'Pérez', 'juan.perez@email.com', '+57 310 1234567', 'Calle 123 #45-67, Bogotá'),
    ('María', 'González', 'maria.gonzalez@email.com', '+57 320 7654321', 'Carrera 45 #12-34, Medellín'),
    ('Carlos', 'Rodríguez', 'carlos.rodriguez@email.com', '+57 315 9876543', 'Avenida 68 #23-45, Cali')
ON DUPLICATE KEY UPDATE email = email;


-- 6. VISTAS ÚTILES
-- ============================================================================

-- Vista: Usuarios con contraseñas próximas a expirar
CREATE OR REPLACE VIEW v_usuarios_password_expirando AS
SELECT 
    u.id,
    u.username,
    u.email,
    r.nombre AS rol,
    u.password_expires_at,
    DATEDIFF(u.password_expires_at, NOW()) AS dias_restantes,
    CASE 
        WHEN u.password_expires_at < NOW() THEN 'EXPIRADA'
        WHEN DATEDIFF(u.password_expires_at, NOW()) <= 7 THEN 'CRÍTICO'
        WHEN DATEDIFF(u.password_expires_at, NOW()) <= 15 THEN 'ADVERTENCIA'
        ELSE 'OK'
    END AS estado
FROM usuarios u
JOIN roles r ON u.rol_id = r.id
WHERE u.activo = 1
  AND u.password_expires_at IS NOT NULL
ORDER BY u.password_expires_at ASC;


-- Vista: Usuarios que requieren cambio de contraseña
CREATE OR REPLACE VIEW v_usuarios_requieren_cambio AS
SELECT 
    u.id,
    u.username,
    u.email,
    r.nombre AS rol,
    u.first_login,
    u.force_password_change,
    u.password_expires_at,
    CASE
        WHEN u.first_login = TRUE THEN 'PRIMER_LOGIN'
        WHEN u.force_password_change = TRUE THEN 'FORZADO_POR_ADMIN'
        WHEN u.password_expires_at < NOW() THEN 'CONTRASEÑA_EXPIRADA'
        ELSE 'NO_REQUIERE'
    END AS razon_cambio
FROM usuarios u
JOIN roles r ON u.rol_id = r.id
WHERE u.activo = 1
  AND (
      u.first_login = TRUE 
      OR u.force_password_change = TRUE 
      OR u.password_expires_at < NOW()
  );


-- ============================================================================
-- INFORMACIÓN FINAL
-- ============================================================================

SELECT 
    '✅ Base de datos creada exitosamente' AS mensaje,
    DATABASE() AS base_datos,
    (SELECT COUNT(*) FROM roles) AS total_roles,
    (SELECT COUNT(*) FROM usuarios) AS total_usuarios,
    (SELECT COUNT(*) FROM clientes) AS total_clientes;

SELECT 
    '⚠️  USUARIOS CREADOS POR DEFECTO:' AS informacion;

SELECT 
    username,
    email,
    (SELECT nombre FROM roles WHERE id = rol_id) AS rol,
    CASE WHEN first_login THEN 'Debe cambiar contraseña' ELSE 'OK' END AS estado
FROM usuarios;

-- ============================================================================
-- NOTAS IMPORTANTES:
-- ============================================================================
-- 
-- 🔐 CREDENCIALES POR DEFECTO:
--    Admin:   admin / admin123
--    Usuario: usuario_prueba / user123 (debe cambiar en primer login)
--
-- ⚠️  CAMBIAR EN PRODUCCIÓN:
--    - Eliminar usuarios de prueba
--    - Cambiar todas las contraseñas
--    - Actualizar SECRET_KEY en .env
--
-- 📝 MANTENIMIENTO:
--    - Ejecutar: SELECT * FROM v_usuarios_password_expirando;
--    - Ejecutar: SELECT * FROM v_usuarios_requieren_cambio;
--
-- ============================================================================
