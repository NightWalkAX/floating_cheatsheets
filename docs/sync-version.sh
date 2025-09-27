#!/bin/bash

# Script para generar el archivo docs/release_info.json con los enlaces de descarga
# correctos y la versión del proyecto.
# Debe ejecutarse desde la raíz del proyecto.

set -e

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RELEASE_INFO_JSON="$PROJECT_ROOT/docs/release_info.json"
OLD_VERSION_JSON="$PROJECT_ROOT/docs/version.json"
VERSION_UTILS_SCRIPT="$PROJECT_ROOT/version_utils.sh"

# Verificar que el script de utilidades de versión existe
if [ ! -f "$VERSION_UTILS_SCRIPT" ]; then
    echo "Error: No se encontró el script version_utils.sh en $PROJECT_ROOT"
    exit 1
fi

# Importar utilidades
source "$VERSION_UTILS_SCRIPT"

# Obtener información de la versión
VERSION=$(get_project_version)
TIMESTAMP=$(get_build_timestamp)
GIT_HASH=$(get_git_hash)
GITHUB_USER="NightWalkAX"
REPO_NAME="floating_cheatsheets"
BASE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}/releases/latest/download"

echo "Generando información de release para la versión: $VERSION"

# Nombres de los archivos de distribución
WINDOWS_FILENAME="floating-cheatsheets-${VERSION}-setup.exe"
LINUX_FILENAME="floating-cheatsheets_${VERSION}_${TIMESTAMP}_${GIT_HASH}.deb"

# URLs completas de descarga
WINDOWS_URL="${BASE_URL}/${WINDOWS_FILENAME}"
LINUX_URL="${BASE_URL}/${LINUX_FILENAME}"

echo "URL de Windows: $WINDOWS_URL"
echo "URL de Linux: $LINUX_URL"

# Crear o actualizar release_info.json
cat > "$RELEASE_INFO_JSON" << EOF
{
  "version": "$VERSION",
  "windowsURL": "$WINDOWS_URL",
  "linuxURL": "$LINUX_URL"
}
EOF

echo "✅ Fichero release_info.json generado/actualizado en $RELEASE_INFO_JSON"

# Eliminar el antiguo version.json si existe
if [ -f "$OLD_VERSION_JSON" ]; then
    rm "$OLD_VERSION_JSON"
    echo "🗑️  Fichero obsoleto version.json eliminado."
fi

echo "🎉 Sincronización de información de release completada."