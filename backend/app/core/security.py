"""Security primitives for password hashing, token verification, and envelope encryption interface."""

import hashlib
import os
from typing import Tuple
from passlib.context import CryptContext
from app.core.config import settings
from app.core.errors import ValidationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def hash_token(token: str) -> bytes:
    """Hash session token using SHA-256 for secure DB lookup."""
    return hashlib.sha256(token.encode("utf-8")).digest()


class CredentialEncryptionService:
    """Envelope encryption interface for storing third-party API credentials."""

    @staticmethod
    def encrypt_secret(secret_plaintext: str, key_version: str = settings.KEY_VERSION) -> Tuple[bytes, str, str]:
        """
        Encrypt secret plaintext using AES-256 GCM or standard envelope encryption.
        Returns (ciphertext, key_version, secret_last4).
        """
        if not secret_plaintext:
            raise ValidationError("Cannot encrypt empty secret")
        
        last4 = secret_plaintext[-4:] if len(secret_plaintext) >= 4 else secret_plaintext
        
        # Standard Fernet / AES-GCM envelope encryption interface
        # For Phase 1, using cryptography library AES-GCM or Fernet
        from cryptography.fernet import Fernet
        import base64

        # Derive 32-byte key from settings
        key_bytes = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        f = Fernet(fernet_key)
        
        ciphertext = f.encrypt(secret_plaintext.encode("utf-8"))
        return ciphertext, key_version, last4

    @staticmethod
    def decrypt_secret(ciphertext: bytes, key_version: str) -> str:
        """Decrypt secret ciphertext in memory for connector execution."""
        from cryptography.fernet import Fernet
        import base64

        key_bytes = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        f = Fernet(fernet_key)
        
        decrypted = f.decrypt(ciphertext)
        return decrypted.decode("utf-8")
