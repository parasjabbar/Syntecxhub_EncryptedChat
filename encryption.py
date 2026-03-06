from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import hashlib
import os

class Encryptor:
    def __init__(self, password="mysecretpassword"):
        """
        Initialize the encryptor with a password.
        The password is used to generate a 32-byte AES key.
        """
        # Generate a consistent 32-byte key from the password
        self.key = hashlib.sha256(password.encode()).digest()
        print(f"[Encryption] Key generated (32 bytes)")
    
    def encrypt_message(self, plain_text):
        """
        Encrypt a message using AES-256 in CBC mode.
        Returns: base64 encoded string containing IV + ciphertext
        """
        try:
            # Generate a random 16-byte Initialization Vector (IV)
            iv = get_random_bytes(AES.block_size)
            
            # Create AES cipher in CBC mode
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Convert message to bytes, pad it, and encrypt
            plain_bytes = plain_text.encode('utf-8')
            padded_data = pad(plain_bytes, AES.block_size)
            encrypted_bytes = cipher.encrypt(padded_data)
            
            # Combine IV and ciphertext, then base64 encode for easy transmission
            combined = iv + encrypted_bytes
            encrypted_message = base64.b64encode(combined).decode('utf-8')
            
            return encrypted_message
            
        except Exception as e:
            print(f"[Encryption Error] {e}")
            return None
    
    def decrypt_message(self, encrypted_text):
        """
        Decrypt a message that was encrypted with encrypt_message.
        Expects: base64 encoded string containing IV + ciphertext
        """
        try:
            # Decode from base64
            combined = base64.b64decode(encrypted_text)
            
            # Extract IV (first 16 bytes) and ciphertext (remaining)
            iv = combined[:AES.block_size]
            ciphertext = combined[AES.block_size:]
            
            # Create cipher for decryption
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Decrypt and remove padding
            decrypted_padded = cipher.decrypt(ciphertext)
            decrypted_bytes = unpad(decrypted_padded, AES.block_size)
            
            # Convert back to string
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"[Decryption Error] {e}")
            return None

# Test the encryption if run directly
if __name__ == "__main__":
    # Create encryptor
    enc = Encryptor("testpassword")
    
    # Test message
    test_msg = "Hello World! This is a secret message."
    print(f"Original: {test_msg}")
    
    # Encrypt
    encrypted = enc.encrypt_message(test_msg)
    print(f"Encrypted: {encrypted}")
    
    # Decrypt
    decrypted = enc.decrypt_message(encrypted)
    print(f"Decrypted: {decrypted}")