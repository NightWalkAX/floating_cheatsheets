#!/bin/bash
# Script de instalación/actualización para Floating CheatSheets

set -e

echo "=== Instalando/Actualizando Floating CheatSheets ==="

# Verificar si se ejecuta como root para operaciones del sistema
if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse como root (sudo ./install.sh)"
    exit 1
fi

# Detener la aplicación si está corriendo
echo "Deteniendo aplicación si está ejecutándose..."
pkill -f "floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "main.py.*floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "/usr/share/floating-cheatsheets/main.py" >/dev/null 2>&1 || true
pkill -f "/usr/bin/floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "python.*floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "python3.*floating-cheatsheets" >/dev/null 2>&1 || true

sleep 2

# Limpiar instalación previa si existe (forzar actualización)
echo "Limpiando instalación previa..."
rm -rf /usr/share/floating-cheatsheets >/dev/null 2>&1 || true
rm -f /usr/bin/floating-cheatsheets >/dev/null 2>&1 || true
rm -f /usr/share/pixmaps/floating-cheatsheets.png >/dev/null 2>&1 || true
rm -f /usr/share/applications/floating-cheatsheets.desktop >/dev/null 2>&1 || true
rm -rf /usr/share/doc/floating-cheatsheets >/dev/null 2>&1 || true

# Crear directorios del sistema
echo "Creando directorios del sistema..."
mkdir -p /usr/share/floating-cheatsheets
mkdir -p /usr/share/doc/floating-cheatsheets
mkdir -p /etc/floating-cheatsheets

