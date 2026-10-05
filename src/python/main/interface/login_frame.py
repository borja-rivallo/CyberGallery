import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        """Configurar la interfaz de login"""
        self.pack(pady=50, padx=50, fill="both", expand=True)

        # Título principal
        title = ctk.CTkLabel(
            self,
            text="CyberGallery",
            font=("Arial", 32, "bold")
        )
        title.pack(pady=30)

        subtitle = ctk.CTkLabel(
            self,
            text="Plataforma segura para artistas",
            font=("Arial", 16),
            text_color="lightblue"
        )
        subtitle.pack(pady=8)

        # Campos de entrada
        self.name_entry = ctk.CTkEntry(
            self,
            placeholder_text="Nombre de usuario",
            width=350,
            height=40
        )
        self.name_entry.pack(pady=12)

        self.email_entry = ctk.CTkEntry(
            self,
            placeholder_text="Email",
            width=350,
            height=40
        )
        self.email_entry.pack(pady=12)

        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Contraseña",
            show="*",
            width=350,
            height=40
        )
        self.password_entry.pack(pady=12)

        # Información de seguridad
        security_info = ctk.CTkLabel(
            self,
            text="Tu contraseña se usa para:\n• Iniciar sesión\n• Encriptar tus obras\n• Proteger tu propiedad intelectual",
            font=("Arial", 13),
            text_color="lightgreen",
            wraplength=450,
            justify="center"
        )
        security_info.pack(pady=12)

        # Requisitos de contraseña
        requirements = ctk.CTkLabel(
            self,
            text="Requisitos de seguridad: 10+ caracteres, 5+ letras, 2+ mayúsculas, 3+ números y 2+ especiales",
            font=("Arial", 12),
            text_color="gray",
            wraplength=450
        )
        requirements.pack(pady=8)

        # Botones de acción
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)

        login_btn = ctk.CTkButton(
            btn_frame,
            text="Iniciar Sesión",
            command=self.login,
            width=160,
            height=45,
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        login_btn.pack(side="left", padx=18)

        register_btn = ctk.CTkButton(
            btn_frame,
            text="Registrar cuenta",
            command=self.register,
            width=160,
            height=45
        )
        register_btn.pack(side="left", padx=18)

        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 12))
        self.status_label.pack(pady=12)

        # Información para testing
        testing_info = ctk.CTkLabel(
            self,
            text="Para login: email y contraseña\nPara registro: nombre de usuario, email y contraseña",
            font=("Arial", 12),
            text_color="yellow",
            wraplength=450
        )
        testing_info.pack(pady=8)

    def login(self):
        """Iniciar sesión de usuario"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            self.status_label.configure(text="Ingresa email y contraseña")
            return

        try:
            success = self.app.account_manager.login_user(email, password)

            if success:
                user_info = self.app.account_manager.get_user_data(email)
                if user_info:
                    self.app.current_user = email
                    self.app.current_user_name = user_info["name"]

                    self.status_label.configure(
                        text=f"¡Bienvenido {user_info['name']}!",
                        text_color="green"
                    )
                    self.app.root.after(1000, self.app.show_main_gallery)
                else:
                    self.status_label.configure(text="Error al obtener información del usuario")
            else:
                self.status_label.configure(text="Email o contraseña incorrectos")

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")

    def register(self):
        """Registrar nuevo usuario generando Identidad Digital (Claves + Certificado)"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not name or not email or not password:
            self.status_label.configure(text="Completa todos los campos")
            return

        try:
            # 1. Feedback visual (Generar RSA 2048 bits tarda un poco)
            self.status_label.configure(
                text="Generando claves criptográficas y certificado digital...", 
                text_color="blue"
            )
            self.app.root.update()

            # 2. Llamada al backend (AccountManager -> PKIManager)
            self.app.account_manager.register_user(email, name, password)

            # 3. Éxito
            self.app.current_user = email
            self.app.current_user_name = name

            self.status_label.configure(
                text=f"¡Identidad Digital creada para {name}!",
                text_color="green"
            )

            self.password_entry.delete(0, "end")
            # Pequeña pausa para que el usuario lea el mensaje antes de cambiar de pantalla
            self.app.root.after(1500, self.app.show_main_gallery)

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")