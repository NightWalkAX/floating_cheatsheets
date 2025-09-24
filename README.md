# 📝 Floating CheatSheets

Un widget flotante circular para acceso rápido a cheatsheets, con inicio automático del sistema.

## ✨ Características

- 🎯 **Widget circular flotante** ajustable y personalizable
- 📊 **Menú dial dinámico** con paginación automática
- 🏷️ **Organización por tags** para categorizar cheatsheets
- ✏️ **Editor integrado** con formato específico
- 💾 **Persistencia** - recuerda posición y configuración
- 🚀 **Inicio automático** con el sistema
- 📦 **Empaquetado .deb** para fácil instalación

## 🎮 Controles

- **Click izquierdo**: Abrir/cerrar menú dial
- **Arrastrar**: Mover widget
- **Click derecho**: Menú contextual (ajustar tamaño, salir)
- **Menú dial**: 
  - Botones circulares para cada cheatsheet
  - `+ Nueva`: Crear cheatsheet
  - `🏷️ Tags`: Filtrar por categoría
  - `◀ Ant` / `Sig ▶`: Navegación entre páginas

## 📄 Formato de CheatSheet

```
código/objeto - descripción
  ejemplo práctico
  
código2 - otra descripción
  ejemplo2
```

**Ejemplo:**
```
git status - Ver estado del repositorio
  git status --short

find . -name - Buscar archivos por nombre
  find . -name "*.py"
```

## 🚀 Instalación

### 📦 Descarga desde GitHub Releases

**La forma más fácil es descargar desde las releases:**

1. Ve a [Releases](https://github.com/your-username/floating_cheatsheets/releases/latest)
2. Descarga el archivo apropiado:
   - **Linux**: `floating-cheatsheets_1.0.0_all.deb`
   - **Windows**: `floating-cheatsheets-1.0.0-setup.exe`

### 🐧 Linux (Debian/Ubuntu)

```bash
# Descargar e instalar el paquete .deb
wget https://github.com/your-username/floating_cheatsheets/releases/latest/download/floating-cheatsheets_1.0.0_all.deb
sudo dpkg -i floating-cheatsheets_1.0.0_all.deb

# Si hay dependencias faltantes:
sudo apt-get install -f
```

### 🪟 Windows

1. Descarga `floating-cheatsheets-1.0.0-setup.exe`
2. Ejecuta el instalador y sigue las instrucciones
3. El programa se instalará y estará disponible en el menú de inicio

### 🔧 Compilar desde código fuente

#### Linux - Paquete .deb

```bash
# Construir el paquete
./build_deb.sh

# O construir todo (Linux + Windows)
./build_all.sh
```

#### Windows - Ejecutable

```bash
# En Windows o Linux con Wine
cd windows
./build_windows.sh

# Crear instalador (requiere NSIS)
makensis installer.nsi
```

### 🛠️ Instalación manual (desarrollo)

```bash
# Instalar dependencias
sudo apt-get install python3 python3-tk

# Ejecutar instalador
./setup/install.sh
```

## 🛠️ Desarrollo

```bash
# Instalar dependencias
sudo apt-get install python3 python3-tk

# Ejecutar desde código fuente
cd src/
python3 main.py
```

## 📁 Estructura del Proyecto

```
floating_cheatsheets/
├── src/                    # Código fuente
│   ├── main.py            # Widget principal
│   ├── cheatsheet_manager.py  # Gestión CRUD
│   └── ui_components.py   # Componentes UI
├── data/                  # Datos de ejemplo
├── debian/               # Empaquetado .deb
├── windows/              # Empaquetado Windows
│   ├── build_windows.spec # Configuración PyInstaller
│   ├── installer.nsi     # Script NSIS
│   └── build_windows.sh  # Script de construcción
├── .github/workflows/    # CI/CD automatizado
├── setup/               # Scripts de instalación
├── assets/             # Recursos (iconos, etc.)
├── build_all.sh        # Script de construcción completa
└── requirements.txt    # Dependencias Python
```

## 🗂️ Ubicación de Datos

Los datos se almacenan en:
- **Configuración**: `~/.local/share/floating-cheatsheets/config.json`
- **CheatSheets**: `~/.local/share/floating-cheatsheets/cheatsheets/`

## 🔧 Configuración

El archivo `config.json` contiene:
```json
{
  "window": {
    "x": 100, "y": 100, "size": 80,
    "always_on_top": true
  },
  "current_tag": "all",
  "data_path": "~/.local/share/floating-cheatsheets/cheatsheets"
}
```

## 🏷️ Tags Predefinidos

- `git` - Comandos de Git
- `linux` - Comandos de terminal Linux
- `python` - Código Python
- `docker` - Comandos Docker
- `bash` - Scripts Bash

## 🚫 Desinstalación

```bash
# Con paquete .deb
sudo dpkg -r floating-cheatsheets

# Manual
sudo rm -rf /usr/share/floating-cheatsheets
sudo rm /usr/bin/floating-cheatsheets
rm ~/.config/autostart/floating-cheatsheets.desktop
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 🤖 CI/CD Automatizado

El proyecto usa GitHub Actions para construir automáticamente ambas versiones:

- **Push a `main`** → Construye `.deb` y `.exe` → Crea release `latest`
- **Pull requests** → Ejecuta tests de construcción
- **Releases automáticos** con ambos formatos disponibles

## 📝 TODO

- [ ] Tema oscuro/claro
- [ ] Más formatos de exportación
- [ ] Sincronización en la nube
- [ ] Atajos de teclado
- [ ] Categorías anidadas
- [x] Soporte multiplataforma (Linux/Windows)
- [x] Automatización CI/CD

## 📄 Licencia

MIT License - Ve el archivo `LICENSE` para más detalles.