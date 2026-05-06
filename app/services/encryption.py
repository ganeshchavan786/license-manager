"""
Encryption Service - Encrypt and decrypt sensitive data

This service provides functionality to:
- Encrypt sensitive data (passwords, API keys, etc.)
- Decrypt encrypted data
- Use Fernet symmetric encryption (AES-128)
"""

from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """
    Get encryption key from settings
    
    Preconditions:
    - SECRET_KEY is set in settings
    
    Postconditions:
    - Returns 32-byte Fernet-compatible key
    """
    # Use SECRET_KEY to derive a Fernet-compatible key
    # Hash the SECRET_KEY to get consistent 32 bytes
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_value(plain_text: str) -> str:
    """
    Encrypt a plain text value
    
    Preconditions:
    - plain_text is non-empty string
    
    Postconditions:
    - Returns encrypted string (base64 encoded)
    - Can be decrypted using decrypt_value()
    """
    if not plain_text:
        return ""
    
    fernet = Fernet(get_encryption_key())
    encrypted = fernet.encrypt(plain_text.encode())
    return encrypted.decode()


def decrypt_value(encrypted_text: str) -> str:
    """
    Decrypt an encrypted value
    
    Preconditions:
    - encrypted_text is valid encrypted string from encrypt_value()
    
    Postconditions:
    - Returns original plain text
    - Raises exception if decryption fails
    """
    if not encrypted_text:
        return ""
    
    try:
        fernet = Fernet(get_encryption_key())
        decrypted = fernet.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")
