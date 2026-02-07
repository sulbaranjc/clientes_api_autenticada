#!/bin/bash
# ============================================================================
# Script para aplicar la migración de políticas de contraseñas
# ============================================================================
# Uso: ./scripts/apply_password_policy_migration.sh
# ============================================================================

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Aplicando Migración: Password Policy Fields${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Cargar variables de entorno
if [ -f .env ]; then
    source .env
    echo -e "${GREEN}✓${NC} Variables de entorno cargadas desde .env"
else
    echo -e "${RED}✗${NC} Archivo .env no encontrado"
    exit 1
fi

# Verificar que las variables estén configuradas
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_NAME" ]; then
    echo -e "${RED}✗${NC} Faltan variables de entorno de base de datos"
    echo "   Asegúrate de que DB_HOST, DB_USER, DB_PASSWORD y DB_NAME estén configuradas"
    exit 1
fi

echo -e "${GREEN}✓${NC} Variables de base de datos verificadas"
echo ""

# Archivo de migración
MIGRATION_FILE="docs/migrations/001_add_password_policy_fields.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}✗${NC} Archivo de migración no encontrado: $MIGRATION_FILE"
    exit 1
fi

echo -e "${YELLOW}⚠${NC}  IMPORTANTE: Esta migración agregará los siguientes campos a la tabla 'usuarios':"
echo "   - first_login"
echo "   - password_expires_at"
echo "   - force_password_change"
echo "   - password_changed_at"
echo "   - last_password_change_ip"
echo ""

# Preguntar confirmación
read -p "¿Deseas continuar? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo -e "${YELLOW}✗${NC} Migración cancelada por el usuario"
    exit 0
fi

echo ""
echo -e "${BLUE}Aplicando migración...${NC}"
echo ""

# Ejecutar migración
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}  ✓ Migración aplicada exitosamente${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo "Verificando cambios..."
    echo ""
    
    # Mostrar estructura de la tabla
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "DESCRIBE usuarios;"
    
    echo ""
    echo -e "${GREEN}✓${NC} La tabla 'usuarios' ha sido actualizada correctamente"
    echo ""
    echo "Próximos pasos:"
    echo "1. Reinicia la aplicación FastAPI"
    echo "2. Ejecuta el script de test: python scripts/test_password_policy.py"
    echo "3. Prueba el login con un usuario existente"
    echo ""
else
    echo ""
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}  ✗ Error al aplicar la migración${NC}"
    echo -e "${RED}============================================================${NC}"
    echo ""
    echo "Revisa los mensajes de error arriba"
    echo ""
    exit 1
fi
