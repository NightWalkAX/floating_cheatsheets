"""
UI Components
Componentes de interfaz de usuario para el widget flotante
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import math
from typing import List, Dict, Callable


class DialMenu:
    """Menú circular (dial) que se expande alrededor del widget principal"""

    def __init__(self, parent_canvas, center_x, center_y, radius=100):
        self.parent_canvas = parent_canvas
        self.parent_window = parent_canvas.master
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.items = []
        self.buttons = []
        self.is_visible = False
        self.menu_window = None
        self.menu_canvas = None
        self.context_menu_callbacks = {}

    def add_item(self, text: str, callback: Callable, color: str = "#4a90e2"):
        """Agregar item al menú dial"""
        self.items.append({
            'text': text,
            'callback': callback,
            'color': color
        })

    def clear_items(self):
        """Limpiar todos los items"""
        self.items.clear()
        self.hide()

    def set_context_menu_callbacks(self, callbacks):
        """Establecer callbacks para el menú contextual"""
        self.context_menu_callbacks = callbacks

    def show(self):
        """Mostrar el menú dial en una ventana temporal expandida"""
        print(f"DEBUG: DialMenu.show() called, is_visible={self.is_visible}, items_count={len(self.items)}")
        if self.is_visible or not self.items:
            print("DEBUG: DialMenu.show() returning early")
            return

        self.is_visible = True
        self.buttons.clear()

        # Crear ventana temporal para el menú
        self.menu_window = tk.Toplevel(self.parent_window)
        self.menu_window.overrideredirect(True)  # Sin bordes
        self.menu_window.attributes('-topmost', True)
        self.menu_window.attributes('-alpha', 0.95)

        # Configurar transparencia - intentar transparentcolor (Windows) o usar compositing (Linux)
        try:
            transparent_color = "#00ff00"  # Verde brillante que será transparente
            self.menu_window.wm_attributes('-transparentcolor', transparent_color)
            self.menu_window.config(bg=transparent_color)
        except tk.TclError:
            # En Linux, usar alpha compositing para transparencia
            self.menu_window.attributes('-alpha', 0.0)  # Ventana completamente transparente
            transparent_color = None

        # Calcular tamaño necesario para el menú
        menu_size = (self.radius + 50) * 2  # Radio + espacio para botones
        self.menu_window.geometry(f"{menu_size}x{menu_size}")

        # Posicionar la ventana del menú centrada en el widget original
        parent_x = self.parent_window.winfo_x()
        parent_y = self.parent_window.winfo_y()
        parent_size = self.parent_window.winfo_width()

        menu_x = parent_x + parent_size//2 - menu_size//2
        menu_y = parent_y + parent_size//2 - menu_size//2
        self.menu_window.geometry(f"{menu_size}x{menu_size}+{menu_x}+{menu_y}")

        # Crear canvas para el menú
        canvas_bg = transparent_color if transparent_color else '#f0f0f0'
        self.menu_canvas = tk.Canvas(
            self.menu_window,
            width=menu_size,
            height=menu_size,
            highlightthickness=0,
            bg=canvas_bg
        )
        self.menu_canvas.pack()

        # Si no hay transparentcolor, configurar el fondo de la ventana
        if not transparent_color:
            self.menu_window.configure(bg='#f0f0f0')
        # Centro del canvas del menú
        canvas_center = menu_size // 2

        # Dibujar widget original en el centro
        widget_size = 60
        center_widget = self.menu_canvas.create_oval(
            canvas_center - widget_size//2, canvas_center - widget_size//2,
            canvas_center + widget_size//2, canvas_center + widget_size//2,
            fill='#4a90e2',
            outline='#2c5aa0',
            width=2,
            tags="center_widget"
        )

        # Texto del widget central
        self.menu_canvas.create_text(
            canvas_center, canvas_center,
            text="📝",
            font=("Arial", 20),
            fill='white',
            tags="center_widget"
        )

        # Bind para menú contextual en el centro
        self.menu_canvas.tag_bind("center_widget", "<Button-3>", self._on_center_right_click)

        # Separar botones de navegación de los demás
        nav_buttons = []
        content_buttons = []

        for item in self.items:
            if "Anterior" in item['text'] or "Siguiente" in item['text']:
                nav_buttons.append(item)
            else:
                content_buttons.append(item)

        # Dibujar botones de contenido en círculo
        if content_buttons:
            angle_step = 2 * math.pi / len(content_buttons)
            for i, item in enumerate(content_buttons):
                angle = i * angle_step - math.pi / 2  # Empezar desde arriba

                # Calcular posición
                x = canvas_center + self.radius * math.cos(angle)
                y = canvas_center + self.radius * math.sin(angle)

                # Crear botón circular
                button_size = 50
                button = self.menu_canvas.create_oval(
                    x - button_size // 2, y - button_size // 2,
                    x + button_size // 2, y + button_size // 2,
                    fill=item['color'],
                    outline='#2c5aa0',
                    width=2,
                    tags=f"dial_button_{i}"
                )

                # Extraer icono y texto del item
                text_parts = item['text'].split(' ', 1)
                if len(text_parts) > 1 and len(text_parts[0]) <= 2:
                    icon = text_parts[0]
                    label = text_parts[1]
                else:
                    icon = ""
                    label = item['text']

                # Icono dentro del botón (centrado y blanco)
                icon_item = None
                if icon:
                    icon_item = self.menu_canvas.create_text(
                        x, y,  # Centrado en el botón
                        text=icon,
                        fill='white',
                        font=("Arial", 18, "bold"),
                        tags=f"dial_button_{i}"
                    )

                # Texto debajo del botón (más pequeño)
                display_text = label[:10] if len(label) > 10 else label
                text_y = y + button_size // 2 + 12
                text_item = self.menu_canvas.create_text(
                    x, text_y,
                    text=display_text,
                    fill='black',
                    font=("Arial", 8, "bold"),
                    tags=f"dial_button_{i}"
                )

                # Guardar referencia y callback
                button_data = {
                    'button': button,
                    'icon': icon_item,
                    'text': text_item,
                    'callback': item['callback'],
                    'full_text': item['text'],
                    'tag': f"dial_button_{i}"
                }
                self.buttons.append(button_data)

                # Bind click event a todos los elementos del botón
                def make_callback(cb):
                    return lambda e: self._on_button_click(cb)

                self.menu_canvas.tag_bind(f"dial_button_{i}", "<Button-1>", 
                                        make_callback(item['callback']))

        # Dibujar botones de navegación abajo (izquierda a derecha)
        if nav_buttons:
            nav_y = canvas_center + self.radius + 30  # Posición fija abajo
            nav_spacing = 100  # Espaciado entre botones
            start_x = canvas_center - (len(nav_buttons) - 1) * nav_spacing // 2

            for i, item in enumerate(nav_buttons):
                x = start_x + i * nav_spacing
                y = nav_y

                # Crear botón rectangular para navegación
                button_width = 80
                button_height = 30
                nav_button = self.menu_canvas.create_rectangle(
                    x - button_width // 2, y - button_height // 2,
                    x + button_width // 2, y + button_height // 2,
                    fill=item['color'],
                    outline='#2c5aa0',
                    width=2,
                    tags=f"nav_button_{i}"
                )

                # Texto del botón de navegación
                nav_text = self.menu_canvas.create_text(
                    x, y,
                    text=item['text'],
                    fill='white',
                    font=("Arial", 9, "bold"),
                    tags=f"nav_button_{i}"
                )

                # Guardar referencia
                nav_data = {
                    'button': nav_button,
                    'text': nav_text,
                    'callback': item['callback'],
                    'tag': f"nav_button_{i}"
                }
                self.buttons.append(nav_data)

                # Bind click event
                self.menu_canvas.tag_bind(f"nav_button_{i}", "<Button-1>", 
                                        make_callback(item['callback']))

        # Bind para cerrar el menú al hacer click fuera
        self.menu_canvas.bind("<Button-1>", self._on_canvas_click)

        print(f"DEBUG: Created menu window with {len(self.items)} items")

    def hide(self):
        """Ocultar el menú dial"""
        if not self.is_visible:
            return

        self.is_visible = False
        self.buttons.clear()

        # Destruir ventana del menú si existe
        if self.menu_window:
            self.menu_window.destroy()
            self.menu_window = None
            self.menu_canvas = None

    def _on_button_click(self, callback):
        """Manejar click en botón del dial"""
        self.hide()
        if callback:
            callback()

    def _on_canvas_click(self, event):
        """Manejar click en el canvas (fuera de los botones)"""
        # Solo cerrar si el click no fue en un botón
        clicked_item = self.menu_canvas.find_closest(event.x, event.y)[0]
        clicked_tags = self.menu_canvas.gettags(clicked_item)
        # Verificar si algún tag contiene "button"
        is_button = any("button" in tag for tag in clicked_tags)
        if not is_button:
            self.hide()

    def _on_center_right_click(self, event):
        """Mostrar menú contextual en el centro"""
        context_menu = tk.Menu(self.menu_window, tearoff=0)

        # Agregar opciones del menú contextual
        if 'nueva' in self.context_menu_callbacks:
            context_menu.add_command(label="Nueva CheatSheet", 
                                   command=self.context_menu_callbacks['nueva'])

        if 'tags' in self.context_menu_callbacks:
            context_menu.add_command(label="Seleccionar Tags", 
                                   command=self.context_menu_callbacks['tags'])

        if 'gestion' in self.context_menu_callbacks:
            context_menu.add_command(label="Gestión", 
                                   command=self.context_menu_callbacks['gestion'])

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()


class CheatSheetEditor:
    """Editor popup para crear/editar cheatsheets"""

    def __init__(self, parent, cheatsheet_data=None, on_save_callback=None):
        self.parent = parent
        self.cheatsheet_data = cheatsheet_data or {}
        self.on_save_callback = on_save_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Editor de CheatSheet")
        self.window.geometry("600x500")
        self.window.attributes('-topmost', True)

        self.setup_ui()
        self.load_data()

        # Hacer modal después de que la ventana esté completamente configurada
        self.window.update()
        self.window.grab_set()  # Modal

    def setup_ui(self):
        """Configurar la interfaz del editor"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Título
        ttk.Label(main_frame, text="Título:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        self.title_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Tags
        ttk.Label(main_frame, text="Tags:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        # Frame para tags dinámicos
        tags_container = ttk.Frame(main_frame)
        tags_container.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Lista para almacenar tags seleccionados
        self.selected_tags = []

        # Frame para mostrar tags seleccionados
        self.selected_tags_frame = ttk.Frame(tags_container)
        self.selected_tags_frame.pack(fill=tk.X, pady=(0, 5))

        # Frame para selector de tags
        selector_frame = ttk.Frame(tags_container)
        selector_frame.pack(fill=tk.X)

        # Combobox para seleccionar tags
        self.available_tags_var = tk.StringVar()
        self.tags_combobox = ttk.Combobox(selector_frame, textvariable=self.available_tags_var, 
                                         state="readonly", width=20)
        self.tags_combobox.pack(side=tk.LEFT, padx=(0, 5))

        # Botón para agregar tag
        self.add_tag_button = ttk.Button(selector_frame, text="Agregar", 
                                        command=self.add_selected_tag)
        self.add_tag_button.pack(side=tk.LEFT, padx=(0, 5))

        # Entry para crear nuevo tag
        self.new_tag_var = tk.StringVar()
        self.new_tag_entry = ttk.Entry(selector_frame, textvariable=self.new_tag_var, 
                                      width=15, font=("Arial", 9))
        self.new_tag_entry.pack(side=tk.LEFT, padx=(0, 5))

        # Botón para crear y agregar nuevo tag
        ttk.Button(selector_frame, text="Crear", command=self.create_and_add_tag).pack(side=tk.LEFT)

        # Inicializar tags disponibles
        self.update_available_tags()

        # Items
        ttk.Label(main_frame, text="Items:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))

        # Frame para items con scrollbar
        items_frame = ttk.Frame(main_frame)
        items_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.items_text = scrolledtext.ScrolledText(items_frame, height=15, width=70)
        self.items_text.pack(fill=tk.BOTH, expand=True)

        # Instrucciones
        instructions = (
            "Formato por item:\n"
            "código/objeto - descripción\n"
            "  ejemplo\n"
            "\n"
            "Separar items con una línea vacía"
        )
        ttk.Label(main_frame, text=instructions, foreground="gray").grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT)

        # Configurar grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def load_data(self):
        """Cargar datos existentes en el editor"""
        if not self.cheatsheet_data:
            return

        self.title_var.set(self.cheatsheet_data.get('title', ''))

        # Cargar tags existentes de la cheatsheet
        existing_tags = self.cheatsheet_data.get('tags', [])
        for tag in existing_tags:
            self.selected_tags.append(tag)
        self.update_selected_tags_display()
        self.update_available_tags()

        # Convertir items a texto
        items_text = ""
        for item in self.cheatsheet_data.get('items', []):
            items_text += f"{item.get('code', '')} - {item.get('description', '')}\n"
            if item.get('example'):
                items_text += f"  {item.get('example')}\n"
            items_text += "\n"

        self.items_text.insert('1.0', items_text.strip())

    def update_available_tags(self):
        """Actualizar la lista de tags disponibles en el combobox"""
        try:
            # Obtener todos los tags del sistema
            manager = None

            # Buscar el manager en diferentes lugares
            if hasattr(self.parent, 'cheatsheet_manager'):
                manager = self.parent.cheatsheet_manager
            elif hasattr(self.parent, 'master') and hasattr(self.parent.master, 'cheatsheet_manager'):
                manager = self.parent.master.cheatsheet_manager

            if not manager:
                # Si no hay manager disponible, usar tags comunes predefinidos
                all_tags = ['git', 'linux', 'python', 'docker', 'terminal', 'bash', 'javascript', 'html', 'css']
            else:
                all_tags = manager.get_all_tags()

            # Filtrar tags ya seleccionados
            available_tags = [tag for tag in all_tags if tag not in self.selected_tags]

            # Actualizar combobox
            self.tags_combobox['values'] = available_tags
            if available_tags:
                self.available_tags_var.set(available_tags[0])
            else:
                self.available_tags_var.set("")

        except Exception as e:
            print(f"Error updating tags: {e}")
            self.tags_combobox['values'] = []
            self.available_tags_var.set("")

    def add_selected_tag(self):
        """Agregar el tag seleccionado del combobox"""
        selected_tag = self.available_tags_var.get().strip()
        if selected_tag and selected_tag not in self.selected_tags:
            self.selected_tags.append(selected_tag)
            self.update_selected_tags_display()
            self.update_available_tags()

    def create_and_add_tag(self):
        """Crear y agregar un nuevo tag"""
        new_tag = self.new_tag_var.get().strip()
        if new_tag and new_tag not in self.selected_tags:
            self.selected_tags.append(new_tag)
            self.new_tag_var.set("")
            self.update_selected_tags_display()
            self.update_available_tags()

    def remove_tag(self, tag):
        """Remover un tag de la selección"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            self.update_selected_tags_display()
            self.update_available_tags()

    def update_selected_tags_display(self):
        """Actualizar la visualización de tags seleccionados"""
        # Limpiar frame anterior
        for widget in self.selected_tags_frame.winfo_children():
            widget.destroy()

        # Mostrar tags seleccionados como etiquetas con botón X
        for tag in self.selected_tags:
            tag_frame = ttk.Frame(self.selected_tags_frame)
            tag_frame.pack(side=tk.LEFT, padx=(0, 5), pady=2)

            # Color de fondo según el tag
            color = get_tag_color(tag)

            # Label del tag
            tag_label = tk.Label(tag_frame, text=tag, bg=color, fg='white',
                               padx=5, pady=2, font=("Arial", 8, "bold"))
            tag_label.pack(side=tk.LEFT)

            # Botón X para remover
            remove_btn = tk.Button(tag_frame, text="×", command=lambda t=tag: self.remove_tag(t),
                                 bg='#ff4444', fg='white', font=("Arial", 6, "bold"),
                                 width=2, pady=0, bd=0)
            remove_btn.pack(side=tk.LEFT)

    def parse_items_text(self) -> List[Dict]:
        """Parsear el texto de items a lista de diccionarios"""
        text = self.items_text.get('1.0', tk.END).strip()
        items = []

        # Dividir por párrafos (doble salto de línea)
        paragraphs = text.split('\n\n')

        for paragraph in paragraphs:
            lines = paragraph.strip().split('\n')
            if not lines or not lines[0].strip():
                continue

            # Primera línea: código - descripción
            first_line = lines[0].strip()
            if ' - ' not in first_line:
                continue

            code, description = first_line.split(' - ', 1)

            # Líneas siguientes: ejemplo (con indentación)
            example_lines = []
            for line in lines[1:]:
                if line.strip():
                    example_lines.append(line.strip())

            item = {
                'code': code.strip(),
                'description': description.strip(),
                'example': '\n'.join(example_lines) if example_lines else ''
            }

            items.append(item)

        return items

    def save(self):
        """Guardar los datos del editor"""
        title = self.title_var.get().strip()

        if not title:
            messagebox.showerror("Error", "El título es requerido")
            return

        # Usar tags seleccionados
        tags = self.selected_tags.copy()

        # Parsear items
        items = self.parse_items_text()

        if not items:
            messagebox.showerror("Error", "Debe agregar al menos un item")
            return

        # Llamar callback de guardado
        if self.on_save_callback:
            success = self.on_save_callback(title, tags, items)
            if success:
                self.window.destroy()
        else:
            self.window.destroy()


class CheatSheetViewer:
    """Visor de cheatsheets en ventana popup"""

    def __init__(self, parent, cheatsheet_data):
        self.parent = parent
        self.cheatsheet_data = cheatsheet_data

        self.window = tk.Toplevel(parent)
        self.window.title(f"CheatSheet: {cheatsheet_data.get('title', 'Sin título')}")
        self.window.geometry("500x400")
        self.window.attributes('-topmost', True)

        self.setup_ui()
        self.load_content()

    def setup_ui(self):
        """Configurar la interfaz del visor"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(main_frame, 
                               text=self.cheatsheet_data.get('title', ''), 
                               font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 5))

        # Tags
        tags = self.cheatsheet_data.get('tags', [])
        if tags:
            tags_text = "Tags: " + ", ".join(tags)
            ttk.Label(main_frame, text=tags_text, foreground="blue").pack(anchor=tk.W, pady=(0, 10))

        # Contenido con scroll
        self.content_text = scrolledtext.ScrolledText(main_frame, 
                                                     state=tk.DISABLED,
                                                     wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.window.destroy).pack()

    def load_content(self):
        """Cargar el contenido de la cheatsheet"""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete('1.0', tk.END)

        for i, item in enumerate(self.cheatsheet_data.get('items', [])):
            if i > 0:
                self.content_text.insert(tk.END, "\n" + "─" * 50 + "\n\n")

            # Código/objeto
            self.content_text.insert(tk.END, f"🔹 {item.get('code', '')}\n", "code")

            # Descripción
            self.content_text.insert(tk.END, f"   {item.get('description', '')}\n\n")

            # Ejemplo
            if item.get('example'):
                self.content_text.insert(tk.END, "   Ejemplo:\n", "example_header")
                self.content_text.insert(tk.END, f"   {item.get('example')}\n", "example")

        # Configurar tags de formato
        self.content_text.tag_config("code", font=("Courier", 10, "bold"), foreground="blue")
        self.content_text.tag_config("example_header", font=("Arial", 9, "italic"))
        self.content_text.tag_config("example", font=("Courier", 9), background="#f0f0f0")

        self.content_text.config(state=tk.DISABLED)


