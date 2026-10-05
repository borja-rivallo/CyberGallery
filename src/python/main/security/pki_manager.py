import subprocess
from pathlib import Path

class PKIManager:
    """Gestor de PKI utilizando OpenSSL"""
    def __init__(self):
        # Directorio base para las autoridades y sus certificados
        self.pki_dir = Path(__file__).resolve().parent.parent.parent.parent / "pki_storage"
        
        # Definición de rutas
        self.root_dir = self.pki_dir / "root" # Certificados de la AC raíz

        self.subordinate_dir = self.pki_dir / "subordinate" # Certificados de la AC subordinada
        self.certs_dir = self.subordinate_dir / "certs" # Certificados de los usuarios
        
        # Crea las carpetas
        for d in [self.root_dir, self.subordinate_dir, self.certs_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        # Crea los archivos para la clave privada y el certificado de la AC raíz
        self.root_key = self.root_dir / "rootCA.key"
        self.root_cert = self.root_dir / "rootCA.crt"
        
        # Crea los archivos para la clave privada y el certificado de la AC subordinada
        self.sub_key = self.subordinate_dir / "subordinateCA.key"
        self.sub_csr = self.subordinate_dir / "subordinateCA.csr"
        self.sub_cert = self.subordinate_dir / "subordinateCA.crt"
        
        # Si no existen las autoridades, las crea
        if not self.root_key.exists():
            self._create_root_ca()
        
        if not self.sub_key.exists():
            self._create_subordinate_ca()

    def _run_openssl(self, command: list):
        """Ejecuta comandos de sistema de OpenSSL"""
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error al ejecutar comando: {e.stderr.strip()}")

    def _create_root_ca(self):
        """Genera la AC Raíz (auto-firmada)"""
        print("Generando AC1 (Raíz)...")

        #  Genera la clave privada de la AC raíz (protegida con AES-256)
        self._run_openssl([
            "openssl", "genrsa", "-aes256", 
            "-passout", "pass:rootpassword", # Contraseña fija para la AC raíz
            "-out", str(self.root_key), "4096" # Clave de 4096 bits = 512 bytes
        ])
        
        # Genera el certificado de la AC raíz
        self._run_openssl([
            "openssl", "req", "-x509", "-new", "-nodes",
            "-key", str(self.root_key),
            "-passin", "pass:rootpassword",
            "-sha256", "-days", "3650", # Duración de 10 años
            "-out", str(self.root_cert),
            "-subj", "/C=ES/O=CyberGallery/CN=CyberGallery Root CA"
        ])

    def _create_subordinate_ca(self):
        """Genera la AC subordinada y la firma con la AC raíz"""
        print("Generando AC2 (Subordinada)...")

        # Genera la clave privada de la AC subordinada (protegida con AES-256)
        self._run_openssl([
            "openssl", "genrsa", "-aes256",
            "-passout", "pass:subpassword", # Contraseña fija para la AC subordinada
            "-out", str(self.sub_key), "4096" # Clave de 4096 bits = 512 bytes
        ])
        
        # Genera el CSR de la AC subordinada
        self._run_openssl([
            "openssl", "req", "-new",
            "-key", str(self.sub_key),
            "-passin", "pass:subpassword",
            "-out", str(self.sub_csr),
            "-subj", "/C=ES/O=CyberGallery/CN=CyberGallery Subordinate CA"
        ])
        
        # La AC raíz firma el certificado de la AC subordinada
        self._run_openssl([
            "openssl", "x509", "-req",
            "-in", str(self.sub_csr),
            "-CA", str(self.root_cert),
            "-CAkey", str(self.root_key),
            "-passin", "pass:rootpassword",
            "-CAcreateserial",
            "-out", str(self.sub_cert),
            "-days", "1825", "-sha256", # Duración de 5 años
            "-extfile", "/etc/ssl/openssl.cnf", "-extensions", "v3_ca"
        ])

    def sign_csr(self, user_csr_path: str, email: str) -> str:
        """La AC subordinada firma el certificado del usuario"""
        user_cert_path = self.certs_dir / f"{email}.crt"
        
        self._run_openssl([
            "openssl", "x509", "-req",
            "-in", str(user_csr_path),
            "-CA", str(self.sub_cert),
            "-CAkey", str(self.sub_key),
            "-passin", "pass:subpassword",
            "-CAcreateserial",
            "-out", str(user_cert_path),
            "-days", "365", "-sha256" # Duración de 1 año
        ])
        
        print(f"Certificado emitido para {email}")
        return str(user_cert_path)

    def verify_cert_chain(self, user_cert_path: str) -> bool:
        """Verifica la cadena de confianza completa"""
        # Crea la cadena completa (raíz + subordinada)
        chain_file = self.pki_dir / "ca-chain.pem"

        # Escribe la cadena en un archivo temporal
        with open(chain_file, "w") as f:
            with open(self.root_cert) as r: f.write(r.read())
            with open(self.sub_cert) as i: f.write(i.read())

        # Verifica el certificado del usuario con la cadena completa
        try:
            self._run_openssl([
                "openssl", "verify",
                "-CAfile", str(chain_file),
                str(user_cert_path)
            ])
            return True
        except Exception:
            return False
