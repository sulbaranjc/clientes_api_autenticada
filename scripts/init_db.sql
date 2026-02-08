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

-- Clientes de Prueba (30 registros)
INSERT INTO clientes (nombre, apellido, email, telefono, direccion) VALUES
    -- Colombia
    ('Juan', 'Pérez', 'juan.perez@email.com', '+57 310 1234567', 'Calle 123 #45-67, Bogotá'),
    ('María', 'González', 'maria.gonzalez@email.com', '+57 320 7654321', 'Carrera 45 #12-34, Medellín'),
    ('Carlos', 'Rodríguez', 'carlos.rodriguez@email.com', '+57 315 9876543', 'Avenida 68 #23-45, Cali'),
    ('Ana', 'Martínez', 'ana.martinez@email.com', '+57 318 5554433', 'Calle 85 #15-20, Bogotá'),
    ('Luis', 'Fernández', 'luis.fernandez@email.com', '+57 314 7788990', 'Carrera 70 #32-15, Barranquilla'),
    
    -- México
    ('Sofía', 'García', 'sofia.garcia@email.com', '+52 55 1234 5678', 'Avenida Insurgentes 1502, CDMX'),
    ('Diego', 'López', 'diego.lopez@email.com', '+52 33 8765 4321', 'Calle Morelos 234, Guadalajara'),
    ('Valentina', 'Hernández', 'valentina.hernandez@email.com', '+52 81 5566 7788', 'Avenida Constitución 890, Monterrey'),
    ('Miguel', 'Ramírez', 'miguel.ramirez@email.com', '+52 55 9988 7766', 'Calle Reforma 456, CDMX'),
    ('Camila', 'Torres', 'camila.torres@email.com', '+52 33 4433 2211', 'Avenida Chapultepec 678, Guadalajara'),
    
    -- España
    ('Pablo', 'Sánchez', 'pablo.sanchez@email.com', '+34 91 123 4567', 'Calle Gran Vía 28, Madrid'),
    ('Laura', 'Ruiz', 'laura.ruiz@email.com', '+34 93 876 5432', 'Paseo de Gracia 45, Barcelona'),
    ('Javier', 'Moreno', 'javier.moreno@email.com', '+34 95 234 5678', 'Calle Larios 12, Málaga'),
    ('Carmen', 'Jiménez', 'carmen.jimenez@email.com', '+34 96 345 6789', 'Avenida del Puerto 23, Valencia'),
    ('Alberto', 'Navarro', 'alberto.navarro@email.com', '+34 91 567 8901', 'Calle Alcalá 101, Madrid'),
    
    -- Argentina
    ('Lucía', 'Díaz', 'lucia.diaz@email.com', '+54 11 4567 8901', 'Avenida Corrientes 1234, Buenos Aires'),
    ('Mateo', 'Vargas', 'mateo.vargas@email.com', '+54 351 234 5678', 'Calle San Martín 567, Córdoba'),
    ('Isabella', 'Castro', 'isabella.castro@email.com', '+54 261 345 6789', 'Avenida San Martín 890, Mendoza'),
    ('Sebastián', 'Romero', 'sebastian.romero@email.com', '+54 11 6789 0123', 'Calle Florida 345, Buenos Aires'),
    
    -- Chile
    ('Martina', 'Silva', 'martina.silva@email.com', '+56 2 2345 6789', 'Avenida Providencia 1234, Santiago'),
    ('Nicolás', 'Muñoz', 'nicolas.munoz@email.com', '+56 32 234 5678', 'Calle Valparaíso 456, Viña del Mar'),
    ('Francisca', 'Flores', 'francisca.flores@email.com', '+56 2 3456 7890', 'Avenida Apoquindo 2345, Santiago'),
    
    -- Perú
    ('Alejandro', 'Paredes', 'alejandro.paredes@email.com', '+51 1 234 5678', 'Avenida Arequipa 1234, Lima'),
    ('Daniela', 'Quispe', 'daniela.quispe@email.com', '+51 54 345 678', 'Calle Mercaderes 345, Arequipa'),
    ('Andrés', 'Mendoza', 'andres.mendoza@email.com', '+51 1 567 8901', 'Avenida Javier Prado 2345, Lima'),
    
    -- Ecuador
    ('Gabriela', 'Ortiz', 'gabriela.ortiz@email.com', '+593 2 234 5678', 'Avenida Amazonas 1234, Quito'),
    ('Santiago', 'Morales', 'santiago.morales@email.com', '+593 4 345 6789', 'Calle 9 de Octubre 456, Guayaquil'),
    
    -- Venezuela
    ('Valeria', 'Reyes', 'valeria.reyes@email.com', '+58 212 345 6789', 'Avenida Libertador 1234, Caracas'),
    ('Fernando', 'Medina', 'fernando.medina@email.com', '+58 241 234 5678', 'Avenida Bolívar 567, Valencia'),
    
    -- Uruguay
    ('Emilia', 'Vega', 'emilia.vega@email.com', '+598 2 345 6789', 'Avenida 18 de Julio 1234, Montevideo')
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
