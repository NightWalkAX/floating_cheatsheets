"""
Internationalization (i18n) Module
Translation system for the user interface
"""

import json
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """Class to handle user interface translations"""

    def __init__(self, languages_file: Optional[str] = None,
                 default_language: Optional[str] = None):
        self.base_path = Path(__file__).parent.parent
        self.languages_file = (languages_file or
                               str(self.base_path / 'data' / 'languages.json'))
        self.languages_config = {}
        self.current_language = None
        self.default_language = default_language or 'es'

        # Callbacks for dynamic UI updates
        self.update_callbacks = []

        self._load_languages_config()
        self.set_language(self.default_language)

    def _load_languages_config(self) -> None:
        """Load languages configuration from JSON file"""
        try:
            with open(self.languages_file, 'r', encoding='utf-8') as f:
                self.languages_config = json.load(f)

            self.default_language = self.languages_config.get(
                'default_language', 'es')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading languages config from "
                  f"{self.languages_file}: {e}")
            # Default configuration if loading fails
            self.languages_config = {
                'default_language': 'es',
                'supported_languages': {
                    'es': {
                        'name': 'Español',
                        'flag': '🇪🇸',
                        'interface': {}
                    },
                    'en': {
                        'name': 'English',
                        'flag': '🇺🇸',
                        'interface': {}
                    }
                }
            }

    def set_language(self, language_code: str) -> bool:
        """Change the current language"""
        if not self.is_language_supported(language_code):
            return False

        self.current_language = language_code

        # Notify all registered callbacks
        for callback in self.update_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error executing update callback: {e}")

        return True

    def get_current_language(self) -> str:
        """Get the current language"""
        return self.current_language or self.default_language

    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return language_code in supported_langs

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return {
            code: info['name']
            for code, info in supported_langs.items()
        }

    def get_language_info(self, language_code: str) -> Dict:
        """Get complete information for a language"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return supported_langs.get(language_code, {})

    def get_text(self, key: str, language: Optional[str] = None,
                 fallback: Optional[str] = None) -> str:
        """
        Get translated text for a specific key

        Args:
            key: Key of text to translate
            language: Specific language (optional, uses current language
                      by default)
            fallback: Fallback text if translation not found

        Returns:
            Translated text or key if not found
        """
        if language is None:
            language = self.get_current_language()

        # Get language configuration
        supported_langs = self.languages_config.get('supported_languages', {})
        lang_config = supported_langs.get(language, {})
        interface_texts = lang_config.get('interface', {})

        # Search for the text
        text = interface_texts.get(key)

        # If not found, try with default language
        if text is None and language != self.default_language:
            default_lang_config = supported_langs.get(
                self.default_language, {})
            default_interface_texts = default_lang_config.get('interface', {})
            text = default_interface_texts.get(key)

        # Usar fallback si se proporciona, sino usar la clave
        if text is None:
            text = fallback if fallback is not None else key

        return text

    def format_text(self, key: str, *args, language: Optional[str] = None,
                    fallback: Optional[str] = None) -> str:
        """
        Get translated text and format it with arguments

        Args:
            key: Key of text to translate
            *args: Arguments to format the text
            language: Specific language (optional)
            fallback: Fallback text if translation not found

        Returns:
            Translated and formatted text
        """
        text = self.get_text(key, language, fallback)

        try:
            return text.format(*args)
        except (IndexError, KeyError, ValueError):
            # If there's a format error, return unformatted text
            return text

    def register_update_callback(self, callback):
        """Register callback for dynamic UI updates"""
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)

    def unregister_update_callback(self, callback):
        """Unregister update callback"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

    def reload_config(self) -> bool:
        """Reload languages configuration from file"""
        try:
            self._load_languages_config()
            # Check that current language is still valid
            if (self.current_language and
                    not self.is_language_supported(self.current_language)):
                self.set_language(self.default_language)
            return True
        except Exception as e:
            print(f"Error reloading languages config: {e}")
            return False


# Instancia global de I18n para uso en toda la aplicación
_i18n_instance = None


def get_i18n(languages_file: Optional[str] = None,
             default_language: Optional[str] = None) -> I18n:
    """Get the global I18n instance (singleton)"""
    global _i18n_instance

    if _i18n_instance is None:
        _i18n_instance = I18n(languages_file, default_language)

    return _i18n_instance


def _(key: str, *args, language: Optional[str] = None,
      fallback: Optional[str] = None) -> str:
    """
    Convenience function to get translated texts

    Usage:
        _('save')  # Gets 'save' text in current language
        _('confirm_delete_tag', 'python')  # Formats with arguments
        _('title', language='en')  # Forces specific language
    """
    i18n = get_i18n()

    if args:
        return i18n.format_text(key, *args, language=language,
                                fallback=fallback)
    else:
        return i18n.get_text(key, language=language, fallback=fallback)


# Usage example
if __name__ == "__main__":
    # Inicializar i18n
    i18n = get_i18n()

    # Test translations
    print("Supported languages:", i18n.get_supported_languages())

    # Test in Spanish
    i18n.set_language('es')
    print(f"ES - Guardar: {_('save')}")
    print(f"ES - Título: {_('title')}")
    print(f"ES - Error formateado: {_('confirm_delete_tag', 'python')}")

    # Test in English
    i18n.set_language('en')
    print(f"EN - Save: {_('save')}")
    print(f"EN - Title: {_('title')}")
    print(f"EN - Formatted error: {_('confirm_delete_tag', 'python')}")

    # Test in French
    i18n.set_language('fr')
    print(f"FR - Enregistrer: {_('save')}")
    print(f"FR - Titre: {_('title')}")
    print(f"FR - Erreur formatée: {_('confirm_delete_tag', 'python')}")
