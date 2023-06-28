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

import base64
import binascii
import json
import sys
from typing import IO

import hex_hunter


def validate_hex_string(encoded_string: bytes, threshold: int) -> bool:
    """return True if the given hex string is a valid find and False otherwise"""
    while len(encoded_string) >= threshold:
        try:
            if hex_hunter.verify_data(bytes.fromhex(encoded_string.decode("utf-8"))):
                return True
            break
        except ValueError:
            encoded_string = encoded_string[:-1]
            continue
    return False


def validate_base64_string(encoded_string: bytes, threshold: int) -> bool:
    """return True if the given base64 string is a valid find and False otherwise"""
    while len(encoded_string) >= threshold:
        try:
            decoded = base64.decodebytes(encoded_string)
            if hex_hunter.verify_data(decoded):
                return True
            print(f"FAILED: {encoded_string.decode('utf-8')}")
            break
        except binascii.Error:
            encoded_string = (
                encoded_string[1:]
                if encoded_string.endswith("=".encode("utf-8"))
                else encoded_string[:-1]
            )
            continue
    return False


def find_hex_encoded_data(config: dict, input_file: IO) -> int:
    """find hex encoded data"""
    found = 0
    encoded_string = bytearray()
    while True:
        read_buffer = input_file.read(1024 * 8)
        if not read_buffer:
            break
        for byte in read_buffer:
            byte = byte.to_bytes(
                1, sys.byteorder
            )  # byte order doesn't matter for 1 byte
            if hex_hunter.is_hex_char_lower(byte):
                encoded_string += byte
                continue
            if validate_hex_string(encoded_string, config["threshold"]):
                found += 1
                print(f'data[{found}]: {encoded_string.decode("utf-8")}')
            encoded_string.clear()
    if validate_hex_string(encoded_string, config["threshold"]):
        found += 1
        print(f'data[{found}]: {encoded_string.decode("utf-8")}')
    return 0


def find_base64_encoded_data(config: dict, input_file: IO) -> int:
    """find base64 encoded data"""
    found = 0
    encoded_string = bytearray()

    while True:
        read_buffer = input_file.read(1024 * 8)
        if not read_buffer:
            break
        for byte in read_buffer:
            byte = byte.to_bytes(
                1, sys.byteorder
            )  # byte order doesn't matter for 1 byte
            if hex_hunter.is_base64_char(byte):
                encoded_string += byte
                continue
            if validate_base64_string(bytes(encoded_string), config["threshold"]):
                found += 1
                print(f'data[{found}]: {encoded_string.decode("utf-8")}')
            encoded_string.clear()
    if validate_base64_string(encoded_string, config["threshold"]):
        found += 1
        print(f'data[{found}]: {encoded_string.decode("utf-8")}')
    return 0


def detect_encoded_data(config: dict):
    """detect encoded data"""
    with hex_hunter.smart_open(config["input_filename"], "rb") as input_file:
        if config["encoding"] == "hex":
            return find_hex_encoded_data(config, input_file)
        if config["encoding"] == "base64":
            return find_base64_encoded_data(config, input_file)
        return find_hex_encoded_data(config, input_file) + find_base64_encoded_data(
            config, input_file
        )


def main():
    """main"""
    with open("settings.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        sys.exit(detect_encoded_data(config))


if __name__ == "__main__":
    main()
