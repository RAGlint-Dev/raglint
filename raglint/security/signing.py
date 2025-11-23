"""
Plugin Code Signing System.

Provides RSA-based signing and verification for trusted plugins.
"""

import logging
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class PluginSigner:
    """Sign and verify plugin code using RSA."""
    
    def __init__(self, private_key_path: Optional[Path] = None, public_key_path: Optional[Path] = None):
        self.private_key = None
        self.public_key = None
        
        if private_key_path and private_key_path.exists():
            self.private_key = self._load_private_key(private_key_path)
        
        if public_key_path and public_key_path.exists():
            self.public_key = self._load_public_key(public_key_path)
    
    def generate_keys(self, private_key_path: Path, public_key_path: Path):
        """Generate a new RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # Save private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        private_key_path.write_bytes(pem_private)
        
        # Save public key
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_key_path.write_bytes(pem_public)
        
        self.private_key = private_key
        self.public_key = public_key
        
        logger.info(f"Generated new key pair: {private_key_path}, {public_key_path}")
    
    def sign_plugin(self, code: str) -> bytes:
        """Sign plugin code with private key."""
        if not self.private_key:
            raise ValueError("No private key loaded")
        
        code_bytes = code.encode('utf-8')
        signature = self.private_key.sign(
            code_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def verify_signature(self, code: str, signature: bytes) -> bool:
        """Verify plugin code signature with public key."""
        if not self.public_key:
            raise ValueError("No public key loaded")
        
        try:
            code_bytes = code.encode('utf-8')
            self.public_key.verify(
                signature,
                code_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False
    
    def _load_private_key(self, path: Path):
        """Load private key from file."""
        pem_data = path.read_bytes()
        return serialization.load_pem_private_key(
            pem_data,
            password=None,
            backend=default_backend()
        )
    
    def _load_public_key(self, path: Path):
        """Load public key from file."""
        pem_data = path.read_bytes()
        return serialization.load_pem_public_key(
            pem_data,
            backend=default_backend()
        )
