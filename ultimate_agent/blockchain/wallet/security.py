import os
from cryptography.fernet import Fernet

class WalletSecurity:
    def __init__(self, encryption_key: str):
        self.fernet = Fernet(encryption_key.encode())

    def encrypt_key(self, raw_key: str) -> bytes:
        return self.fernet.encrypt(raw_key.encode())

    def decrypt_key(self, encrypted: bytes) -> str:
        return self.fernet.decrypt(encrypted).decode()

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()

# Usage:
# from ultimate_agent.config.settings import settings
# wallet_security = WalletSecurity(settings.WALLET_ENCRYPTION_KEY)
# encrypted = wallet_security.encrypt_key("private_key")
# decrypted = wallet_security.decrypt_key(encrypted)
