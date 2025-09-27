#!/usr/bin/env python3
"""
Floating CheatSheets Widget
A circular floating widget for quick access to cheatsheets
"""

import tkinter as tk
from tkinter import ttk
import json
import math
from pathlib import Path
from cheatsheet_manager import CheatSheetManager
from ui_components import (
    DialMenu, CheatSheetEditor, CheatSheetViewer, TagManager, get_tag_color
)
from search_components import show_search_dialog
from i18n import get_i18n, _


class FloatingWidget:
    """Main widget"""
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.load_config()
        self.create_circular_widget()
        self.menu_open = False
        self.current_page = 0
        self.current_tag = "all"
        self.current_language = "es"  # Default language

        # Initialize translation system
        self.i18n = get_i18n()

        # Initialize manager and dial menu (after load_config)
        self.cheatsheet_manager = None
        self.dial_menu = None

        self.bind_events()

        # Initialize manager after loading config
        self.cheatsheet_manager = CheatSheetManager(self.config['data_path'])

        # Load language from configuration and setup i18n
        self.current_language = self.config.get('current_language', 'es')
        self.i18n.set_language(self.current_language)

        # Register callback for dynamic UI updates
        self.i18n.register_update_callback(self.update_ui_texts)

    def setup_window(self):
        """Setup the main window"""
        self.root.title(_("window_title"))
        self.root.overrideredirect(True)  # No window borders
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-alpha', 0.95)  # Transparency

        # Setup transparency - try transparentcolor (Windows) or compositing (Linux)
        try:
            # Bright green that will be transparent
            self.transparent_color = "#00ff00"
            self.root.wm_attributes(
                '-transparentcolor', self.transparent_color
            )
            self.root.config(bg=self.transparent_color)
        except tk.TclError:
            # On Linux, use a very light background that simulates transparency
            self.transparent_color = '#f0f0f0'
            self.root.config(bg=self.transparent_color)

    def load_config(self):
        """Load configuration from file"""
        # Use user's home directory for data
        self.user_data_path = (
            Path.home() / '.local' / 'share' / 'floating-cheatsheets'
        )
        self.user_data_path.mkdir(parents=True, exist_ok=True)

        config_path = self.user_data_path / 'config.json'

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                "window": {
                    "x": 100, "y": 100, "size": 80, "always_on_top": True
                },
                "data_path": str(self.user_data_path / 'cheatsheets'),
                "current_tag": "all",
                "pagination": {"items_per_page": 3, "max_items_first_page": 3}
            }

        # Setup window according to config (ensure self.size exists before save)
        self.size = self.config['window']['size']

        # Create initial configuration if it didn't exist
        if not config_path.exists():
            self.save_config()
        x = self.config['window']['x']
        y = self.config['window']['y']
        self.root.geometry(f"{self.size}x{self.size}+{x}+{y}")

        # Create cheatsheets directory if it doesn't exist
        cheatsheets_path = Path(self.config['data_path'])
        cheatsheets_path.mkdir(parents=True, exist_ok=True)

        # Copy example cheatsheets if directory is empty
        if not any(cheatsheets_path.glob('*.json')):
            self.copy_example_cheatsheets(cheatsheets_path)

    def save_config(self):
        """Save current configuration"""
        # Update current position
        self.config['window']['x'] = self.root.winfo_x()
        self.config['window']['y'] = self.root.winfo_y()
        self.config['window']['size'] = self.size
        self.config['current_language'] = self.current_language

        config_path = self.user_data_path / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def copy_example_cheatsheets(self, target_path):
        """Copy example cheatsheets to user directory"""
        examples = [
            {
                "title": "Git Commands",
                "tags": ["git", "version-control", "terminal"],
                "items": [
                    {
                        "code": "git status",
                        "description": "View repository status",
                        "example": "git status --short"
                    },
                    {
                        "code": "git add .",
                        "description": "Add all changes to staging",
                        "example": "git add . && git status"
                    },
                    {
                        "code": "git commit -m",
                        "description": "Make commit with message",
                        "example": "git commit -m \"Initial commit\""
                    }
                ],
                "created": "2025-09-24",
                "updated": "2025-09-24"
            },
            {
                "title": "Linux Commands",
                "tags": ["linux", "terminal", "bash"],
                "items": [
                    {
                        "code": "ls",
                        "description": "List files and directories",
                        "example": "ls -la"
                    },
                    {
                        "code": "find",
                        "description": "Search for files and directories",
                        "example": "find . -name \"*.py\""
                    },
                    {
                        "code": "grep",
                        "description": "Search for text in files",
                        "example": "grep -r \"function\" ."
                    }
                ],
                "created": "2025-09-24",
                "updated": "2025-09-24"
            }
        ]

        for i, example in enumerate(examples):
            filename = f"example-{i+1}.json"
            with open(target_path / filename, 'w') as f:
                json.dump(example, f, indent=2, ensure_ascii=False)

    def create_circular_widget(self):
        """Create the main circular widget"""
        self.canvas = tk.Canvas(
            self.root, 
            width=self.size, 
            height=self.size,
            highlightthickness=0
        )
        self.canvas.pack()

        # Use the same transparent color as the window
        self.canvas.configure(bg=self.transparent_color)

        # Draw main circle
        margin = 4
        self.circle = self.canvas.create_oval(
            margin, margin, 
            self.size - margin, self.size - margin,
            fill='#4a90e2', 
            outline='#2c5aa0', 
            width=2
        )

        # Widget text
        self.canvas.create_text(
            self.size // 2, self.size // 2,
            text="📝", 
            font=("Arial", str(self.size // 3)), 
            fill='white'
        )

    def bind_events(self):
        """Setup mouse events"""
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.show_context_menu)  # Right click

        # Variables for dragging and movement detection
        self.drag_data = {
            "x": 0, "y": 0, "has_moved": False, "is_resizing": False
        }

    def on_click(self, event):
        """Handle widget click"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["has_moved"] = False

        # Detect if click is near border for resizing
        center_x = self.size // 2
        center_y = self.size // 2
        distance = math.sqrt((event.x - center_x)**2 + (event.y - center_y)**2)
        border_threshold = (self.size // 2) - 10  # 10 pixels from border

        self.drag_data["is_resizing"] = distance > border_threshold

    def on_drag(self, event):
        """Handle widget drag"""
        # Calculate distance moved
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # If moves more than 5 pixels, consider it dragging
        if abs(delta_x) > 5 or abs(delta_y) > 5:
            self.drag_data["has_moved"] = True

            # Cerrar el menú si está abierto
            if self.menu_open:
                self.hide_dial_menu()

            if self.drag_data["is_resizing"]:
                # Redimensionar basado en la distancia del centro
                center_x = self.size // 2
                center_y = self.size // 2
                new_distance = math.sqrt((event.x - center_x)**2 + (event.y - center_y)**2)
                new_size = max(50, min(150, int(new_distance * 2)))

                if new_size != self.size:
                    self.size = new_size
                    self.root.geometry(f"{self.size}x{self.size}")
                    self.canvas.configure(width=self.size, height=self.size)
                    self.redraw_widget()
            else:
                # Mover la ventana
                x = self.root.winfo_x() + delta_x
                y = self.root.winfo_y() + delta_y
                self.root.geometry(f"+{x}+{y}")

    def on_release(self, event):
        """Handle mouse release"""
        # If it didn't move, it's a normal click
        if not self.drag_data["has_moved"]:
            print(f"DEBUG: Left click detected, menu_open={self.menu_open}")
            if not self.menu_open:
                print("DEBUG: Trying to show dial menu...")
                self.show_dial_menu()
            else:
                print("DEBUG: Hiding dial menu...")
                self.hide_dial_menu()

        # Save configuration after dragging
        self.save_config()

    def show_context_menu(self, event):
        """Show context menu (right click)"""
        context_menu = tk.Menu(self.root, tearoff=0)

        # Search option
        search_label = _("search_cheatsheets", fallback="🔍 Buscar CheatSheets")
        context_menu.add_command(label=search_label,
                                command=self.show_search_dialog)
        context_menu.add_separator()

        # Languages submenu
        language_menu = tk.Menu(context_menu, tearoff=0)
        context_menu.add_cascade(label=_("language"), menu=language_menu)

        # Add available languages
        if self.cheatsheet_manager:
            languages = self.cheatsheet_manager.get_supported_languages()
            language_var = tk.StringVar(value=self.current_language)

            for code, name in languages.items():
                flag = self.cheatsheet_manager.get_language_info(code).get('flag', '')
                label = f"{flag} {name}"
                language_menu.add_radiobutton(
                    label=label,
                    variable=language_var,
                    value=code,
                    command=lambda lang=code: self.change_language(lang)
                )

        context_menu.add_separator()
        context_menu.add_command(label=_("exit"), command=self.root.quit)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def change_language(self, language_code):
        """Change the current language of the application"""
        if self.current_language != language_code:
            self.current_language = language_code
            self.i18n.set_language(language_code)
            self.save_config()

            # Actualizar menú si está abierto
            if self.menu_open:
                self.hide_dial_menu()
                self.show_dial_menu()

    def update_ui_texts(self):
        """Update all UI texts when language changes"""
        # Update window title
        self.root.title(_("window_title"))

        # If there are tag or configuration windows open,
        # they will be updated automatically on next opening

    def resize_widget(self):
        """Window to adjust widget size"""
        resize_window = tk.Toplevel(self.root)
        resize_window.title(_("adjust_size_title"))
        resize_window.geometry("200x100")
        resize_window.attributes('-topmost', True)

        tk.Label(resize_window, text=_("size")).pack(pady=5)

        size_var = tk.IntVar(value=self.size)
        size_scale = tk.Scale(
            resize_window, 
            from_=50, to=150, 
            orient=tk.HORIZONTAL,
            variable=size_var
        )
        size_scale.pack(pady=5)

        def apply_size():
            self.size = size_var.get()
            self.root.geometry(f"{self.size}x{self.size}")
            self.canvas.configure(width=self.size, height=self.size)
            self.redraw_widget()
            self.save_config()
            resize_window.destroy()

        tk.Button(resize_window, text=_("apply"),
                  command=apply_size).pack(pady=5)

    def redraw_widget(self):
        """Redraw widget with new size"""
        self.canvas.delete("all")

        # Reconfigure transparent background
        self.canvas.configure(bg=self.transparent_color)

        # Redraw main circle
        margin = 4
        self.circle = self.canvas.create_oval(
            margin, margin, 
            self.size - margin, self.size - margin,
            fill='#4a90e2', 
            outline='#2c5aa0', 
            width=2
        )

        # Redraw widget text
        self.canvas.create_text(
            self.size // 2, self.size // 2,
            text="📝", 
            font=("Arial", str(self.size // 3)), 
            fill='white'
        )

        # Reset dial menu so it recreates with new dimensions
        self.dial_menu = None

    def show_dial_menu(self, filtered_cheatsheets=None):
        """Show dial menu with dynamic pagination
        
        Args:
            filtered_cheatsheets: Optional list of cheatsheets to display.
                                 If None, uses current tag and language filters.
        """
        if self.menu_open:
            return

        print("DEBUG: show_dial_menu called")

        # Verify that manager is initialized
        if not self.cheatsheet_manager:
            print("ERROR: CheatSheetManager not initialized!")
            return

        self.menu_open = True

        # Create dial menu if it doesn't exist
        if not self.dial_menu:
            center_x = self.size // 2
            center_y = self.size // 2
            radius = 80  # Radio fijo para mejor posicionamiento
            self.dial_menu = DialMenu(self.canvas, center_x, center_y, radius)

            # Configurar callbacks del menú contextual incluyendo búsqueda
            context_callbacks = {
                'nueva': self.create_new_cheatsheet,
                'tags': self.show_tag_selector,
                'gestion': self.show_tag_manager,
                'buscar': self.show_search_dialog
            }
            self.dial_menu.set_context_menu_callbacks(context_callbacks)

            print(f"DEBUG: Created dial menu at ({center_x}, {center_y}) with radius {radius}")

        # Get cheatsheets - use filtered list if provided, otherwise apply normal filters
        try:
            if filtered_cheatsheets is not None:
                cheatsheets = filtered_cheatsheets
                print(f"DEBUG: Using filtered cheatsheets: {len(cheatsheets)} items")
            else:
                if self.current_tag == "all":
                    # Obtener todas las cheatsheets del idioma actual
                    cheatsheets = self.cheatsheet_manager.get_cheatsheets_by_language(self.current_language)
                else:
                    # Obtener cheatsheets por tag e idioma
                    cheatsheets = self.cheatsheet_manager.get_cheatsheets_by_tag_and_language(
                        self.current_tag, self.current_language)
                print(f"DEBUG: Found {len(cheatsheets)} cheatsheets for tag '{self.current_tag}' in language '{self.current_language}'")
        except Exception as e:
            print(f"ERROR: Failed to get cheatsheets: {e}")
            cheatsheets = []

        # Calculate pagination
        items_per_page = 3  # Maximum 6 cheatsheets per page
        total_pages = max(1, (len(cheatsheets) + items_per_page - 1) // items_per_page)

        # Clear previous items
        self.dial_menu.clear_items()

        # Current page of cheatsheets
        start_idx = self.current_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(cheatsheets))
        page_cheatsheets = cheatsheets[start_idx:end_idx]

        # Add cheatsheets from current page
        for sheet in page_cheatsheets:
            title = sheet['title']
            filename = sheet.get('filename', '')
            color = get_tag_color(sheet.get('tags', [''])[0]) if sheet.get('tags') else '#4a90e2'

            self.dial_menu.add_item(
                text=title,
                callback=lambda f=filename: self.show_cheatsheet(f),
                color=color
            )

        # If no cheatsheets, add basic options to start
        if len(cheatsheets) == 0:
            self.dial_menu.add_item(
                text=_("new_cheatsheet"),
                callback=self.create_new_cheatsheet,
                color="#28a745"
            )
            # Agregar opción para cambiar idioma si el actual no tiene sheets
            current_lang_info = self.cheatsheet_manager.get_language_info(
                self.current_language)
            lang_name = current_lang_info.get('name', self.current_language)
            lang_flag = current_lang_info.get('flag', '')
            self.dial_menu.add_item(
                text=f"{lang_flag} {lang_name}",
                callback=self.show_language_selector,
                color="#17a2b8"
            )

        # Only navigation buttons if multiple pages (always at bottom)
        if total_pages > 1:
            # Botón anterior (si no estamos en la primera página)
            if self.current_page > 0:
                self.dial_menu.add_item(
                    text=f"◀ {_('previous')}",
                    callback=self.previous_page,
                    color="#666666"
                )

            # Botón siguiente (si no estamos en la última página)
            if self.current_page < total_pages - 1:
                self.dial_menu.add_item(
                    text=f"{_('next')} ▶",
                    callback=self.next_page,
                    color="#666666"
                )

        # Show the menu
        self.dial_menu.show()

    def hide_dial_menu(self):
        """Hide dial menu"""
        if not self.menu_open:
            return

        self.menu_open = False
        if self.dial_menu:
            self.dial_menu.hide()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.hide_dial_menu()
            self.show_dial_menu()

    def next_page(self):
        """Go to next page"""
        # Get cheatsheets filtered by language
        if self.current_tag == "all":
            cheatsheets = self.cheatsheet_manager.get_cheatsheets_by_language(self.current_language)
        else:
            cheatsheets = self.cheatsheet_manager.get_cheatsheets_by_tag_and_language(
                self.current_tag, self.current_language)

        total_pages = max(1, (len(cheatsheets) + 2) // 3)  # 3 items per page

        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.hide_dial_menu()
            self.show_dial_menu()

    def show_cheatsheet(self, filename):
        """Show a specific cheatsheet"""
        # Hide dial menu first
        self.hide_dial_menu()

        cheatsheet_data = self.cheatsheet_manager.get_cheatsheet_by_filename(filename)
        if cheatsheet_data:
            CheatSheetViewer(self.root, cheatsheet_data)

    def create_new_cheatsheet(self):
        """Create new cheatsheet"""
        # Hide dial menu before opening editor
        self.hide_dial_menu()

        def on_save(title, tags, items):
            try:
                # Usar el idioma actual de la aplicación
                current_language = getattr(self, 'current_language', 'es')
                self.cheatsheet_manager.create_cheatsheet(
                    title, tags, items, current_language)
                # Refresh menu if it's open
                if self.menu_open:
                    self.hide_dial_menu()
                    self.show_dial_menu()
                return True
            except Exception as e:
                print(f"Error creating cheatsheet: {e}")
                return False

        CheatSheetEditor(self.root, on_save_callback=on_save)

    def show_tag_selector(self):
        """Show tag selector"""
        # Ocultar el menú dial antes de mostrar el selector
        self.hide_dial_menu()

        # Create simple window to select tag
        tag_window = tk.Toplevel(self.root)
        tag_window.title(_("select_tag_title"))
        tag_window.geometry("200x300")
        tag_window.attributes('-topmost', True)

        ttk.Label(tag_window, text=_("filter_by_tag")).pack(pady=10)

        # List of tags
        if self.cheatsheet_manager:
            tags = ["all"] + self.cheatsheet_manager.get_all_tags()
        else:
            tags = ["all"]

        for tag in tags:
            btn = ttk.Button(
                tag_window,
                text=tag.title() if tag != "all" else _("all"),
                command=lambda t=tag: self.select_tag(t, tag_window)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)

    def select_tag(self, tag, window):
        """Select a specific tag"""
        self.current_tag = tag
        self.current_page = 0  # Reset page
        window.destroy()

        # Refresh menu
        if self.menu_open:
            self.hide_dial_menu()
            self.show_dial_menu()

    def show_tag_manager(self):
        """Show tag manager"""
        # Hide dial menu before showing manager
        self.hide_dial_menu()

        def on_tags_changed():
            """Callback when tags are modified"""
            # Refresh menu if it's open
            if self.menu_open:
                self.hide_dial_menu()
                self.show_dial_menu()

        TagManager(self.root, self.cheatsheet_manager, on_tags_changed)

    def show_language_selector(self):
        """Show language selector"""
        # Hide dial menu before showing selector
        self.hide_dial_menu()

        # Create simple window to select language
        # Create simple window to select language
        lang_window = tk.Toplevel(self.root)
        lang_window.title(_("language"))
        lang_window.geometry("300x400")
        lang_window.attributes('-topmost', True)

        ttk.Label(lang_window, text=_("language") + ":").pack(pady=10)

        # List of available languages"language"))
        lang_window.geometry("300x400")
        lang_window.attributes('-topmost', True)

        ttk.Label(lang_window, text=_("language") + ":").pack(pady=10)

        # List of available languages
        if self.cheatsheet_manager:
            languages = self.cheatsheet_manager.get_supported_languages()
            for code, name in languages.items():
                lang_info = self.cheatsheet_manager.get_language_info(code)
                flag = lang_info.get('flag', '')
                is_current = code == self.current_language
                btn_text = f"{'▶ ' if is_current else ''}{flag} {name}"
                
                btn = ttk.Button(
                    lang_window,
                    text=btn_text,
                    command=lambda lang=code: self.select_language(lang,
                                                                   lang_window)
                )
                btn.pack(fill=tk.X, padx=10, pady=2)

    def select_language(self, language_code, window):
        """Select a specific language"""
        self.change_language(language_code)
        window.destroy()

        # Refresh menu
        if self.menu_open:
            self.hide_dial_menu()
            self.show_dial_menu()

    def show_search_dialog(self):
        """Show search dialog and handle selected cheatsheet"""
        def on_cheatsheet_selected(cheatsheet_data):
            # Show selected cheatsheet directly
            filename = cheatsheet_data.get('filename')
            if filename:
                self.show_cheatsheet(filename)
        
        # Show search dialog
        show_search_dialog(
            parent=self.root,
            cheatsheet_manager=self.cheatsheet_manager,
            on_select_callback=on_cheatsheet_selected,
            current_language=self.current_language,
            current_tag=self.current_tag
        )

    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.save_config()
            self.root.quit()
        finally:
            self.save_config()


if __name__ == "__main__":
    app = FloatingWidget()
    app.run()
