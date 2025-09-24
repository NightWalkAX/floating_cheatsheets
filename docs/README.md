# GitHub Pages - Floating CheatSheets

Esta carpeta contiene la página web de GitHub Pages para el proyecto Floating CheatSheets.

## 🚀 Configuración de GitHub Pages

1. Ve a tu repositorio en GitHub
2. Navega a **Settings** > **Pages**
3. En **Source**, selecciona **GitHub Actions**
4. La página se desplegará automáticamente en: `https://nightwalkaex.github.io/floating_cheatsheets/`

## 🔄 Sincronización Automática de Versión

La versión se sincroniza automáticamente desde el archivo `VERSION` en la raíz del proyecto:

- **Manual**: Ejecuta `./docs/sync-version.sh`
- **Automático**: Se ejecuta automáticamente cuando se actualiza `VERSION` mediante GitHub Actions

## 📁 Estructura

```
docs/
├── index.html          # Página principal
├── styles.css          # Estilos CSS
├── script.js          # JavaScript interactivo
├── version.json       # Versión dinámica (auto-generado)
├── sync-version.sh    # Script de sincronización
└── README.md          # Este archivo
```

## 🛠️ Desarrollo Local

Para probar la página localmente:

```bash
# Opción 1: Servidor HTTP simple con Python
cd docs
python3 -m http.server 8000

# Opción 2: Servidor HTTP con Node.js
npx http-server docs -p 8000

# Opción 3: Live Server (VS Code extension)
# Abre index.html y usa "Go Live"
```

Luego visita: `http://localhost:8000`

## 🎨 Personalización

### Cambiar información del repositorio
Edita las variables en `script.js`:

```javascript
const CONFIG = {
    githubUser: 'TU_USUARIO',
    repoName: 'TU_REPOSITORIO',
    version: null // Se carga dinámicamente
};
```

### Actualizar versión
1. Cambia la versión en el archivo `VERSION` en la raíz
2. Ejecuta `./docs/sync-version.sh` (o déjalo automático)
3. La página se actualizará automáticamente

## ✨ Características

- 📱 **Responsive**: Funciona en móviles y escritorio
- 🎯 **Detección de SO**: Destaca la descarga apropiada
- 📋 **Copiar código**: Botones para copiar comandos
- 🔄 **Versión dinámica**: Se actualiza automáticamente
- ⚡ **Animaciones**: Efectos suaves y modernos
- 🎨 **Diseño moderno**: Gradientes y efectos visuales

## 🔧 Troubleshooting

### La versión no se actualiza
1. Verifica que `version.json` existe y tiene el formato correcto
2. Ejecuta manualmente: `./docs/sync-version.sh`
3. Revisa que el archivo `VERSION` contiene la versión correcta

### GitHub Pages no se despliega
1. Verifica que GitHub Actions está habilitado
2. Revisa los logs en la pestaña **Actions**
3. Asegúrate de que la rama principal es `main` o `master`

### Los enlaces de descarga no funcionan
1. Verifica que las releases existen en GitHub
2. Asegúrate de que los nombres de archivos coinciden
3. Revisa que `CONFIG.githubUser` y `CONFIG.repoName` son correctos