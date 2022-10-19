import sys
import hex_hunter


def validate_hex_string(encoded_string: bytes, threshold: int):
    while len(encoded_string) > threshold:
        try:
            if hex_hunter.verify_data(bytes.fromhex(encoded_string.decode("utf-8"))):
                return True
            break
        except ValueError as e:
            encoded_string = encoded_string[:-1]
            continue
    return False


def find_hex_encoded_data(config: dict) -> int:
    found = 0
    encoded_string = bytes()
    while True:
        read_buffer = sys.stdin.buffer.read(1024 * 8)
        if not read_buffer:
            break
        for b in read_buffer:
            b = b.to_bytes(1, sys.byteorder)  # byte order doesn't matter for 1 byte
            if hex_hunter.is_hex_char_lower(b):
                encoded_string += b
            else:
                if validate_hex_string(encoded_string, config["threshold"]):
                    found += 1
                    print(f'data[{found}]: {encoded_string.decode("utf-8")}')
                encoded_string = bytes()
    if validate_hex_string(encoded_string, config["threshold"]):
        found += 1
        print(f'data[{found}]: {encoded_string.decode("utf-8")}')
    return 0


if __name__ == "__main__":
    config = {"threshold": 10, "encoding": "hex"}
    sys.exit(find_hex_encoded_data(config))
