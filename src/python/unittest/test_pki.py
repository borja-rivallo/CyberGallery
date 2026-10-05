import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.python.main.security.pki_manager import PKIManager

class TestPKIManager(unittest.TestCase):
    """Tests para PKIManager"""

    def setUp(self):
        """Configuración inicial"""
        # Patchers principales
        self.patchers = [
            patch('src.python.main.security.pki_manager.subprocess.run'),
            patch('builtins.open', mock_open(read_data="mock cert content"))
        ]
        
        self.mock_run, self.mock_open = [p.start() for p in self.patchers]
        self.mock_run.return_value = MagicMock(returncode=0)
        
        # Mock de PKIManager
        with patch('src.python.main.security.pki_manager.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.mkdir.return_value = None
            mock_path_instance.__truediv__.return_value = mock_path_instance
            mock_path.return_value = mock_path_instance
            
            self.pki_manager = PKIManager()
        
        # Limpieza automática
        for p in self.patchers:
            self.addCleanup(p.stop)

    def test_verify_cert_chain_success(self):
        """Test: Verificación exitosa de cadena de certificados"""
        result = self.pki_manager.verify_cert_chain("/path/to/user.crt")
        self.assertTrue(result)
        self.mock_run.assert_called()

    def test_verify_cert_chain_failure(self):
        """Test: Verificación fallida de cadena de certificados"""
        self.mock_run.side_effect = Exception("Verification failed")
        result = self.pki_manager.verify_cert_chain("/path/to/invalid.crt")
        self.assertFalse(result)

    def test_sign_csr_success(self):
        """Test: Firma exitosa de CSR"""
        # Mock para que devuelva ruta con email
        with patch.object(self.pki_manager.certs_dir, '__truediv__') as mock_div:
            mock_div.return_value = f"/mock/certs/user@example.com.crt"
            
            cert_path = self.pki_manager.sign_csr("/path/to/user.csr", "user@example.com")
            
            self.assertIn("user@example.com", cert_path)
            self.mock_run.assert_called()

    def test_sign_csr_failure(self):
        """Test: Firma fallida de CSR"""
        from subprocess import CalledProcessError
        self.mock_run.side_effect = CalledProcessError(1, "openssl", stderr="OpenSSL failed")
        
        with self.assertRaises(Exception) as context:
            self.pki_manager.sign_csr("/path/to/invalid.csr", "user@example.com")
        
        self.assertIn("Error al ejecutar comando", str(context.exception))

    def test_pki_manager_initialization(self):
        """Test: PKIManager se inicializa correctamente"""
        # Verificar que los directorios existen
        self.assertIsNotNone(self.pki_manager.root_dir)
        self.assertIsNotNone(self.pki_manager.subordinate_dir)
        self.assertIsNotNone(self.pki_manager.certs_dir)

    def test_run_openssl_command_failure(self):
        """Test: Manejo de errores en comandos OpenSSL"""
        from subprocess import CalledProcessError
        self.mock_run.side_effect = CalledProcessError(1, "openssl", stderr="OpenSSL command failed")
        
        with self.assertRaises(Exception) as context:
            self.pki_manager._run_openssl(["openssl", "version"])
        
        self.assertIn("Error al ejecutar comando", str(context.exception))

    def test_pki_directory_structure(self):
        """Test: Estructura de directorios PKI"""
        # Verificar que las rutas principales están definidas
        self.assertTrue(hasattr(self.pki_manager, 'root_dir'))
        self.assertTrue(hasattr(self.pki_manager, 'subordinate_dir')) 
        self.assertTrue(hasattr(self.pki_manager, 'certs_dir'))
        self.assertTrue(hasattr(self.pki_manager, 'root_key'))
        self.assertTrue(hasattr(self.pki_manager, 'root_cert'))
        self.assertTrue(hasattr(self.pki_manager, 'sub_key'))
        self.assertTrue(hasattr(self.pki_manager, 'sub_cert'))

if __name__ == '__main__':
    unittest.main()