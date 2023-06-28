"""
encoding-samples.py

This script is used to generate SAMPLE data for documentation. It generates a SAMPLE string and encodes it using
base16, base32, base64, and base85. It then prints the encoded strings and their lengths. The output is used in the
documentation for the `hex_hunter` package.
"""
from base64 import b64encode, b16encode, b32encode, b85encode, urlsafe_b64encode


def create_samples(plain: str) -> dict:
    """create samples"""
    plain_bytes = plain.encode("utf-8")

    return {
        "base16": b16encode(plain_bytes),
        "base32": b32encode(plain_bytes),
        "base64": b64encode(plain_bytes),
        "b64url": urlsafe_b64encode(plain_bytes).rstrip(b"="),
        "base85": b85encode(plain_bytes),
    }


SAMPLE = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~123456"

print(f"plain : {SAMPLE} ({len(SAMPLE)})")
for encoding, encoded_bytes in create_samples(SAMPLE).items():
    decoded_bytes = encoded_bytes.decode("utf-8")
    print(f"{encoding}: {decoded_bytes} ({len(decoded_bytes)})")
