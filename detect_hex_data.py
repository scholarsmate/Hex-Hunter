import sys

CSUM_ENDIANESS = sys.byteorder


def is_hex(b: bytes) -> bool:
    return b in "0123456789abcdefABCDEF".encode("utf-8")


def is_hex_upper(b: bytes) -> bool:
    return b in "0123456789ABCDEF".encode("utf-8")


def is_hex_lower(b: bytes) -> bool:
    return b in "0123456789abcdef".encode("utf-8")


def crc16(data: bytes, offset: int, length: int):
    """crc16 generates a 2-byte checksum"""
    if (
        data is None
        or offset < 0
        or offset > len(data) - 1
        and offset + length > len(data)
    ):
        raise ValueError
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


def verify_data(data: bytes):
    return data[-2:] == crc16(data[:-2], 0, len(data) - 2).to_bytes(2, CSUM_ENDIANESS)


if __name__ == "__main__":
    threshold = 10
    hex_string = bytes()
    found = 0
    while True:
        buffer = sys.stdin.buffer.read(1024)
        if not buffer:
            break
        for b in buffer:
            b = b.to_bytes(1, sys.byteorder)  # byte order doesn't matter for 1 byte
            if is_hex_lower(b):
                hex_string += b
            else:
                while len(hex_string) > threshold:
                    try:
                        data = bytes.fromhex(hex_string.decode("utf-8"))
                        if verify_data(data):
                            found += 1
                            print(
                                f'data[{found}] ({len(data)}): {hex_string.decode("utf-8")}'
                            )
                        else:
                            print(f"FAILED ({len(data)}): {hex_string.decode('utf-8')}")
                    except ValueError as e:
                        print(f"ERROR {e}: {hex_string.decode('utf-8')}")
                        hex_string = hex_string[:-1]
                        continue
                    break
                hex_string = bytes()
