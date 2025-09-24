#!/bin/bash
# Script para construir el paquete .deb

set -e

echo "=== Construyendo paquete .deb ==="

# Verificar que estamos en el directorio correcto
if [ ! -f "src/main.py" ]; then
    echo "Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

# Importar utilidades de versión
source "$(dirname "$0")/version_utils.sh"

# Obtener información de versión dinámica
PROJECT_VERSION=$(get_project_version)
BUILD_TIMESTAMP=$(get_build_timestamp)
GIT_HASH=$(get_git_hash)

echo "Versión del proyecto: ${PROJECT_VERSION}"
echo "Timestamp: ${BUILD_TIMESTAMP}"
echo "Git hash: ${GIT_HASH}"

# Limpiar builds anteriores
rm -rf build/ dist/ *.deb

# Crear icono si no existe
if [ ! -f "assets/icon.png" ]; then
    mkdir -p assets
    # Crear un icono simple (puedes reemplazar con un icono real)
    convert -size 64x64 xc:transparent -fill "#4a90e2" -draw "circle 32,32 32,8" assets/icon.png 2>/dev/null || echo "Advertencia: No se pudo crear icono automático"
fi

# Instalar dependencias de construcción si no están instaladas
if ! command -v dpkg-buildpackage &> /dev/null; then
    echo "Instalando herramientas de construcción..."
    sudo apt-get update
    sudo apt-get install -y build-essential devscripts debhelper
fi

# Construir el paquete
echo "Construyendo paquete..."
dpkg-buildpackage -us -uc -b

# Generar nombre dinámico para el paquete
DYNAMIC_PACKAGE_NAME=$(generate_package_name)

# Mover y renombrar el .deb al directorio actual
ORIGINAL_DEB=$(ls ../floating-cheatsheets_*.deb)
mv "$ORIGINAL_DEB" "./$DYNAMIC_PACKAGE_NAME"

echo "=== Paquete .deb creado exitosamente ==="
echo "Archivo: ${DYNAMIC_PACKAGE_NAME}"
echo "Versión: ${PROJECT_VERSION}"
echo "Build: ${BUILD_TIMESTAMP}"
echo "Git hash: ${GIT_HASH}"
echo ""
echo "Para instalar:"
echo "sudo dpkg -i ${DYNAMIC_PACKAGE_NAME}"
echo ""
echo "Para instalar dependencias si faltan:"
echo "sudo apt-get install -f"