# Funciones auxiliares para colores y temas
def get_tag_color(tag: str) -> str:
    """Obtener color basado en el tag"""
    colors = {
        'git': '#f14e32',
        'linux': '#ffa500', 
        'python': '#3776ab',
        'docker': '#0db7ed',
        'terminal': '#4d4d4d',
        'bash': '#4eaa25'
    }
    return colors.get(tag.lower(), '#4a90e2')


class TagManager:
    """Gestor de tags y cheatsheets con interfaz con pestañas"""

    def __init__(self, parent, cheatsheet_manager, on_change_callback=None):
        self.parent = parent
        self.cheatsheet_manager = cheatsheet_manager
        self.on_change_callback = on_change_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Gestionar Tags y CheatSheets")
        self.window.geometry("600x600")
        self.window.attributes('-topmost', True)

        self.setup_ui()
        self.refresh_tags()
        self.refresh_cheatsheets()

        # Hacer modal después de configurar
        self.window.update()
        self.window.grab_set()

    def setup_ui(self):
        """Configurar la interfaz con pestañas"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Pestaña de Tags
        self.tags_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tags_frame, text="Tags")
        self.setup_tags_tab()

        # Pestaña de CheatSheets
        self.cheatsheets_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cheatsheets_frame, text="CheatSheets")
        self.setup_cheatsheets_tab()

        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.close).pack()

    def setup_tags_tab(self):
        """Configurar la pestaña de gestión de tags"""

        # Frame para crear nuevo tag
        create_frame = ttk.LabelFrame(self.tags_frame, text="Crear nuevo tag", padding="5")
        create_frame.pack(fill=tk.X, pady=(0, 10))

        self.new_tag_var = tk.StringVar()
        entry_frame = ttk.Frame(create_frame)
        entry_frame.pack(fill=tk.X)

        ttk.Entry(entry_frame, textvariable=self.new_tag_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(entry_frame, text="Crear", command=self.create_tag).pack(side=tk.LEFT)

        # Lista de tags existentes
        ttk.Label(self.tags_frame, text="Tags existentes:").pack(anchor=tk.W, pady=(0, 5))

        # Frame con scrollbar para la lista
        list_frame = ttk.Frame(self.tags_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbar y listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tags_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.tags_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tags_listbox.yview)

        # Botones de acción para tags
        buttons_frame = ttk.Frame(self.tags_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Renombrar", command=self.rename_tag).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Eliminar", command=self.delete_tag).pack(side=tk.LEFT, padx=(0, 5))

    def setup_cheatsheets_tab(self):
        """Configurar la pestaña de gestión de cheatsheets"""

        # Lista de cheatsheets
        ttk.Label(self.cheatsheets_frame, text="CheatSheets existentes:").pack(anchor=tk.W, pady=(0, 5))

        # Frame con scrollbar para la lista
        list_frame = ttk.Frame(self.cheatsheets_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbar y listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cheatsheets_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.cheatsheets_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.cheatsheets_listbox.yview)

        # Botones de acción para cheatsheets
        buttons_frame = ttk.Frame(self.cheatsheets_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Nueva", command=self.create_cheatsheet).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Editar", command=self.edit_cheatsheet).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Eliminar", command=self.delete_cheatsheet).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Ver", command=self.view_cheatsheet).pack(side=tk.LEFT)

    def refresh_tags(self):
        """Actualizar la lista de tags"""
        self.tags_listbox.delete(0, tk.END)

        tags_info = self.cheatsheet_manager.get_tags_with_usage()
        for tag_info in tags_info:
            display_text = f"{tag_info['name']} ({tag_info['usage_count']} usos)"
            self.tags_listbox.insert(tk.END, display_text)

    def create_tag(self):
        """Crear un nuevo tag"""
        tag_name = self.new_tag_var.get().strip()

        if not tag_name:
            messagebox.showwarning("Advertencia", "Ingrese un nombre para el tag")
            return

        if not self.cheatsheet_manager.create_tag(tag_name):
            messagebox.showerror("Error", "Nombre de tag inválido. Use solo letras, números, guiones y guiones bajos.")
            return

        # El tag se creará automáticamente cuando se use en una cheatsheet
        messagebox.showinfo("Información", f"Tag '{tag_name}' validado. Se creará cuando lo use en una cheatsheet.")
        self.new_tag_var.set("")

    def rename_tag(self):
        """Renombrar el tag seleccionado"""
        selection = self.tags_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un tag para renombrar")
            return

        # Obtener el tag seleccionado
        selected_text = self.tags_listbox.get(selection[0])
        old_tag = selected_text.split(" (")[0]  # Extraer solo el nombre del tag

        # Ventana para nuevo nombre
        new_name = simpledialog.askstring("Renombrar Tag", 
                                         f"Nuevo nombre para '{old_tag}':",
                                         initialvalue=old_tag)

        if not new_name or new_name.strip() == old_tag:
            return

        if self.cheatsheet_manager.rename_tag(old_tag, new_name.strip()):
            messagebox.showinfo("Éxito", f"Tag renombrado de '{old_tag}' a '{new_name.strip()}'")
            self.refresh_tags()
            if self.on_change_callback:
                self.on_change_callback()
        else:
            messagebox.showerror("Error", "No se pudo renombrar el tag")

    def delete_tag(self):
        """Eliminar el tag seleccionado"""
        selection = self.tags_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un tag para eliminar")
            return

        # Obtener el tag seleccionado
        selected_text = self.tags_listbox.get(selection[0])
        tag_name = selected_text.split(" (")[0]  # Extraer solo el nombre del tag
        usage_count = self.cheatsheet_manager.get_tag_usage_count(tag_name)

        # Confirmar eliminación
        message = f"¿Eliminar el tag '{tag_name}'?\n"
        if usage_count > 0:
            message += f"Se eliminará de {usage_count} cheatsheet(s)."

        if messagebox.askyesno("Confirmar eliminación", message):
            if self.cheatsheet_manager.delete_tag(tag_name):
                messagebox.showinfo("Éxito", f"Tag '{tag_name}' eliminado")
                self.refresh_tags()
                if self.on_change_callback:
                    self.on_change_callback()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el tag")

    def refresh_cheatsheets(self):
        """Actualizar la lista de cheatsheets"""
        if hasattr(self, 'cheatsheets_listbox'):
            self.cheatsheets_listbox.delete(0, tk.END)

            cheatsheets = self.cheatsheet_manager.get_all_cheatsheets()
            for sheet in cheatsheets:
                title = sheet.get('title', 'Sin título')
                tags = ', '.join(sheet.get('tags', []))
                display_text = f"{title} [{tags}]"
                self.cheatsheets_listbox.insert(tk.END, display_text)

    def create_cheatsheet(self):
        """Crear nueva cheatsheet"""
        def on_save(title, tags, items):
            try:
                self.cheatsheet_manager.create_cheatsheet(title, tags, items)
                self.refresh_cheatsheets()
                self.refresh_tags()
                if self.on_change_callback:
                    self.on_change_callback()
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Error creando cheatsheet: {e}")
                return False

        CheatSheetEditor(self.window, on_save_callback=on_save)

    def edit_cheatsheet(self):
        """Editar cheatsheet seleccionada"""
        selection = self.cheatsheets_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una cheatsheet para editar")
            return

        cheatsheets = self.cheatsheet_manager.get_all_cheatsheets()
        selected_sheet = cheatsheets[selection[0]]

        def on_save(title, tags, items):
            try:
                self.cheatsheet_manager.update_cheatsheet(
                    selected_sheet['filename'],
                    title, tags, items
                )
                self.refresh_cheatsheets()
                self.refresh_tags()
                if self.on_change_callback:
                    self.on_change_callback()
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Error actualizando cheatsheet: {e}")
                return False

        CheatSheetEditor(self.window, cheatsheet_data=selected_sheet, on_save_callback=on_save)

    def delete_cheatsheet(self):
        """Eliminar cheatsheet seleccionada"""
        selection = self.cheatsheets_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una cheatsheet para eliminar")
            return

        cheatsheets = self.cheatsheet_manager.get_all_cheatsheets()
        selected_sheet = cheatsheets[selection[0]]
        title = selected_sheet.get('title', 'Sin título')

        if messagebox.askyesno("Confirmar eliminación", f"¿Eliminar la cheatsheet '{title}'?"):
            if self.cheatsheet_manager.delete_cheatsheet(selected_sheet['filename']):
                messagebox.showinfo("Éxito", f"CheatSheet '{title}' eliminada")
                self.refresh_cheatsheets()
                self.refresh_tags()
                if self.on_change_callback:
                    self.on_change_callback()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la cheatsheet")

    def view_cheatsheet(self):
        """Ver cheatsheet seleccionada"""
        selection = self.cheatsheets_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una cheatsheet para ver")
            return

        cheatsheets = self.cheatsheet_manager.get_all_cheatsheets()
        selected_sheet = cheatsheets[selection[0]]

        CheatSheetViewer(self.window, selected_sheet)

    def close(self):
        """Cerrar la ventana"""
        self.window.destroy()


def truncate_text(text: str, max_length: int = 10) -> str:
    """Truncar texto para botones pequeños"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
