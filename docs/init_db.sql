-- =========================================================
-- SCRIPT INICIALIZADOR DE BASE DE DATOS PARA EL PROYECTO CLIENTES AUTENTICADO
-- Autor: Juan Carlos Sulbarán González
-- Fecha: 2025-11-12
-- Descripción:
--   Este script elimina la base de datos si ya existe,
--   la crea desde cero e inicializa clientes, roles y usuarios.
-- Base de datos: clientes_autenticado_db
-- Usuario: profesor | Contraseña: 4688
-- =========================================================

-- 1️⃣ Eliminar base de datos si existe
DROP DATABASE IF EXISTS clientes_autenticado_db;

-- 2️⃣ Crear base de datos
CREATE DATABASE clientes_autenticado_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

-- 3️⃣ Seleccionar la base de datos
USE clientes_autenticado_db;

-- =========================================================
-- 4️⃣ Tabla clientes
-- =========================================================
CREATE TABLE clientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  telefono VARCHAR(50),
  direccion VARCHAR(255)
);

-- =========================================================
-- 5️⃣ Tabla roles
-- =========================================================
CREATE TABLE roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(150)
);

-- =========================================================
-- 6️⃣ Tabla usuarios
-- =========================================================
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  rol_id INT NOT NULL,
  activo TINYINT NOT NULL DEFAULT 1,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en TIMESTAMP NULL DEFAULT NULL
    ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_usuarios_roles
    FOREIGN KEY (rol_id)
    REFERENCES roles(id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);


-- =========================================================
-- 7️⃣ Datos iniciales de roles
-- =========================================================
INSERT INTO roles (nombre, descripcion) VALUES
  ('admin', 'Puede crear, modificar y eliminar clientes'),
  ('lector', 'Solo puede consultar y filtrar clientes');

-- =========================================================
-- 8️⃣ Datos de ejemplo en clientes
-- =========================================================

INSERT INTO clientes (nombre, apellido, email, telefono, direccion) VALUES
('Juan', 'Pérez', 'juan.perez@example.com', '555-0101', 'Calle 123, Ciudad'),
('María', 'García', 'maria.garcia@example.com', '555-0102', 'Avenida 456, Ciudad'),
('Carlos', 'Rodríguez', 'carlos.rodriguez@example.com', '555-0103', 'Plaza 789, Ciudad'),
('Ana', 'Martínez', 'ana.martinez@example.com', '555-0104', 'Paseo 321, Ciudad'),
('Luis', 'López', 'luis.lopez@example.com', '555-0105', 'Boulevard 654, Ciudad'),
('Sofía', 'Hernández', 'sofia.hernandez@example.com', '555-0106', 'Calle Mayor 12, Ciudad'),
('Miguel', 'Sánchez', 'miguel.sanchez@example.com', '555-0107', 'Avenida del Sol 45, Ciudad'),
('Laura', 'Ramírez', 'laura.ramirez@example.com', '555-0108', 'Calle Luna 78, Ciudad'),
('Javier', 'Torres', 'javier.torres@example.com', '555-0109', 'Plaza Central 3, Ciudad'),
('Elena', 'Flores', 'elena.flores@example.com', '555-0110', 'Paseo del Río 56, Ciudad'),
('Daniel', 'Vargas', 'daniel.vargas@example.com', '555-0111', 'Calle Norte 90, Ciudad'),
('Paula', 'Moreno', 'paula.moreno@example.com', '555-0112', 'Avenida Libertad 102, Ciudad'),
('Alejandro', 'Castro', 'alejandro.castro@example.com', '555-0113', 'Boulevard Central 14, Ciudad'),
('Lucía', 'Ortiz', 'lucia.ortiz@example.com', '555-0114', 'Calle Jardín 27, Ciudad'),
('Fernando', 'Navarro', 'fernando.navarro@example.com', '555-0115', 'Plaza del Mercado 8, Ciudad'),
('Isabel', 'Rojas', 'isabel.rojas@example.com', '555-0116', 'Paseo de los Álamos 61, Ciudad'),
('Ricardo', 'Molina', 'ricardo.molina@example.com', '555-0117', 'Avenida Central 200, Ciudad'),
('Carmen', 'Delgado', 'carmen.delgado@example.com', '555-0118', 'Calle Primavera 33, Ciudad'),
('Andrés', 'Gutiérrez', 'andres.gutierrez@example.com', '555-0119', 'Boulevard del Parque 77, Ciudad'),
('Natalia', 'Peña', 'natalia.pena@example.com', '555-0120', 'Calle Horizonte 5, Ciudad');



-- admin (password: admin123)
INSERT INTO usuarios (username, email, password_hash, rol_id)
VALUES ('admin', 'admin@test.com', '$2b$12$o00cK68S.E1NdDf5.tAhd.FeZF.UmrHj4X14TzSDgBJ/dsp4jlLAe', 1);

-- lector (password: lector123)
INSERT INTO usuarios (username, email, password_hash, rol_id)
VALUES ('lector', 'lector@test.com', '$2b$12$IYBfsBcTC4ZM74Oeez98EemoXhThcPWJCd7DBpQcVIItA1uem4wVm', 2);

-- =========================================================
-- 9️⃣ Verificación
-- =========================================================
-- SELECT * FROM clientes;
-- SELECT * FROM roles;
SELECT * FROM usuarios;
SELECT username, password_hash, activo FROM usuarios;
