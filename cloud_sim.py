import requests
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Step 1: Generate ECC key pair (simulating the cloud)
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

# Step 2: Send public key to FastAPI server
response = requests.post("http://127.0.0.1:8000/init", json={"public_key": pem_public_key})
if response.status_code != 200:
    print("❌ Key exchange failed:", response.json())
    exit()

response_data = response.json()

# Step 3: Derive AES key from shared secret using ECDH
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

# Step 4: Decrypt the AES key using the derived key
iv = base64.b64decode(response_data["iv"])
encrypted_aes_key = base64.b64decode(response_data["encrypted_aes_key"])

cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv))
decryptor = cipher.decryptor()
padded_key = decryptor.update(encrypted_aes_key) + decryptor.finalize()

pad_len = padded_key[-1]
aes_key = padded_key[:-pad_len]

print("✅ AES key successfully received and decrypted:")
print(aes_key.hex())

# 🔓 Optional Step 5: Function to decrypt encrypted values from server
def decrypt_value(base64_iv: str, base64_ciphertext: str):
    iv = base64.b64decode(base64_iv)
    ciphertext = base64.b64decode(base64_ciphertext)

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_value = decryptor.update(ciphertext) + decryptor.finalize()

    pad_len = padded_value[-1]
    plaintext = padded_value[:-pad_len]

    return plaintext.decode("utf-8")

# Example: simulate receiving data from server
print("\n🔐 Enter encrypted data from server for decryption:")

iv_input = input("Paste 'iv': ").strip()
val_input = input("Paste 'value': ").strip()

try:
    decrypted = decrypt_value(iv_input, val_input)
    print(f"\n✅ Decrypted value: {decrypted}")
except Exception as e:
    print(f"\n❌ Decryption failed: {str(e)}")
