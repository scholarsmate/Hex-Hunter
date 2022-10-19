"""
detect encoded data
"""
import base64
import binascii
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
            if hex_hunter.verify_data(base64.decodebytes(encoded_string)):
                return True
            break
        except binascii.Error:
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


def find_base64_encoded_data(config: dict, input_file: IO) -> int:
    """find base64 encoded data"""
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
            if hex_hunter.is_base64_char(byte):
                encoded_string += byte
            else:
                if validate_base64_string(encoded_string, config["threshold"]):
                    found += 1
                    print(f'data[{found}]: {encoded_string.decode("utf-8")}')
                encoded_string = bytes()
    if validate_base64_string(encoded_string, config["threshold"]):
        found += 1
        print(f'data[{found}]: {encoded_string.decode("utf-8")}')
    return 0


def detect_encoded_data(config: dict):
    """detect encoded data"""
    if config["input_filename"] is None or config["input_filename"] == "-":
        if config["encoding"] == "hex":
            return find_hex_encoded_data(config, sys.stdin)
        if config["encoding"] == "base64":
            return find_base64_encoded_data(config, sys.stdin)
        raise ValueError
    with open(config["input_filename"], "rb") as input_file:
        if config["encoding"] == "hex":
            return find_hex_encoded_data(config, input_file)
        if config["encoding"] == "base64":
            return find_base64_encoded_data(config, input_file)
    raise ValueError


def main():
    """main"""
    config = {
        "threshold": 10,
        "encoding": "base64",
        "input_filename": None,  # "-" or None for stdin, any other string for a filename
    }
    sys.exit(detect_encoded_data(config))


if __name__ == "__main__":
    main()
