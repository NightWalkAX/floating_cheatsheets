"""
CheatSheet Manager
Maneja las operaciones CRUD de las cheatsheets
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class CheatSheetManager:
    def __init__(self, data_path: str = None):
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / 'data' / 'cheatsheets' if data_path is None else Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

    def get_all_cheatsheets(self) -> List[Dict]:
        """Obtener todas las cheatsheets"""
        cheatsheets = []

        for file_path in self.data_path.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filename'] = file_path.stem
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

    def create_cheatsheet(self, title: str, tags: List[str], items: List[Dict]) -> str:
        """Crear una nueva cheatsheet"""
        # Generar filename desde el título
        filename = self._generate_filename(title)

        cheatsheet_data = {
            "title": title,
            "tags": tags,
            "items": items,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "updated": datetime.now().strftime("%Y-%m-%d")
        }

        file_path = self.data_path / f"{filename}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cheatsheet_data, f, indent=2, ensure_ascii=False)

        return filename

    def update_cheatsheet(self, filename: str, title: str, tags: List[str], items: List[Dict]) -> bool:
        """Actualizar una cheatsheet existente"""
        file_path = self.data_path / f"{filename}.json"

        if not file_path.exists():
            return False

        try:
            # Cargar datos existentes para preservar fecha de creación
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            cheatsheet_data = {
                "title": title,
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

    def validate_cheatsheet_data(self, title: str, tags: List[str], items: List[Dict]) -> List[str]:
        """Validar datos de cheatsheet, retorna lista de errores"""
        errors = []

        if not title or not title.strip():
            errors.append("El título es requerido")

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


# Ejemplo de uso y testing
if __name__ == "__main__":
    manager = CheatSheetManager()
    
    # Crear cheatsheet de ejemplo
    items = [
        {
            "code": "docker run",
            "description": "Ejecutar un contenedor",
            "example": "docker run -d -p 80:80 nginx"
        }
    ]

    filename = manager.create_cheatsheet("Docker Commands", ["docker", "containers"], items)
    print(f"Created: {filename}")

    # Listar todas
    sheets = manager.get_all_cheatsheets()
    print(f"Total sheets: {len(sheets)}")

    # Obtener tags
    tags = manager.get_all_tags()
    print(f"Available tags: {tags}")
