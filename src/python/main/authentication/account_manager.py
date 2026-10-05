from src.python.main.authentication.password_manager import PasswordManager
from src.python.storage.storage_accounts import JSONStoreAccounts
from src.python.main.exception_management import ExceptionManagement
from src.python.main.security.pki_manager import PKIManager
from src.python.main.security.signature_manager import SignatureManager
import re

class AccountManager():
    """Gestor de cuentas de usuarios"""
    def __init__(self):
        self._password_manager = PasswordManager()
        self._json_manager = JSONStoreAccounts()
        self._pki_manager = PKIManager()
        self._signature_manager = SignatureManager()

    def _valid_email(self, email: str) -> bool:
        """Valida el formato de un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True
        return False

    def register_user(self, email:str, name:str, password:str):
        """Registra un nuevo usuario y genera su clave privada y su certificado"""
        if not self._valid_email(email):
            raise ExceptionManagement("Formato del email inválido")

        if not self._password_manager.valid_password(password):
            raise ExceptionManagement("Contraseña inválida")

        user_list = self._json_manager.read_store()
        for user in user_list:
            if user["email"] == email:
                raise ExceptionManagement("El email ya está en uso")
            
        # Crea el hash de la contraseña tras generar un salt    
        password_hash, salt = self._password_manager.hash_password(password)

        # Genera la clave privada (protegida por su contraseña) y el CSR para el usuario
        key_path, csr_path = self._signature_manager.generate_identity(email, password)

        # La AC subordinada firma el certificado del usuario
        cert_path = self._pki_manager.sign_csr(csr_path, email)

        new_user_data = {
            "email":email,
            "name":name,
            "password_hash":password_hash,
            "salt": salt,
            "key_path": key_path, # Ruta a la clave privada del usuario
            "cert_path": cert_path # Ruta al certificado del usuario
        }

        # Añade el nuevo usuario a users.json
        self._json_manager.add_item(new_user_data)
        return new_user_data

    def login_user(self, email: str, password: str) -> bool:
        """Inicia sesión usando un email"""
        user_list = self._json_manager.read_store()

        # Comprueba si el email está en users.json
        for user in user_list:
            if user["email"] == email:
                return self._password_manager.password_check(
                    password, 
                    user["password_hash"],
                    user["salt"]
                )

        return False

    def get_user_data(self, email:str):
        """Obtiene los datos de un usuario"""
        user_list = self._json_manager.read_store()
        
        # Comprueba si el email está en users.json y devuelve los datos asociados
        for user in user_list:
            if user["email"] == email:
                return {
                    "name": user["name"],
                    "email": user["email"],
                    "password_hash": user["password_hash"],
                    "salt": user["salt"],
                    "key_path": user["key_path"],
                    "cert_path": user["cert_path"]
                }
            
        return None
