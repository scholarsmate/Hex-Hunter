"""
detect encoded data

The script is used to detect encoded data, specifically data encoded in hexadecimal or base64 format, in a provided
input file. The code is broken down into several functions, each responsible for a specific task. Here's a brief
overview:

1. `validate_hex_string`: This function takes a string of bytes and a threshold value. It tries to convert the byte
string from hexadecimal to bytes using the `bytes.fromhex` function. If this operation is successful and the
`hex_hunter.verify_data` function (from the hex_hunter library) returns True, the function returns True, indicating the
string was valid hexadecimal encoded data above the given threshold. If it fails due to a ValueError (which happens when
the string is not a valid hexadecimal string), it removes the last character from the string and tries again. The loop
continues until the length of the string is less than the threshold.

2. `validate_base64_string`: Similar to `validate_hex_string`, this function attempts to validate a string of bytes as
base64-encoded data. If the `base64.decodebytes` operation is successful and `hex_hunter.verify_data` returns True, the
function returns True. If the operation fails due to a binascii.Error (which happens when the string is not valid
base64), it tries again after removing one character from the end of the string. The loop continues until the length of
the string is less than the threshold.

3. `find_hex_encoded_data`: This function takes a configuration dictionary and an input file. It reads the file byte by
byte and checks if each byte represents a hexadecimal character. If it does, it appends the byte to a buffer. When it
encounters a non-hexadecimal byte, it checks if the buffer is a valid hexadecimal string using `validate_hex_string`.
If it is, it prints the data and increments a counter. The function repeats this process until it reaches the end of the
file.

4. `find_base64_encoded_data`: This function is similar to `find_hex_encoded_data` but works with base64 encoded data.

5. `detect_encoded_data`: This function takes a configuration dictionary. It opens the input file specified in the
configuration and calls either `find_hex_encoded_data` or `find_base64_encoded_data` depending on the encoding
specified in the configuration.

6. `main`: This function opens a JSON file called `settings.json`, reads a configuration from it, and calls
`detect_encoded_data` with the configuration.

The code is intended to be run as a script. When it's run, it calls the `main` function.
"""


from json import load
from typing import Iterator
from base64 import (
    b16decode,
    b32decode,
    b64decode,
    b85decode,
)
from hex_hunter import (
    BASE_16_BYTES_MC,
    BASE_32_BYTES_MC,
    BASE_64_BYTES,
    BASE_85_BYTES,
    find_encoded_data,
    smart_open,
)


def b16decode_casefold(encoded: bytes) -> bytes:
    """decode base16 (hex) encoded data with case folding"""
    return b16decode(encoded, True)


def b32decode_casefold(encoded: bytes) -> bytes:
    """decode base32 encoded data with case folding"""
    return b32decode(encoded, True)


def correct_base64_error(encoded: bytes) -> bytes:
    return encoded[1:] if encoded.endswith("=".encode("utf-8")) else encoded[:-1]


def detect_encoded_data(config: dict) -> Iterator[tuple[str, int, bytes]]:
    """detect encoded data"""
    encodings = {
        "base16": (BASE_16_BYTES_MC, b16decode_casefold, None),
        "base32": (BASE_32_BYTES_MC, b32decode_casefold, None),
        "base64": (BASE_64_BYTES, b64decode, correct_base64_error),
        "base85": (BASE_85_BYTES, b85decode, None),
    }

    for encoding, (
        valid_byte_set,
        validator_function,
        error_correction,
    ) in encodings.items():
        if (
            "encoding" not in config
            or config["encoding"] == "all"
            or config["encoding"] == encoding
        ):
            with smart_open(config["input_filename"], "rb") as input_file:
                for offset, data in find_encoded_data(
                    input_file,
                    config["threshold"],
                    valid_byte_set,
                    validator_function,
                    error_correction,
                ):
                    yield encoding, offset, data


def main():
    """main"""
    with open("settings.json", "r", encoding="utf-8") as config_file:
        config = load(config_file)
        for encoding, offset, data in detect_encoded_data(config):
            print(
                f'encoding: {encoding}, offset: {offset}, length: {len(data)}, data: {data.decode("utf-8")}'
            )


if __name__ == "__main__":
    main()