# Copiar archivos de la aplicación
echo "Copiando archivos de la aplicación..."
cp -r src/* /usr/share/floating-cheatsheets/
chmod +x /usr/share/floating-cheatsheets/main.py

# Copiar datos del sistema (archivos de idioma y configuración)
echo "Copiando archivos de datos y idiomas..."
cp -r data/* /usr/share/floating-cheatsheets/
chmod -R 644 /usr/share/floating-cheatsheets/data/ >/dev/null 2>&1 || true

# Crear script ejecutable en /usr/bin
echo "Creando script ejecutable..."
tee /usr/bin/floating-cheatsheets > /dev/null << 'EOF'
#!/bin/bash
cd /usr/share/floating-cheatsheets
python3 main.py "$@"
EOF

chmod +x /usr/bin/floating-cheatsheets

# Instalar icono
echo "Instalando icono..."
if [ -f "assets/icon.png" ]; then
    cp assets/icon.png /usr/share/pixmaps/floating-cheatsheets.png
    chmod 644 /usr/share/pixmaps/floating-cheatsheets.png
fi

# Instalar archivo .desktop del sistema
echo "Instalando archivo .desktop..."
if [ -f "setup/floating-cheatsheets.desktop" ]; then
    cp setup/floating-cheatsheets.desktop /usr/share/applications/
    chmod 644 /usr/share/applications/floating-cheatsheets.desktop
fi

# Copiar documentación
echo "Instalando documentación..."
[ -f "README.md" ] && cp README.md /usr/share/doc/floating-cheatsheets/
[ -f "LICENSE" ] && cp LICENSE /usr/share/doc/floating-cheatsheets/
[ -f "VERSION" ] && cp VERSION /usr/share/doc/floating-cheatsheets/

# Configurar para cada usuario existente
echo "Configurando para usuarios existentes..."
for home_dir in /home/*; do
    if [ -d "$home_dir" ]; then
        user_name=$(basename "$home_dir")
        echo "Configurando para usuario: $user_name"
        
        # Crear directorio de autostart para el usuario
        sudo -u "$user_name" mkdir -p "$home_dir/.config/autostart" 2>/dev/null || true
        
        # Copiar archivo .desktop para autostart
        if [ -f "setup/floating-cheatsheets.desktop" ]; then
            sudo -u "$user_name" cp setup/floating-cheatsheets.desktop "$home_dir/.config/autostart/" 2>/dev/null || true
        fi
        
        # Crear directorio de datos del usuario
        sudo -u "$user_name" mkdir -p "$home_dir/.local/share/floating-cheatsheets/cheatsheets" 2>/dev/null || true
        
        # Copiar archivos de configuración y datos si no existen
        if [ ! -f "$home_dir/.local/share/floating-cheatsheets/config.json" ]; then
            sudo -u "$user_name" cp data/config.json "$home_dir/.local/share/floating-cheatsheets/" 2>/dev/null || true
        fi
        
        if [ ! -f "$home_dir/.local/share/floating-cheatsheets/languages.json" ]; then
            sudo -u "$user_name" cp data/languages.json "$home_dir/.local/share/floating-cheatsheets/" 2>/dev/null || true
        fi
        
        # Copiar cheatsheets de ejemplo si el directorio está vacío
        if [ -z "$(ls -A "$home_dir/.local/share/floating-cheatsheets/cheatsheets/" 2>/dev/null)" ]; then
            sudo -u "$user_name" cp data/cheatsheets/*.json "$home_dir/.local/share/floating-cheatsheets/cheatsheets/" 2>/dev/null || true
        fi
        
        # Ajustar permisos
        chown -R "$user_name":"$user_name" "$home_dir/.local/share/floating-cheatsheets" 2>/dev/null || true
        chown -R "$user_name":"$user_name" "$home_dir/.config/autostart/floating-cheatsheets.desktop" 2>/dev/null || true
    fi
done

# Actualizar registros del sistema
echo "Actualizando registros del sistema..."
update-desktop-database /usr/share/applications/ >/dev/null 2>&1 || echo "Base de datos de aplicaciones actualizada"
gtk-update-icon-cache -f -t /usr/share/pixmaps/ >/dev/null 2>&1 || echo "Cache de iconos actualizado"
update-menus >/dev/null 2>&1 || true

# Configurar para el usuario actual (si no es root)
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    CURRENT_USER_HOME=$(eval echo ~$SUDO_USER)
    echo "Configurando para el usuario actual: $SUDO_USER"
    
    sudo -u "$SUDO_USER" mkdir -p "$CURRENT_USER_HOME/.config/autostart" 2>/dev/null || true
    sudo -u "$SUDO_USER" mkdir -p "$CURRENT_USER_HOME/.local/share/floating-cheatsheets/cheatsheets" 2>/dev/null || true
    
    if [ -f "setup/floating-cheatsheets.desktop" ]; then
        sudo -u "$SUDO_USER" cp setup/floating-cheatsheets.desktop "$CURRENT_USER_HOME/.config/autostart/" 2>/dev/null || true
    fi
    
    if [ ! -f "$CURRENT_USER_HOME/.local/share/floating-cheatsheets/config.json" ]; then
        sudo -u "$SUDO_USER" cp data/config.json "$CURRENT_USER_HOME/.local/share/floating-cheatsheets/" 2>/dev/null || true
    fi
    
    if [ ! -f "$CURRENT_USER_HOME/.local/share/floating-cheatsheets/languages.json" ]; then
        sudo -u "$SUDO_USER" cp data/languages.json "$CURRENT_USER_HOME/.local/share/floating-cheatsheets/" 2>/dev/null || true
    fi
    
    if [ -z "$(ls -A "$CURRENT_USER_HOME/.local/share/floating-cheatsheets/cheatsheets/" 2>/dev/null)" ]; then
        sudo -u "$SUDO_USER" cp data/cheatsheets/*.json "$CURRENT_USER_HOME/.local/share/floating-cheatsheets/cheatsheets/" 2>/dev/null || true
    fi
    
    chown -R "$SUDO_USER":"$SUDO_USER" "$CURRENT_USER_HOME/.local/share/floating-cheatsheets" 2>/dev/null || true
    chown "$SUDO_USER":"$SUDO_USER" "$CURRENT_USER_HOME/.config/autostart/floating-cheatsheets.desktop" 2>/dev/null || true
fi

echo "=== Instalación/Actualización completada ==="
echo "Floating CheatSheets se iniciará automáticamente en el próximo login."
echo "Para iniciarlo ahora, ejecute: floating-cheatsheets"
echo ""
echo "Archivos instalados:"
echo "  - Ejecutable: /usr/bin/floating-cheatsheets"
echo "  - Aplicación: /usr/share/floating-cheatsheets/"
echo "  - Icono: /usr/share/pixmaps/floating-cheatsheets.png"
echo "  - Desktop: /usr/share/applications/floating-cheatsheets.desktop"
echo "  - Documentación: /usr/share/doc/floating-cheatsheets/"