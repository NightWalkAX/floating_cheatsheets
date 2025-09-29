# Release Notes

## v1.2.1 - Installation and Uninstallation Improvements (2025-09-29)

### 🔧 Critical Installation Improvements

- **Root Permission Installation**: Mandatory sudo permission validation for secure installation
- **Automatic Updater**: Automatic removal of previous installations before updating
- **Process Stopping**: Automatically stops the application before performing updates
- **Complete System Installation**: Includes documentation in `/usr/share/doc/floating-cheatsheets/`

### 📦 Enhanced Installation Files

- **Language Files Inclusion**: Automatic copying of `languages.json` and all necessary data
- **Multi-User Configuration**: Configures autostart for existing and current users
- **Complete File Structure**:
  - Executable: `/usr/bin/floating-cheatsheets`
  - Application: `/usr/share/floating-cheatsheets/`
  - Icon: `/usr/share/pixmaps/floating-cheatsheets.png`
  - Desktop: `/usr/share/applications/floating-cheatsheets.desktop`
  - Documentation: `/usr/share/doc/floating-cheatsheets/`

### 🗑️ Complete Uninstallation

- **Exhaustive Removal**: Uses `rm -rf` to completely remove all system files
- **Cache Cleanup**: Removes cache, logs, and temporary files
- **Registry Updates**: Improvements in `update-desktop-database` and `gtk-update-icon-cache`
- **Final Verification**: Checks that all files were removed correctly
- **Enhanced Feedback**: Shows which files are being removed in real-time

### 🛠️ Correcciones de Release Workflow

- **Prevención de Pérdida de Versiones**: No elimina releases anteriores automáticamente
- **Inclusión de Changelog**: Integra automáticamente el changelog en las release notes
- **Bump de Versión Automático**: Incrementa versión basada en archivo VERSION
- **Soporte para Branch Special**: Permite releases desde branch `special` además de `main`

## v1.2.0 - Sistema de Búsqueda Avanzada (2025-09-27)

### 🔍 Nuevas Características Principales

- **Sistema de Búsqueda Completo**: Nuevo módulo `search_components.py` con funcionalidad avanzada
- **Búsqueda desde Menú Contextual**: Opción "🔍 Buscar CheatSheets" en click derecho del widget
- **Búsqueda en TagManager**: Integración de búsqueda rápida y avanzada en gestión de cheatsheets
- **Filtros Avanzados**: Búsqueda por texto, etiquetas y lenguajes simultáneamente
- **Búsqueda en Tiempo Real**: Actualización instantánea de resultados mientras escribes

### 🛠️ Componentes Nuevos

- **SearchDialog**: Diálogo completo de búsqueda con filtros y resultados detallados
- **QuickSearchEntry**: Componente embebible para búsqueda rápida
- **Menús Contextuales Mejorados**: Integración de búsqueda en DialMenu

### 📊 Funcionalidades de Búsqueda

- **Búsqueda de Texto Libre**: Busca en títulos, descripciones y contenido
- **Filtrado por Etiquetas**: Selección múltiple de tags para filtrar resultados  
- **Filtrado por Idioma**: Búsqueda específica por idioma o en todos los idiomas
- **Resultados Detallados**: Vista completa con información de cada cheatsheet
- **Navegación Intuitiva**: Doble-click para seleccionar, botones de acción claros

### 🎨 Mejoras de Interfaz

- **Traducciones Completas**: Nuevas claves de traducción para funcionalidad de búsqueda
- **Integración Seamless**: Búsqueda integrada naturalmente en flujos de trabajo existentes
- **Feedback Visual**: Contadores de resultados y mensajes informativos
- **Búsqueda Contextual**: Mantiene filtros actuales como punto de partida

### 🔧 Mejoras Técnicas

- **Arquitectura Modular**: Código de búsqueda separado en módulo independiente
- **APIs Extendidas**: CheatSheetManager con nuevos métodos de búsqueda
- **Callbacks Configurables**: Sistema flexible para manejo de resultados
- **Compatibilidad Completa**: Funciona con sistema multiidioma existente

## v1.1.0 - Soporte Multiidioma (2025-09-27)

### 🌍 Nuevas Características Principales

