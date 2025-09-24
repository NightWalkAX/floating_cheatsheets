#!/bin/bash
# Script de instalación para Floating CheatSheets

set -e

echo "=== Instalando Floating CheatSheets ==="

# Crear directorios del sistema
sudo mkdir -p /usr/share/floating-cheatsheets
sudo mkdir -p /etc/floating-cheatsheets

# Copiar archivos de la aplicación
sudo cp -r src/* /usr/share/floating-cheatsheets/
sudo chmod +x /usr/share/floating-cheatsheets/main.py

# Crear script ejecutable en /usr/bin
sudo tee /usr/bin/floating-cheatsheets > /dev/null << 'EOF'
#!/bin/bash
cd /usr/share/floating-cheatsheets
python3 main.py
EOF

sudo chmod +x /usr/bin/floating-cheatsheets

# Instalar icono
if [ -f "assets/icon.png" ]; then
    sudo cp assets/icon.png /usr/share/pixmaps/floating-cheatsheets.png
fi

# Instalar archivo .desktop para autostart
mkdir -p ~/.config/autostart
cp setup/floating-cheatsheets.desktop ~/.config/autostart/

# Crear directorio de datos del usuario
mkdir -p ~/.local/share/floating-cheatsheets/cheatsheets

# Copiar datos de ejemplo si no existen
if [ ! -f ~/.local/share/floating-cheatsheets/config.json ]; then
    cp data/config.json ~/.local/share/floating-cheatsheets/
fi

if [ ! -f ~/.local/share/floating-cheatsheets/cheatsheets/git-commands.json ]; then
    cp data/cheatsheets/*.json ~/.local/share/floating-cheatsheets/cheatsheets/
fi

echo "=== Instalación completada ==="
echo "Floating CheatSheets se iniciará automáticamente en el próximo login."
echo "Para iniciarlo ahora, ejecute: floating-cheatsheets"