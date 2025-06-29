# Run this program only once to generate the key pairs.

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate private key
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

private_key_location = "keys/private_key.pem"
public_key_location = "keys/public_key.pem"

# Save private key (keep safe, cloud-only)
with open(private_key_location, "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

# Extract and save public key
public_key = private_key.public_key()
with open(public_key_location, "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

print("✅ RSA key pair generated: 'public_key.pem' and 'private_key.pem'")