- **Soporte Multiidioma Completo**: Interfaz localizada en Español, Inglés, Francés y Portugués
- **Filtrado por Idioma**: Nueva opción para filtrar cheatsheets por idioma específico  
- **Sistema de Configuración Expandible**: Gestión dinámica de idiomas desde archivo JSON
- **Migración Automática**: Script incluido para migrar cheatsheets existentes
- **UI Dinámicamente Localizada**: Textos de interfaz se actualizan automáticamente

### 🔧 Mejoras Técnicas

- **Nuevo Módulo i18n**: Sistema completo de internacionalización
- **Configuración Externa**: Los idiomas se gestionan desde `data/languages.json`
- **CheatSheets Multiidioma**: Campo `language` añadido a todos los cheatsheets
- **Callbacks de Actualización**: Sistema para actualizar UI dinámicamente

### 📊 CheatSheets Ampliados

- **Contenido Multiidioma**: Cheatsheets disponibles en 4 idiomas
- **Nuevas Traducciones**: Contenido localizado para cada idioma soportado
- **Formato Mejorado**: Estructura JSON actualizada con soporte de idioma

### 🎨 Mejoras de UI

- **Selector de Idioma**: Nuevo botón en el menú dial para cambiar idioma
- **Indicadores Visuales**: Banderas y nombres de idioma
- **Filtrado Inteligente**: Muestra solo cheatsheets del idioma seleccionado

## v1.0.0 - Primera Release (2025-09-24)

### 🎉 Nuevas Características

- **Widget Flotante Circular**: Interfaz flotante completamente funcional con menú dial dinámico
- **Sistema de CheatSheets**: Soporte completo para crear, editar y organizar cheatsheets
- **Organización por Tags**: Sistema de etiquetas para categorizar y filtrar cheatsheets
- **Editor Integrado**: Editor con sintaxis específica para crear cheatsheets fácilmente
- **Persistencia de Configuración**: Recuerda posición, tamaño y configuración entre sesiones
- **Inicio Automático**: Opción para iniciar automáticamente con el sistema
- **Paginación Automática**: Navegación inteligente cuando hay muchos cheatsheets

### 📦 CheatSheets Incluidos

Esta release incluye 7 cheatsheets listos para usar:

1. **Linux Commands** - Comandos esenciales de terminal
2. **Git Commands** - Control de versiones completo
3. **Python Básico** - Fundamentos de programación Python
4. **VS Code Shortcuts** - Atajos de productividad
5. **Docker Commands** - Gestión de contenedores
6. **HTML & CSS Básico** - Desarrollo web frontend
7. **NPM & Node.js** - Gestión de paquetes JavaScript

### 🛠️ Instalación

#### Linux (Ubuntu/Debian)
```bash
# Descargar el archivo .deb desde releases
sudo dpkg -i floating-cheatsheets_1.0.0_*.deb
sudo apt-get install -f  # Instalar dependencias si es necesario
```

#### Windows
```bash
# Descargar floating-cheatsheets-1.0.0-setup.exe desde releases
# Ejecutar el instalador y seguir las instrucciones
```

#### Desde Código Fuente
```bash
git clone https://github.com/usuario/floating_cheatsheets.git
cd floating_cheatsheets
./setup/install.sh  # Linux
# O usar build_all.sh para crear paquetes
```

### 🏗️ Sistema de Build

- **Build Dinámico**: Sistema de versionado automático que incluye timestamp y git hash
- **Multi-plataforma**: Soporte para Linux (.deb) y Windows (.exe)
- **Empaquetado Debian**: Configuración completa para crear paquetes .deb
- **Instalador NSIS**: Instalador profesional para Windows

### 🔧 Dependencias

- Python 3.6+
- tkinter (incluido con Python)
- Plataformas soportadas: Linux, Windows

### 🐛 Problemas Conocidos

- En algunos entornos Linux con temas oscuros, algunos elementos de UI pueden no contrastar correctamente
- El widget flotante puede no funcionar correctamente en algunos gestores de ventanas menos comunes

### 🚀 Próximas Características (Roadmap)

- Soporte para temas personalizados
- Importar/exportar cheatsheets
- Sincronización en la nube
- Más formatos de contenido (imágenes, enlaces)
- Búsqueda global en cheatsheets

### 🤝 Contribuir

Las contribuciones son bienvenidas! Consultar `DEVELOPMENT.md` para instrucciones de desarrollo.

### 📄 Licencia

MIT License - ver archivo `LICENSE` para detalles.

---

**Descarga**: [Releases en GitHub](https://github.com/usuario/floating_cheatsheets/releases/v1.0.0)