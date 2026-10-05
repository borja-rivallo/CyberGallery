import subprocess
import os
import base64
from pathlib import Path

class SignatureManager:
    """Gestor de identidad del usuario y firmas digitales"""
    def __init__(self):
        # Almacenamiento local para el usuario (actual) de claves privadas y CSR 
        self.userkey_storage = Path(__file__).resolve().parent.parent.parent.parent / "userkey_storage"
        self.userkey_storage.mkdir(parents=True, exist_ok=True)

    def _run_openssl(self, command: list):
        """Ejecuta comandos con subprocess (usado para OpenSSL)"""
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            raise Exception("Error al ejecutar un comando OpenSSL")

    def generate_identity(self, email: str, password: str) -> tuple:
        """Genera una clave privada y un CSR para un nuevo usuario"""
        key_path = self.userkey_storage / f"{email}.key"
        csr_path = self.userkey_storage / f"{email}.csr"
       
        # Genera la clave privada y la cifra con AES-256
        self._run_openssl([
            "openssl", "genrsa", "-aes256",
            "-passout", f"pass:{password}", # Contraseña para proteger la clave privada
            "-out", str(key_path), "2048" # Clave de 2048 bits = 256 bytes
        ])

        # Genera el CSR utilizando la clave privada del usuario
        subj = f"/C=ES/O=CyberGallery Users/CN={email}/emailAddress={email}"
        self._run_openssl([
            "openssl", "req", "-new",
            "-key", str(key_path),
            "-passin", f"pass:{password}", # Contraseña para desbloquear la clave privada
            "-out", str(csr_path),
            "-subj", subj
        ])

        return str(key_path), str(csr_path)

    def sign_file_hash(self, hash_hex: str, private_key_path: str, password: str) -> str:
        """Firma un hash de un archivo utilizando la clave privada"""
        temp_hash_file = f"{private_key_path}.hash.tmp"
        signature_file = f"{private_key_path}.sig.tmp"
        
        try:
            # Guarda el hash en binario en un archivo temporal
            with open(temp_hash_file, "wb") as f:
                f.write(bytes.fromhex(hash_hex))

            # Genera la firma digital del hash y la escribe en un archivo temporal
            self._run_openssl([
                "openssl", "dgst", "-sha256",
                "-sign", str(private_key_path),
                "-passin", f"pass:{password}", # Contraseña para desbloquear la clave privada
                "-out", str(signature_file),
                str(temp_hash_file)
            ])

            # Lee la firma y la devuelve en Base64
            with open(signature_file, "rb") as f:
                sig_bytes = f.read()
            return base64.b64encode(sig_bytes).decode('utf-8')

        finally:
            if os.path.exists(temp_hash_file): os.remove(temp_hash_file)
            if os.path.exists(signature_file): os.remove(signature_file)

    def verify_signature(self, hash_hex: str, signature_b64: str, cert_path: str) -> bool:
        """Verifica una firma usando el certificado público"""
        temp_hash_file = f"{cert_path}.vhash.tmp"
        temp_sig_file = f"{cert_path}.vsig.tmp"
        pub_key_file = f"{cert_path}.pub.tmp"

        try:
            # Extrae la clave pública del certificado
            self._run_openssl([
                "openssl", "x509", "-in", str(cert_path), 
                "-pubkey", "-noout", "-out", str(pub_key_file)
            ])

            # Escribe el hash y la firma digital en archivos temporales
            with open(temp_hash_file, "wb") as f:
                f.write(bytes.fromhex(hash_hex))
            with open(temp_sig_file, "wb") as f:
                f.write(base64.b64decode(signature_b64))

            # Verifica la firma digital
            self._run_openssl([
                "openssl", "dgst", "-sha256",
                "-verify", str(pub_key_file),
                "-signature", str(temp_sig_file),
                str(temp_hash_file) 
            ])
            return True
        
        except Exception:
            return False
        
        finally:
            for f in [temp_hash_file, temp_sig_file, pub_key_file]:
                if os.path.exists(f): os.remove(f)
