# services/theme_manager.py
from ui.theme import LIGHT_THEME, DARK_THEME

class ThemeManager:
    _theme = LIGHT_THEME
    _is_dark = False

    @classmethod
    def use_dark_mode(cls):
        cls._theme = DARK_THEME
        cls._is_dark = True

    @classmethod
    def use_light_mode(cls):
        cls._theme = LIGHT_THEME
        cls._is_dark = False

    @classmethod
    def get(cls, key: str, fallback=None):
        return cls._theme.get(key, fallback) 

    @classmethod
    def is_dark_mode(cls):
        return cls._is_dark

    @classmethod
    def toggle_theme(cls):
        if cls._is_dark:
            cls.use_light_mode()
        else:
            cls.use_dark_mode()
