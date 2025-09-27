# Sistema de Idiomas - CheatSheet Manager

Este documento describe las nuevas funcionalidades de soporte multiidioma implementadas en el CheatSheet Manager.

## 📋 Características

- ✅ **Soporte multiidioma**: Español, Inglés, Francés y Portugués (expandible)
- ✅ **Configuración externa**: Los idiomas se cargan desde un archivo JSON
- ✅ **Filtrado por idioma**: Buscar y filtrar cheatsheets por idioma específico
- ✅ **Interfaz localizada**: Textos de interfaz traducidos para cada idioma
- ✅ **Migración automática**: Script para migrar cheatsheets existentes
- ✅ **Gestión dinámica**: Agregar/eliminar idiomas sin modificar código

## 🗂️ Estructura de Archivos

```
data/
├── languages.json          # Configuración de idiomas e interfaz
├── cheatsheets/            # Archivos de cheatsheets
│   ├── python-basic.json   # Con campo "language": "es"
│   └── ...
└── config.json
```

## 🌍 Configuración de Idiomas

El archivo `data/languages.json` contiene:

```json
{
  "default_language": "es",
  "supported_languages": {
    "es": {
      "name": "Español",
      "flag": "🇪🇸",
      "interface": {
        "title": "Título",
        "search": "Buscar",
        "create": "Crear",
        "edit": "Editar",
        "delete": "Eliminar",
        "error_title_required": "El título es requerido"
      }
    },
    "en": {
      "name": "English",
      "flag": "🇺🇸",
      "interface": {
        "title": "Title",
        "search": "Search",
        "create": "Create",
        "edit": "Edit",
        "delete": "Delete",
        "error_title_required": "Title is required"
      }
    }
  }
}
```

## 📝 Formato de CheatSheets

Los archivos JSON de cheatsheets ahora incluyen el campo `language`:

```json
{
  "title": "Python Básico",
  "language": "es",
  "tags": ["python", "programming", "básico"],
  "items": [
    {
      "code": "print()",
      "description": "Imprimir en consola",
      "example": "print(\"Hola mundo\")"
    }
  ],
  "created": "2024-01-01",
  "updated": "2024-01-02"
}
```

## 🚀 Uso del API

### Crear CheatSheet con Idioma

```python
from cheatsheet_manager import CheatSheetManager

manager = CheatSheetManager()

# Crear en español (predeterminado)
items = [{"code": "ls", "description": "Listar archivos", "example": "ls -la"}]
filename = manager.create_cheatsheet("Comandos Linux", ["linux"], items, "es")

# Crear en inglés
items = [{"code": "ls", "description": "List files", "example": "ls -la"}]
filename = manager.create_cheatsheet("Linux Commands", ["linux"], items, "en")
```

### Filtrar por Idioma

```python
# Obtener cheatsheets en español
es_sheets = manager.get_cheatsheets_by_language('es')

# Obtener cheatsheets de Python en inglés
python_en = manager.get_cheatsheets_by_tag_and_language('python', 'en')

# Buscar "docker" solo en inglés
docker_results = manager.search_cheatsheets_by_language('docker', 'en')
```

### Gestión de Idiomas

```python
# Obtener idiomas soportados
languages = manager.get_supported_languages()
# {'es': 'Español', 'en': 'English', 'fr': 'Français', 'pt': 'Português'}

# Estadísticas por idioma
stats = manager.get_language_statistics()
# {'es': {'name': 'Español', 'flag': '🇪🇸', 'count': 15}, ...}

# Obtener texto de interfaz
title_es = manager.get_interface_text('title', 'es')  # "Título"
title_en = manager.get_interface_text('title', 'en')  # "Title"
```

### Validación de Idiomas

```python
# Validar si un idioma es soportado
is_valid = manager.validate_language('es')  # True
is_valid = manager.validate_language('de')  # False

# Validar datos de cheatsheet con idioma
errors = manager.validate_cheatsheet_data(
    title="Test",
    tags=["test"],
    items=[{"code": "test", "description": "test"}],
    language="es"
)
```

