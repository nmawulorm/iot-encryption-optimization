import requests, base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Simulate cloud ECC key generation
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Send public key to FastAPI server
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

response = requests.post("http://localhost:8000/init", json={"public_key": pem_public_key})
response_data = response.json()

# Load ephemeral public key
ephemeral_public_key = serialization.load_pem_public_key(
    response_data["ephemeral_public_key"].encode()
)

shared_key = private_key.exchange(ec.ECDH(), ephemeral_public_key)

derived_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"key_exchange"
).derive(shared_key)

# Decrypt AES key
iv = base64.b64decode(response_data["iv"])
encrypted_aes_key = base64.b64decode(response_data["encrypted_aes_key"])

cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv))
decryptor = cipher.decryptor()
padded_key = decryptor.update(encrypted_aes_key) + decryptor.finalize()

# Unpad
pad_len = padded_key[-1]
aes_key = padded_key[:-pad_len]

print("✅ AES key successfully received and decrypted:")
print(aes_key.hex())
