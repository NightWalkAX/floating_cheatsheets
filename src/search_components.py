"""
Search Components
Search and filter components for cheatsheets
"""

import tkinter as tk
from tkinter import ttk
from i18n import get_i18n, _


class SearchDialog:
    """Search dialog for finding cheatsheets"""

    def __init__(self, parent, cheatsheet_manager, on_select_callback=None,
                 current_language=None, current_tag="all"):
        self.parent = parent
        self.cheatsheet_manager = cheatsheet_manager
        self.on_select_callback = on_select_callback
        self.current_language = current_language or "es"
        self.current_tag = current_tag
        
        self.window = None
        self.search_var = None
        self.tag_filter_var = None
        self.language_filter_var = None
        self.results_tree = None
        self.last_search_results = []
        
        self.i18n = get_i18n()
        
    def show(self):
        """Show search dialog"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_set()
            return
            
        self.window = tk.Toplevel(self.parent)
        title = _("search_cheatsheets_title", fallback="Buscar CheatSheets")
        self.window.title(title)
        self.window.geometry("650x500")
        self.window.attributes('-topmost', True)
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_initial_data()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"650x500+{x}+{y}")
        
    def setup_ui(self):
        """Setup search dialog interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Search entry
        ttk.Label(main_frame, text=_("search", fallback="Buscar") + ":").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
            
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=3,
                          sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame,
                                     textvariable=self.search_var,
                                     font=("Arial", 11))
        self.search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E),
                              padx=(0, 5))
        
        # Search button
        search_text = _("search", fallback="Buscar")
        self.search_button = ttk.Button(search_frame, text=search_text,
                                        command=self.perform_search)
        self.search_button.grid(row=0, column=1)
        
        # Clear button
        clear_text = _("clear", fallback="Limpiar")
        self.clear_button = ttk.Button(search_frame, text=clear_text,
                                       command=self.clear_search)
        self.clear_button.grid(row=0, column=2, padx=(5, 0))
        
        # Filters frame
        filters_text = _("filters", fallback="Filtros")
        filters_frame = ttk.LabelFrame(main_frame, text=filters_text,
                                       padding="5")
        filters_frame.grid(row=2, column=0, columnspan=3,
                           sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Tag filter
        ttk.Label(filters_frame, text=_("tag", fallback="Etiqueta") + ":").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
            
        self.tag_filter_var = tk.StringVar()
        self.tag_filter_combo = ttk.Combobox(filters_frame, textvariable=self.tag_filter_var,
                                            state="readonly", width=15)
        self.tag_filter_combo.grid(row=0, column=1, padx=(0, 10))
        self.tag_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.perform_search())
        
        # Language filter
        ttk.Label(filters_frame, text=_("language", fallback="Idioma") + ":").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5))
            
        self.language_filter_var = tk.StringVar()
        self.language_filter_combo = ttk.Combobox(filters_frame, textvariable=self.language_filter_var,
                                                 state="readonly", width=15)
        self.language_filter_combo.grid(row=0, column=3, padx=(0, 10))
        self.language_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.perform_search())
        
        # Results info
        self.results_info_var = tk.StringVar()
        self.results_info_label = ttk.Label(main_frame, textvariable=self.results_info_var,
                                           foreground="gray")
        self.results_info_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Results tree
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_container = ttk.Frame(results_frame)
        tree_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)
        
        self.results_tree = ttk.Treeview(tree_container, columns=('title', 'tags', 'language', 'items'),
                                        show='headings', height=12)
        
        # Configure columns
        self.results_tree.heading('title', text=_("title", fallback="Título"))
        self.results_tree.heading('tags', text=_("tags", fallback="Etiquetas"))
        self.results_tree.heading('language', text=_("language", fallback="Idioma"))
        self.results_tree.heading('items', text=_("items_count", fallback="Items"))
        
        self.results_tree.column('title', width=200, minwidth=150)
        self.results_tree.column('tags', width=150, minwidth=100)
        self.results_tree.column('language', width=80, minwidth=60)
        self.results_tree.column('items', width=60, minwidth=50)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind double-click to select
        self.results_tree.bind('<Double-1>', self.on_item_double_click)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Select button
        self.select_button = ttk.Button(buttons_frame, text=_("select", fallback="Seleccionar"),
                                       command=self.select_cheatsheet, state=tk.DISABLED)
        self.select_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # View button
        self.view_button = ttk.Button(buttons_frame, text=_("view", fallback="Ver"),
                                     command=self.view_cheatsheet, state=tk.DISABLED)
        self.view_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Close button
        self.close_button = ttk.Button(buttons_frame, text=_("close", fallback="Cerrar"),
                                      command=self.close)
        self.close_button.pack(side=tk.RIGHT)
        
        # Bind selection change
        self.results_tree.bind('<<TreeviewSelect>>', self.on_selection_change)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Focus on search entry
        self.search_entry.focus_set()
        
    def load_initial_data(self):
        """Load initial data for filters and results"""
        try:
            # Load tags for filter
            all_tags = self.cheatsheet_manager.get_all_tags()
            tag_options = [_("all_tags", fallback="Todas las etiquetas")] + all_tags
            self.tag_filter_combo['values'] = tag_options
            
            # Set current tag if specified
            if self.current_tag and self.current_tag != "all":
                if self.current_tag in all_tags:
                    self.tag_filter_var.set(self.current_tag)
                else:
                    self.tag_filter_var.set(tag_options[0])
            else:
                self.tag_filter_var.set(tag_options[0])
            
            # Load languages for filter
            supported_languages = self.cheatsheet_manager.get_supported_languages()
            language_options = [_("all_languages", fallback="Todos los idiomas")]
            for code, name in supported_languages.items():
                language_options.append(f"{name} ({code})")
            
            self.language_filter_combo['values'] = language_options
            
            # Set current language if specified
            if self.current_language:
                current_lang_display = None
                for code, name in supported_languages.items():
                    if code == self.current_language:
                        current_lang_display = f"{name} ({code})"
                        break
                
                if current_lang_display and current_lang_display in language_options:
                    self.language_filter_var.set(current_lang_display)
                else:
                    self.language_filter_var.set(language_options[0])
            else:
                self.language_filter_var.set(language_options[0])
            
            # Load initial results (all cheatsheets)
            self.perform_search()
            
        except Exception as e:
            print(f"Error loading initial data: {e}")
            self.results_info_var.set(_("error_loading_data", fallback="Error cargando datos"))
    
    def perform_search(self):
        """Perform search with current filters"""
        try:
            query = self.search_var.get().strip()
            
            # Get selected tag
            selected_tag = self.tag_filter_var.get()
            if selected_tag == _("all_tags", fallback="Todas las etiquetas"):
                tag_filter = "all"
            else:
                tag_filter = selected_tag
            
            # Get selected language
            selected_language = self.language_filter_var.get()
            if selected_language == _("all_languages", fallback="Todos los idiomas"):
                language_filter = None
            else:
                # Extract language code from "Name (code)" format
                if '(' in selected_language and selected_language.endswith(')'):
                    language_filter = selected_language.split('(')[-1][:-1]
                else:
                    language_filter = None
            
            # Perform search
            if query:
                # Search with query
                if language_filter:
                    results = self.cheatsheet_manager.search_cheatsheets_by_language(query, language_filter)
                else:
                    results = self.cheatsheet_manager.search_cheatsheets(query)
                
                # Apply tag filter to search results if needed
                if tag_filter != "all":
                    results = [sheet for sheet in results if tag_filter in sheet.get('tags', [])]
            else:
                # No query, get by filters
                if tag_filter != "all" and language_filter:
                    results = self.cheatsheet_manager.get_cheatsheets_by_tag_and_language(tag_filter, language_filter)
                elif tag_filter != "all":
                    results = self.cheatsheet_manager.get_cheatsheets_by_tag(tag_filter)
                elif language_filter:
                    results = self.cheatsheet_manager.get_cheatsheets_by_language(language_filter)
                else:
                    results = self.cheatsheet_manager.get_all_cheatsheets()
            
            self.last_search_results = results
            self.update_results_display(results)
            
        except Exception as e:
            print(f"Error performing search: {e}")
            self.results_info_var.set(_("search_error", fallback="Error en la búsqueda"))
            self.last_search_results = []
            self.update_results_display([])
    
    def update_results_display(self, results):
        """Update results display"""
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add new results
        for sheet in results:
            title = sheet.get('title', _("no_title", fallback="Sin título"))
            tags = ', '.join(sheet.get('tags', []))
            language = sheet.get('language', 'es')
            items_count = len(sheet.get('items', []))
            
            # Get language display name
            supported_languages = self.cheatsheet_manager.get_supported_languages()
            language_display = supported_languages.get(language, language)
            
            self.results_tree.insert('', 'end', values=(title, tags, language_display, items_count),
                                   tags=(sheet.get('filename', ''),))
        
        # Update results info
        count = len(results)
        if count == 0:
            info_text = _("no_results_found", fallback="No se encontraron resultados")
        elif count == 1:
            info_text = _("one_result_found", fallback="1 resultado encontrado")
        else:
            info_text = _("multiple_results_found", fallback=f"{count} resultados encontrados").format(count)
        
        self.results_info_var.set(info_text)
        
        # Update button states
        self.update_button_states()
    
    def clear_search(self):
        """Clear search and filters"""
        self.search_var.set("")
        
        # Reset filters to "all"
        tag_options = list(self.tag_filter_combo['values'])
        if tag_options:
            self.tag_filter_var.set(tag_options[0])
        
        language_options = list(self.language_filter_combo['values'])
        if language_options:
            self.language_filter_var.set(language_options[0])
        
        # Perform search to show all results
        self.perform_search()
        
        # Focus back to search entry
        self.search_entry.focus_set()
    
    def on_selection_change(self, event):
        """Handle selection change in results tree"""
        self.update_button_states()
    
    def update_button_states(self):
        """Update button states based on selection"""
        selected_items = self.results_tree.selection()
        has_selection = len(selected_items) > 0
        
        state = tk.NORMAL if has_selection else tk.DISABLED
        self.select_button.config(state=state)
        self.view_button.config(state=state)
    
    def on_item_double_click(self, event):
        """Handle double-click on item"""
        self.select_cheatsheet()
    
    def get_selected_cheatsheet(self):
        """Get currently selected cheatsheet data"""
        selected_items = self.results_tree.selection()
        if not selected_items:
            return None
        
        selected_item = selected_items[0]
        item_tags = self.results_tree.item(selected_item, 'tags')
        if not item_tags:
            return None
        
        filename = item_tags[0]
        
        # Find the cheatsheet in results
        for sheet in self.last_search_results:
            if sheet.get('filename') == filename:
                return sheet
        
        return None
    
    def select_cheatsheet(self):
        """Select cheatsheet and close dialog"""
        selected_sheet = self.get_selected_cheatsheet()
        if selected_sheet and self.on_select_callback:
            self.close()
            self.on_select_callback(selected_sheet)
    
    def view_cheatsheet(self):
        """View selected cheatsheet"""
        selected_sheet = self.get_selected_cheatsheet()
        if selected_sheet:
            from ui_components import CheatSheetViewer
            viewer = CheatSheetViewer(self.window, selected_sheet)
    
    def close(self):
        """Close dialog"""
        if self.window:
            self.window.grab_release()
            self.window.destroy()
            self.window = None


