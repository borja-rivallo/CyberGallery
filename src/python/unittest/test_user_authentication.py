import unittest
from unittest.mock import patch
from src.python.main.authentication.account_manager import AccountManager
from src.python.main.authentication.password_manager import PasswordManager
from src.python.main.exception_management import ExceptionManagement


class TestPasswordManager(unittest.TestCase):
    """Tests para PasswordManager"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.password_manager = PasswordManager()

    def test_valid_password_meets_all_requirements(self):
        """Test: Contraseña que cumple todos los requisitos"""
        valid_password = "ABCbcde12345/-_"
        self.assertTrue(self.password_manager.valid_password(valid_password))

    def test_invalid_password_too_short(self):
        """Test: Contraseña demasiado corta"""
        short_password = "Ab1/-"
        self.assertFalse(self.password_manager.valid_password(short_password))

    def test_invalid_password_insufficient_alphabetic_chars(self):
        """Test: Contraseña con caracteres alfabéticos insuficientes"""
        password = "Ab12/-_3456"
        self.assertFalse(self.password_manager.valid_password(password))

    def test_invalid_password_insufficient_numeric_chars(self):
        """Test: Contraseña con caracteres numéricos insuficientes"""
        password = "Abcdef/-_GH"
        self.assertFalse(self.password_manager.valid_password(password))

    def test_valid_password_invalid_special_chars(self):
        """Test: Caracteres especiales no permitidos"""
        invalid_special_password = "ABCcde12345@#$"
        self.assertFalse(self.password_manager.valid_password(invalid_special_password))

    def test_invalid_password_insufficient_special_chars(self):
        """Test: Contraseña con caracteres especiales insuficientes"""
        password = "Abcde12345G"
        self.assertFalse(self.password_manager.valid_password(password))

    def test_invalid_password_insufficient_uppercase_chars(self):
        """Test: Contraseña con caracteres en mayúscula insuficientes"""
        password = "abcde12345/-_"
        self.assertFalse(self.password_manager.valid_password(password))

    def test_hash_password_returns_tuple(self):
        """Test: hash_password devuelve una tupla (hash, salt)"""
        password = "TestPassword123/-_"
        result = self.password_manager.hash_password(password)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        hash_result, salt = result
        
        self.assertIsInstance(hash_result, str)
        self.assertIsInstance(salt, str)
        self.assertEqual(len(hash_result), 64)
        self.assertEqual(len(salt), 64)

    def test_hash_password_different_salts(self):
        """Test: Hashes diferentes para la misma contraseña (debido a salts diferentes)"""
        password = "TestPassword123/-_"
        hash1, salt1 = self.password_manager.hash_password(password)
        hash2, salt2 = self.password_manager.hash_password(password)
        
        self.assertNotEqual(salt1, salt2)
        self.assertNotEqual(hash1, hash2)

    def test_password_check_correct_password(self):
        """Test: Verificación de contraseña correcta"""
        password = "ValidPassword123/-_"
        stored_hash, stored_salt = self.password_manager.hash_password(password)
        self.assertTrue(self.password_manager.password_check(password, stored_hash, stored_salt))

    def test_password_check_incorrect_password(self):
        """Test: Verificación de contraseña incorrecta"""
        original_password = "ValidPassword123/-_"
        wrong_password = "WrongPassword123/-_"
        stored_hash, stored_salt = self.password_manager.hash_password(original_password)
        self.assertFalse(self.password_manager.password_check(wrong_password, stored_hash, stored_salt))

    def test_password_check_wrong_salt(self):
        """Test: Verificación falla con salt incorrecto"""
        password = "ValidPassword123/-_"
        stored_hash, stored_hash = self.password_manager.hash_password(password)
        wrong_salt = self.password_manager.generate_salt()
        self.assertFalse(self.password_manager.password_check(password, stored_hash, wrong_salt))

    def test_generate_salt(self):
        """Test: generate_salt produce salts válidos"""
        salt1 = self.password_manager.generate_salt()
        salt2 = self.password_manager.generate_salt()
        
        self.assertIsInstance(salt1, str)
        self.assertEqual(len(salt1), 64)
        self.assertNotEqual(salt1, salt2)


class TestAccountManager(unittest.TestCase):
    """Tests para AccountManager"""

    def setUp(self):
        """Configuración inicial"""
        # Patcher para almacenamiento
        self.json_patcher = patch('src.python.main.authentication.account_manager.JSONStoreAccounts')
        self.mock_json_cls = self.json_patcher.start()
        self.mock_json = self.mock_json_cls.return_value
        
        # Patcher para PKI
        self.pki_patcher = patch('src.python.main.authentication.account_manager.PKIManager')
        self.mock_pki_cls = self.pki_patcher.start()
        self.mock_pki = self.mock_pki_cls.return_value

        # Patcher para SignatureManager
        self.sig_patcher = patch('src.python.main.authentication.account_manager.SignatureManager')
        self.mock_sig_cls = self.sig_patcher.start()
        self.mock_sig = self.mock_sig_cls.return_value

        self.account_manager = AccountManager()
        self.password_manager = PasswordManager()

    def tearDown(self):
        self.json_patcher.stop()
        self.pki_patcher.stop()
        self.sig_patcher.stop()

    def test_register_user_success(self):
        """Test: Registro exitoso de usuario con generación de identidad y certificados"""
        self.mock_json.read_store.return_value = []
        
        # Configurar rutas simuladas
        self.mock_sig.generate_identity.return_value = ("/tmp/user.key", "/tmp/user.csr")
        self.mock_pki.sign_csr.return_value = "/tmp/user.crt"

        email = "user@example.com"
        name = "Usuario"
        password = "ABCbcde12345/-_"

        new_user = self.account_manager.register_user(email, name, password)

        # Verificaciones de datos del usuario
        self.assertEqual(new_user["email"], email)
        self.assertEqual(new_user["name"], name)
        self.assertIn("password_hash", new_user)
        self.assertIn("salt", new_user)
        
        # Verificaciones de firmas y certificados
        self.assertEqual(new_user["key_path"], "/tmp/user.key")
        self.assertEqual(new_user["cert_path"], "/tmp/user.crt")

        # Verificar llamadas para generar identidad 
        self.mock_sig.generate_identity.assert_called_once_with(email, password)
        self.mock_pki.sign_csr.assert_called_once_with("/tmp/user.csr", email)

        # Verificar almacenamiento
        self.mock_json.add_item.assert_called_once()
        called_arg = self.mock_json.add_item.call_args[0][0]
        self.assertEqual(called_arg["email"], email)
        self.assertEqual(called_arg["key_path"], "/tmp/user.key")
        self.assertEqual(called_arg["cert_path"], "/tmp/user.crt")

    def test_register_user_invalid_email(self):
        """Test: Email con formato inválido lanza ExceptionManagement"""
        self.mock_json.read_store.return_value = []

        with self.assertRaises(ExceptionManagement):
            self.account_manager.register_user("bad-email", "Nombre", "ABCbcde12345/-_")
            
        # Comprobar que no se intentó generar identidad
        self.mock_sig.generate_identity.assert_not_called()

    def test_register_user_invalid_password(self):
        """Test: Contraseña inválida lanza ExceptionManagement"""
        self.mock_json.read_store.return_value = []
    
        invalid_password = "short1A/"

        with self.assertRaises(ExceptionManagement):
            self.account_manager.register_user("user2@example.com", "Nombre", invalid_password)

    def test_register_user_duplicate_email(self):
        """Test: Registrar con email ya existente lanza ExceptionManagement"""
        existing_user = {
            "email": "dup@example.com", 
            "name": "Dup", 
            "password_hash": "x"*64,
            "salt": "y"*64
        }

        self.mock_json.read_store.return_value = [existing_user]

        with self.assertRaises(ExceptionManagement):
            self.account_manager.register_user("dup@example.com", "Nuevo", "ABCbcde12345/-_")

    def test_login_user_success(self):
        """Test: Login correcto devuelve True"""
        password = "ValidPassword123/-_"
        hash_result, salt = self.password_manager.hash_password(password)

        user = {
            "email": "login@example.com", 
            "name": "Log", 
            "password_hash": hash_result,
            "salt": salt,
            "key_path": "/path/key",
            "cert_path": "/path/cert"
        }

        self.mock_json.read_store.return_value = [user]

        result = self.account_manager.login_user("login@example.com", password)
        self.assertTrue(result)

    def test_login_user_wrong_password(self):
        """Test: Contraseña incorrecta devuelve False"""
        original_password = "ValidPassword123/-_"
        wrong_password = "WrongPassword123/-_"
        hash_result, salt = self.password_manager.hash_password(original_password)

        user = {
            "email": "login2@example.com", 
            "name": "Log2", 
            "password_hash": hash_result,
            "salt": salt
        }

        self.mock_json.read_store.return_value = [user]

        result = self.account_manager.login_user("login2@example.com", wrong_password)
        self.assertFalse(result)

    def test_login_user_nonexistent_email(self):
        """Test: email no existente devuelve False"""
        self.mock_json.read_store.return_value = []

        result = self.account_manager.login_user("noone@example.com", "whatever")
        self.assertFalse(result)

    def test_get_user_data_existing(self):
        """Test: Obtener datos de usuario existente (incluyendo rutas de seguridad)"""
        hash_result, salt = self.password_manager.hash_password("SomePass123/-_")

        user = {
            "email": "get@example.com", 
            "name": "GetName", 
            "password_hash": hash_result,
            "salt": salt,
            "key_path": "/users/get.key",
            "cert_path": "/users/get.crt"
        }

        self.mock_json.read_store.return_value = [user]

        data = self.account_manager.get_user_data("get@example.com")

        self.assertIsNotNone(data)
        self.assertEqual(data["email"], "get@example.com")
        self.assertEqual(data["name"], "GetName")
        self.assertEqual(data["password_hash"], hash_result)
        self.assertEqual(data["salt"], salt)
        self.assertEqual(data["key_path"], "/users/get.key")
        self.assertEqual(data["cert_path"], "/users/get.crt")

    def test_get_user_data_nonexistent(self):
        """Test: Obtener datos de email inexistente devuelve None"""
        self.mock_json.read_store.return_value = []
        data = self.account_manager.get_user_data("missing@example.com")
        self.assertIsNone(data)


if __name__ == '__main__':
    unittest.main()