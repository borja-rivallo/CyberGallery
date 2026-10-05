import re
import os
import hashlib

class PasswordManager():
    """Gestor de contraseñas"""
    def __init__(self):
        self._min_lenth = 10
        self._min_alphabetic_char = 5
        self._min_numeric_char = 3
        self._min_special_char = 2
        self._min_uppercase_char = 2

    def valid_password(self, password:str) -> bool:
        """Comprueba que una contraseña cumple los requisitos mínimos"""
        if len(password) < self._min_lenth:
            return False

        alphabetic_chars = len(re.findall(r'[a-zA-Z]', password))
        if alphabetic_chars < self._min_alphabetic_char:
            return False

        numeric_chars = len(re.findall(r'[0-9]', password))
        if numeric_chars < self._min_numeric_char:
            return False

        special_chars = len(re.findall(r'[/\-_]', password))
        if special_chars < self._min_special_char:
            return False

        uppercase_chars = len(re.findall(r'[A-Z]', password))
        if uppercase_chars < self._min_uppercase_char:
            return False

        return True
    
    def generate_salt(self) -> str:
        """Genera un salt aleatorio"""
        return (os.urandom(32)).hex()

    def hash_password(self, password:str) -> str:
        """Aplica SHA3-256 a una contraseña"""
        # Se genera una secuencia de bytes aleatoria que evita el mismo hash para contraseñas iguales
        salt = self.generate_salt()

        # Es necesario transformarla a bytes antes de aplicar la función resumen
        password_b = (password + salt).encode("utf-8")
        password_hash = hashlib.sha3_256(password_b)

        return password_hash.hexdigest(), salt

    def password_check(self, password:str, stored_hash:str, salt:str) -> bool:
        """Verifica una contraseña comparando su hash"""
        # Es necesario transformarla a bytes antes de aplicar la función resumen
        password_b = (password + salt).encode("utf-8")
        password_hash = hashlib.sha3_256(password_b)

        return password_hash.hexdigest() == stored_hash
    