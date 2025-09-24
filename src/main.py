#!/usr/bin/env python3
"""
Floating CheatSheets Widget
Un widget circular flotante para acceso rápido a cheatsheets
"""

import tkinter as tk
from tkinter import ttk
import json
import math
from pathlib import Path
from cheatsheet_manager import CheatSheetManager
from ui_components import DialMenu, CheatSheetEditor, CheatSheetViewer, TagManager, get_tag_color


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

        # Inicializar manager y dial menu (después de load_config)
        self.cheatsheet_manager = None
        self.dial_menu = None

        self.bind_events()

        # Inicializar manager después de cargar config
        self.cheatsheet_manager = CheatSheetManager(self.config['data_path'])

    def setup_window(self):
        """Configurar la ventana principal"""
        self.root.title("CheatSheets")
        self.root.overrideredirect(True)  # Sin bordes de ventana
        self.root.attributes('-topmost', True)  # Siempre encima
        self.root.attributes('-alpha', 0.95)  # Transparencia

        # Configurar transparencia - intentar transparentcolor (Windows) o usar compositing (Linux)
        try:
            self.transparent_color = "#00ff00"  # Verde brillante que será transparente
            self.root.wm_attributes('-transparentcolor', self.transparent_color)
            self.root.config(bg=self.transparent_color)
        except tk.TclError:
            # En Linux, usar un fondo muy claro que simule transparencia
            self.transparent_color = '#f0f0f0'
            self.root.config(bg=self.transparent_color)

    def load_config(self):
        """Cargar configuración desde archivo"""
        # Usar directorio home del usuario para datos
        self.user_data_path = Path.home() / '.local' / 'share' / 'floating-cheatsheets'
        self.user_data_path.mkdir(parents=True, exist_ok=True)

        config_path = self.user_data_path / 'config.json'

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Configuración por defecto
            self.config = {
                "window": {"x": 100, "y": 100, "size": 80, "always_on_top": True},
                "data_path": str(self.user_data_path / 'cheatsheets'),
                "current_tag": "all",
                "pagination": {"items_per_page": 3, "max_items_first_page": 3}
            }

        # Configurar ventana según config (asegurar que self.size existe antes de save)
        self.size = self.config['window']['size']

        # Crear configuración inicial si no existía
        if not config_path.exists():
            self.save_config()
        x = self.config['window']['x']
        y = self.config['window']['y']
        self.root.geometry(f"{self.size}x{self.size}+{x}+{y}")

        # Crear directorio de cheatsheets si no existe
        cheatsheets_path = Path(self.config['data_path'])
        cheatsheets_path.mkdir(parents=True, exist_ok=True)

        # Copiar cheatsheets de ejemplo si el directorio está vacío
        if not any(cheatsheets_path.glob('*.json')):
            self.copy_example_cheatsheets(cheatsheets_path)

    def save_config(self):
        """Guardar configuración actual"""
        # Actualizar posición actual
        self.config['window']['x'] = self.root.winfo_x()
        self.config['window']['y'] = self.root.winfo_y()
        self.config['window']['size'] = self.size

        config_path = self.user_data_path / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def copy_example_cheatsheets(self, target_path):
        """Copiar cheatsheets de ejemplo al directorio del usuario"""
        examples = [
            {
                "title": "Git Commands",
                "tags": ["git", "version-control", "terminal"],
                "items": [
                    {
                        "code": "git status",
                        "description": "Ver estado del repositorio",
                        "example": "git status --short"
                    },
                    {
                        "code": "git add .",
                        "description": "Agregar todos los cambios al staging",
                        "example": "git add . && git status"
                    },
                    {
                        "code": "git commit -m",
                        "description": "Hacer commit con mensaje",
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
                        "description": "Listar archivos y directorios",
                        "example": "ls -la"
                    },
                    {
                        "code": "find",
                        "description": "Buscar archivos y directorios",
                        "example": "find . -name \"*.py\""
                    },
                    {
                        "code": "grep",
                        "description": "Buscar texto en archivos",
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
        """Crear el widget circular principal"""
        self.canvas = tk.Canvas(
            self.root, 
            width=self.size, 
            height=self.size,
            highlightthickness=0
        )
        self.canvas.pack()

        # Usar el mismo color transparente que la ventana
        self.canvas.configure(bg=self.transparent_color)

        # Dibujar círculo principal
        margin = 4
        self.circle = self.canvas.create_oval(
            margin, margin, 
            self.size - margin, self.size - margin,
            fill='#4a90e2', 
            outline='#2c5aa0', 
            width=2
        )

        # Texto del widget
        self.canvas.create_text(
            self.size // 2, self.size // 2,
            text="📝", 
            font=("Arial", str(self.size // 3)), 
            fill='white'
        )

    def bind_events(self):
        """Configurar eventos del mouse"""
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.show_context_menu)  # Click derecho

        # Variables para arrastrar y detectar movimiento
        self.drag_data = {"x": 0, "y": 0, "has_moved": False, "is_resizing": False}

    def on_click(self, event):
        """Manejar click en el widget"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["has_moved"] = False

        # Detectar si el click es cerca del borde para redimensionar
        center_x = self.size // 2
        center_y = self.size // 2
        distance = math.sqrt((event.x - center_x)**2 + (event.y - center_y)**2)
        border_threshold = (self.size // 2) - 10  # 10 pixels del borde

        self.drag_data["is_resizing"] = distance > border_threshold

    def on_drag(self, event):
        """Manejar arrastre del widget"""
        # Calcular la distancia movida
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # Si se mueve más de 5 píxeles, considerar que está arrastrando
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
        """Manejar liberación del mouse"""
        # Si no se movió, es un click normal
        if not self.drag_data["has_moved"]:
            print(f"DEBUG: Left click detected, menu_open={self.menu_open}")
            if not self.menu_open:
                print("DEBUG: Trying to show dial menu...")
                self.show_dial_menu()
            else:
                print("DEBUG: Hiding dial menu...")
                self.hide_dial_menu()

        # Guardar configuración después del arrastre
        self.save_config()

    def show_context_menu(self, event):
        """Mostrar menú contextual (click derecho)"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Salir", command=self.root.quit)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def resize_widget(self):
        """Ventana para ajustar el tamaño del widget"""
        resize_window = tk.Toplevel(self.root)
        resize_window.title("Ajustar Tamaño")
        resize_window.geometry("200x100")
        resize_window.attributes('-topmost', True)

        tk.Label(resize_window, text="Tamaño:").pack(pady=5)

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

        tk.Button(resize_window, text="Aplicar", command=apply_size).pack(pady=5)

    def redraw_widget(self):
        """Redibujar el widget con el nuevo tamaño"""
        self.canvas.delete("all")

        # Reconfigurar fondo transparente
        self.canvas.configure(bg=self.transparent_color)

        # Redibujar círculo principal
        margin = 4
        self.circle = self.canvas.create_oval(
            margin, margin, 
            self.size - margin, self.size - margin,
            fill='#4a90e2', 
            outline='#2c5aa0', 
            width=2
        )

        # Redibujar texto del widget
        self.canvas.create_text(
            self.size // 2, self.size // 2,
            text="📝", 
            font=("Arial", str(self.size // 3)), 
            fill='white'
        )

        # Resetear dial menu para que se recree con nuevas dimensiones
        self.dial_menu = None
    
    def show_dial_menu(self):
        """Mostrar menú dial con paginación dinámica"""
        if self.menu_open:
            return

        print("DEBUG: show_dial_menu called")

        # Verificar que el manager esté inicializado
        if not self.cheatsheet_manager:
            print("ERROR: CheatSheetManager not initialized!")
            return

        self.menu_open = True

        # Crear dial menu si no existe
        if not self.dial_menu:
            center_x = self.size // 2
            center_y = self.size // 2
            radius = 80  # Radio fijo para mejor posicionamiento
            self.dial_menu = DialMenu(self.canvas, center_x, center_y, radius)

            # Configurar callbacks del menú contextual
            context_callbacks = {
                'nueva': self.create_new_cheatsheet,
                'tags': self.show_tag_selector,
                'gestion': self.show_tag_manager
            }
            self.dial_menu.set_context_menu_callbacks(context_callbacks)

            print(f"DEBUG: Created dial menu at ({center_x}, {center_y}) with radius {radius}")

        # Obtener cheatsheets según tag actual
        try:
            cheatsheets = self.cheatsheet_manager.get_cheatsheets_by_tag(self.current_tag)
            print(f"DEBUG: Found {len(cheatsheets)} cheatsheets for tag '{self.current_tag}'")
        except Exception as e:
            print(f"ERROR: Failed to get cheatsheets: {e}")
            cheatsheets = []

        # Calcular paginación
        items_per_page = 3  # Máximo 6 cheatsheets por página
        total_pages = max(1, (len(cheatsheets) + items_per_page - 1) // items_per_page)

        # Limpiar items anteriores
        self.dial_menu.clear_items()

        # Página actual de cheatsheets
        start_idx = self.current_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(cheatsheets))
        page_cheatsheets = cheatsheets[start_idx:end_idx]

        # Agregar cheatsheets de la página actual
        for sheet in page_cheatsheets:
            title = sheet['title']
            filename = sheet.get('filename', '')
            color = get_tag_color(sheet.get('tags', [''])[0]) if sheet.get('tags') else '#4a90e2'

            self.dial_menu.add_item(
                text=title,
                callback=lambda f=filename: self.show_cheatsheet(f),
                color=color
            )

        # Solo botones de navegación si hay múltiples páginas (siempre abajo)
        if total_pages > 1:
            # Botón anterior (si no estamos en la primera página)
            if self.current_page > 0:
                self.dial_menu.add_item(
                    text="◀ Anterior",
                    callback=self.previous_page,
                    color="#666666"
                )

            # Botón siguiente (si no estamos en la última página)
            if self.current_page < total_pages - 1:
                self.dial_menu.add_item(
                    text="Siguiente ▶",
                    callback=self.next_page,
                    color="#666666"
                )

        # Mostrar el menú
        self.dial_menu.show()

    def hide_dial_menu(self):
        """Ocultar menú dial"""
        if not self.menu_open:
            return

        self.menu_open = False
        if self.dial_menu:
            self.dial_menu.hide()

    def previous_page(self):
        """Ir a página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self.hide_dial_menu()
            self.show_dial_menu()

    def next_page(self):
        """Ir a página siguiente"""
        cheatsheets = self.cheatsheet_manager.get_cheatsheets_by_tag(self.current_tag)
        total_pages = max(1, (len(cheatsheets) + 2) // 3)  # 3 items per page

        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.hide_dial_menu()
            self.show_dial_menu()

    def show_cheatsheet(self, filename):
        """Mostrar una cheatsheet específica"""
        # Ocultar el menú dial primero
        self.hide_dial_menu()

        cheatsheet_data = self.cheatsheet_manager.get_cheatsheet_by_filename(filename)
        if cheatsheet_data:
            CheatSheetViewer(self.root, cheatsheet_data)

    def create_new_cheatsheet(self):
        """Crear nueva cheatsheet"""
        # Ocultar el menú dial antes de abrir el editor
        self.hide_dial_menu()

        def on_save(title, tags, items):
            try:
                self.cheatsheet_manager.create_cheatsheet(title, tags, items)
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
        """Mostrar selector de tags"""
        # Ocultar el menú dial antes de mostrar el selector
        self.hide_dial_menu()

        # Crear ventana simple para seleccionar tag
        tag_window = tk.Toplevel(self.root)
        tag_window.title("Seleccionar Tag")
        tag_window.geometry("200x300")
        tag_window.attributes('-topmost', True)

        ttk.Label(tag_window, text="Filtrar por tag:").pack(pady=10)

        # Lista de tags
        tags = ["all"] + self.cheatsheet_manager.get_all_tags()

        for tag in tags:
            btn = ttk.Button(
                tag_window,
                text=tag.title() if tag != "all" else "Todos",
                command=lambda t=tag: self.select_tag(t, tag_window)
            )
            btn.pack(fill=tk.X, padx=10, pady=2)

    def select_tag(self, tag, window):
        """Seleccionar un tag específico"""
        self.current_tag = tag
        self.current_page = 0  # Reset page
        window.destroy()

        # Refresh menu
        if self.menu_open:
            self.hide_dial_menu()
            self.show_dial_menu()

    def show_tag_manager(self):
        """Mostrar el gestor de tags"""
        # Ocultar el menú dial antes de mostrar el gestor
        self.hide_dial_menu()

        def on_tags_changed():
            """Callback cuando se modifican los tags"""
            # Refresh menu if it's open
            if self.menu_open:
                self.hide_dial_menu()
                self.show_dial_menu()

        TagManager(self.root, self.cheatsheet_manager, on_tags_changed)

    def run(self):
        """Ejecutar la aplicación"""
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
