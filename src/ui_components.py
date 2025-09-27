"""
UI Components
User interface components for the floating widget
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import math
from typing import List, Dict, Callable
from i18n import get_i18n, _


class DialMenu:
    """Circular menu (dial) that expands around the main widget"""

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
        """Add item to dial menu"""
        self.items.append({
            'text': text,
            'callback': callback,
            'color': color
        })

    def clear_items(self):
        """Clear all items"""
        self.items.clear()
        self.hide()

    def set_context_menu_callbacks(self, callbacks):
        """Set callbacks for context menu"""
        self.context_menu_callbacks = callbacks

    def show(self):
        """Show dial menu in an expanded temporary window"""
        print(f"DEBUG: DialMenu.show() called, is_visible={self.is_visible}, items_count={len(self.items)}")
        if self.is_visible:
            print("DEBUG: DialMenu.show() returning early - already visible")
            return

        self.is_visible = True
        self.buttons.clear()

        # Create temporary window for the menu
        self.menu_window = tk.Toplevel(self.parent_window)
        self.menu_window.overrideredirect(True)  # No window borders
        self.menu_window.attributes('-topmost', True)
        self.menu_window.attributes('-alpha', 0.95)

        # Configure transparency - try transparentcolor (Windows) or use compositing (Linux)
        try:
            transparent_color = "#00ff00"  # Bright green that will be transparent
            self.menu_window.wm_attributes('-transparentcolor', transparent_color)
            self.menu_window.config(bg=transparent_color)
        except tk.TclError:
            # On Linux, use alpha compositing for transparency
            self.menu_window.attributes('-alpha', 0.0)  # Completely transparent window
            transparent_color = None

        # Calculate necessary size for the menu
        menu_size = (self.radius + 50) * 2  # Radius + space for buttons
        self.menu_window.geometry(f"{menu_size}x{menu_size}")

        # Position the menu window centered on the original widget
        parent_x = self.parent_window.winfo_x()
        parent_y = self.parent_window.winfo_y()
        parent_size = self.parent_window.winfo_width()

        menu_x = parent_x + parent_size // 2 - menu_size // 2
        menu_y = parent_y + parent_size // 2 - menu_size // 2
        self.menu_window.geometry(f"{menu_size}x{menu_size}+{menu_x}+{menu_y}")

        # Create canvas for the menu
        canvas_bg = transparent_color if transparent_color else '#f0f0f0'
        self.menu_canvas = tk.Canvas(
            self.menu_window,
            width=menu_size,
            height=menu_size,
            highlightthickness=0,
            bg=canvas_bg
        )
        self.menu_canvas.pack()

        # If no transparentcolor, configure the window background
        if not transparent_color:
            self.menu_window.configure(bg='#f0f0f0')
        # Center of the menu canvas
        canvas_center = menu_size // 2

        # Draw original widget in the center
        widget_size = 60
        center_widget = self.menu_canvas.create_oval(
            canvas_center - widget_size//2, canvas_center - widget_size//2,
            canvas_center + widget_size//2, canvas_center + widget_size//2,
            fill='#4a90e2',
            outline='#2c5aa0',
            width=2,
            tags="center_widget"
        )

        # Central widget text
        self.menu_canvas.create_text(
            canvas_center, canvas_center,
            text="📝",
            font=("Arial", 20),
            fill='white',
            tags="center_widget"
        )

        # Bind for context menu in the center
        self.menu_canvas.tag_bind("center_widget", "<Button-3>", self._on_center_right_click)

        # Separate navigation buttons from the others
        nav_buttons = []
        content_buttons = []

        for item in self.items:
            if "Anterior" in item['text'] or "Siguiente" in item['text']:
                nav_buttons.append(item)
            else:
                content_buttons.append(item)

        # Draw content buttons in a circle
        if content_buttons:
            angle_step = 2 * math.pi / len(content_buttons)
            for i, item in enumerate(content_buttons):
                angle = i * angle_step - math.pi / 2  # Start from the top

                # Calculate position
                x = canvas_center + self.radius * math.cos(angle)
                y = canvas_center + self.radius * math.sin(angle)

                # Create circular button
                button_size = 50
                button = self.menu_canvas.create_oval(
                    x - button_size // 2, y - button_size // 2,
                    x + button_size // 2, y + button_size // 2,
                    fill=item['color'],
                    outline='#2c5aa0',
                    width=2,
                    tags=f"dial_button_{i}"
                )

                # Extract icon and text from item
                text_parts = item['text'].split(' ', 1)
                if len(text_parts) > 1 and len(text_parts[0]) <= 2:
                    icon = text_parts[0]
                    label = text_parts[1]
                else:
                    icon = ""
                    label = item['text']

                # Icon inside the button (centered and white)
                icon_item = None
                if icon:
                    icon_item = self.menu_canvas.create_text(
                        x, y,  # Centered on the button
                        text=icon,
                        fill='white',
                        font=("Arial", 18, "bold"),
                        tags=f"dial_button_{i}"
                    )

                # Text below the button (smaller)
                display_text = label[:10] if len(label) > 10 else label
                text_y = y + button_size // 2 + 12
                text_item = self.menu_canvas.create_text(
                    x, text_y,
                    text=display_text,
                    fill='black',
                    font=("Arial", 8, "bold"),
                    tags=f"dial_button_{i}"
                )

                # Save reference and callback
                button_data = {
                    'button': button,
                    'icon': icon_item,
                    'text': text_item,
                    'callback': item['callback'],
                    'full_text': item['text'],
                    'tag': f"dial_button_{i}"
                }
                self.buttons.append(button_data)

                # Bind click event to all button elements
                def make_callback(cb):
                    return lambda e: self._on_button_click(cb)

                self.menu_canvas.tag_bind(f"dial_button_{i}", "<Button-1>", 
                                        make_callback(item['callback']))

        # Draw navigation buttons at the bottom (left to right)
        if nav_buttons:
            nav_y = canvas_center + self.radius + 30  # Fixed position at the bottom
            nav_spacing = 100  # Spacing between buttons
            start_x = canvas_center - (len(nav_buttons) - 1) * nav_spacing // 2

            for i, item in enumerate(nav_buttons):
                x = start_x + i * nav_spacing
                y = nav_y

                # Create rectangular button for navigation
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

                # Navigation button text
                nav_text = self.menu_canvas.create_text(
                    x, y,
                    text=item['text'],
                    fill='white',
                    font=("Arial", 9, "bold"),
                    tags=f"nav_button_{i}"
                )

                # Save reference
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

        # Bind to close the menu when clicking outside
        self.menu_canvas.bind("<Button-1>", self._on_canvas_click)

        print(f"DEBUG: Created menu window with {len(self.items)} items")

    def hide(self):
        """Hide dial menu"""
        if not self.is_visible:
            return

        self.is_visible = False
        self.buttons.clear()

    # Destroy menu window if it exists
        if self.menu_window:
            self.menu_window.destroy()
            self.menu_window = None
            self.menu_canvas = None

    def _on_button_click(self, callback):
        """Handle click on dial button"""
        self.hide()
        if callback:
            callback()

    def _on_canvas_click(self, event):
        """Handle click on canvas (outside buttons)"""
    # Only close if the click was not on a button
        clicked_item = self.menu_canvas.find_closest(event.x, event.y)[0]
        clicked_tags = self.menu_canvas.gettags(clicked_item)
    # Check if any tag contains "button"
        is_button = any("button" in tag for tag in clicked_tags)
        if not is_button:
            self.hide()

    def _on_center_right_click(self, event):
        """Show context menu in center"""
        context_menu = tk.Menu(self.menu_window, tearoff=0)

    # Add options to the context menu
        if 'buscar' in self.context_menu_callbacks:
            search_label = _("search_cheatsheets", fallback="🔍 Buscar")
            context_menu.add_command(
                label=search_label,
                command=self.context_menu_callbacks['buscar'])
            context_menu.add_separator()

        if 'nueva' in self.context_menu_callbacks:
            context_menu.add_command(
                label=_("new_cheatsheet"),
                command=self.context_menu_callbacks['nueva'])

        if 'tags' in self.context_menu_callbacks:
            context_menu.add_command(
                label=_("select_tag_title"),
                command=self.context_menu_callbacks['tags'])

        if 'gestion' in self.context_menu_callbacks:
            context_menu.add_command(
                label=_("manage_tags"),
                command=self.context_menu_callbacks['gestion'])

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()


class CheatSheetEditor:
    """Popup editor for creating/editing cheatsheets"""

    def __init__(self, parent, cheatsheet_data=None, on_save_callback=None):
        self.parent = parent
        self.cheatsheet_data = cheatsheet_data or {}
        self.on_save_callback = on_save_callback

        self.window = tk.Toplevel(parent)
        self.window.title(_("cheatsheet_editor_title"))
        self.window.geometry("600x500")
        self.window.attributes('-topmost', True)

        self.setup_ui()
        self.load_data()

        # Hacer modal después de que la ventana esté completamente configurada
        self.window.update()
        self.window.grab_set()  # Modal

    def setup_ui(self):
        """Setup editor interface"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Título
        ttk.Label(main_frame, text=_("title") + ":").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var,
                                     width=50)
        self.title_entry.grid(row=1, column=0, columnspan=2,
                              sticky=(tk.W, tk.E), pady=(0, 10))

        # Tags
        ttk.Label(main_frame, text=_("tags") + ":").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))

        # Frame for dynamic tags
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
        self.add_tag_button = ttk.Button(selector_frame, text=_("add"),
                                         command=self.add_selected_tag)
        self.add_tag_button.pack(side=tk.LEFT, padx=(0, 5))

        # Entry para crear nuevo tag
        self.new_tag_var = tk.StringVar()
        self.new_tag_entry = ttk.Entry(selector_frame,
                                       textvariable=self.new_tag_var,
                                       width=15, font=("Arial", 9))
        self.new_tag_entry.pack(side=tk.LEFT, padx=(0, 5))

        # Botón para crear y agregar nuevo tag
        ttk.Button(selector_frame, text=_("create_and_add"),
                   command=self.create_and_add_tag).pack(side=tk.LEFT)

        # Inicializar tags disponibles
        self.update_available_tags()

        # Items
        ttk.Label(main_frame, text=_("items") + ":").grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5))

        # Frame para items con scrollbar
        items_frame = ttk.Frame(main_frame)
        items_frame.grid(row=5, column=0, columnspan=2,
                         sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.items_text = scrolledtext.ScrolledText(items_frame, height=15,
                                                    width=70)
        self.items_text.pack(fill=tk.BOTH, expand=True)

        # Instrucciones
        instructions = _("format_instructions")
        ttk.Label(main_frame, text=instructions, foreground="gray").grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_frame, text=_("save"), command=self.save).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text=_("cancel"),
                   command=self.window.destroy).pack(side=tk.LEFT)

        # Configurar grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def load_data(self):
        """Load existing data into editor"""
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
        """Update list of available tags in combobox"""
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
        """Add selected tag from combobox"""
        selected_tag = self.available_tags_var.get().strip()
        if selected_tag and selected_tag not in self.selected_tags:
            self.selected_tags.append(selected_tag)
            self.update_selected_tags_display()
            self.update_available_tags()

    def create_and_add_tag(self):
        """Create and add a new tag"""
        new_tag = self.new_tag_var.get().strip()
        if new_tag and new_tag not in self.selected_tags:
            self.selected_tags.append(new_tag)
            self.new_tag_var.set("")
            self.update_selected_tags_display()
            self.update_available_tags()

    def remove_tag(self, tag):
        """Remove a tag from selection"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            self.update_selected_tags_display()
            self.update_available_tags()

    def update_selected_tags_display(self):
        """Update display of selected tags"""
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
        """Parse items text to list of dictionaries"""
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
        """Save editor data"""
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
    """Cheatsheet viewer in popup window"""

    def __init__(self, parent, cheatsheet_data):
        self.parent = parent
        self.cheatsheet_data = cheatsheet_data

        self.window = tk.Toplevel(parent)
        title = cheatsheet_data.get('title', _('cheatsheet_viewer_title'))
        self.window.title(f"{_('cheatsheet_viewer_title')}: {title}")
        self.window.geometry("500x400")
        self.window.attributes('-topmost', True)

        self.setup_ui()
        self.load_content()

    def setup_ui(self):
        """Setup viewer interface"""
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
        ttk.Button(main_frame, text=_("close"),
                   command=self.window.destroy).pack()

    def load_content(self):
        """Load cheatsheet content"""
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


# Helper functions for colors and themes
def get_tag_color(tag: str) -> str:
    """Get color based on tag"""
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
    """Tag and cheatsheet manager with tabbed interface"""

    def __init__(self, parent, cheatsheet_manager, on_change_callback=None):
        self.parent = parent
        self.cheatsheet_manager = cheatsheet_manager
        self.on_change_callback = on_change_callback
        self.current_filtered_results = []  # Store search results

        self.window = tk.Toplevel(parent)
        self.window.title(_("tag_manager_title"))
        self.window.geometry("600x600")
        self.window.attributes('-topmost', True)

        self.setup_ui()
        self.refresh_tags()
        
        # Force correct language selection and refresh cheatsheets
        self.window.after(200, self._initialize_correct_language)

        # Hacer modal después de configurar
        self.window.update()
        self.window.grab_set()

    def setup_ui(self):
        """Setup tabbed interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Pestaña de Tags
        self.tags_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tags_frame, text=_("tags"))
        self.setup_tags_tab()

        # Pestaña de CheatSheets
        self.cheatsheets_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cheatsheets_frame, text="CheatSheets")
        self.setup_cheatsheets_tab()

        # Botón cerrar
        ttk.Button(main_frame, text=_("close"), command=self.close).pack()

    def setup_tags_tab(self):
        """Setup tag management tab"""

        # Frame para crear nuevo tag
        create_frame = ttk.LabelFrame(self.tags_frame, text=_("create_new_tag"),
                                      padding="5")
        create_frame.pack(fill=tk.X, pady=(0, 10))

        self.new_tag_var = tk.StringVar()
        entry_frame = ttk.Frame(create_frame)
        entry_frame.pack(fill=tk.X)

        ttk.Entry(entry_frame, textvariable=self.new_tag_var,
                  width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(entry_frame, text=_("create"),
                   command=self.create_tag).pack(side=tk.LEFT)

        # Lista de tags existentes
        ttk.Label(self.tags_frame, text=_("existing_tags")).pack(
            anchor=tk.W, pady=(0, 5))

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

        ttk.Button(buttons_frame, text=_("rename"),
                   command=self.rename_tag).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text=_("delete"),
                   command=self.delete_tag).pack(side=tk.LEFT, padx=(0, 5))

    def setup_cheatsheets_tab(self):
        """Setup cheatsheet management tab with language filter"""

        # Language filter
        filter_frame = ttk.Frame(self.cheatsheets_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(filter_frame, text=_("language") + ":").pack(side=tk.LEFT)
        self.language_var = tk.StringVar()
        self.language_combobox = ttk.Combobox(filter_frame, textvariable=self.language_var, state="readonly", width=10)
        self.language_combobox.pack(side=tk.LEFT, padx=(5, 10))

        # Populate language combobox
        supported_langs = self.cheatsheet_manager.get_supported_languages()
        lang_codes = list(supported_langs.keys())
        self.language_combobox['values'] = lang_codes

        # Set combobox value to current app language
        self._set_language_combobox_to_current()

        self.language_combobox.bind('<<ComboboxSelected>>', lambda e: self.refresh_cheatsheets())

        # Register callback to update combobox if app language changes
        self._register_language_update_callback()
        
        # Force an immediate update to ensure correct initial state
        self.window.after(100, self._force_update_language_combobox)

        # Search frame
        search_frame = ttk.Frame(self.cheatsheets_frame)
        search_frame.pack(fill=tk.X, pady=(5, 5))
        
        # Import here to avoid circular import
        from search_components import QuickSearchEntry
        
        # Add quick search entry
        self.quick_search = QuickSearchEntry(
            search_frame, 
            self.cheatsheet_manager,
            on_results_callback=self.on_search_results,
            placeholder=_("search_cheatsheets_placeholder", fallback="Buscar cheatsheets..."),
            width=40
        )
        self.quick_search.get_frame().pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Advanced search button
        advanced_search_btn = ttk.Button(
            search_frame, 
            text=_("advanced_search", fallback="Búsqueda Avanzada"),
            command=self.show_advanced_search
        )
        advanced_search_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Lista de cheatsheets
        ttk.Label(self.cheatsheets_frame, text=_("existing_cheatsheets")).pack(
            anchor=tk.W, pady=(5, 5))

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

        ttk.Button(buttons_frame, text=_("new"),
                   command=self.create_cheatsheet).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text=_("edit"),
                   command=self.edit_cheatsheet).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text=_("delete"),
                   command=self.delete_cheatsheet).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text=_("view"),
                   command=self.view_cheatsheet).pack(side=tk.LEFT)

    def _set_language_combobox_to_current(self):
        # Get current language from parent (FloatingWidget) or manager
        lang_codes = self.language_combobox['values']
        current_lang = None
        
        # Try multiple strategies to get current language
        # Strategy 1: From i18n instance
        i18n = self._find_i18n_instance()
        if i18n:
            current_lang = i18n.get_current_language()
            print(f"DEBUG: Got language from i18n: {current_lang}")
        
        # Strategy 2: From parent's current_language attribute
        if not current_lang and hasattr(self.parent, 'current_language'):
            current_lang = getattr(self.parent, 'current_language', None)
            print(f"DEBUG: Got language from parent: {current_lang}")
        
        # Strategy 3: From cheatsheet_manager default
        if not current_lang:
            current_lang = getattr(self.cheatsheet_manager, 'default_language', None)
            print(f"DEBUG: Got language from manager: {current_lang}")
        
        # Strategy 4: Use first available language
        if not current_lang and lang_codes:
            current_lang = lang_codes[0]
            print(f"DEBUG: Using first available language: {current_lang}")
            
        # Set combobox value
        if current_lang and current_lang in lang_codes:
            self.language_var.set(str(current_lang))
            print(f"DEBUG: Set combobox to: {current_lang}")
        else:
            fallback = str(lang_codes[0]) if lang_codes else ''
            self.language_var.set(fallback)
            print(f"DEBUG: Set combobox to fallback: {fallback}")

    def _register_language_update_callback(self):
        """Register callback for language updates with multiple strategies"""
        # Strategy 1: Try to get i18n instance from parent chain
        i18n = self._find_i18n_instance()
        
        if i18n and hasattr(i18n, 'register_update_callback'):
            def update_language_combobox():
                try:
                    self._force_update_language_combobox()
                except Exception as e:
                    print(f"Error updating language combobox: {e}")
            
            # Store callback reference to prevent garbage collection
            self._language_update_callback = update_language_combobox
            i18n.register_update_callback(update_language_combobox)
            print("DEBUG: Successfully registered language update callback")
        else:
            print("DEBUG: Could not register callback, will use polling method")
            # Strategy 2: Use polling as fallback
            self._setup_language_polling()

    def _find_i18n_instance(self):
        """Find i18n instance from various sources"""
        # Try parent chain
        current = self.parent
        for level in range(3):  # Search up to 3 levels up
            if hasattr(current, 'i18n'):
                i18n = getattr(current, 'i18n', None)
                if i18n:
                    return i18n
            if hasattr(current, 'parent'):
                current = current.parent
            else:
                break
        
        # Try global i18n
        try:
            from i18n import get_i18n
            return get_i18n()
        except (ImportError, AttributeError):
            pass
        
        return None

    def _setup_language_polling(self):
        """Setup periodic polling to check for language changes"""
        self._last_known_language = None
        self._check_language_change()

    def _check_language_change(self):
        """Check if language has changed and update if needed"""
        try:
            if not hasattr(self, 'window') or not self.window.winfo_exists():
                return
            
            i18n = self._find_i18n_instance()
            if i18n:
                current_lang = i18n.get_current_language()
                if self._last_known_language != current_lang:
                    print(f"DEBUG: Language changed from {self._last_known_language} to {current_lang}")
                    self._last_known_language = current_lang
                    self._force_update_language_combobox()
            
            # Schedule next check
            self.window.after(1000, self._check_language_change)  # Check every second
        except Exception as e:
            print(f"Error in language polling: {e}")

    def _force_update_language_combobox(self):
        """Force update of language combobox"""
        try:
            # Check if the window still exists
            if not hasattr(self, 'window') or not self.window.winfo_exists():
                return
            
            # Check if we have the language combobox
            if not hasattr(self, 'language_combobox') or not hasattr(self, 'language_var'):
                return
            
            print("DEBUG: Forcing language combobox update")
            
            # Get current language from i18n
            i18n = self._find_i18n_instance()
            current_lang = None
            if i18n:
                current_lang = i18n.get_current_language()
            
            # If no i18n, try to get from parent
            if not current_lang and hasattr(self.parent, 'current_language'):
                current_lang = getattr(self.parent, 'current_language', None)
            
            # Refresh language list
            supported_langs = self.cheatsheet_manager.get_supported_languages()
            lang_codes = list(supported_langs.keys())
            
            # Update combobox values
            self.language_combobox['values'] = lang_codes
            
            # Set appropriate language
            if current_lang and current_lang in lang_codes:
                if self.language_var.get() != current_lang:
                    print(f"DEBUG: Updating combobox from {self.language_var.get()} to {current_lang}")
                    self.language_var.set(current_lang)
                    # Force refresh of cheatsheets list
                    self.refresh_cheatsheets()
            elif lang_codes:
                if not self.language_var.get():
                    self.language_var.set(lang_codes[0])
                    self.refresh_cheatsheets()
            else:
                self.language_var.set("")
            
        except Exception as e:
            print(f"Error in _force_update_language_combobox: {e}")

    def refresh_tags(self):
        """Update tag list"""
        self.tags_listbox.delete(0, tk.END)

        tags_info = self.cheatsheet_manager.get_tags_with_usage()
        for tag_info in tags_info:
            display_text = (f"{tag_info['name']} "
                          f"({tag_info['usage_count']} usos)")
            self.tags_listbox.insert(tk.END, display_text)

    def create_tag(self):
        """Create a new tag"""
        tag_name = self.new_tag_var.get().strip()

        if not tag_name:
            messagebox.showwarning(_("error_invalid_tag_name"),
                                   _("error_invalid_tag_name"))
            return

        if not self.cheatsheet_manager.create_tag(tag_name):
            messagebox.showerror(_("error_invalid_tag_name"),
                                 _("error_invalid_tag_name"))
            return

        # El tag se creará automáticamente cuando se use en una cheatsheet
        messagebox.showinfo(_("info_tag_validated", tag_name),
                            _("info_tag_validated", tag_name))
        self.new_tag_var.set("")

    def rename_tag(self):
        """Rename selected tag"""
        selection = self.tags_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", 
                                 "Seleccione un tag para renombrar")
            return

        # Obtener el tag seleccionado
        selected_text = self.tags_listbox.get(selection[0])
        old_tag = selected_text.split(" (")[0]  # Extraer nombre del tag

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
        """Delete selected tag"""
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
        """Update cheatsheet list according to selected language"""
        if hasattr(self, 'cheatsheets_listbox'):
            self.cheatsheets_listbox.delete(0, tk.END)

            # Get selected language from combobox
            selected_lang = self.language_var.get() if hasattr(self, 'language_var') else None
            
            print(f"DEBUG: refresh_cheatsheets - selected_lang: {selected_lang}")
            
            # Always filter by language if we have a valid one
            if selected_lang and selected_lang.strip():
                if self.cheatsheet_manager.validate_language(selected_lang):
                    cheatsheets = self.cheatsheet_manager.get_cheatsheets_by_language(selected_lang)
                    print(f"DEBUG: Found {len(cheatsheets)} cheatsheets for language {selected_lang}")
                else:
                    print(f"DEBUG: Invalid language {selected_lang}, showing all cheatsheets")
                    cheatsheets = self.cheatsheet_manager.get_all_cheatsheets()
            else:
                print("DEBUG: No language selected, showing all cheatsheets")
                cheatsheets = self.cheatsheet_manager.get_all_cheatsheets()

            for sheet in cheatsheets:
                title = sheet.get('title', 'Sin título')
                tags = ', '.join(sheet.get('tags', []))
                lang = sheet.get('language', '')
                display_text = f"{title} [{tags}] ({lang})"
                self.cheatsheets_listbox.insert(tk.END, display_text)
                
            print(f"DEBUG: Added {len(cheatsheets)} cheatsheets to listbox")

    def create_cheatsheet(self):
        """Create new cheatsheet"""
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
        """Edit selected cheatsheet"""
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
        """Delete selected cheatsheet"""
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
        """View selected cheatsheet"""
        selection = self.cheatsheets_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una cheatsheet para ver")
            return

        cheatsheets = self.cheatsheet_manager.get_all_cheatsheets()
        selected_sheet = cheatsheets[selection[0]]

        CheatSheetViewer(self.window, selected_sheet)

    def on_search_results(self, results, query):
        """Handle search results from quick search"""
        # Clear current listbox
        self.cheatsheets_listbox.delete(0, tk.END)
        
        # Add search results to listbox
        for sheet in results:
            title = sheet.get('title', 'Sin título')
            language = sheet.get('language', 'es')
            tags = ', '.join(sheet.get('tags', []))
            items_count = len(sheet.get('items', []))
            
            # Format display text
            display_text = f"{title} ({language}) - {items_count} items"
            if tags:
                display_text += f" [{tags}]"
            
            self.cheatsheets_listbox.insert(tk.END, display_text)
        
        # Store current results for access by other methods
        self.current_filtered_results = results
        
        # Update label to show search info
        if query:
            info_text = f"Resultados de búsqueda para '{query}': {len(results)} encontrados"
        else:
            info_text = f"Mostrando todos los cheatsheets: {len(results)}"
        
        # Find and update the label (this could be improved with a dedicated label)
        for child in self.cheatsheets_frame.winfo_children():
            if isinstance(child, ttk.Label) and hasattr(child, 'cget'):
                try:
                    current_text = child.cget('text')
                    if 'cheatsheets' in current_text.lower() or 'resultados' in current_text.lower():
                        child.config(text=info_text)
                        break
                except Exception:
                    pass

    def show_advanced_search(self):
        """Show advanced search dialog"""
        from search_components import show_search_dialog
        
        def on_select(cheatsheet_data):
            # Refresh the list to show all results and highlight the selected one
            self.refresh_cheatsheets()
            
            # Try to select the chosen cheatsheet in the listbox
            filename = cheatsheet_data.get('filename')
            if filename:
                all_sheets = self.cheatsheet_manager.get_all_cheatsheets()
                for i, sheet in enumerate(all_sheets):
                    if sheet.get('filename') == filename:
                        self.cheatsheets_listbox.selection_clear(0, tk.END)
                        self.cheatsheets_listbox.selection_set(i)
                        self.cheatsheets_listbox.see(i)
                        break
        
        # Get current language from combobox
        current_lang = self.language_var.get() if hasattr(self, 'language_var') else 'es'
        
        show_search_dialog(
            parent=self.window,
            cheatsheet_manager=self.cheatsheet_manager,
            on_select_callback=on_select,
            current_language=current_lang,
            current_tag="all"
        )

    def _initialize_correct_language(self):
        """Initialize TagManager with correct language from app"""
        print("DEBUG: _initialize_correct_language() called")
        
        # Force update language combobox to current app language
        self._force_update_language_combobox()
        
        # Refresh cheatsheets with correct language
        self.refresh_cheatsheets()

    def update_language_display(self):
        """Update language combobox when app language changes"""
        print("DEBUG: update_language_display() called manually")
        self._force_update_language_combobox()

    def close(self):
        """Close window"""
        self.window.destroy()


def truncate_text(text: str, max_length: int = 10) -> str:
    """Truncate text for small buttons"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
