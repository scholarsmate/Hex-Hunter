"""
detect encoded data
"""

import sys
from typing import IO

import hex_hunter


def validate_hex_string(encoded_string: bytes, threshold: int):
    """return True if the given string is a valid find and False otherwise"""
    while len(encoded_string) > threshold:
        try:
            if hex_hunter.verify_data(bytes.fromhex(encoded_string.decode("utf-8"))):
                return True
            break
        except ValueError:
            encoded_string = encoded_string[:-1]
            continue
    return False


def find_hex_encoded_data(config: dict, input_file: IO) -> int:
    """find hex encoded data"""
    found = 0
    encoded_string = bytes()
    while True:
        read_buffer = input_file.buffer.read(1024 * 8)
        if not read_buffer:
            break
        for byte in read_buffer:
            byte = byte.to_bytes(
                1, sys.byteorder
            )  # byte order doesn't matter for 1 byte
            if hex_hunter.is_hex_char_lower(byte):
                encoded_string += byte
            else:
                if validate_hex_string(encoded_string, config["threshold"]):
                    found += 1
                    print(f'data[{found}]: {encoded_string.decode("utf-8")}')
                encoded_string = bytes()
    if validate_hex_string(encoded_string, config["threshold"]):
        found += 1
        print(f'data[{found}]: {encoded_string.decode("utf-8")}')
    return 0


def main():
    """main"""
    config = {"threshold": 10, "encoding": "hex"}
    sys.exit(find_hex_encoded_data(config, sys.stdin))


if __name__ == "__main__":
    main()
