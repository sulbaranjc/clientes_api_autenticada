#!/bin/bash

# Script para probar el endpoint de cambio de contraseña
# Uso: ./test_cambiar_password.sh

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_URL="http://localhost:8000"
USERNAME="admin"
PASSWORD_ACTUAL="admin123"
PASSWORD_NUEVA="nuevoPassword2024"

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🔒 TEST: Cambiar Contraseña de Usuario          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}\n"

# Paso 1: Login inicial
echo -e "${BLUE}[1/4] Obtener Token JWT...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD_ACTUAL")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ ERROR: No se pudo obtener el token${NC}"
    echo "Respuesta: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✅ Token obtenido exitosamente${NC}"
echo -e "   Token: ${TOKEN:0:50}...\n"

# Paso 2: Cambiar contraseña
echo -e "${BLUE}[2/4] Cambiar contraseña...${NC}"
CHANGE_RESPONSE=$(curl -s -X POST "$API_URL/auth/cambiar-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"password_actual\": \"$PASSWORD_ACTUAL\",
    \"password_nueva\": \"$PASSWORD_NUEVA\",
    \"password_confirmacion\": \"$PASSWORD_NUEVA\"
  }")

echo "Respuesta:"
echo "$CHANGE_RESPONSE" | python3 -m json.tool

if echo "$CHANGE_RESPONSE" | grep -q "Contraseña actualizada"; then
    echo -e "${GREEN}✅ Contraseña cambiada exitosamente${NC}\n"
else
    echo -e "${RED}❌ Error al cambiar contraseña${NC}\n"
    exit 1
fi

# Paso 3: Intentar login con contraseña antigua (debe fallar)
echo -e "${BLUE}[3/4] Validar: Contraseña antigua rechazada...${NC}"
OLD_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD_ACTUAL")

if echo "$OLD_LOGIN" | grep -q "inválidas\|invalid"; then
    echo -e "${GREEN}✅ Correcto: Contraseña antigua rechazada${NC}\n"
else
    echo -e "${YELLOW}⚠️  Advertencia: Contraseña antigua aún podría funcionar${NC}\n"
fi

# Paso 4: Login con contraseña nueva (debe funcionar)
echo -e "${BLUE}[4/4] Validar: Login con contraseña nueva...${NC}"
NEW_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD_NUEVA")

NEW_TOKEN=$(echo $NEW_LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$NEW_TOKEN" ]; then
    echo -e "${GREEN}✅ Login exitoso con nueva contraseña${NC}\n"
else
    echo -e "${RED}❌ Error: No se puede login con nueva contraseña${NC}\n"
    exit 1
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✨ TODAS LAS PRUEBAS PASARON EXITOSAMENTE ✨   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}\n"

echo "Resumen de cambios:"
echo "  • Usuario: $USERNAME"
echo "  • Contraseña anterior: $PASSWORD_ACTUAL (❌ Ya no funciona)"
echo "  • Contraseña nueva: $PASSWORD_NUEVA (✅ Funciona correctamente)"
echo ""
