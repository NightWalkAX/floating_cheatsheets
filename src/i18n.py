"""
Internationalization (i18n) Module
Sistema de traducciones para la interfaz de usuario
"""

import json
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """Clase para manejar las traducciones de la interfaz de usuario"""
    
    def __init__(self, languages_file: Optional[str] = None,
                 default_language: Optional[str] = None):
        self.base_path = Path(__file__).parent.parent
        self.languages_file = (languages_file or
                               str(self.base_path / 'data' / 'languages.json'))
        self.languages_config = {}
        self.current_language = None
        self.default_language = default_language or 'es'
        
        # Callbacks para actualización dinámica de UI
        self.update_callbacks = []
        
        self._load_languages_config()
        self.set_language(self.default_language)
    
    def _load_languages_config(self) -> None:
        """Cargar configuración de idiomas desde archivo JSON"""
        try:
            with open(self.languages_file, 'r', encoding='utf-8') as f:
                self.languages_config = json.load(f)
                
            self.default_language = self.languages_config.get(
                'default_language', 'es')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading languages config from "
                  f"{self.languages_file}: {e}")
            # Configuración por defecto si falla la carga
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
        """Cambiar el idioma actual"""
        if not self.is_language_supported(language_code):
            return False
        
        self.current_language = language_code
        
        # Notificar a todos los callbacks registrados
        for callback in self.update_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error executing update callback: {e}")
        
        return True
    
    def get_current_language(self) -> str:
        """Obtener el idioma actual"""
        return self.current_language or self.default_language
    
    def is_language_supported(self, language_code: str) -> bool:
        """Verificar si un idioma es soportado"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return language_code in supported_langs
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Obtener lista de idiomas soportados"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return {
            code: info['name']
            for code, info in supported_langs.items()
        }
    
    def get_language_info(self, language_code: str) -> Dict:
        """Obtener información completa de un idioma"""
        supported_langs = self.languages_config.get('supported_languages', {})
        return supported_langs.get(language_code, {})
    
    def get_text(self, key: str, language: Optional[str] = None,
                 fallback: Optional[str] = None) -> str:
        """
        Obtener texto traducido para una clave específica
        
        Args:
            key: Clave del texto a traducir
            language: Idioma específico (opcional, usa el idioma actual
                      por defecto)
            fallback: Texto de respaldo si no se encuentra la traducción
            
        Returns:
            Texto traducido o clave si no se encuentra
        """
        if language is None:
            language = self.get_current_language()
        
        # Obtener configuración del idioma
        supported_langs = self.languages_config.get('supported_languages', {})
        lang_config = supported_langs.get(language, {})
        interface_texts = lang_config.get('interface', {})
        
        # Buscar el texto
        text = interface_texts.get(key)
        
        # Si no se encuentra, intentar con el idioma por defecto
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
        Obtener texto traducido y formatearlo con argumentos
        
        Args:
            key: Clave del texto a traducir
            *args: Argumentos para formatear el texto
            language: Idioma específico (opcional)
            fallback: Texto de respaldo si no se encuentra la traducción
            
        Returns:
            Texto traducido y formateado
        """
        text = self.get_text(key, language, fallback)
        
        try:
            return text.format(*args)
        except (IndexError, KeyError, ValueError):
            # Si hay error de formato, devolver el texto sin formatear
            return text
    
    def register_update_callback(self, callback):
        """Registrar callback para actualización dinámica de UI"""
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)
    
    def unregister_update_callback(self, callback):
        """Desregistrar callback de actualización"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
    
    def reload_config(self) -> bool:
        """Recargar configuración de idiomas desde archivo"""
        try:
            self._load_languages_config()
            # Verificar que el idioma actual sigue siendo válido
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
    """Obtener la instancia global de I18n (singleton)"""
    global _i18n_instance
    
    if _i18n_instance is None:
        _i18n_instance = I18n(languages_file, default_language)
    
    return _i18n_instance


def _(key: str, *args, language: Optional[str] = None,
      fallback: Optional[str] = None) -> str:
    """
    Función de conveniencia para obtener textos traducidos
    
    Usage:
        _('save')  # Obtiene el texto 'save' en el idioma actual
        _('confirm_delete_tag', 'python')  # Formatea con argumentos
        _('title', language='en')  # Fuerza idioma específico
    """
    i18n = get_i18n()
    
    if args:
        return i18n.format_text(key, *args, language=language,
                                fallback=fallback)
    else:
        return i18n.get_text(key, language=language, fallback=fallback)


# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar i18n
    i18n = get_i18n()
    
    # Probar traducciones
    print("Idiomas soportados:", i18n.get_supported_languages())
    
    # Probar en español
    i18n.set_language('es')
    print(f"ES - Guardar: {_('save')}")
    print(f"ES - Título: {_('title')}")
    print(f"ES - Error formateado: {_('confirm_delete_tag', 'python')}")
    
    # Probar en inglés
    i18n.set_language('en')
    print(f"EN - Save: {_('save')}")
    print(f"EN - Title: {_('title')}")
    print(f"EN - Formatted error: {_('confirm_delete_tag', 'python')}")
    
    # Probar en francés
    i18n.set_language('fr')
    print(f"FR - Enregistrer: {_('save')}")
    print(f"FR - Titre: {_('title')}")
    print(f"FR - Erreur formatée: {_('confirm_delete_tag', 'python')}")
