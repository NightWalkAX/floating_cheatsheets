#!/usr/bin/env python3
"""
Script para migrar cheatsheets existentes y agregar el campo de idioma
"""

import sys
from pathlib import Path

# Agregar el directorio src al path para importar CheatSheetManager
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from cheatsheet_manager import CheatSheetManager


def migrate_existing_cheatsheets():
    """Migrar cheatsheets existentes para agregar campo de idioma"""
    manager = CheatSheetManager()
    
    print("🔄 Iniciando migración de cheatsheets existentes...")
    
    # Obtener todas las cheatsheets
    all_sheets = manager.get_all_cheatsheets()
    updated_count = 0
    
    for sheet in all_sheets:
        # Si la cheatsheet no tiene campo de idioma, agregarlo
        if 'language' not in sheet or not sheet['language']:
            print(f"📝 Actualizando: {sheet['title']}")
            
            # Determinar idioma basado en contenido (heurística simple)
            language = detect_language_from_content(sheet)
            
            # Actualizar la cheatsheet
            success = manager.update_cheatsheet(
                sheet['filename'],
                sheet['title'],
                sheet['tags'],
                sheet['items'],
                language
            )
            
            if success:
                updated_count += 1
                print(f"  ✅ Actualizada a idioma: {language}")
            else:
                print(f"  ❌ Error al actualizar")
    
    print(f"\n✨ Migración completada: {updated_count} cheatsheets actualizadas")
    
    # Mostrar estadísticas finales
    stats = manager.get_language_statistics()
    print("\n📊 Estadísticas por idioma:")
    for code, info in stats.items():
        if info['count'] > 0:
            print(f"  {info['name']} {info.get('flag', '')}: {info['count']} cheatsheets")


def detect_language_from_content(sheet):
    """Detectar idioma basado en el contenido de la cheatsheet"""
    title = sheet.get('title', '').lower()
    
    # Palabras clave en español
    spanish_words = ['básico', 'avanzado', 'comandos', 'fórmulas', 'intermedio']
    
    # Buscar en título
    for word in spanish_words:
        if word in title:
            return 'es'
    
    # Si contiene caracteres especiales del español
    if any(char in title for char in 'ñáéíóúü'):
        return 'es'
    
    # Por defecto, inglés
    return 'en'


def show_language_management_examples():
    """Mostrar ejemplos de gestión de idiomas"""
    manager = CheatSheetManager()
    
    print("\n🌍 Ejemplos de gestión de idiomas:")
    
    # 1. Obtener idiomas soportados
    print("\n1. Idiomas soportados:")
    for code, name in manager.get_supported_languages().items():
        info = manager.get_language_info(code)
        flag = info.get('flag', '')
        print(f"   {code}: {name} {flag}")
    
    # 2. Filtrar por idioma
    print("\n2. Cheatsheets en español:")
    es_sheets = manager.get_cheatsheets_by_language('es')
    for sheet in es_sheets[:3]:  # Mostrar solo las primeras 3
        print(f"   • {sheet['title']}")
    print(f"   ... y {len(es_sheets) - 3} más" if len(es_sheets) > 3 else "")
    
    # 3. Filtrar por tag e idioma
    print("\n3. Cheatsheets de Python en español:")
    python_es = manager.get_cheatsheets_by_tag_and_language('python', 'es')
    for sheet in python_es:
        print(f"   • {sheet['title']}")
    
    # 4. Buscar en idioma específico
    print("\n4. Buscar 'docker' en inglés:")
    docker_en = manager.search_cheatsheets_by_language('docker', 'en')
    for sheet in docker_en:
        print(f"   • {sheet['title']}")
    
    # 5. Obtener texto de interfaz
    print("\n5. Textos de interfaz:")
    for lang in ['es', 'en']:
        title_text = manager.get_interface_text('title', lang)
        search_text = manager.get_interface_text('search', lang)
        print(f"   {lang}: {title_text} | {search_text}")


def validate_configuration():
    """Validar configuración de idiomas"""
    manager = CheatSheetManager()
    
    print("\n🔍 Validando configuración de idiomas...")
    
    errors = manager.validate_languages_config()
    if errors:
        print("❌ Errores encontrados:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("✅ Configuración válida")
    
    # Mostrar información de configuración
    print(f"\n📄 Archivo de configuración: {manager.languages_file}")
    print(f"🌐 Idioma predeterminado: {manager.default_language}")


if __name__ == "__main__":
    print("🚀 Script de migración y gestión de idiomas")
    print("=" * 50)
    
    # Validar configuración
    validate_configuration()
    
    # Migrar cheatsheets existentes
    migrate_existing_cheatsheets()
    
    # Mostrar ejemplos de uso
    show_language_management_examples()
    
    print("\n🎉 ¡Migración y ejemplos completados!")