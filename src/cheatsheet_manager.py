"""
CheatSheet Manager
Handles CRUD operations for cheatsheets
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class CheatSheetManager:
    """Class to manage cheatsheets"""
    def __init__(
            self,
            data_path: str = None,
            default_language: str = None,
            languages_file: str = None
            ):
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / 'data' / 'cheatsheets' if data_path is None else Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Load languages configuration
        self.languages_file = languages_file or str(self.base_path / 'data' / 'languages.json')
        self._load_languages_config()

        # Set default language
        self.default_language = default_language or self.languages_config.get('default_language', 'en')

    def get_all_cheatsheets(self) -> List[Dict]:
        """Get all cheatsheets"""
        cheatsheets = []

        for file_path in self.data_path.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filename'] = file_path.stem
                    # Add default language if it doesn't exist
                    if 'language' not in data:
                        data['language'] = self.default_language
                    cheatsheets.append(data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading {file_path}: {e}")
                continue

        return sorted(cheatsheets, key=lambda x: x.get('updated', ''))

    def get_cheatsheet_by_filename(self, filename: str) -> Optional[Dict]:
        """Get a specific cheatsheet by filename"""
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
        """Get cheatsheets filtered by tag"""
        if tag == "all":
            return self.get_all_cheatsheets()

        all_sheets = self.get_all_cheatsheets()
        return [sheet for sheet in all_sheets if tag in sheet.get('tags', [])]

    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        all_sheets = self.get_all_cheatsheets()
        tags = set()

        for sheet in all_sheets:
            tags.update(sheet.get('tags', []))

        return sorted(list(tags))

    def create_cheatsheet(self, title: str, tags: List[str], items: List[Dict], language: str = None) -> str:
        """Create a new cheatsheet"""
        # Generate filename from title
        filename = self._generate_filename(title)

        # Use default language if not specified
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
        """Update an existing cheatsheet"""
        file_path = self.data_path / f"{filename}.json"

        if not file_path.exists():
            return False

        try:
            # Load existing data to preserve creation date
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            # Use existing language or default if not specified
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
        """Delete a cheatsheet"""
        file_path = self.data_path / f"{filename}.json"

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except OSError:
            return False

    def _generate_filename(self, title: str) -> str:
        """Generate valid filename from title"""
        # Convert to lowercase and replace spaces and special characters
        filename = title.lower()
        filename = ''.join(c if c.isalnum() or c in '-_' else '-' for c in filename)
        # Clean multiple dashes
        filename = '-'.join(filter(None, filename.split('-')))

        # Ensure filename is unique
        counter = 1
        original_filename = filename

        while (self.data_path / f"{filename}.json").exists():
            filename = f"{original_filename}-{counter}"
            counter += 1

        return filename

    def search_cheatsheets(self, query: str) -> List[Dict]:
        """Search cheatsheets by term"""
        query = query.lower()
        all_sheets = self.get_all_cheatsheets()
        results = []

        for sheet in all_sheets:
            # Search in title
            if query in sheet.get('title', '').lower():
                results.append(sheet)
                continue

            # Search in tags
            if any(query in tag.lower() for tag in sheet.get('tags', [])):
                results.append(sheet)
                continue

            # Search in items
            for item in sheet.get('items', []):
                if (query in item.get('code', '').lower() or 
                    query in item.get('description', '').lower() or 
                    query in item.get('example', '').lower()):
                    results.append(sheet)
                    break

        return results

    def validate_cheatsheet_data(
            self, title: str,
            tags: List[str],
            items: List[Dict],
            language: str = None
            ) -> List[str]:
        """Validate cheatsheet data, returns list of errors"""
        errors = []

        if not title or not title.strip():
            errors.append("Title is required")

        if language and not self.validate_language(language):
            available_langs = ', '.join(self.get_supported_languages().keys())
            error_msg = self.get_interface_text('error_language_unsupported')
            errors.append(f"{error_msg}: {available_langs}")

        if not isinstance(tags, list):
            errors.append("Tags must be a list")

        if not isinstance(items, list) or len(items) == 0:
            errors.append("There must be at least one item")

        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"Item {i+1}: must be an object")
                continue

            if not item.get('code', '').strip():
                errors.append(f"Item {i+1}: code is required")

            if not item.get('description', '').strip():
                errors.append(f"Item {i+1}: description is required")

        return errors

    def create_tag(
            self,
            tag_name: str
            ) -> bool:
        """
        Create a new tag (doesn't actually need to create file, just validate)
        """
        if not tag_name or not tag_name.strip():
            return False

        # Normalize the tag
        tag_name = tag_name.strip().lower()

        # Validate that it doesn't contain problematic special characters
        if not tag_name.replace('-', '').replace('_', '').isalnum():
            return False

        return True

    def delete_tag(self, tag_name: str) -> bool:
        """Remove a tag from all cheatsheets that use it"""
        if not tag_name:
            return False

        modified_count = 0
        all_sheets = self.get_all_cheatsheets()

        for sheet in all_sheets:
            tags = sheet.get('tags', [])
            if tag_name in tags:
                # Remove the tag
                tags.remove(tag_name)

                # Update the cheatsheet
                self.update_cheatsheet(
                    sheet['filename'],
                    sheet['title'],
                    tags,
                    sheet['items']
                )
                modified_count += 1

        return modified_count > 0

    def rename_tag(self, old_tag: str, new_tag: str) -> bool:
        """Rename a tag in all cheatsheets that use it"""
        if not old_tag or not new_tag:
            return False

        # Validate the new tag
        if not self.create_tag(new_tag):
            return False

        new_tag = new_tag.strip().lower()
        modified_count = 0
        all_sheets = self.get_all_cheatsheets()

        for sheet in all_sheets:
            tags = sheet.get('tags', [])
            if old_tag in tags:
                # Replace the tag
                tag_index = tags.index(old_tag)
                tags[tag_index] = new_tag

                # Update the cheatsheet
                self.update_cheatsheet(
                    sheet['filename'],
                    sheet['title'],
                    tags,
                    sheet['items']
                )
                modified_count += 1

        return modified_count > 0

    def get_tag_usage_count(self, tag_name: str) -> int:
        """Get the number of cheatsheets that use a specific tag"""
        all_sheets = self.get_all_cheatsheets()
        count = 0

        for sheet in all_sheets:
            if tag_name in sheet.get('tags', []):
                count += 1

        return count

    def get_tags_with_usage(self) -> List[Dict[str, any]]:
        """Get all tags with their usage count"""
        tags = self.get_all_tags()
        tag_info = []

        for tag in tags:
            usage_count = self.get_tag_usage_count(tag)
            tag_info.append({
                'name': tag,
                'usage_count': usage_count
            })

        # Sort by descending usage
        return sorted(tag_info, key=lambda x: x['usage_count'], reverse=True)

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return {code: info['name'] for code, info in supported_langs.items()}

    def get_available_languages(self) -> List[str]:
        """Get list of language codes available in cheatsheets"""
        all_sheets = self.get_all_cheatsheets()
        languages = set()

        for sheet in all_sheets:
            languages.add(sheet.get('language', self.default_language))

        return sorted(list(languages))

    def get_cheatsheets_by_language(self, language: str) -> List[Dict]:
        """Get cheatsheets filtered by language"""
        if not self.validate_language(language):
            return []

        all_sheets = self.get_all_cheatsheets()
        return [sheet for sheet in all_sheets
                if sheet.get('language', self.default_language) == language]

    def get_cheatsheets_by_tag_and_language(
            self,
            tag: str,
            language: str
            ) -> List[Dict]:
        """Get cheatsheets filtered by tag and language"""
        if not self.validate_language(language):
            return []

        sheets_by_tag = self.get_cheatsheets_by_tag(tag)
        return [sheet for sheet in sheets_by_tag
                if sheet.get('language', self.default_language) == language]

    def search_cheatsheets_by_language(
            self,
            query: str,
            language: str
            ) -> List[Dict]:
        """Search cheatsheets by term in a specific language"""
        if not self.validate_language(language):
            return []

        all_results = self.search_cheatsheets(query)
        return [sheet for sheet in all_results
                if sheet.get('language', self.default_language) == language]

    def get_language_statistics(self) -> Dict[str, Dict]:
        """Get statistics per language"""
        all_sheets = self.get_all_cheatsheets()
        stats = {}

        supported_langs = self.languages_config.get('supported_languages', {})
        for lang_code, lang_info in supported_langs.items():
            sheets_count = len([
                s for s in all_sheets
                if s.get('language', self.default_language) == lang_code
            ])
            stats[lang_code] = {
                'name': lang_info['name'],
                'flag': lang_info.get('flag', ''),
                'count': sheets_count
            }

        return stats

    def migrate_cheatsheets_language(
            self,
            from_language: str,
            to_language: str
            ) -> int:
        """Migrate cheatsheets from one language to another"""
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
        """Validate if a language is supported"""
        return language in self.languages_config.get('supported_languages', {})

    def _load_languages_config(self) -> None:
        """Load languages configuration from JSON file"""
        try:
            with open(self.languages_file, 'r', encoding='utf-8') as f:
                self.languages_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            error_msg = (
                f"Error loading languages config from {self.languages_file}: {e}"
            )
            print(error_msg)
            # Default configuration if loading fails
            self.languages_config = {
                'default_language': 'es',
                'supported_languages': {
                    'es': {
                        'name': 'Español',
                        'flag': '🇪🇸',
                        'interface': {
                            'error_language_unsupported': (
                                'Idioma no soportado. Idiomas disponibles'
                            )
                        }
                    },
                    'en': {
                        'name': 'English',
                        'flag': '🇺🇸',
                        'interface': {
                            'error_language_unsupported': (
                                'Language not supported. Available languages'
                            )
                        }
                    }
                }
            }

    def reload_languages_config(self) -> bool:
        """Reload languages configuration from file"""
        try:
            self._load_languages_config()
            return True
        except Exception as e:
            print(f"Error reloading languages config: {e}")
            return False

    def get_interface_text(
            self, key: str, language: Optional[str] = None
    ) -> str:
        """Get interface text in the specified language"""
        if language is None:
            language = self.default_language

        supported_langs = self.languages_config.get('supported_languages', {})
        lang_config = supported_langs.get(language, {})
        interface_texts = lang_config.get('interface', {})

        return interface_texts.get(key, key)

    def get_language_info(self, language: str) -> Dict:
        """Get complete information for a language"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return supported_langs.get(language, {})

    def add_language(
            self, code: str, name: str, flag: str = '',
            interface: Optional[Dict] = None
    ) -> bool:
        """Add a new language to the configuration"""
        if interface is None:
            interface = {}

        new_language = {
            'name': name,
            'flag': flag,
            'interface': interface
        }

        supported_langs = self.languages_config.setdefault('supported_languages', {})
        supported_langs[code] = new_language

        # Save changes to file
        return self._save_languages_config()

    def remove_language(self, code: str) -> bool:
        """Remove a language from the configuration"""
        if code == self.default_language:
            return False  # Cannot remove default language

        supported_languages = self.languages_config.get(
            'supported_languages', {}
        )
        if code in supported_languages:
            del supported_languages[code]
            return self._save_languages_config()

        return False

    def update_language_interface(
            self, code: str, interface_updates: Dict
    ) -> bool:
        """Update interface texts for a language"""
        supported_langs = self.languages_config.get('supported_languages', {})
        lang_config = supported_langs.get(code)
        if not lang_config:
            return False

        lang_config.setdefault('interface', {}).update(interface_updates)
        return self._save_languages_config()

    def _save_languages_config(self) -> bool:
        """Save languages configuration to file"""
        try:
            with open(self.languages_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.languages_config, f, indent=2, ensure_ascii=False
                )
            return True
        except Exception as e:
            print(f"Error saving languages config: {e}")
            return False

    def validate_languages_config(self) -> List[str]:
        """Validate the structure of the languages configuration"""
        errors = []

        if not isinstance(self.languages_config, dict):
            errors.append("Configuration must be a JSON object")
            return errors

        if 'supported_languages' not in self.languages_config:
            errors.append("Missing 'supported_languages' key")
        else:
            supported = self.languages_config['supported_languages']
            if not isinstance(supported, dict):
                errors.append("'supported_languages' must be an object")
            else:
                for code, info in supported.items():
                    if not isinstance(info, dict):
                        errors.append(f"Language '{code}': must be an object")
                        continue

                    if 'name' not in info:
                        errors.append(
                            f"Language '{code}': missing 'name' field"
                        )

                    if ('interface' in info and
                            not isinstance(info['interface'], dict)):
                        errors.append(
                            f"Language '{code}': 'interface' must be an object"
                        )

        default_lang = self.languages_config.get('default_language')
        default_lang = self.languages_config.get('default_language')
        supported_langs = self.languages_config.get('supported_languages', {})
        if default_lang and default_lang not in supported_langs:
            error_msg = (
                f"Default language '{default_lang}' is not in supported_languages"
            )
            errors.append(error_msg)

        return errors


# Usage example and testing
if __name__ == "__main__":
    manager = CheatSheetManager()

    # Show supported languages
    print("Supported languages:")
    for code, name in manager.get_supported_languages().items():
        info = manager.get_language_info(code)
        flag = info.get('flag', '')
        print(f"  {code}: {name} {flag}")

    # Create example cheatsheet in Spanish
    items_es = [
        {
            "code": "docker run",
            "description": "Run a container",
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

    # Create example cheatsheet in English
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

    # Statistics per language
    stats = manager.get_language_statistics()
    print("Statistics per language:")
    for code, info in stats.items():
        name = info['name']
        flag = info.get('flag', '')
        count = info['count']
        print(f"  {name} {flag}: {count} cheatsheets")

    # List cheatsheets by language
    es_sheets = manager.get_cheatsheets_by_language('es')
    print(f"Cheatsheets in Spanish: {len(es_sheets)}")

    en_sheets = manager.get_cheatsheets_by_language('en')
    print(f"Cheatsheets in English: {len(en_sheets)}")

    # Get interface text
    error_msg_es = manager.get_interface_text('error_title_required', 'es')
    error_msg_en = manager.get_interface_text('error_title_required', 'en')
    print(f"Error message ES: {error_msg_es}")
    print(f"Error message EN: {error_msg_en}")
