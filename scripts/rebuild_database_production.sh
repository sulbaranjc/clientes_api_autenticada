#!/bin/bash

# ============================================================================
# Script para Reconstruir Base de Datos en Servidor de Producción
# ============================================================================

set -e  # Salir si algún comando falla

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

clear
print_header "RECONSTRUIR BASE DE DATOS EN PRODUCCIÓN"
echo ""

# Configuración
CONTAINER_NAME="clientes-api-autenticado-db"
DB_NAME="clientes_autenticado_db"
BACKUP_DIR="/tmp/db_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    print_error "No se encuentra docker-compose.yml. Ejecuta desde el directorio del proyecto."
    exit 1
fi

# Advertencia
print_warning "⚠️  ADVERTENCIA: Este script eliminará y recreará la base de datos"
echo ""
echo "Esto hará lo siguiente:"
echo "  1. Crear backup de la BD actual"
echo "  2. Detener contenedor de base de datos"
echo "  3. Eliminar volumen de datos"
echo "  4. Levantar contenedor con init_db.sql"
echo "  5. Verificar que se crearon las tablas con los nuevos campos"
echo ""
read -p "¿Estás SEGURO de continuar? (escribe 'SI' en mayúsculas): " -r
echo ""

if [ "$REPLY" != "SI" ]; then
    print_warning "Operación cancelada"
    exit 0
fi

# PASO 1: Crear backup
print_header "PASO 1: CREAR BACKUP"
echo ""

print_warning "Creando backup de la base de datos actual..."
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql"

docker exec "$CONTAINER_NAME" mysqldump \
    -u profesor -p4688 \
    "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "Backup creado: $BACKUP_FILE"
    ls -lh "$BACKUP_FILE"
else
    print_error "Error al crear backup"
    exit 1
fi

# PASO 2: Detener y eliminar contenedor de BD
print_header "PASO 2: DETENER CONTENEDOR"
echo ""

print_warning "Deteniendo contenedor de base de datos..."
docker-compose stop db
print_success "Contenedor detenido"

# PASO 3: Eliminar volumen de datos
print_header "PASO 3: ELIMINAR VOLUMEN DE DATOS"
echo ""

print_warning "Eliminando volumen de datos (esto borrará la BD)..."
VOLUME_NAME=$(docker volume ls | grep clientes.*db_data | awk '{print $2}')

if [ -z "$VOLUME_NAME" ]; then
    print_warning "No se encontró volumen, continuando..."
else
    docker volume rm "$VOLUME_NAME" 2>/dev/null || print_warning "Volumen en uso, se eliminará con down"
    docker-compose down -v
    print_success "Volumen eliminado"
fi

# PASO 4: Copiar init_db.sql actualizado
print_header "PASO 4: PREPARAR SCRIPT DE INICIALIZACIÓN"
echo ""

if [ -f "scripts/init_db.sql" ]; then
    print_warning "Copiando script actualizado..."
    cp -f scripts/init_db.sql docs/init_db.sql
    print_success "Script actualizado en docs/init_db.sql"
else
    print_error "No se encuentra scripts/init_db.sql"
    exit 1
fi

# PASO 5: Levantar contenedor con nueva BD
print_header "PASO 5: CREAR NUEVA BASE DE DATOS"
echo ""

print_warning "Levantando contenedor de base de datos..."
docker-compose up -d db

# Esperar a que MySQL esté listo
print_warning "Esperando que MySQL esté listo..."
RETRIES=30
until docker exec "$CONTAINER_NAME" mysqladmin ping -h localhost --silent 2>/dev/null; do
    RETRIES=$((RETRIES - 1))
    if [ $RETRIES -le 0 ]; then
        print_error "MySQL no respondió a tiempo"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""
print_success "MySQL está activo"

# Dar tiempo para que se ejecute el init script
print_warning "Esperando que se ejecute el script de inicialización..."
sleep 5

# PASO 6: Verificar tablas creadas
print_header "PASO 6: VERIFICAR NUEVA BASE DE DATOS"
echo ""

print_warning "Verificando tablas..."
TABLES=$(docker exec "$CONTAINER_NAME" mysql -u profesor -p4688 -D "$DB_NAME" -e "SHOW TABLES;" -s -N 2>/dev/null)

if [ ! -z "$TABLES" ]; then
    print_success "Tablas encontradas:"
    echo "$TABLES" | while read table; do
        echo "  - $table"
    done
else
    print_error "No se encontraron tablas"
    exit 1
fi

# Verificar campos de password policy
print_warning "Verificando campos de política de contraseñas..."
FIELDS=$(docker exec "$CONTAINER_NAME" mysql -u profesor -p4688 -D "$DB_NAME" \
    -e "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='usuarios' AND COLUMN_NAME IN ('first_login', 'password_expires_at', 'force_password_change', 'password_changed_at', 'last_password_change_ip');" \
    -s -N 2>/dev/null | wc -l)

if [ "$FIELDS" -eq 5 ]; then
    print_success "Los 5 campos de política de contraseñas están presentes ✓"
else
    print_error "Faltan campos de política de contraseñas ($FIELDS/5)"
    exit 1
fi

# Verificar usuarios creados
print_warning "Verificando usuarios creados..."
USERS=$(docker exec "$CONTAINER_NAME" mysql -u profesor -p4688 -D "$DB_NAME" \
    -e "SELECT username, email FROM usuarios;" -s -N 2>/dev/null)

if [ ! -z "$USERS" ]; then
    print_success "Usuarios encontrados:"
    echo "$USERS" | while read line; do
        echo "  - $line"
    done
else
    print_error "No se encontraron usuarios"
    exit 1
fi

# PASO 7: Reiniciar aplicación
print_header "PASO 7: REINICIAR APLICACIÓN"
echo ""

print_warning "Reiniciando contenedor de la aplicación..."
docker-compose restart app
print_success "Aplicación reiniciada"

# Resumen final
echo ""
print_header "RESUMEN FINAL"
echo ""
print_success "✅ Base de datos reconstruida exitosamente"
print_success "✅ Backup guardado en: $BACKUP_FILE"
print_success "✅ Tablas verificadas con campos de política de contraseñas"
print_success "✅ Usuarios por defecto creados"
echo ""
print_warning "PRÓXIMOS PASOS:"
echo "  1. Verificar API: curl http://localhost:8000/docs"
echo "  2. Probar login con: admin / admin123"
echo "  3. Cambiar contraseñas en producción"
echo ""
print_success "🚀 ¡El despliegue está listo!"
echo ""
