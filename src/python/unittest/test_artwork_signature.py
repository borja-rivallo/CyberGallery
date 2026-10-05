import unittest
from unittest.mock import patch, MagicMock
import subprocess
import base64
from src.python.main.security.signature_manager import SignatureManager

class TestArtworkSignature(unittest.TestCase):
    """Tests para SignatureManager"""

    def setUp(self):
        """Configuración de mocks"""
        self.mock_run_patcher = patch("src.python.main.security.signature_manager.subprocess.run")
        self.mock_path_patcher = patch("src.python.main.security.signature_manager.Path")
        self.mock_open_patcher = patch("builtins.open")
        self.mock_remove_patcher = patch("os.remove")
        self.mock_exists_patcher = patch("os.path.exists")
        
        # Iniciamos los patchers
        self.mock_run = self.mock_run_patcher.start()
        self.mock_path = self.mock_path_patcher.start()
        self.mock_open = self.mock_open_patcher.start()
        self.mock_remove = self.mock_remove_patcher.start()
        self.mock_exists = self.mock_exists_patcher.start()
        
        self.mock_exists.return_value = True
        self.mock_run.return_value = MagicMock(returncode=0)
        
        mock_userkey_storage = MagicMock()
        mock_userkey_storage.__truediv__.side_effect = lambda x: f"/mock/userkey_storage/{x}"
        
        mock_path_instance = MagicMock()
        mock_path_instance.mkdir.return_value = None
        mock_path_instance.__truediv__.return_value = mock_userkey_storage
        mock_path_instance.resolve.return_value = mock_path_instance
        mock_path_instance.parent = mock_path_instance
        
        self.mock_path.return_value = mock_path_instance
        
        self.manager = SignatureManager()
        self.manager.userkey_storage = MagicMock()
        self.manager.userkey_storage.__truediv__.side_effect = lambda x: f"/mock/userkey_storage/{x}"

    def tearDown(self):
        """Detener todos los parches"""
        self.mock_run_patcher.stop()
        self.mock_path_patcher.stop()
        self.mock_open_patcher.stop()
        self.mock_remove_patcher.stop()
        self.mock_exists_patcher.stop()

    def test_generate_identity_success(self):
        """Test: Generación correcta de par de claves y CSR"""
        # Simular éxito en la ejecución de un comando
        self.mock_run.return_value.returncode = 0
        
        key, csr = self.manager.generate_identity("user@test.com", "secure_pass")
        
        self.assertEqual(key, "/mock/userkey_storage/user@test.com.key")
        self.assertEqual(csr, "/mock/userkey_storage/user@test.com.csr")
        
        # Comprobar el número de comandos ejecutados
        self.assertEqual(self.mock_run.call_count, 2)
        
        # Verificar argumentos del primer comando (genrsa)
        args_genrsa = self.mock_run.call_args_list[0][0][0]
        self.assertIn("genrsa", args_genrsa)
        self.assertIn("-aes256", args_genrsa)
        self.assertIn("pass:secure_pass", args_genrsa)

        # Verificar argumentos del segundo comando (req)
        args_req = self.mock_run.call_args_list[1][0][0]
        self.assertIn("req", args_req)
        self.assertIn("-new", args_req)
        self.assertTrue(any("/CN=user@test.com" in arg for arg in args_req))

    def test_generate_identity_openssl_failure(self):
        """Test: Fallo en OpenSSL durante generación de identidad lanza excepción"""
        # Configurar el mock para que falle al ser llamado
        self.mock_run.side_effect = subprocess.CalledProcessError(1, ["openssl"], stderr="Permission denied")
        
        with self.assertRaises(Exception) as context:
            self.manager.generate_identity("user@test.com", "pass")
            
        self.assertIn("Error al ejecutar un comando OpenSSL", str(context.exception))

    def test_sign_file_hash_success(self):
        """Test: Firma exitosa de un hash de archivo"""
        signature_data = b"fake_signature_data_1234567890"
        
        # Simular archivo de firma
        mock_file = MagicMock()
        mock_file.read.return_value = signature_data
        
        self.mock_open.return_value.__enter__.return_value = mock_file
        
        # Configurar mock para ejecución de comando exitosa
        self.mock_run.return_value.returncode = 0
        
        # Firmar el hash
        valid_hex_hash = "a" * 64 
        signature = self.manager.sign_file_hash(valid_hex_hash, "/path/key", "pass")
        
        # Validar que se llamó a open
        self.assertTrue(self.mock_open.called)
        
        # Validar llamada a openssl dgst -sign
        args_sign = self.mock_run.call_args[0][0]
        self.assertIn("dgst", args_sign)
        self.assertIn("-sign", args_sign)
        self.assertIn("/path/key", args_sign)
        
        # Comprobar que la firma devuelta es correcta
        self.assertIsInstance(signature, str)
        expected_base64 = base64.b64encode(signature_data).decode('utf-8')
        self.assertEqual(signature, expected_base64)

    def test_sign_file_hash_process_failure(self):
        """Test: Fallo crítico al firmar"""
        # Configurar open
        signature_data = b"fake_signature_data"
        mock_file = MagicMock()
        mock_file.read.return_value = signature_data
        self.mock_open.return_value.__enter__.return_value = mock_file
        
        # Configurar el mock para dar error al ejecutar el comando
        self.mock_run.side_effect = subprocess.CalledProcessError(1, ["openssl"], stderr="Bad password")
        
        valid_hex_hash = "b" * 64
        
        with self.assertRaises(Exception) as context:
            self.manager.sign_file_hash(valid_hex_hash, "/path/key", "wrong_pass")
            
        self.assertIn("Error al ejecutar un comando OpenSSL", str(context.exception))

    def test_verify_signature_valid(self):
        """Test: Verificación de firma válida devuelve True"""
        # Configurar mock para open
        mock_file = MagicMock()
        self.mock_open.return_value.__enter__.return_value = mock_file
        
        # Configurar ejecución correcta de comandos
        self.mock_run.return_value.returncode = 0
        
        valid_hex_hash = "d" * 64
        valid_b64_sig = "c2lnbmF0dXJl"
        
        result = self.manager.verify_signature(valid_hex_hash, valid_b64_sig, "/path/cert")
        
        self.assertTrue(result)
        
        # Verificar número de comandos ejecutados
        self.assertGreaterEqual(self.mock_run.call_count, 2)
        
        # Verificar llamada a extracción de clave pública
        args_pubkey = self.mock_run.call_args_list[0][0][0]
        self.assertIn("x509", args_pubkey)
        self.assertIn("-pubkey", args_pubkey)
        
        # Verificar llamada a verificación
        args_verify = self.mock_run.call_args_list[1][0][0]
        self.assertIn("dgst", args_verify)
        self.assertIn("-verify", args_verify)

    def test_verify_signature_invalid(self):
        """Test: Verificación de firma inválida devuelve False"""
        # Configurar mock para open
        mock_file = MagicMock()
        self.mock_open.return_value.__enter__.return_value = mock_file
        
        # Simular error en la verificación
        self.mock_run.side_effect = [
            MagicMock(returncode=0),
            subprocess.CalledProcessError(1, ["openssl"], stderr="Verification failure")  # dgst verify ERROR
        ]
        
        valid_hex_hash = "e" * 64
        result = self.manager.verify_signature(valid_hex_hash, "c2lnbmF0dXJl", "/path/cert")
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()