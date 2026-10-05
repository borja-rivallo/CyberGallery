# CyberGallery

A secure Python desktop application utilizing a CustomTkinter GUI, designed to protect digital art portfolios. The system implements a full Public Key Infrastructure (PKI) to establish digital identities, enforces AES-256-GCM symmetric encryption for private artwork storage, and ensures data integrity via SHA-256 digital signatures.

## Technical Features
* **Authentication:** Strong password policies with SHA3-256 hashing and dynamic, cryptographically secure salting.
* **PKI Architecture:** Automated generation of Root and Subordinate Certificate Authorities (CAs) via OpenSSL.
* **Digital Signatures:** File hashes are signed with the author's AES-256 protected private key, ensuring non-repudiation and integrity.
* **Symmetric Encryption:** Private artworks are encrypted using AES-GCM, deriving keys securely via PBKDF2-HMAC-SHA256 (100,000 iterations) with random nonces.

## Execution Instructions
1. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:

   ```bash
   python3 -m src.python.main.main
   ```
3. Run tests:

   ```bash
   python3 -m unittest discover -s src/python/unittest
   ```
