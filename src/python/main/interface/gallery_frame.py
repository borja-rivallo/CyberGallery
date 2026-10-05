import customtkinter as ctk
from tkinter import filedialog, simpledialog, messagebox
import os
from src.python.main.interface.password_dialog import ask_encryption_password

class GalleryFrame(ctk.CTkTabview):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_tabs()

    def setup_tabs(self):
        """Crea y configura las pestañas de la galería"""
        self.add("Inicio")
        self.add("Subir obra")
        self.add("Mis obras")
        self.add("Galería pública")
        self.add("Mi perfil")

        self.setup_home_tab(self.tab("Inicio"))
        self.setup_upload_tab(self.tab("Subir obra"))
        self.setup_my_artworks_tab(self.tab("Mis obras"))
        self.setup_public_gallery_tab(self.tab("Galería pública"))
        self.setup_profile_tab(self.tab("Mi perfil"))

    def setup_home_tab(self, tab):
        """Configura la pestaña de inicio"""
        welcome = ctk.CTkLabel(
            tab,
            text=f"¡Bienvenido, {self.app.current_user_name}!",
            font=("Arial", 28, "bold")
        )
        welcome.pack(pady=30)

        email_label = ctk.CTkLabel(
            tab,
            text=f"Conectado como: {self.app.current_user}",
            font=("Arial", 16),
            text_color="lightblue"
        )
        email_label.pack(pady=8)

        # Información de la aplicación
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(pady=30, padx=30, fill="x")

        ctk.CTkLabel(
            info_frame,
            text="Características de CyberGallery:",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        features = [
            "   - Encriptación AES-GCM para todas tus obras",
            "   - Soporte para imágenes JPG, PNG, BMP",
            "   - Opción de hacer obras públicas o privadas",
            "   - Gestión completa de tu portfolio digital",
            "   - Protección de propiedad intelectual"
        ]

        for feature in features:
            ctk.CTkLabel(
                info_frame,
                text=feature,
                font=("Arial", 14),
                justify="left"
            ).pack(anchor="w", pady=3)

        # Botón de cerrar sesión
        logout_btn = ctk.CTkButton(
            tab,
            text="Cerrar sesión",
            font=("Arial", 20, "bold"),
            command=self.app.logout,
            fg_color="#DC143C",
            hover_color="#B22222",
            width=250,
            height=50
        )
        logout_btn.pack(pady=30)

    def setup_upload_tab(self, tab):
        """Configura la pestaña de subida de obras"""
        title = ctk.CTkLabel(
            tab,
            text="Subir nueva obra de arte",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Información del artista
        owner_info = ctk.CTkLabel(
            tab,
            text=f"Artista: {self.app.current_user_name}",
            font=("Arial", 16),
            text_color="lightgreen"
        )
        owner_info.pack(pady=8)

        # Formulario de subida
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(pady=20, padx=25, fill="x")

        # Título de la obra
        ctk.CTkLabel(form_frame, text="Título de la obra:", font=("Arial", 14, "bold")).pack(anchor="w", pady=8)
        self.artwork_title = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ej: Estrellas nocturnas",
            width=500,
            height=35
        )
        self.artwork_title.pack(anchor="w", pady=8)

        # Selección de archivo
        ctk.CTkLabel(form_frame, text="Archivo de imagen:", font=("Arial", 14, "bold")).pack(anchor="w", pady=12)
        
        file_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        file_frame.pack(anchor="w", pady=8)

        self.file_path_label = ctk.CTkLabel(
            file_frame,
            text="Ningún archivo seleccionado",
            width=300,
            font=("Arial", 13)
        )
        self.file_path_label.pack(side="left", padx=12)

        browse_btn = ctk.CTkButton(
            file_frame,
            text="Examinar archivos",
            command=self.browse_file,
            width=150,
            height=35
        )
        browse_btn.pack(side="left", padx=12)

        # Configuración de privacidad
        ctk.CTkLabel(form_frame, text="Visibilidad:", font=("Arial", 14, "bold")).pack(anchor="w", pady=12)
        self.public_var = ctk.BooleanVar()
        public_cb = ctk.CTkCheckBox(
            form_frame,
            text="Hacer pública (otros usuarios podrán ver esta obra)",
            variable=self.public_var,
            font=("Arial", 13)
        )
        public_cb.pack(anchor="w", pady=8)

        # Botón de subida
        upload_btn = ctk.CTkButton(
            tab,
            text="Subir y encriptar obra",
            command=self.upload_artwork,
            width=350,
            height=55,
            fg_color="#2E8B57",
            hover_color="#3CB371",
            font=("Arial", 16, "bold")
        )
        upload_btn.pack(pady=25)

        # Estado de la subida
        self.upload_status = ctk.CTkLabel(tab, text="", font=("Arial", 14))
        self.upload_status.pack(pady=12)

        # Variables de instancia
        self.selected_file = None

    def setup_my_artworks_tab(self, tab):
        """Configura la pestaña de las obras pertenecientes al usuario"""
        title = ctk.CTkLabel(
            tab,
            text=f"Mis obras - {self.app.current_user_name}",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Controles
        controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        controls_frame.pack(pady=12)

        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="Actualizar galería",
            command=self.refresh_my_artworks,
            width=180,
            height=35
        )
        refresh_btn.pack(side="left", padx=8)

        # Frame scrollable para las obras
        self.my_artworks_scroll_frame = ctk.CTkScrollableFrame(tab)
        self.my_artworks_scroll_frame.pack(pady=12, padx=20, fill="both", expand=True)

        self.refresh_my_artworks()

    def setup_public_gallery_tab(self, tab):
        """Configura la pestaña de galería pública"""
        title = ctk.CTkLabel(
            tab,
            text="Galería pública",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        subtitle = ctk.CTkLabel(
            tab,
            text="Descubre obras de otros artistas",
            font=("Arial", 16),
            text_color="lightblue"
        )
        subtitle.pack(pady=8)

        # Controles
        controls_frame = ctk.CTkFrame(tab, fg_color="transparent")
        controls_frame.pack(pady=12)

        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="Actualizar galería",
            command=self.refresh_public_gallery,
            width=180,
            height=35
        )
        refresh_btn.pack(side="left", padx=8)

        search_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=25)

        ctk.CTkLabel(search_frame, text="Buscar:", font=("Arial", 14)).pack(side="left", padx=(0, 12))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Título o artista...",
            width=250,
            height=35
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_search_changed())

        # Frame scrollable para las obras públicas
        self.public_scroll_frame = ctk.CTkScrollableFrame(tab)
        self.public_scroll_frame.pack(pady=12, padx=20, fill="both", expand=True)

        self.refresh_public_gallery()

    def setup_profile_tab(self, tab):
        """Configura la pestaña de perfil del usuario"""
        title = ctk.CTkLabel(
            tab,
            text="Mi perfil",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Información del perfil
        profile_frame = ctk.CTkFrame(tab)
        profile_frame.pack(pady=20, padx=25, fill="x")

        ctk.CTkLabel(profile_frame, text="Nombre de artista:", font=("Arial", 14, "bold")).pack(anchor="w", pady=8)
        ctk.CTkLabel(profile_frame, text=self.app.current_user_name, font=("Arial", 16)).pack(anchor="w", pady=3)

        ctk.CTkLabel(profile_frame, text="Email:", font=("Arial", 14, "bold")).pack(anchor="w", pady=12)
        ctk.CTkLabel(profile_frame, text=self.app.current_user, font=("Arial", 16)).pack(anchor="w", pady=3)

    def browse_file(self):
        """Selecciona el archivo de imagen"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar obra de arte",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_path_label.configure(text=f"{filename}")

    def upload_artwork(self):
        """Sube la obra: Hash -> Firma Digital -> Cifrado GCM"""
        if not hasattr(self, "selected_file") or not self.selected_file:
            self.upload_status.configure(text="Selecciona un archivo primero")
            return

        if not self.artwork_title.get().strip():
            self.upload_status.configure(text="Ingresa un título para la obra")
            return

        try:
            # 1. Diálogo para pedir contraseña (necesaria para desbloquear la clave privada)
            password = ask_encryption_password(self.app.root, self.app.account_manager, self.app.current_user)
            if not password:
                self.upload_status.configure(text="Subida cancelada")
                return

            # 2. Feedback visual de seguridad (Importante porque OpenSSL tarda un poco)
            self.upload_status.configure(text="Firmando digitalmente y encriptando obra...", text_color="blue")
            self.app.root.update()

            # 3. Llamada al backend
            artwork_id = self.app.artwork_manager.upload_artwork(
                user=self.app.current_user,
                title=self.artwork_title.get().strip(),
                file_path=self.selected_file,
                is_public=self.public_var.get(),
                password=password
            )

            # 4. Éxito
            self.upload_status.configure(
                text=f"¡Obra firmada y protegida correctamente!",
                text_color="green"
            )

            # Limpieza y actualización
            self.artwork_title.delete(0, "end")
            self.file_path_label.configure(text="Ningún archivo seleccionado")
            self.selected_file = None
            self.public_var.set(False)

            self.refresh_my_artworks()
            self.refresh_public_gallery()

            if self.public_var.get():
                messagebox.showinfo("Obra Pública", "Tu obra es ahora visible en la galería pública.")

        except Exception as e:
            self.upload_status.configure(
                text=f"Error de seguridad: {str(e)}",
                text_color="red"
            )

    def refresh_my_artworks(self):
        """Actualiza la lista de obras del usuario"""
        try:
            # Limpiar contenedor anterior
            for widget in self.my_artworks_scroll_frame.winfo_children():
                widget.destroy()

            artworks = self.app.artwork_manager.get_user_artworks(self.app.current_user)

            if not artworks:
                empty_label = ctk.CTkLabel(
                    self.my_artworks_scroll_frame,
                    text=(
                        "Tu galería está vacía\n\n"
                        "Ve a la pestaña \"Subir obra\" para añadir tu primera obra de arte."
                    ),
                    font=("Arial", 16),
                    justify="center",
                    text_color="gray"
                )
                empty_label.pack(pady=60)
                return

            # Título de la galería
            title_label = ctk.CTkLabel(
                self.my_artworks_scroll_frame,
                text=f"Tu galería ({len(artworks)} obras)",
                font=("Arial", 18, "bold")
            )
            title_label.pack(anchor="w", pady=(0, 25))

            # Crear un frame por cada obra
            for i, artwork in enumerate(artworks, 1):
                self.create_my_artwork_preview(artwork, i)

        except Exception as e:
            error_label = ctk.CTkLabel(
                self.my_artworks_scroll_frame,
                text=f"Error cargando obras: {str(e)}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(pady=25)

    def create_my_artwork_preview(self, artwork, index):
        """Crea la vista previa para una obra perteneciente al usuario"""
        # Frame principal para la obra
        artwork_frame = ctk.CTkFrame(self.my_artworks_scroll_frame)
        artwork_frame.pack(fill="x", pady=12, padx=12)

        # Frame para icono e información
        content_frame = ctk.CTkFrame(artwork_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=12)

        # Lado izquierdo: Icono
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent", width=140)
        left_frame.pack(side="left", padx=(0, 25))

        # Icono basado en el tipo de archivo y visibilidad
        icon_color = "#2E8B57" if artwork.is_public else "#1f6aa5"  # Verde para público, azul para privado
        
        # Texto del icono basado en tipo de archivo
        file_icon = "\nIMAGEN"
        icon_text = f"{file_icon}\n{artwork.file_type.upper().replace('.', '')}"
        
        icon_label = ctk.CTkLabel(
            left_frame,
            text=icon_text,
            font=("Arial", 16, "bold"),
            width=120,
            height=120,
            fg_color=icon_color,
            corner_radius=18,
            text_color="white"
        )
        icon_label.pack()

        # Lado derecho: Información
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="x", expand=True)

        # Información de la obra
        visibility = "PÚBLICA" if artwork.is_public else "PRIVADA"
        file_size_mb = artwork.file_size / (1024 * 1024) if artwork.file_size > 0 else 0

        info_text = (
            f"{artwork.title}\n\n"
            f"Archivo: {artwork.filename}\n"
            f"Tamaño: {file_size_mb:.2f} MB\n"
            f"{visibility}\n"
            f"Subida: {artwork.upload_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"Tipo: {artwork.file_type}"
        )

        info_label = ctk.CTkLabel(
            right_frame,
            text=info_text,
            font=("Arial", 14),
            justify="left",
            anchor="w"
        )
        info_label.pack(anchor="w")

        # Botones de acción
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=(12, 0))

        # Botón para ver detalles
        view_btn = ctk.CTkButton(
            btn_frame,
            text="Ver detalles",
            command=lambda a=artwork: self.view_my_artwork_details(a),
            width=140,
            height=35
        )
        view_btn.pack(side="left", padx=(0, 12))

        # Botón para descargar
        download_btn = ctk.CTkButton(
            btn_frame,
            text="Descargar",
            command=lambda a=artwork: self.download_artwork(a),
            width=140,
            height=35,
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        download_btn.pack(side="left", padx=(0, 12))

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=lambda a=artwork: self.delete_artwork_confirmation(a),
            width=140,
            height=35,
            fg_color="#DC143C",
            hover_color="#B22222"
        )
        delete_btn.pack(side="left", padx=(0, 12))

        # Separador
        if index < len(self.app.artwork_manager.get_user_artworks(self.app.current_user)):
            separator = ctk.CTkFrame(self.my_artworks_scroll_frame, height=2, fg_color="gray")
            separator.pack(fill="x", pady=8)

    def delete_artwork_confirmation(self, artwork):
        """Muestra diálogo de confirmación para eliminar obra"""
        try:
            # Diálogo de confirmación
            response = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Estás seguro de que quieres eliminar la obra?\n\n"
                f"  - Título: {artwork.title}\n"
                f"  - Archivo: {artwork.filename}\n"
                f"  - Fecha: {artwork.upload_date.strftime('%Y-%m-%d')}\n\n"
                f"Esta acción no se puede deshacer",
                icon="warning"
            )
            
            if not response:
                return

            # Mostrar progreso
            progress_window = ctk.CTkToplevel(self.app.root)
            progress_window.title("Eliminando obra...")
            progress_window.geometry("350x120")
            progress_window.transient(self.app.root)
            progress_window.grab_set()
            
            progress_label = ctk.CTkLabel(
                progress_window, 
                text=f"Eliminando \"{artwork.title}\"...",
                font=("Arial", 14)
            )
            progress_label.pack(pady=25)
            
            self.app.root.update()

            # Ejecutar eliminación
            success = self.app.artwork_manager.delete_artwork(artwork.artwork_id)

            progress_window.destroy()

            if success:
                messagebox.showinfo(
                    "Eliminación exitosa",
                    f"La obra \"{artwork.title}\" ha sido eliminada correctamente"
                )
                
                # Actualizar las vistas
                self.refresh_my_artworks()
                self.refresh_public_gallery()
                
            else:
                messagebox.showerror(
                    "Error",
                    f"No se pudo eliminar la obra \"{artwork.title}\""
                )

        except Exception as e:
            if "progress_window" in locals():
                progress_window.destroy()
            messagebox.showerror(
                "Error",
                f"Error al eliminar la obra:\n\n{str(e)}"
            )

    def refresh_public_gallery(self, search_term=None):
        """Actualiza la galería pública"""
        try:
            # Limpiar contenedor anterior
            for widget in self.public_scroll_frame.winfo_children():
                widget.destroy()

            # Obtener obras públicas
            public_artworks = self.app.artwork_manager.get_public_artworks()
            
            # Filtrar por búsqueda si hay término
            if search_term:
                search_term = search_term.lower()
                public_artworks = [
                    art for art in public_artworks 
                    if search_term in art.title.lower() or search_term in art.owner.lower()
                ]

            if not public_artworks:
                empty_text = "No hay obras públicas disponibles"
                if search_term:
                    empty_text = f"No se encontraron obras para \"{search_term}\""
                    
                empty_label = ctk.CTkLabel(
                    self.public_scroll_frame,
                    text=empty_text,
                    font=("Arial", 16),
                    justify="center",
                    text_color="gray"
                )
                empty_label.pack(pady=60)
                return

            # Título con contador
            count_label = ctk.CTkLabel(
                self.public_scroll_frame,
                text=f"Obras públicas ({len(public_artworks)} obras)",
                font=("Arial", 18, "bold")
            )
            count_label.pack(anchor="w", pady=(0, 25))

            # Crear vista para cada obra pública
            for i, artwork in enumerate(public_artworks, 1):
                self.create_public_artwork_preview(artwork, i)

        except Exception as e:
            error_label = ctk.CTkLabel(
                self.public_scroll_frame,
                text=f"Error cargando galería pública: {str(e)}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(pady=25)

    def create_public_artwork_preview(self, artwork, index):
        """Crea la vista previa para una obra pública"""
        # Frame principal para la obra
        artwork_frame = ctk.CTkFrame(self.public_scroll_frame)
        artwork_frame.pack(fill="x", pady=12, padx=12)

        # Frame para icono e información
        content_frame = ctk.CTkFrame(artwork_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=12)

        # Lado izquierdo: Icono representativo
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent", width=140)
        left_frame.pack(side="left", padx=(0, 25))

        # Icono para obra pública (siempre verde)
        file_icon = "\nIMAGEN"
        icon_text = f"{file_icon}\n{artwork.file_type.upper().replace('.', '')}"

        icon_label = ctk.CTkLabel(
            left_frame,
            text=icon_text,
            font=("Arial", 14, "bold"),
            width=120,
            height=120,
            fg_color="#2E8B57",
            corner_radius=18,
            text_color="white"
        )
        icon_label.pack()

        # Lado derecho: Información
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="left", fill="x", expand=True)

        # Información de la obra
        file_size_mb = artwork.file_size / (1024 * 1024) if artwork.file_size > 0 else 0

        info_text = (
            f"{artwork.title}\n\n"
            f"Artista: {artwork.owner}\n"
            f"Archivo: {artwork.filename}\n"
            f"Tamaño: {file_size_mb:.2f} MB\n"
            f"Subida: {artwork.upload_date.strftime('%Y-%m-%d %H:%M')}\n"
            f"Tipo: {artwork.file_type}"
        )

        info_label = ctk.CTkLabel(
            right_frame,
            text=info_text,
            font=("Arial", 14),
            justify="left",
            anchor="w"
        )
        info_label.pack(anchor="w")

        # Botones de acción
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=(12, 0))

        # Botón para ver detalles
        view_btn = ctk.CTkButton(
            btn_frame,
            text="Ver detalles",
            command=lambda a=artwork: self.view_public_artwork_details(a),
            width=140,
            height=35
        )
        view_btn.pack(side="left", padx=(0, 12))

        # Botón para descargar
        download_btn = ctk.CTkButton(
            btn_frame,
            text="Descargar",
            command=lambda a=artwork: self.download_artwork(a),
            width=140,
            height=35,
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        download_btn.pack(side="left", padx=(0, 12))

        # Separador
        if index < len(self.app.artwork_manager.get_public_artworks()):
            separator = ctk.CTkFrame(self.public_scroll_frame, height=2, fg_color="gray")
            separator.pack(fill="x", pady=8)

    def view_my_artwork_details(self, artwork):
        """Ver detalles de obra propia"""
        try:
            # Crear ventana de detalles
            details_window = ctk.CTkToplevel(self.app.root)
            details_window.title(f"{artwork.title}")
            details_window.geometry("550x500")
            details_window.transient(self.app.root)
            
            # Título
            title_label = ctk.CTkLabel(
                details_window,
                text=f"{artwork.title}",
                font=("Arial", 20, "bold")
            )
            title_label.pack(pady=15)
            
            # Información detallada
            info_frame = ctk.CTkFrame(details_window)
            info_frame.pack(pady=20, padx=25, fill="both", expand=True)
            
            visibility = "PÚBLICA" if artwork.is_public else "PRIVADA"
            file_size_mb = artwork.file_size / (1024 * 1024) if artwork.file_size > 0 else 0
            
            # Texto diferente para obras públicas vs privadas
            if artwork.is_public:
                info_text = (
                    f"Archivo: {artwork.filename}\n"
                    f"Tamaño: {file_size_mb:.2f} MB ({artwork.file_size} bytes)\n"
                    f"Hash: {artwork.file_hash[:16]}...\n"
                    f"Subida: {artwork.upload_date.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Tipo: {artwork.file_type}\n"
                    f"Visibilidad: {visibility}\n\n"
                    f"Esta obra es pública y accesible para todos los usuarios"
                )
            else:
                info_text = (
                    f"Archivo: {artwork.filename}\n"
                    f"Tamaño: {file_size_mb:.2f} MB ({artwork.file_size} bytes)\n"
                    f"Hash: {artwork.file_hash[:16]}...\n"
                    f"Subida: {artwork.upload_date.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Tipo: {artwork.file_type}\n"
                    f"Visibilidad: {visibility}\n\n"
                    f"Esta obra está encriptada y protegida con tu contraseña"
                )
            
            info_label = ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=("Arial", 14),
                justify="left"
            )
            info_label.pack(padx=25, pady=25, anchor="w")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {e}")

    def view_public_artwork_details(self, artwork):
        """Muestra los detalles de una obra pública"""
        try:
            # Crear ventana de detalles
            details_window = ctk.CTkToplevel(self.app.root)
            details_window.title(f"{artwork.title}")
            details_window.geometry("550x450")
            details_window.transient(self.app.root)
            
            # Título
            title_label = ctk.CTkLabel(
                details_window,
                text=f"{artwork.title}",
                font=("Arial", 20, "bold")
            )
            title_label.pack(pady=15)
            
            # Información detallada
            info_frame = ctk.CTkFrame(details_window)
            info_frame.pack(pady=20, padx=25, fill="both", expand=True)
            
            file_size_mb = artwork.file_size / (1024 * 1024) if artwork.file_size > 0 else 0
            
            info_text = (
                f"Artista: {artwork.owner}\n\n"
                f"Archivo: {artwork.filename}\n"
                f"Tamaño: {file_size_mb:.2f} MB\n"
                f"Hash: {artwork.file_hash[:16]}...\n"
                f"Subida: {artwork.upload_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"Tipo: {artwork.file_type}\n\n"
                f"Esta obra es pública y puede ser vista por todos los usuarios"
            )
            
            info_label = ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=("Arial", 14),
                justify="left"
            )
            info_label.pack(padx=25, pady=25, anchor="w")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles: {e}")

    def download_artwork(self, artwork):
        """Descarga una obra con VERIFICACIÓN DE FIRMA Y PKI"""
        try:
            # 1. Verificar permisos
            if not artwork.is_public and artwork.owner != self.app.current_user:
                messagebox.showinfo("Acceso denegado", "Solo el autor puede descargar obras privadas.")
                return

            password = None
            # 2. Pedir contraseña (si es privada)
            if not artwork.is_public:
                password = simpledialog.askstring(
                    "Seguridad",
                    f"Introduce contraseña para verificar integridad y descifrar:",
                    show="*", parent=self.app.root
                )
                if not password: return

            # 3. Elegir destino
            # Sugerimos un nombre de archivo
            default_name = f"{artwork.title.replace(' ', '_')}_{artwork.owner}{artwork.file_type}"
            file_path = filedialog.asksaveasfilename(
                title="Guardar obra verificada...",
                defaultextension=artwork.file_type,
                initialfile=default_name
            )
            
            if not file_path: return

            # 4. Feedback visual (Verificando PKI...)
            # Usamos un Toplevel temporal si quieres, o el status label si hay uno visible.
            # Aquí asumimos que usamos un messagebox informativo al final.
            self.app.root.config(cursor="watch") # Poner cursor de espera
            self.app.root.update()

            # 5. LLAMADA AL BACKEND (Ahora devuelve un diccionario con detalles)
            result = self.app.artwork_manager.download_artwork(
                artwork_id=artwork.artwork_id,
                output_path=file_path,
                password=password
            )
            
            self.app.root.config(cursor="") # Restaurar cursor

            # 6. GESTIÓN DE LA RESPUESTA DE SEGURIDAD
            if result["success"]:
                msg = f"✅ Descarga completada en:\n{file_path}\n\n"
                
                # Comprobamos si la verificación de firma fue exitosa
                if result.get("signature_verified"):
                    msg += "🔐 SEGURIDAD VERIFICADA:\n"
                    msg += "   • Firma Digital: VÁLIDA (Integridad confirmada)\n"
                    msg += "   • Certificado PKI: VÁLIDO (Identidad confirmada)\n"
                    msg += f"   • Autor certificado: {artwork.owner}"
                    
                    messagebox.showinfo("Obra Auténtica", msg)
                else:
                    # Esto ocurre si pki_verified=True pero signature_verified=False
                    # (aunque tu backend probablemente lance excepción antes)
                    messagebox.showwarning("Advertencia de Integridad", 
                        "La obra se descargó, pero la firma digital NO coincide con el autor."
                    )
            else:
                # Si success es False, mostramos el error específico
                error_msg = result.get("error", "Error desconocido")
                messagebox.showerror("Error en Descarga", f"No se pudo completar la operación.\n{error_msg}")

        except Exception as e:
            self.app.root.config(cursor="")
            messagebox.showerror("Error Crítico", f"Fallo en el proceso de seguridad:\n{str(e)}")

    def on_search_changed(self):
        """Maneja un cambio en la búsqueda"""
        search_term = self.search_entry.get().strip()
        # Si está vacío o solo espacios, refrescar sin filtro
        if not search_term:
            self.refresh_public_gallery()
        else:
            self.refresh_public_gallery(search_term)