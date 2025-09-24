#!/bin/bash
# Script de desinstalación para Floating CheatSheets (instalación manual)

set -e

echo "=== Desinstalando Floating CheatSheets ==="

# Verificar si se ejecuta como root para poder eliminar archivos del sistema
if [ "$EUID" -ne 0 ]; then
    echo "Este script debe ejecutarse como root (sudo ./uninstall.sh)"
    exit 1
fi

# Detener la aplicación si está corriendo
echo "Deteniendo aplicación..."
pkill -f "floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "main.py.*floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "/usr/share/floating-cheatsheets/main.py" >/dev/null 2>&1 || true
pkill -f "/usr/bin/floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "python.*floating-cheatsheets" >/dev/null 2>&1 || true
pkill -f "python3.*floating-cheatsheets" >/dev/null 2>&1 || true

sleep 2

# Eliminar archivos del sistema
echo "Eliminando archivos del sistema..."
rm -rf /usr/share/floating-cheatsheets/ || true
rm -f /usr/bin/floating-cheatsheets || true
rm -f /usr/share/pixmaps/floating-cheatsheets.png || true
rm -f /usr/share/applications/floating-cheatsheets.desktop || true
rm -rf /etc/floating-cheatsheets/ || true

# Eliminar datos de usuario para todos los usuarios
echo "Eliminando datos de usuario..."
for home_dir in /home/*; do
    if [ -d "$home_dir" ]; then
        user_name=$(basename "$home_dir")
        echo "Limpiando datos para usuario: $user_name"
        
        # Eliminar datos de usuario
        rm -rf "$home_dir/.local/share/floating-cheatsheets" >/dev/null 2>&1 || true
        rm -rf "$home_dir/.config/floating-cheatsheets" >/dev/null 2>&1 || true
        rm -f "$home_dir/.config/autostart/floating-cheatsheets.desktop" >/dev/null 2>&1 || true
    fi
done

# Limpiar datos de root
echo "Limpiando datos de root..."
rm -rf /root/.local/share/floating-cheatsheets >/dev/null 2>&1 || true
rm -rf /root/.config/floating-cheatsheets >/dev/null 2>&1 || true
rm -f /root/.config/autostart/floating-cheatsheets.desktop >/dev/null 2>&1 || true

# Forzar cierre de procesos restantes
remaining_processes=$(pgrep -f "floating-cheatsheets" 2>/dev/null || true)
if [ -n "$remaining_processes" ]; then
    echo "Forzando cierre de procesos restantes..."
    pkill -9 -f "floating-cheatsheets" >/dev/null 2>&1 || true
    pkill -9 -f "python.*floating-cheatsheets" >/dev/null 2>&1 || true
    pkill -9 -f "/usr/share/floating-cheatsheets" >/dev/null 2>&1 || true
fi

# Actualizar registros del sistema
echo "Actualizando registros del sistema..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications/ >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/pixmaps/ >/dev/null 2>&1 || true
fi

if command -v update-menus >/dev/null 2>&1; then
    update-menus >/dev/null 2>&1 || true
fi

# Limpiar archivos temporales
rm -f /tmp/*floating-cheatsheets* >/dev/null 2>&1 || true
rm -f /tmp/.*floating-cheatsheets* >/dev/null 2>&1 || true
rm -f /var/log/*floating-cheatsheets* >/dev/null 2>&1 || true

echo "=== Desinstalación completada ==="
echo "Floating CheatSheets ha sido completamente eliminado del sistema."