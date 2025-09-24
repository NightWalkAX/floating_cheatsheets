#!/bin/bash
# Utilidad para obtener información de versión del proyecto

get_project_version() {
    # Método 1: Leer desde debian/changelog
    if [ -f "debian/changelog" ]; then
        VERSION=$(head -1 debian/changelog | grep -o '([^)]*)' | tr -d '()')
        echo "$VERSION"
        return
    fi
    
    # Método 2: Usar git tag si estamos en un repositorio git
    if [ -d ".git" ] && command -v git &> /dev/null; then
        VERSION=$(git describe --tags --exact-match 2>/dev/null || git describe --tags 2>/dev/null)
        if [ -n "$VERSION" ]; then
            echo "$VERSION"
            return
        fi
    fi
    
    # Método 3: Leer desde archivo VERSION si existe
    if [ -f "VERSION" ]; then
        VERSION=$(cat VERSION | tr -d '\n\r ')
        echo "$VERSION"
        return
    fi
    
    # Fallback: versión por defecto
    echo "1.0.0"
}

get_build_timestamp() {
    date +"%Y%m%d_%H%M%S"
}

get_git_hash() {
    if [ -d ".git" ] && command -v git &> /dev/null; then
        git rev-parse --short HEAD 2>/dev/null
    else
        echo "nogit"
    fi
}

# Función para generar nombre de paquete con versión dinámica
generate_package_name() {
    local app_name="floating-cheatsheets"
    local version=$(get_project_version)
    local timestamp=$(get_build_timestamp)
    local git_hash=$(get_git_hash)
    
    echo "${app_name}_${version}_${timestamp}_${git_hash}.deb"
}

# Función para generar nombre simple con solo versión
generate_simple_package_name() {
    local app_name="floating-cheatsheets"
    local version=$(get_project_version)
    
    echo "${app_name}_${version}_all.deb"
}

# Si se ejecuta directamente, mostrar información
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo "=== Información de versión del proyecto ==="
    echo "Versión del proyecto: $(get_project_version)"
    echo "Timestamp de build: $(get_build_timestamp)"
    echo "Git hash: $(get_git_hash)"
    echo ""
    echo "Nombres de paquete sugeridos:"
    echo "  Simple: $(generate_simple_package_name)"
    echo "  Completo: $(generate_package_name)"
fi