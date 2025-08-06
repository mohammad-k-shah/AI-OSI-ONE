"""
Token Manager

Handles secure storage and encryption of API tokens.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from utils.logger import LoggerMixin


class TokenManager(LoggerMixin):
    """Manages secure storage and encryption of API tokens."""
    
    def __init__(self, key_file: Optional[str] = None):
        """Initialize token manager."""
        super().__init__()
        self.key_file = Path(key_file) if key_file else Path("config/auth/encryption.key")
        self.tokens_file = Path("config/auth/tokens.json")
        self._fernet: Optional[Fernet] = None
        self._load_or_create_key()
        self._ensure_auth_dir()
    
    def _ensure_auth_dir(self) -> None:
        """Ensure the auth directory exists."""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        self.tokens_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_or_create_key(self) -> None:
        """Load existing encryption key or create a new one."""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                self._fernet = Fernet(key)
                self.log_info("Encryption key loaded from file")
            else:
                self._create_new_key()
        except Exception as e:
            self.log_error("Failed to load encryption key", error=str(e))
            self._create_new_key()
    
    def _create_new_key(self) -> None:
        """Create a new encryption key."""
        try:
            # Generate a key from a password (in production, use a secure password)
            password = os.getenv("OSI_AGENT_PASSWORD", "default_password_change_in_production")
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Save the key
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            self._fernet = Fernet(key)
            self.log_info("New encryption key created and saved")
            
        except Exception as e:
            self.log_error("Failed to create encryption key", error=str(e))
            raise
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token."""
        if not self._fernet:
            raise RuntimeError("Encryption key not available")
        
        try:
            encrypted = self._fernet.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.log_error("Failed to encrypt token", error=str(e))
            raise
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token."""
        if not self._fernet:
            raise RuntimeError("Encryption key not available")
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.log_error("Failed to decrypt token", error=str(e))
            raise
    
    def store_token(self, service: str, token: str) -> None:
        """Store an encrypted token."""
        try:
            encrypted_token = self.encrypt_token(token)
            
            # Load existing tokens
            tokens = self._load_tokens()
            tokens[service] = encrypted_token
            
            # Save tokens
            self._save_tokens(tokens)
            self.log_info("Token stored successfully", service=service)
            
        except Exception as e:
            self.log_error("Failed to store token", service=service, error=str(e))
            raise
    
    def get_token(self, service: str) -> Optional[str]:
        """Get a decrypted token."""
        try:
            tokens = self._load_tokens()
            encrypted_token = tokens.get(service)
            
            if not encrypted_token:
                return None
            
            return self.decrypt_token(encrypted_token)
            
        except Exception as e:
            self.log_error("Failed to get token", service=service, error=str(e))
            return None
    
    def remove_token(self, service: str) -> bool:
        """Remove a stored token."""
        try:
            tokens = self._load_tokens()
            if service in tokens:
                del tokens[service]
                self._save_tokens(tokens)
                self.log_info("Token removed successfully", service=service)
                return True
            return False
            
        except Exception as e:
            self.log_error("Failed to remove token", service=service, error=str(e))
            return False
    
    def list_tokens(self) -> list[str]:
        """List all stored token services."""
        try:
            tokens = self._load_tokens()
            return list(tokens.keys())
        except Exception as e:
            self.log_error("Failed to list tokens", error=str(e))
            return []
    
    def _load_tokens(self) -> Dict[str, str]:
        """Load tokens from file."""
        if not self.tokens_file.exists():
            return {}
        
        try:
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log_error("Failed to load tokens file", error=str(e))
            return {}
    
    def _save_tokens(self, tokens: Dict[str, str]) -> None:
        """Save tokens to file."""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(tokens, f, indent=2)
        except Exception as e:
            self.log_error("Failed to save tokens file", error=str(e))
            raise
    
    def validate_token(self, service: str, token: str) -> bool:
        """Validate if a token is valid (basic check)."""
        if not token:
            return False
        
        # Basic validation - in production, you might want to test the token
        # against the actual service API
        return len(token) > 10
    
    def rotate_token(self, service: str, new_token: str) -> bool:
        """Rotate a token (replace with new one)."""
        try:
            if self.validate_token(service, new_token):
                self.store_token(service, new_token)
                self.log_info("Token rotated successfully", service=service)
                return True
            else:
                self.log_warning("Invalid token provided for rotation", service=service)
                return False
        except Exception as e:
            self.log_error("Failed to rotate token", service=service, error=str(e))
            return False 