## 🔧 Métodos Nuevos

### Gestión de Idiomas
- `get_supported_languages()` - Obtener idiomas soportados
- `get_available_languages()` - Idiomas con cheatsheets existentes
- `get_language_info(code)` - Información completa de un idioma
- `validate_language(code)` - Validar código de idioma

### Filtrado y Búsqueda
- `get_cheatsheets_by_language(language)` - Filtrar por idioma
- `get_cheatsheets_by_tag_and_language(tag, language)` - Filtrar por tag e idioma
- `search_cheatsheets_by_language(query, language)` - Buscar en idioma específico

### Estadísticas
- `get_language_statistics()` - Estadísticas por idioma
- `migrate_cheatsheets_language(from, to)` - Migrar entre idiomas

### Interfaz y Configuración
- `get_interface_text(key, language)` - Obtener texto localizado
- `reload_languages_config()` - Recargar configuración
- `validate_languages_config()` - Validar estructura de configuración

### Gestión Dinámica
- `add_language(code, name, flag, interface)` - Agregar idioma
- `remove_language(code)` - Eliminar idioma
- `update_language_interface(code, updates)` - Actualizar textos

## 🔄 Migración de CheatSheets Existentes

Para migrar cheatsheets existentes:

```bash
python migrate_languages.py
```

Este script:
1. ✅ Valida la configuración de idiomas
2. 🔄 Detecta cheatsheets sin campo `language`
3. 🤖 Determina el idioma automáticamente (heurística)
4. 💾 Actualiza los archivos JSON
5. 📊 Muestra estadísticas finales

## 🌟 Agregar Nuevos Idiomas

Para agregar un nuevo idioma sin programar:

1. **Editar `data/languages.json`**:
```json
{
  "supported_languages": {
    "de": {
      "name": "Deutsch",
      "flag": "🇩🇪",
      "interface": {
        "title": "Titel",
        "search": "Suchen",
        "create": "Erstellen",
        "edit": "Bearbeiten",
        "delete": "Löschen",
        "error_title_required": "Titel ist erforderlich"
      }
    }
  }
}
```

2. **Recargar configuración**:
```python
manager.reload_languages_config()
```

## 🎯 Casos de Uso

### Aplicación Multiidioma
```python
# Configurar idioma de la aplicación
app_language = 'en'
manager = CheatSheetManager(default_language=app_language)

# Mostrar solo cheatsheets del idioma actual
current_sheets = manager.get_cheatsheets_by_language(app_language)

# Obtener textos localizados para la UI
ui_texts = {
    'title': manager.get_interface_text('title', app_language),
    'search': manager.get_interface_text('search', app_language),
    'create': manager.get_interface_text('create', app_language)
}
```

### Sistema de Filtros Avanzado
```python
def filter_cheatsheets(tag=None, language=None, query=None):
    if query and language:
        return manager.search_cheatsheets_by_language(query, language)
    elif tag and language:
        return manager.get_cheatsheets_by_tag_and_language(tag, language)
    elif language:
        return manager.get_cheatsheets_by_language(language)
    elif tag:
        return manager.get_cheatsheets_by_tag(tag)
    else:
        return manager.get_all_cheatsheets()
```

## 🚨 Consideraciones Importantes

1. **Retrocompatibilidad**: CheatSheets sin campo `language` usan el idioma predeterminado
2. **Validación**: Los métodos CRUD validan automáticamente los códigos de idioma
3. **Fallback**: Si falla la carga de idiomas, se usa configuración mínima hardcodeada
4. **Encoding**: Todos los archivos usan UTF-8 para soporte completo de caracteres especiales

## 📈 Mejoras Futuras

- [ ] Detección automática de idioma por contenido (IA)
- [ ] Importación masiva de traducciones
- [ ] Cache de configuración de idiomas
- [ ] API REST para gestión de idiomas
- [ ] Interfaz web para edición de traducciones