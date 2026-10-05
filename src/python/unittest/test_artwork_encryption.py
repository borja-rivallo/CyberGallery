import unittest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
from src.python.main.artwork.artwork_manager import ArtworkManager, Artwork

class TestArtworkEncryption(unittest.TestCase):
    """Tests para ArtworkManager y GCMManager"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.sample_data = {
            "artwork_id": "test-uuid-123",
            "title": "Test Artwork",
            "owner": "user@example.com",
            "filename": "test.jpg",
            "file_hash": "a" * 64,
            "upload_date": datetime(2024, 1, 1, 10, 0, 0),
            "is_public": True,
            "file_size": 1024,
            "file_type": ".jpg",
            "encrypted_data_base64": "c2FtcGxlZGF0YQ==",
            "encryption_data": {
                "algorithm": "AES-256-GCM",
                "nonce": "b" * 16,
                "salt": "c" * 16,
                "key_derivation": "PBKDF2-HMAC-SHA256-100000"
            },
            "digital_signature": "c2lnbmF0dXJlX2V4YW1wbGVfYmFzZTY0" 
        }
        
        # Patchers para todas las dependencias de seguridad y almacenamiento
        self.patchers = [
            patch('src.python.main.artwork.artwork_manager.JSONStoreArtworks'),
            patch('src.python.main.artwork.artwork_manager.GCMManager'),
            patch('src.python.main.artwork.artwork_manager.SignatureManager'),
            patch('src.python.main.artwork.artwork_manager.PKIManager'),
            patch('src.python.main.artwork.artwork_manager.AccountManager'),
            patch('src.python.main.artwork.artwork_manager.uuid')
        ]
        
        self.mocks = [p.start() for p in self.patchers]
        self.mock_json, self.mock_gcm, self.mock_sig, self.mock_pki, self.mock_acc, self.mock_uuid = [m.return_value for m in self.mocks]
        
        # Configuración por defecto
        self.mock_json.read_store.return_value = []
        self.manager = ArtworkManager()
        
        # Limpieza automática al finalizar cada test
        for p in self.patchers:
            self.addCleanup(p.stop)

    def test_artwork_creation(self):
        """Test: Creación de objeto Artwork verifica campo de firma digital"""
        artwork = Artwork(**self.sample_data)
        
        self.assertEqual(artwork.artwork_id, "test-uuid-123")
        self.assertEqual(artwork.title, "Test Artwork")
        self.assertEqual(artwork.owner, "user@example.com")
        self.assertEqual(artwork.digital_signature, "c2lnbmF0dXJlX2V4YW1wbGVfYmFzZTY0")
        self.assertEqual(artwork.encryption_data["algorithm"], "AES-256-GCM")

    def test_artwork_to_dict(self):
        """Test: Conversión de Artwork a diccionario incluye la firma"""
        artwork = Artwork(**self.sample_data)
        result = artwork.to_dict()
        
        self.assertEqual(result["artwork_id"], "test-uuid-123")
        self.assertEqual(result["digital_signature"], "c2lnbmF0dXJlX2V4YW1wbGVfYmFzZTY0")
        self.assertIsInstance(result["upload_date"], str)

    def test_artwork_from_dict(self):
        """Test: Creación de Artwork desde diccionario recupera la firma"""
        dict_data = self.sample_data.copy()
        # Simular formato string de fecha en JSON
        dict_data["upload_date"] = "2024-01-01T10:00:00"
        
        artwork = Artwork.from_dict(dict_data)
        
        self.assertEqual(artwork.artwork_id, "test-uuid-123")
        self.assertIsInstance(artwork.upload_date, datetime)
        self.assertEqual(artwork.digital_signature, "c2lnbmF0dXJlX2V4YW1wbGVfYmFzZTY0")

    def test_artwork_from_dict_without_signature(self):
        """Test: Creación de Artwork maneja ausencia de firma (ej. versiones antiguas o errores)"""
        data_no_sig = self.sample_data.copy()
        data_no_sig["upload_date"] = "2024-01-01T10:00:00"
        data_no_sig["digital_signature"] = None
        
        artwork = Artwork.from_dict(data_no_sig)
        self.assertIsNone(artwork.digital_signature)

    def test_download_artwork_invalid_signature(self):
        """Test: Descarga debe fallar si la firma digital es inválida (Integridad comprometida)"""
        # Preparar datos almacenados
        stored_data = self.sample_data.copy()
        stored_data["upload_date"] = "2024-01-01T10:00:00"
        self.mock_json.read_store.return_value = [stored_data]
        
        # Credenciales válidas
        self.mock_acc.get_user_data.return_value = {"cert_path": "/valid/cert.crt"}
        self.mock_pki.verify_cert_chain.return_value = True
        
        # Simular que SignatureManager rechaza la firma
        self.mock_sig.verify_signature.return_value = False
        
        with self.assertRaises(Exception) as context:
            self.manager.download_artwork("test-uuid-123", "out.jpg")
            
        self.assertIn("La firma digital no coincide", str(context.exception))

    def test_download_artwork_invalid_pki_chain(self):
        """Test: Descarga debe fallar si la cadena de certificados no es confiable (Autenticación fallida)"""
        stored_data = self.sample_data.copy()
        stored_data["upload_date"] = "2024-01-01T10:00:00"
        self.mock_json.read_store.return_value = [stored_data]
        
        self.mock_acc.get_user_data.return_value = {"cert_path": "/fake/cert.crt"}
        # Simular que PKIManager rechaza el certificado
        self.mock_pki.verify_cert_chain.return_value = False
        
        with self.assertRaises(Exception) as context:
            self.manager.download_artwork("test-uuid-123", "out.jpg")
            
        self.assertIn("Cadena de certificación inválida", str(context.exception))

    def test_delete_artwork_success(self):
        """Test: Eliminación exitosa de obra"""
        self.mock_json.delete_item_by_id.return_value = True
        
        result = self.manager.delete_artwork("test-uuid-123")
        
        self.assertTrue(result)
        self.mock_json.delete_item_by_id.assert_called_once_with("test-uuid-123")

    def test_delete_artwork_not_found(self):
        """Test: Eliminación de obra no encontrada"""
        self.mock_json.delete_item_by_id.return_value = False
        
        result = self.manager.delete_artwork("nonexistent-id")
        
        self.assertFalse(result)

    def test_delete_artwork_exception(self):
        """Test: Eliminación con excepción de almacenamiento"""
        self.mock_json.delete_item_by_id.side_effect = Exception("Storage error")
        
        with self.assertRaises(Exception) as context:
            self.manager.delete_artwork("test-error-123")
        
        self.assertIn("Error al eliminar obra", str(context.exception))

    def test_get_user_artworks(self):
        """Test: Obtener obras filtradas por usuario"""
        data = self.sample_data.copy()
        data["upload_date"] = "2024-01-01T10:00:00"
        self.mock_json.read_store.return_value = [data]
        
        artworks = self.manager.get_user_artworks("user@example.com")
        
        self.assertEqual(len(artworks), 1)
        self.assertEqual(artworks[0].title, "Test Artwork")
        self.assertEqual(artworks[0].owner, "user@example.com")

    def test_get_public_artworks(self):
        """Test: Obtener obras filtradas por visibilidad pública"""
        public_data = self.sample_data.copy()
        public_data["upload_date"] = "2024-01-01T10:00:00"
        public_data["is_public"] = True
        
        private_data = self.sample_data.copy()
        private_data["artwork_id"] = "priv-1"
        private_data["upload_date"] = "2024-01-01T10:00:00"
        private_data["is_public"] = False
        
        self.mock_json.read_store.return_value = [public_data, private_data]
        
        public_artworks = self.manager.get_public_artworks()
        
        self.assertEqual(len(public_artworks), 1)
        self.assertEqual(public_artworks[0].artwork_id, "test-uuid-123")
        self.assertTrue(public_artworks[0].is_public)

    # TESTS MÍNIMOS AÑADIDOS

    def test_upload_artwork_success(self):
        """Test: Subida exitosa de obra con cifrado"""
        # Mockear uuid
        self.mock_uuid.uuid4.return_value = "test-uuid-456"
        
        # Mockear file read
        file_content = b"test file content"
        with patch('builtins.open', mock_open(read_data=file_content)):
            # Mockear hash calculation
            with patch('hashlib.sha256') as mock_sha256:
                mock_hash_instance = MagicMock()
                mock_hash_instance.hexdigest.return_value = "test_hash_123"
                mock_sha256.return_value = mock_hash_instance
                
                # Mockear signature generation
                self.mock_sig.sign_file_hash.return_value = "mock_signature"
                
                # Mockear cifrado
                encrypted_data = b"encrypted_data"
                encryption_info = {"algorithm": "AES-256-GCM"}
                self.mock_gcm.encrypt_artwork.return_value = (encrypted_data, encryption_info)
                
                # Mockear user data
                self.mock_acc.get_user_data.return_value = {"key_path": "/user/key.pem"}
                
                # Ejecutar subida
                artwork_id = self.manager.upload_artwork(
                    user="user@example.com",
                    title="Test Artwork",
                    file_path="/path/to/file.jpg",
                    is_public=True,
                    password="user_password"
                )
                
                # Verificaciones básicas
                self.mock_gcm.encrypt_artwork.assert_called_once()
                self.mock_sig.sign_file_hash.assert_called_once()
                self.mock_json.add_item.assert_called_once()

    def test_download_artwork_success(self):
        """Test: Descarga exitosa de obra"""
        # Mockear datos almacenados
        stored_data = self.sample_data.copy()
        stored_data["upload_date"] = "2024-01-01T10:00:00"
        self.mock_json.read_store.return_value = [stored_data]
        
        # Mockear verificación exitosa
        self.mock_acc.get_user_data.return_value = {"cert_path": "/valid/cert.crt"}
        self.mock_pki.verify_cert_chain.return_value = True
        self.mock_sig.verify_signature.return_value = True
        
        # Mockear descifrado exitoso
        decrypted_data = b"decrypted file content"
        self.mock_gcm.decrypt_artwork.return_value = decrypted_data
        
        # Mockear file write y hash verification
        with patch('builtins.open', mock_open()):
            with patch('hashlib.sha256') as mock_sha256:
                mock_hash_instance = MagicMock()
                mock_hash_instance.hexdigest.return_value = "a" * 64  # Hash que coincide
                mock_sha256.return_value = mock_hash_instance
                
                result = self.manager.download_artwork("test-uuid-123", "/output/path.jpg")
                
                # Verificaciones básicas
                self.assertTrue(result["success"])
                self.mock_gcm.decrypt_artwork.assert_called_once()

    def test_hash_calculation(self):
        """Test: Cálculo correcto de hash SHA256"""
        test_data = b"test data"
        
        with patch('hashlib.sha256') as mock_sha256:
            mock_hash_instance = MagicMock()
            mock_hash_instance.hexdigest.return_value = "test_hash"
            mock_sha256.return_value = mock_hash_instance
            
            result = self.manager._calculate_file_hash(test_data)
            
            self.assertEqual(result, "test_hash")
            mock_sha256.assert_called_once_with(test_data)

    def test_file_type_detection(self):
        """Test: Detección correcta del tipo de archivo"""
        result = self.manager._get_file_type("/path/to/image.jpg")
        self.assertEqual(result, ".jpg")
        
        result = self.manager._get_file_type("/path/to/document.pdf")
        self.assertEqual(result, ".pdf")

if __name__ == '__main__':
    unittest.main()