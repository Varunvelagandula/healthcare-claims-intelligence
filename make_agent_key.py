import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

os.makedirs("keys", exist_ok=True)
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

private = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
public = key.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo,
)

with open("keys/agent_key.p8", "wb") as f:
    f.write(private)

# Print ONLY the public key, as one line, ready to paste into Snowflake
print("".join(public.decode().strip().splitlines()[1:-1]))