#!/bin/bash

# ============================================================================
# Script de Inicialización de Base de Datos
# Descripción: Ejecuta init_db.sql para crear la base de datos completa
# ============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con formato
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SQL_FILE="$SCRIPT_DIR/init_db.sql"

# Archivo .env
ENV_FILE="$PROJECT_ROOT/.env"

# Banner
clear
print_header "INICIALIZACIÓN DE BASE DE DATOS"
echo ""

# Verificar que existe el archivo SQL
if [ ! -f "$SQL_FILE" ]; then
    print_error "No se encuentra el archivo: $SQL_FILE"
    exit 1
fi

# Cargar variables de entorno
if [ -f "$ENV_FILE" ]; then
    print_success "Cargando configuración desde .env..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    print_error "No se encuentra el archivo .env en: $ENV_FILE"
    exit 1
fi

# Verificar variables requeridas
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    print_error "Variables de entorno DB_HOST, DB_USER o DB_PASSWORD no configuradas"
    exit 1
fi

# Mostrar configuración
echo ""
print_warning "CONFIGURACIÓN ACTUAL:"
echo "  Host: $DB_HOST"
echo "  Usuario: $DB_USER"
echo "  Base de datos: clientes_autenticado_db (se creará)"
echo ""

# Confirmar antes de proceder
print_warning "⚠️  ADVERTENCIA: Este script creará/sobrescribirá la base de datos"
echo ""
read -p "¿Deseas continuar? (s/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    print_warning "Operación cancelada por el usuario"
    exit 0
fi

# Crear backup de la base de datos existente (si existe)
print_header "PASO 1: BACKUP DE SEGURIDAD"
echo ""

DB_EXISTS=$(mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" -e "SHOW DATABASES LIKE 'clientes_autenticado_db';" -s -N 2>/dev/null)

if [ ! -z "$DB_EXISTS" ]; then
    BACKUP_FILE="$SCRIPT_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    print_warning "Base de datos existente detectada. Creando backup..."
    
    mysqldump -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" clientes_autenticado_db > "$BACKUP_FILE" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Backup creado: $BACKUP_FILE"
    else
        print_error "Error al crear backup, pero continuando..."
    fi
else
    print_success "No existe base de datos previa, no se requiere backup"
fi

# Ejecutar el script SQL
echo ""
print_header "PASO 2: EJECUTAR SCRIPT SQL"
echo ""

print_warning "Ejecutando init_db.sql..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" < "$SQL_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    print_success "Base de datos inicializada correctamente"
else
    echo ""
    print_error "Error al ejecutar el script SQL"
    exit 1
fi

# Verificar la creación
echo ""
print_header "PASO 3: VERIFICACIÓN"
echo ""

print_warning "Verificando tablas creadas..."
TABLES=$(mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" -D clientes_autenticado_db -e "SHOW TABLES;" -s -N 2>/dev/null)

if [ ! -z "$TABLES" ]; then
    print_success "Tablas creadas:"
    echo "$TABLES" | while read table; do
        echo "  - $table"
    done
else
    print_error "No se pudieron verificar las tablas"
    exit 1
fi

# Verificar usuarios creados
echo ""
print_warning "Verificando usuarios creados..."
USERS=$(mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" -D clientes_autenticado_db -e "SELECT username, email FROM usuarios;" -s -N 2>/dev/null)

if [ ! -z "$USERS" ]; then
    print_success "Usuarios encontrados:"
    echo "$USERS" | while read line; do
        echo "  - $line"
    done
else
    print_error "No se pudieron verificar los usuarios"
    exit 1
fi

# Resumen final
echo ""
print_header "RESUMEN FINAL"
echo ""
print_success "✅ Base de datos inicializada correctamente"
print_success "✅ Tablas creadas y verificadas"
print_success "✅ Usuarios por defecto creados"
echo ""
print_warning "CREDENCIALES POR DEFECTO:"
echo "  Admin:   admin / admin123"
echo "  Usuario: usuario_prueba / user123"
echo ""
print_warning "⚠️  IMPORTANTE:"
echo "  - Cambia las contraseñas en producción"
echo "  - Actualiza SECRET_KEY en .env"
echo "  - Ejecuta: python scripts/test_password_policy.py"
echo ""
print_success "🚀 ¡La base de datos está lista para usar!"
echo ""
