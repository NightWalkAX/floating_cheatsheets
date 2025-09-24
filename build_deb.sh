#!/bin/bash
# Script para construir el paquete .deb

set -e

echo "=== Construyendo paquete .deb ==="

# Verificar que estamos en el directorio correcto
if [ ! -f "src/main.py" ]; then
    echo "Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

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

# Mover el .deb al directorio actual
mv ../floating-cheatsheets_*.deb .

echo "=== Paquete .deb creado exitosamente ==="
echo "Archivo: $(ls *.deb)"
echo ""
echo "Para instalar:"
echo "sudo dpkg -i $(ls *.deb)"