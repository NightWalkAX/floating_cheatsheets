#!/bin/bash
# Script de desinstalación para Floating CheatSheets

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

# Eliminar archivos del sistema usando los comandos mejorados
echo "Eliminando archivos del sistema..."

# Eliminar ejecutable principal
echo "  - Eliminando ejecutable..."
rm -rf /usr/bin/floating-cheatsheets >/dev/null 2>&1 || true

# Eliminar icono
echo "  - Eliminando icono..."
rm -rf /usr/share/pixmaps/floating-cheatsheets.png >/dev/null 2>&1 || true

# Eliminar archivo .desktop del sistema
echo "  - Eliminando archivo .desktop..."
rm -rf /usr/share/applications/floating-cheatsheets.desktop >/dev/null 2>&1 || true

# Eliminar directorio principal de la aplicación
echo "  - Eliminando aplicación..."
rm -rf /usr/share/floating-cheatsheets >/dev/null 2>&1 || true

# Eliminar documentación
echo "  - Eliminando documentación..."
rm -rf /usr/share/doc/floating-cheatsheets >/dev/null 2>&1 || true

# Eliminar archivos de configuración del sistema
echo "  - Eliminando configuración del sistema..."
rm -rf /etc/floating-cheatsheets >/dev/null 2>&1 || true

# Eliminar datos de usuario para todos los usuarios
echo "Eliminando datos de usuario..."
for home_dir in /home/*; do
    if [ -d "$home_dir" ]; then
        user_name=$(basename "$home_dir")
        echo "  - Limpiando datos para usuario: $user_name"
        
        # Eliminar datos de usuario (archivos de datos, configuración y autostart)
        rm -rf "$home_dir/.local/share/floating-cheatsheets" >/dev/null 2>&1 || true
        rm -rf "$home_dir/.config/floating-cheatsheets" >/dev/null 2>&1 || true
        rm -f "$home_dir/.config/autostart/floating-cheatsheets.desktop" >/dev/null 2>&1 || true
        
        # Limpiar archivos de cache específicos del usuario
        rm -rf "$home_dir/.cache/floating-cheatsheets" >/dev/null 2>&1 || true
    fi
done

# Limpiar datos de root
echo "Limpiando datos de root..."
rm -rf /root/.local/share/floating-cheatsheets >/dev/null 2>&1 || true
rm -rf /root/.config/floating-cheatsheets >/dev/null 2>&1 || true
rm -f /root/.config/autostart/floating-cheatsheets.desktop >/dev/null 2>&1 || true
rm -rf /root/.cache/floating-cheatsheets >/dev/null 2>&1 || true

# Forzar cierre de procesos restantes
remaining_processes=$(pgrep -f "floating-cheatsheets" 2>/dev/null || true)
if [ -n "$remaining_processes" ]; then
    echo "Forzando cierre de procesos restantes..."
    pkill -9 -f "floating-cheatsheets" >/dev/null 2>&1 || true
    pkill -9 -f "python.*floating-cheatsheets" >/dev/null 2>&1 || true
    pkill -9 -f "/usr/share/floating-cheatsheets" >/dev/null 2>&1 || true
    pkill -9 -f "main.py.*floating" >/dev/null 2>&1 || true
fi

# Actualizar registros del sistema usando los comandos mejorados
echo "Actualizando registros del sistema..."

# Actualizar base de datos de aplicaciones
echo "  - Actualizando base de datos de aplicaciones..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications/ >/dev/null 2>&1 || echo "    Base de datos actualizada"
else
    update-desktop-database >/dev/null 2>&1 || echo "    Base de datos actualizada"
fi

# Actualizar cache de iconos
echo "  - Actualizando cache de iconos..."
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/pixmaps/ >/dev/null 2>&1 || echo "    Cache de iconos actualizado"
    # También intentar actualizar otros directorios comunes de iconos
    gtk-update-icon-cache /usr/share/icons/hicolor/ >/dev/null 2>&1 || true
fi

# Actualizar menús del sistema
echo "  - Actualizando menús del sistema..."
if command -v update-menus >/dev/null 2>&1; then
    update-menus >/dev/null 2>&1 || true
fi

# Limpiar archivos temporales y logs
echo "Limpiando archivos temporales y logs..."
rm -f /tmp/*floating-cheatsheets* >/dev/null 2>&1 || true
rm -f /tmp/.*floating-cheatsheets* >/dev/null 2>&1 || true
rm -f /var/log/*floating-cheatsheets* >/dev/null 2>&1 || true
rm -rf /var/cache/*floating-cheatsheets* >/dev/null 2>&1 || true

# Limpiar posibles archivos de systemd (si se usaran en el futuro)
rm -f /etc/systemd/system/*floating-cheatsheets* >/dev/null 2>&1 || true
rm -f /etc/systemd/user/*floating-cheatsheets* >/dev/null 2>&1 || true

# Verificación final
echo "Verificando eliminación completa..."
if [ -f "/usr/bin/floating-cheatsheets" ] || [ -d "/usr/share/floating-cheatsheets" ]; then
    echo "ADVERTENCIA: Algunos archivos no pudieron ser eliminados completamente."
    echo "Es posible que necesites reiniciar el sistema para completar la desinstalación."
else
    echo "✓ Verificación completada: Todos los archivos del sistema fueron eliminados."
fi

echo ""
echo "=== Desinstalación completada ==="
echo "Floating CheatSheets ha sido completamente eliminado del sistema."
echo ""
echo "Archivos eliminados:"
echo "  - /usr/bin/floating-cheatsheets"
echo "  - /usr/share/floating-cheatsheets/"
echo "  - /usr/share/pixmaps/floating-cheatsheets.png"
echo "  - /usr/share/applications/floating-cheatsheets.desktop"
echo "  - /usr/share/doc/floating-cheatsheets/"
echo "  - /etc/floating-cheatsheets/"
echo "  - Datos de usuario en todos los directorios home/"
echo ""
echo "Se han actualizado los registros del sistema (aplicaciones, iconos, menús)."