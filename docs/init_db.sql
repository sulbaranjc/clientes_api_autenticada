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
('Luis', 'López', 'luis.lopez@example.com', '555-0105', 'Boulevard 654, Ciudad');

-- admin
INSERT INTO usuarios (username, email, password_hash, rol_id)
VALUES ('admin', 'admin@test.com', '$2b$12$1FERac3oRY3l2090Xl7EGuDzO4zUe9Nyowy3XLaZ2t6znkmwB9I76', 1);

-- lector
INSERT INTO usuarios (username, email, password_hash, rol_id)
VALUES ('lector', 'lector@test.com', '$2b$12$IBWpsxUBSMIhWALA3L3Fk.97qcrHZ7xEpbkyFmaBmBtn1hca/j3Em', 2);

-- =========================================================
-- 9️⃣ Verificación
-- =========================================================
-- SELECT * FROM clientes;
-- SELECT * FROM roles;
SELECT * FROM usuarios;
SELECT username, password_hash, activo FROM usuarios;
