from cryptography.fernet import Fernet
import base64
import argparse
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SymmetricKeyEncryption:
    def __init__(self, password: str = None):
        """
        Initialize the encryption class with a password-based key derivation
        or generate a random key.
        """
        if password:
            self.key = self._derive_key_from_password(password)
        else:
            self.key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.key)
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """
        Derive a key from a password using PBKDF2.
        """
        # Use a salt (in production, store this securely)
        salt = b'salt_1234567890'  # In production, use os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt the given data (string) and return encrypted string.
        """
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt the given encrypted data and return original string.
        """
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def get_key(self) -> str:
        """
        Get the encryption key as a base64 string.
        """
        return base64.urlsafe_b64encode(self.key).decode()


def main():
    parser = argparse.ArgumentParser(description='Symmetric encryption/decryption tool')
    parser.add_argument('operation', choices=['encrypt', 'decrypt'], 
                       help='Operation to perform: encrypt or decrypt')
    parser.add_argument('--data', '-d', required=True, 
                       help='Data to encrypt or encrypted data to decrypt')
    parser.add_argument('--password', '-p', default="my_secure_password_123",
                       help='Password for key derivation (default: my_secure_password_123)')
    
    args = parser.parse_args()
    
    # Initialize encryptor with password
    encryptor = SymmetricKeyEncryption(args.password)
    
    if args.operation == 'encrypt':
        try:
            encrypted_result = encryptor.encrypt_data(args.data)
            print(f"Original Data: {args.data}")
            print(f"Encrypted Data: {encrypted_result}")
        except Exception as e:
            print(f"Encryption failed: {e}")
    
    elif args.operation == 'decrypt':
        try:
            decrypted_result = encryptor.decrypt_data(args.data)
            print(f"Encrypted Data: {args.data}")
            print(f"Decrypted Data: {decrypted_result}")
        except Exception as e:
            print(f"Decryption failed: {e}")


if __name__ == "__main__":
    main()