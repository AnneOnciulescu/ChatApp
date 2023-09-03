from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

class Key:
    def __init__(self):
        # Generate a new RSA key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Serialize the private key to PEM format
        self.private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize the public key to PEM format
        self.public_key = self.private_key.public_key()

        self.public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def validate_key(self, pem_key):
        try:
            serialization.load_pem_public_key(pem_key, backend=default_backend())
        except:
            raise ValueError('Wrong key format')
        
    def decrypt(self, text):
        data = base64.b64decode(text.encode('utf-8'))
        
        plaintext = self.private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return plaintext.decode('utf-8')

 
    def encrypt(self, plaintext_data, public_key_pem):
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )

        ciphertext = public_key.encrypt(
            plaintext_data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Specify the hash algorithm here
                algorithm=hashes.SHA256(),  # Specify the same hash algorithm here
                label=None
            )
        )

        return base64.b64encode(ciphertext).decode('utf-8')
