import os
import uuid
import hashlib
from datetime import datetime
import base64

from src.python.main.security.gcm_manager import GCMManager
from src.python.main.security.signature_manager import SignatureManager
from src.python.main.security.pki_manager import PKIManager
from src.python.storage.storage_artwork import JSONStoreArtworks
from src.python.main.authentication.account_manager import AccountManager

class Artwork:
    """Clase que representa una obra de arte"""
    def __init__(self, artwork_id: str, title: str, owner: str, filename: str,
                file_hash: str, upload_date: datetime, is_public: bool = False,
                file_size: int = 0, file_type: str = "", encrypted_data_base64: str = None,
                encryption_data: dict = None, digital_signature: str = None):
        self.artwork_id = artwork_id
        self.title = title
        self.owner = owner # Email del propietario
        self.filename = filename
        self.file_hash = file_hash
        self.upload_date = upload_date
        self.is_public = is_public
        self.file_size = file_size
        self.file_type = file_type
        self.encrypted_data_base64 = encrypted_data_base64
        self.encryption_data = encryption_data
        self.digital_signature = digital_signature

    def to_dict(self) -> dict:
        """Convierte un objeto Artwork a diccionario"""
        return {
            "artwork_id": self.artwork_id,
            "title": self.title,
            "owner": self.owner,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "upload_date": self.upload_date.isoformat(),
            "is_public": self.is_public,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "encrypted_data_base64": self.encrypted_data_base64,
            "encryption_data": self.encryption_data,
            "digital_signature": self.digital_signature
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Artwork desde un diccionario"""
        return cls(
            artwork_id = data["artwork_id"],
            title = data["title"],
            owner = data["owner"],
            filename = data["filename"],
            file_hash = data["file_hash"],
            upload_date = datetime.fromisoformat(data["upload_date"]),
            is_public = data["is_public"],
            file_size = data.get("file_size", 0),
            file_type = data.get("file_type", ""),
            encrypted_data_base64 = data.get("encrypted_data_base64"),
            encryption_data = data.get("encryption_data"),
            digital_signature = data.get("digital_signature")
        )

class ArtworkManager:
    """Gestor de cifrado para obras de arte"""
    def __init__(self):
        self.storage = JSONStoreArtworks()
        self.gcm_manager = GCMManager()
        self.signature_manager = SignatureManager()
        self.pki_manager = PKIManager()
        self.account_manager = AccountManager()

        print("\nArtworkManager inicializado:")
        print(f"   - Cifrado: {self.gcm_manager.algorithm}")

    def upload_artwork(self, user: str, title: str, file_path: str,
                       is_public: bool, password: str) -> str:
        """Sube una obra de arte, la cifra y la almacena"""
        print(f"\nIniciando subida de obra... {title}")
        print(f"    - Propietario: {user}")
        print(f"    - Archivo: {file_path}")
        print(f"    - Pública: {is_public}")

        artwork_id = str(uuid.uuid4())
        print(f"    - ID de la obra: {artwork_id}")

        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
            print(f"Archivo leído: {len(file_data)} bytes")
        except Exception as e:
            raise Exception(f"Error leyendo archivo: {e}")
        
        # Calcula el hash del archivo original
        file_hash = self._calculate_file_hash(file_data) 
        print(f"Hash SHA256 del archivo: {file_hash}")

        # Obtiene la ruta a la clave privada del autor
        user_data = self.account_manager.get_user_data(user)
        key_path = user_data["key_path"]

        # Firma el hash con la clave privada obtenida
        signature = self.signature_manager.sign_file_hash(file_hash, key_path, password)
        print(f"Firma digital generada: {len(signature)} caracteres")

        # Configura la contraseña a usar para el cifrado
        if is_public:
            # Contraseña por defecto para obras públicas
            encryption_password = "default_artwork_password"
            print("Obra pública: cifrada con contraseña por defecto")
        else:
            # Contraseña del propietario para obras privadas
            encryption_password = password
            print("Obra privada: cifrada con contraseña del usuario")

        # Cifra con GCM usando PBKDF2 con salt + AES-GCM con nonce
        encrypted_data, encryption_data = self.gcm_manager.encrypt_artwork(file_data, encryption_password)

        if encryption_data:
            print(f"    - Algoritmo: {encryption_data.get('algorithm', 'N/A')}")
            print(f"    - Derivación: {encryption_data.get('key_derivation', 'N/A')}")
            print(f"    - Salt utilizado: {encryption_data.get('salt', 'N/A')[:16]}...")

        # Convierte datos cifrados a base64 para poder almacenarlos
        encrypted_data_base64 = base64.b64encode(encrypted_data).decode("utf-8")
        print(f"Datos convertidos a base64: {len(encrypted_data_base64)} caracteres")

        artwork = Artwork(
            artwork_id=artwork_id,
            title=title,
            owner=user,
            filename=os.path.basename(file_path),
            file_hash=file_hash,
            upload_date=datetime.now(),
            is_public=is_public,
            file_size=len(file_data),
            file_type=self._get_file_type(file_path),
            encrypted_data_base64=encrypted_data_base64,
            encryption_data=encryption_data,
            digital_signature=signature
        )

        # Almacena la obra en artworks.json
        artwork_dict = artwork.to_dict()
        self.storage.add_item(artwork_dict)

        print(f"Obra subida correctamente: {title}")
        print(f"    - ID: {artwork_id}")
        print(f"    - Tamaño original: {len(file_data)} bytes")
        print(f"    - Tamaño cifrado: {len(encrypted_data)} bytes")

        return artwork_id

    def download_artwork(self, artwork_id: str, output_path: str, password: str = None):
        """Descarga una obra de arte"""
        print(f"\nIniciando descarga de la obra: {artwork_id}")
        print(f"    - Destino: {output_path}")

        try:
            # Busca la obra en el almacenamiento
            all_artworks_data = self.storage.read_store()
            artwork_data = None
            
            for art_data in all_artworks_data:
                if art_data.get("artwork_id") == artwork_id:
                    artwork_data = art_data
                    break

            if not artwork_data:
                raise Exception("Obra no encontrada")
            
            # Crea objeto con los datos de la obra encontrada
            artwork = Artwork.from_dict(artwork_data)
            print(f"Obra encontrada: {artwork.title}")
            print(f"    - Propietario: {artwork.owner}")
            print(f"    - Tipo: {'Pública' if artwork.is_public else 'Privada'}")
            
            # Obtiene el certificado del autor
            owner_data = self.account_manager.get_user_data(artwork.owner)
            cert_path = owner_data["cert_path"]

            # Verifica la cadena de confianza del certificado
            if not self.pki_manager.verify_cert_chain(cert_path):
                raise Exception("Cadena de certificación inválida")
            
            # Verifica la firma digital del archivo
            sig_valid = self.signature_manager.verify_signature(
            artwork.file_hash, artwork.digital_signature, cert_path)

            if not sig_valid:
                raise Exception("La firma digital no coincide")

            if artwork.encryption_data:
                print(f"    - Algoritmo: {artwork.encryption_data.get('algorithm', 'N/A')}")
                print(f"    - Derivación: {artwork.encryption_data.get('key_derivation', 'N/A')}")

            # Obtiene los datos cifrados en base64
            encrypted_data = base64.b64decode(artwork.encrypted_data_base64)
            print(f"    - Datos cifrados: {len(encrypted_data)} bytes")

            # Determina la contraseña para el descifrado según el tipo
            if artwork.is_public:
                # Obra pública: Usa contraseña por defecto
                decryption_password = "default_artwork_password"
                print("    - Usando contraseña por defecto para obra pública")
            else:
                # Obra privada: Usa contraseña proporcionada por el usuario
                if not password:
                    raise Exception("Se requiere contraseña para obras privadas")
                decryption_password = password
                print("    - Usando contraseña proporcionada por el usuario")

            # Descifra la obra usando GCM
            decrypted_data = self.gcm_manager.decrypt_artwork(
                encrypted_data, 
                artwork.encryption_data, 
                decryption_password
            )
            print(f"    - Obra descifrada: {len(decrypted_data)} bytes")

            # Verifica el hash del archivo
            downloaded_hash = self._calculate_file_hash(decrypted_data)
            if downloaded_hash != artwork.file_hash:
                raise Exception(f"El hash del archivo descifrado ({downloaded_hash}) no coincide con el original ({artwork.file_hash})")
            else:
                print("    - Hash verificado: Archivo intacto")

            # Guarda el archivo descifrado en la ruta indicada
            with open(output_path, "wb") as f:
                f.write(decrypted_data)
            print(f"    - Archivo guardado en: {output_path}")

            print(f"Descarga completada: {artwork.title}")
            return {
                "success": True, 
                "signature_verified": sig_valid,
                "pki_verified": True
            }

        except Exception as e:
            raise Exception(f"Error al descargar obra: {e}")
        
    def delete_artwork(self, artwork_id: str) -> bool:
        """Elimina una obra de arte"""
        print(f"\nEliminando la obra: {artwork_id}")

        try:
            success = self.storage.delete_item_by_id(artwork_id)
            if success:
                print(f"Obra eliminada correctamente: {artwork_id}")
            else:
                print(f"No se encontró la obra para eliminar: {artwork_id}")
            return success
        except Exception as e:
            raise Exception(f"Error al eliminar obra: {e}")

    def get_user_artworks(self, user: str) -> list:
        """Obtiene las obras de un usuario"""
        all_artworks_data = self.storage.read_store()
        user_artworks = []

        for artwork_data in all_artworks_data:
            if artwork_data.get("owner") == user:
                artwork = Artwork.from_dict(artwork_data)
                user_artworks.append(artwork)

        return user_artworks

    def get_public_artworks(self) -> list:
        """Obtiene las obras públicas"""
        all_artworks_data = self.storage.read_store()
        public_artworks = []

        for artwork_data in all_artworks_data:
            if artwork_data.get("is_public", False):
                artwork = Artwork.from_dict(artwork_data)
                public_artworks.append(artwork)

        return public_artworks
    
    def _calculate_file_hash(self, data: bytes) -> str:
        """Calcula el hash SHA256 del archivo"""
        return hashlib.sha256(data).hexdigest()
    
    def _get_file_type(self, file_path: str) -> str:
        """Obtiene el tipo de archivo"""
        return os.path.splitext(file_path)[1].lower()