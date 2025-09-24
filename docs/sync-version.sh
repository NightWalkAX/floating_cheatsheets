#!/bin/bash

# Script para sincronizar la versión desde VERSION a docs/version.json
# Este script debe ejecutarse cada vez que se actualice la versión

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION_FILE="$PROJECT_ROOT/VERSION"
VERSION_JSON="$PROJECT_ROOT/docs/version.json"

if [ ! -f "$VERSION_FILE" ]; then
    echo "Error: No se encontró el archivo VERSION en $VERSION_FILE"
    exit 1
fi

# Leer la versión del archivo VERSION
VERSION=$(cat "$VERSION_FILE" | tr -d '\n\r')

if [ -z "$VERSION" ]; then
    echo "Error: El archivo VERSION está vacío"
    exit 1
fi

# Crear o actualizar version.json
cat > "$VERSION_JSON" << EOF
{
  "version": "$VERSION"
}
EOF

echo "✅ Versión $VERSION sincronizada en docs/version.json"

# Si existe package.json, también actualizarlo
PACKAGE_JSON="$PROJECT_ROOT/package.json"
if [ -f "$PACKAGE_JSON" ]; then
    # Usar jq si está disponible, sino usar sed
    if command -v jq >/dev/null 2>&1; then
        jq --arg version "$VERSION" '.version = $version' "$PACKAGE_JSON" > "${PACKAGE_JSON}.tmp" && mv "${PACKAGE_JSON}.tmp" "$PACKAGE_JSON"
        echo "✅ package.json actualizado con versión $VERSION"
    else
        sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" "$PACKAGE_JSON"
        echo "✅ package.json actualizado con versión $VERSION (usando sed)"
    fi
fi

echo "🎉 Sincronización de versión completada"