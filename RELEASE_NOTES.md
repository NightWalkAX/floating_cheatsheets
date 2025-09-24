# Release Notes

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