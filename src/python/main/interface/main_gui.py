import customtkinter as ctk
from src.python.main.interface.login_frame import LoginFrame
from src.python.main.interface.gallery_frame import GalleryFrame
from src.python.main.authentication.account_manager import AccountManager
from src.python.main.artwork.artwork_manager import ArtworkManager

class ArtGalleryApp:
    def __init__(self):
        # Configuración de la GUI
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Inicialización de gestores de cuentas y obras
        self.account_manager = AccountManager()
        self.artwork_manager = ArtworkManager()

        # Datos de sesión
        self.current_user = None
        self.current_user_name = None

        # Ventana principal
        self.root = ctk.CTk()
        self.root.title("CyberGallery")
        self.root.geometry("1000x900")

        self.current_frame = None
        # Siempre se inicia en el frame de inicio de sesión
        self.show_login_frame()

    def show_login_frame(self):
        """Mostrar frame de login"""
        self.clear_frame()
        self.current_frame = LoginFrame(self.root, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_main_gallery(self):
        """Mostrar frame de galería principal"""
        self.clear_frame()
        self.current_frame = GalleryFrame(self.root, self)
        self.current_frame.pack(fill="both", expand=True)

    def clear_frame(self):
        """Limpiar frame actual"""
        try:
            if self.current_frame and self.current_frame.winfo_exists():
                self.current_frame.destroy()
        except Exception as e:
            print(f"Error limpiando frame: {e}")
        finally:
            self.current_frame = None

    def logout(self):
        """Cerrar sesión"""
        self.current_user = None
        self.current_user_name = None
        self.clear_frame()
        self.root.after(100, self.show_login_frame)

    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error en la aplicación: {e}")

def run():
    """Función para ejecutar la aplicación desde otros módulos"""
    app = ArtGalleryApp()
    app.run()
