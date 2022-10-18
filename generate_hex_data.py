import secrets
import sys

CSUM_ENDIANESS = sys.byteorder


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


def gen_random_data(nbytes: int) -> bytes:
    """generate a random byte-string that contains the given number of bytes, plus 2 (for checksum)"""
    data: bytes = secrets.token_bytes(nbytes)
    checksum = crc16(data, 0, len(data)).to_bytes(2, CSUM_ENDIANESS)
    data += checksum
    return data


def verify_data(data: bytes):
    return data[-2:] == crc16(data[:-2], 0, len(data) - 2).to_bytes(2, CSUM_ENDIANESS)


if __name__ == "__main__":
    with open("answer_key", "w") as answers:
        for i in range(0, 1000):
            r = secrets.token_bytes(secrets.choice(range(4, 1024)))
            s = gen_random_data(
                secrets.choice(range(8, 1024))
            )  # with 2-byte checksum length range is 10 - 1026
            sys.stdout.buffer.write(r)
            sys.stdout.buffer.write(s.hex().encode("utf-8"))
            sys.stdout.flush()
            print(f"data[{i}]: {s.hex()}", file=answers)
            if not verify_data(s):
                sys.exit(-1)
        sys.exit(0)
