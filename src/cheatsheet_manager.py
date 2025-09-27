"""
CheatSheet Manager
Maneja las operaciones CRUD de las cheatsheets
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class CheatSheetManager:
    def __init__(self, data_path: str = None, default_language: str = None, languages_file: str = None):
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / 'data' / 'cheatsheets' if data_path is None else Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Cargar configuración de idiomas
        self.languages_file = languages_file or str(self.base_path / 'data' / 'languages.json')
        self._load_languages_config()
        
        # Establecer idioma predeterminado
        self.default_language = default_language or self.languages_config.get('default_language', 'es')

    def get_all_cheatsheets(self) -> List[Dict]:
        """Obtener todas las cheatsheets"""
        cheatsheets = []

        for file_path in self.data_path.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filename'] = file_path.stem
                    # Agregar idioma predeterminado si no existe
                    if 'language' not in data:
                        data['language'] = self.default_language
                    cheatsheets.append(data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading {file_path}: {e}")
                continue

        return sorted(cheatsheets, key=lambda x: x.get('updated', ''))

    def get_cheatsheet_by_filename(self, filename: str) -> Optional[Dict]:
        """Obtener una cheatsheet específica por nombre de archivo"""
        file_path = self.data_path / f"{filename}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['filename'] = filename
                # Agregar idioma predeterminado si no existe
                if 'language' not in data:
                    data['language'] = self.default_language
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def get_cheatsheets_by_tag(self, tag: str) -> List[Dict]:
        """Obtener cheatsheets filtradas por tag"""
        if tag == "all":
            return self.get_all_cheatsheets()

        all_sheets = self.get_all_cheatsheets()
        return [sheet for sheet in all_sheets if tag in sheet.get('tags', [])]

    def get_all_tags(self) -> List[str]:
        """Obtener todos los tags únicos"""
        all_sheets = self.get_all_cheatsheets()
        tags = set()

        for sheet in all_sheets:
            tags.update(sheet.get('tags', []))

        return sorted(list(tags))

    def create_cheatsheet(self, title: str, tags: List[str], items: List[Dict], language: str = None) -> str:
        """Crear una nueva cheatsheet"""
        # Generar filename desde el título
        filename = self._generate_filename(title)
        
        # Usar idioma predeterminado si no se especifica
        if language is None:
            language = self.default_language

        cheatsheet_data = {
            "title": title,
            "language": language,
            "tags": tags,
            "items": items,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "updated": datetime.now().strftime("%Y-%m-%d")
        }

        file_path = self.data_path / f"{filename}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cheatsheet_data, f, indent=2, ensure_ascii=False)

        return filename

    def update_cheatsheet(self, filename: str, title: str, tags: List[str], items: List[Dict], language: str = None) -> bool:
        """Actualizar una cheatsheet existente"""
        file_path = self.data_path / f"{filename}.json"

        if not file_path.exists():
            return False

        try:
            # Cargar datos existentes para preservar fecha de creación
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Usar idioma existente o predeterminado si no se especifica
            if language is None:
                language = existing_data.get('language', self.default_language)

            cheatsheet_data = {
                "title": title,
                "language": language,
                "tags": tags,
                "items": items,
                "created": existing_data.get("created", datetime.now().strftime("%Y-%m-%d")),
                "updated": datetime.now().strftime("%Y-%m-%d")
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cheatsheet_data, f, indent=2, ensure_ascii=False)

            return True

        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def delete_cheatsheet(self, filename: str) -> bool:
        """Eliminar una cheatsheet"""
        file_path = self.data_path / f"{filename}.json"

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except OSError:
            return False

    def _generate_filename(self, title: str) -> str:
        """Generar nombre de archivo válido desde el título"""
        # Convertir a minúsculas y reemplazar espacios y caracteres especiales
        filename = title.lower()
        filename = ''.join(c if c.isalnum() or c in '-_' else '-' for c in filename)
        filename = '-'.join(filter(None, filename.split('-')))  # Limpiar guiones múltiples

        # Asegurar que el filename sea único
        counter = 1
        original_filename = filename

        while (self.data_path / f"{filename}.json").exists():
            filename = f"{original_filename}-{counter}"
            counter += 1

        return filename

    def search_cheatsheets(self, query: str) -> List[Dict]:
        """Buscar cheatsheets por término"""
        query = query.lower()
        all_sheets = self.get_all_cheatsheets()
        results = []

        for sheet in all_sheets:
            # Buscar en título
            if query in sheet.get('title', '').lower():
                results.append(sheet)
                continue

            # Buscar en tags
            if any(query in tag.lower() for tag in sheet.get('tags', [])):
                results.append(sheet)
                continue

            # Buscar en items
            for item in sheet.get('items', []):
                if (query in item.get('code', '').lower() or 
                    query in item.get('description', '').lower() or 
                    query in item.get('example', '').lower()):
                    results.append(sheet)
                    break

        return results

    def validate_cheatsheet_data(self, title: str, tags: List[str], items: List[Dict], language: str = None) -> List[str]:
        """Validar datos de cheatsheet, retorna lista de errores"""
        errors = []

        if not title or not title.strip():
            errors.append("El título es requerido")

        if language and not self.validate_language(language):
            available_langs = ', '.join(self.get_supported_languages().keys())
            error_msg = self.get_interface_text('error_language_unsupported')
            errors.append(f"{error_msg}: {available_langs}")

        if not isinstance(tags, list):
            errors.append("Los tags deben ser una lista")

        if not isinstance(items, list) or len(items) == 0:
            errors.append("Debe haber al menos un item")

        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"Item {i+1}: debe ser un objeto")
                continue

            if not item.get('code', '').strip():
                errors.append(f"Item {i+1}: el código es requerido")

            if not item.get('description', '').strip():
                errors.append(f"Item {i+1}: la descripción es requerida")

        return errors

    def create_tag(self, tag_name: str) -> bool:
        """Crear un nuevo tag (realmente no necesita crear archivo, solo validar)"""
        if not tag_name or not tag_name.strip():
            return False

        # Normalizar el tag
        tag_name = tag_name.strip().lower()

        # Validar que no contenga caracteres especiales problemáticos
        if not tag_name.replace('-', '').replace('_', '').isalnum():
            return False

        return True

    def delete_tag(self, tag_name: str) -> bool:
        """Eliminar un tag de todas las cheatsheets que lo usen"""
        if not tag_name:
            return False

        modified_count = 0
        all_sheets = self.get_all_cheatsheets()

        for sheet in all_sheets:
            tags = sheet.get('tags', [])
            if tag_name in tags:
                # Remover el tag
                tags.remove(tag_name)

                # Actualizar la cheatsheet
                self.update_cheatsheet(
                    sheet['filename'],
                    sheet['title'],
                    tags,
                    sheet['items']
                )
                modified_count += 1

        return modified_count > 0

    def rename_tag(self, old_tag: str, new_tag: str) -> bool:
        """Renombrar un tag en todas las cheatsheets que lo usen"""
        if not old_tag or not new_tag:
            return False

        # Validar el nuevo tag
        if not self.create_tag(new_tag):
            return False

        new_tag = new_tag.strip().lower()
        modified_count = 0
        all_sheets = self.get_all_cheatsheets()

        for sheet in all_sheets:
            tags = sheet.get('tags', [])
            if old_tag in tags:
                # Reemplazar el tag
                tag_index = tags.index(old_tag)
                tags[tag_index] = new_tag
 
                # Actualizar la cheatsheet
                self.update_cheatsheet(
                    sheet['filename'],
                    sheet['title'],
                    tags,
                    sheet['items']
                )
                modified_count += 1

        return modified_count > 0

    def get_tag_usage_count(self, tag_name: str) -> int:
        """Obtener el número de cheatsheets que usan un tag específico"""
        all_sheets = self.get_all_cheatsheets()
        count = 0

        for sheet in all_sheets:
            if tag_name in sheet.get('tags', []):
                count += 1

        return count

    def get_tags_with_usage(self) -> List[Dict[str, any]]:
        """Obtener todos los tags con su conteo de uso"""
        tags = self.get_all_tags()
        tag_info = []

        for tag in tags:
            usage_count = self.get_tag_usage_count(tag)
            tag_info.append({
                'name': tag,
                'usage_count': usage_count
            })

        # Ordenar por uso descendente
        return sorted(tag_info, key=lambda x: x['usage_count'], reverse=True)

    def get_supported_languages(self) -> Dict[str, str]:
        """Obtener idiomas soportados"""
        return {code: info['name'] for code, info in self.languages_config.get('supported_languages', {}).items()}

    def get_available_languages(self) -> List[str]:
        """Obtener lista de códigos de idiomas disponibles en cheatsheets"""
        all_sheets = self.get_all_cheatsheets()
        languages = set()
        
        for sheet in all_sheets:
            languages.add(sheet.get('language', self.default_language))
        
        return sorted(list(languages))

    def get_cheatsheets_by_language(self, language: str) -> List[Dict]:
        """Obtener cheatsheets filtradas por idioma"""
        if not self.validate_language(language):
            return []
        
        all_sheets = self.get_all_cheatsheets()
        return [sheet for sheet in all_sheets 
                if sheet.get('language', self.default_language) == language]

    def get_cheatsheets_by_tag_and_language(self, tag: str, language: str) -> List[Dict]:
        """Obtener cheatsheets filtradas por tag e idioma"""
        if not self.validate_language(language):
            return []
        
        sheets_by_tag = self.get_cheatsheets_by_tag(tag)
        return [sheet for sheet in sheets_by_tag 
                if sheet.get('language', self.default_language) == language]

    def search_cheatsheets_by_language(self, query: str, language: str) -> List[Dict]:
        """Buscar cheatsheets por término en un idioma específico"""
        if not self.validate_language(language):
            return []
        
        all_results = self.search_cheatsheets(query)
        return [sheet for sheet in all_results 
                if sheet.get('language', self.default_language) == language]

    def get_language_statistics(self) -> Dict[str, Dict]:
        """Obtener estadísticas por idioma"""
        all_sheets = self.get_all_cheatsheets()
        stats = {}
        
        for lang_code, lang_info in self.languages_config.get('supported_languages', {}).items():
            sheets_count = len([s for s in all_sheets 
                              if s.get('language', self.default_language) == lang_code])
            stats[lang_code] = {
                'name': lang_info['name'],
                'flag': lang_info.get('flag', ''),
                'count': sheets_count
            }
        
        return stats

    def migrate_cheatsheets_language(self, from_language: str, to_language: str) -> int:
        """Migrar cheatsheets de un idioma a otro"""
        if (not self.validate_language(from_language) or 
            not self.validate_language(to_language)):
            return 0
        
        modified_count = 0
        sheets_to_migrate = self.get_cheatsheets_by_language(from_language)
        
        for sheet in sheets_to_migrate:
            success = self.update_cheatsheet(
                sheet['filename'],
                sheet['title'],
                sheet['tags'],
                sheet['items'],
                to_language
            )
            if success:
                modified_count += 1
        
        return modified_count

    def validate_language(self, language: str) -> bool:
        """Validar si un idioma es soportado"""
        return language in self.languages_config.get('supported_languages', {})

    def _load_languages_config(self) -> None:
        """Cargar configuración de idiomas desde archivo JSON"""
        try:
            with open(self.languages_file, 'r', encoding='utf-8') as f:
                self.languages_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading languages config from {self.languages_file}: {e}")
            # Configuración por defecto si falla la carga
            self.languages_config = {
                'default_language': 'es',
                'supported_languages': {
                    'es': {
                        'name': 'Español',
                        'flag': '🇪🇸',
                        'interface': {
                            'error_language_unsupported': 'Idioma no soportado. Idiomas disponibles'
                        }
                    },
                    'en': {
                        'name': 'English',
                        'flag': '🇺🇸',
                        'interface': {
                            'error_language_unsupported': 'Language not supported. Available languages'
                        }
                    }
                }
            }

    def reload_languages_config(self) -> bool:
        """Recargar configuración de idiomas desde archivo"""
        try:
            self._load_languages_config()
            return True
        except Exception as e:
            print(f"Error reloading languages config: {e}")
            return False

    def get_interface_text(self, key: str, language: str = None) -> str:
        """Obtener texto de interfaz en el idioma especificado"""
        if language is None:
            language = self.default_language
        
        lang_config = self.languages_config.get('supported_languages', {}).get(language, {})
        interface_texts = lang_config.get('interface', {})
        
        return interface_texts.get(key, key)

    def get_language_info(self, language: str) -> Dict:
        """Obtener información completa de un idioma"""
        return self.languages_config.get('supported_languages', {}).get(language, {})

    def add_language(self, code: str, name: str, flag: str = '', interface: Dict = None) -> bool:
        """Agregar un nuevo idioma a la configuración"""
        if interface is None:
            interface = {}
        
        new_language = {
            'name': name,
            'flag': flag,
            'interface': interface
        }
        
        self.languages_config.setdefault('supported_languages', {})[code] = new_language
        
        # Guardar cambios al archivo
        return self._save_languages_config()

    def remove_language(self, code: str) -> bool:
        """Eliminar un idioma de la configuración"""
        if code == self.default_language:
            return False  # No se puede eliminar el idioma predeterminado
        
        supported_languages = self.languages_config.get('supported_languages', {})
        if code in supported_languages:
            del supported_languages[code]
            return self._save_languages_config()
        
        return False

    def update_language_interface(self, code: str, interface_updates: Dict) -> bool:
        """Actualizar textos de interfaz de un idioma"""
        lang_config = self.languages_config.get('supported_languages', {}).get(code)
        if not lang_config:
            return False
        
        lang_config.setdefault('interface', {}).update(interface_updates)
        return self._save_languages_config()

    def _save_languages_config(self) -> bool:
        """Guardar configuración de idiomas al archivo"""
        try:
            with open(self.languages_file, 'w', encoding='utf-8') as f:
                json.dump(self.languages_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving languages config: {e}")
            return False

    def validate_languages_config(self) -> List[str]:
        """Validar la estructura de la configuración de idiomas"""
        errors = []
        
        if not isinstance(self.languages_config, dict):
            errors.append("La configuración debe ser un objeto JSON")
            return errors
        
        if 'supported_languages' not in self.languages_config:
            errors.append("Falta la clave 'supported_languages'")
        else:
            supported = self.languages_config['supported_languages']
            if not isinstance(supported, dict):
                errors.append("'supported_languages' debe ser un objeto")
            else:
                for code, info in supported.items():
                    if not isinstance(info, dict):
                        errors.append(f"Idioma '{code}': debe ser un objeto")
                        continue
                    
                    if 'name' not in info:
                        errors.append(f"Idioma '{code}': falta el campo 'name'")
                    
                    if 'interface' in info and not isinstance(info['interface'], dict):
                        errors.append(f"Idioma '{code}': 'interface' debe ser un objeto")
        
        default_lang = self.languages_config.get('default_language')
        if default_lang and default_lang not in self.languages_config.get('supported_languages', {}):
            errors.append(f"El idioma predeterminado '{default_lang}' no está en supported_languages")
        
        return errors


# Ejemplo de uso y testing
if __name__ == "__main__":
    manager = CheatSheetManager()
    
    # Mostrar idiomas soportados
    print("Idiomas soportados:")
    for code, name in manager.get_supported_languages().items():
        info = manager.get_language_info(code)
        flag = info.get('flag', '')
        print(f"  {code}: {name} {flag}")
    
    # Crear cheatsheet de ejemplo en español
    items_es = [
        {
            "code": "docker run",
            "description": "Ejecutar un contenedor",
            "example": "docker run -d -p 80:80 nginx"
        }
    ]
    
    filename_es = manager.create_cheatsheet(
        "Comandos Docker", 
        ["docker", "containers"], 
        items_es, 
        "es"
    )
    print(f"Created (ES): {filename_es}")
    
    # Crear cheatsheet de ejemplo en inglés
    items_en = [
        {
            "code": "docker run",
            "description": "Run a container",
            "example": "docker run -d -p 80:80 nginx"
        }
    ]
    
    filename_en = manager.create_cheatsheet(
        "Docker Commands", 
        ["docker", "containers"], 
        items_en, 
        "en"
    )
    print(f"Created (EN): {filename_en}")

    # Estadísticas por idioma
    stats = manager.get_language_statistics()
    print("Estadísticas por idioma:")
    for code, info in stats.items():
        print(f"  {info['name']} {info.get('flag', '')}: {info['count']} cheatsheets")

    # Listar cheatsheets por idioma
    es_sheets = manager.get_cheatsheets_by_language('es')
    print(f"Cheatsheets en español: {len(es_sheets)}")
    
    en_sheets = manager.get_cheatsheets_by_language('en')
    print(f"Cheatsheets in English: {len(en_sheets)}")

    # Obtener texto de interfaz
    error_msg_es = manager.get_interface_text('error_title_required', 'es')
    error_msg_en = manager.get_interface_text('error_title_required', 'en')
    print(f"Error message ES: {error_msg_es}")
    print(f"Error message EN: {error_msg_en}")
