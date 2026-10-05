import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class GCMManager:
    """Gestor de cifrado simétrico para obras de arte"""
    def __init__(self):
        self.algorithm = "AES-256-GCM"

    def encrypt_artwork(self, data: bytes, password: str, associated_data: bytes = None) -> tuple[bytes, dict]:
        """Cifra la obra usando AES-256-GCM con derivación segura de clave"""
        # Genera salt único e IV para cada cifrado
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        # Deriva clave de forma segura
        key = self._derive_key_secure(password, salt)

        # Datos del algoritmo de cifrado
        encryption_data = {
            "algorithm": self.algorithm,
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "salt": base64.b64encode(salt).decode("utf-8"),
            "key_derivation": "PBKDF2-HMAC-SHA256-100000"
        }
        
        aesgcm = AESGCM(key)
        encrypted_data = aesgcm.encrypt(nonce, data, associated_data)

        print(f"Cifrado GCM realizado: {len(data)} bytes -> {len(encrypted_data)} bytes")
        return encrypted_data, encryption_data
        
    def decrypt_artwork(self, encrypted_data: bytes, encryption_data: dict, password: str, associated_data: bytes = None) -> bytes:
        """Descifra la obra usando AES-256-GCM"""
        nonce = base64.b64decode(encryption_data["nonce"])
        salt = base64.b64decode(encryption_data["salt"])
        
        # Deriva la clave mediante PBKDF2
        key = self._derive_key_secure(password, salt)
        
        aesgcm = AESGCM(key)
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, associated_data)

        print(f"Descifrado GCM realizado: {len(encrypted_data)} bytes -> {len(decrypted_data)} bytes")
        return decrypted_data
    
    def _derive_key_secure(self, password: str, salt: bytes) -> bytes:
        """Derivación segura de clave usando PBKDF2"""
        # Iteraciones para que el proceso sea más lento
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )

        return kdf.derive(password.encode('utf-8'))