class QuickSearchEntry:
    """Quick search entry widget for embedding in other interfaces"""
    
    def __init__(self, parent, cheatsheet_manager, on_results_callback=None,
                 placeholder="Buscar cheatsheets...", width=30):
        self.parent = parent
        self.cheatsheet_manager = cheatsheet_manager
        self.on_results_callback = on_results_callback
        self.placeholder = placeholder
        
        self.frame = ttk.Frame(parent)
        self.search_var = tk.StringVar()
        self.last_results = []
        
        self.setup_ui(width)
        
    def setup_ui(self, width):
        """Setup quick search UI"""
        # Search entry
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var,
                                     width=width, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Search button
        self.search_button = ttk.Button(self.frame, text="🔍", width=3,
                                       command=self.perform_search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        self.clear_button = ttk.Button(self.frame, text="✖", width=3,
                                      command=self.clear_search)
        self.clear_button.pack(side=tk.LEFT)
        
        # Bind events
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        self.search_entry.bind('<KeyRelease>', self.on_key_release)
        
        # Placeholder functionality
        self.setup_placeholder()
    
    def setup_placeholder(self):
        """Setup placeholder functionality"""
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.config(foreground='gray')
        
        def on_focus_in(event):
            if self.search_entry.get() == self.placeholder:
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(foreground='black')
        
        def on_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, self.placeholder)
                self.search_entry.config(foreground='gray')
        
        self.search_entry.bind('<FocusIn>', on_focus_in)
        self.search_entry.bind('<FocusOut>', on_focus_out)
    
    def get_frame(self):
        """Get the main frame widget"""
        return self.frame
    
    def get_search_query(self):
        """Get current search query"""
        query = self.search_var.get().strip()
        return query if query != self.placeholder else ""
    
    def perform_search(self):
        """Perform search and notify callback"""
        query = self.get_search_query()
        
        try:
            if query:
                results = self.cheatsheet_manager.search_cheatsheets(query)
            else:
                results = self.cheatsheet_manager.get_all_cheatsheets()
            
            self.last_results = results
            
            if self.on_results_callback:
                self.on_results_callback(results, query)
                
        except Exception as e:
            print(f"Error in quick search: {e}")
            self.last_results = []
            if self.on_results_callback:
                self.on_results_callback([], query)
    
    def clear_search(self):
        """Clear search"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, self.placeholder)
        self.search_entry.config(foreground='gray')
        self.perform_search()  # Show all results
    
    def on_key_release(self, event):
        """Handle key release for real-time search"""
        # Only perform real-time search for certain keys
        if event.keysym in ['BackSpace', 'Delete'] or len(event.keysym) == 1:
            # Delay search to avoid too many calls
            self.search_entry.after(300, self.perform_search)
    
    def set_query(self, query):
        """Set search query programmatically"""
        self.search_entry.delete(0, tk.END)
        if query:
            self.search_entry.insert(0, query)
            self.search_entry.config(foreground='black')
        else:
            self.search_entry.insert(0, self.placeholder)
            self.search_entry.config(foreground='gray')
    
    def get_last_results(self):
        """Get last search results"""
        return self.last_results


# Helper functions
def show_search_dialog(parent, cheatsheet_manager, on_select_callback=None,
                      current_language=None, current_tag="all"):
    """Convenience function to show search dialog"""
    dialog = SearchDialog(parent, cheatsheet_manager, on_select_callback,
                         current_language, current_tag)
    dialog.show()
    return dialog