"""
hex_hunter module
"""
import binascii
from contextlib import contextmanager
import secrets
import sys
import logging
from typing import Optional, BinaryIO, TextIO, Union, Iterator, IO, Callable

from fastcrc import crc16 as fast_crc16

__all__ = [
    "BASE_16_CHARS_UC",
    "BASE_16_BYTES_UC",
    "BASE_16_BYTES_LC",
    "BASE_16_BYTES_MC",
    "BASE_32_CHARS_UC",
    "BASE_32_BYTES_UC",
    "BASE_32_BYTES_LC",
    "BASE_32_BYTES_MC",
    "BASE_64_CHARS",
    "BASE_64_BYTES",
    "BASE_64_URL_CHARS",
    "BASE_64_URL_BYTES",
    "BASE_85_CHARS",
    "BASE_85_BYTES",
    "crc16_xmodem",
    "gen_random_data",
    "verify_data",
    "smart_open",
    "validate_encoded",
    "find_encoded_data",
]

CSUM_ENDIANESS = sys.byteorder

#                   0000000001111111
#                   1234567890123456
BASE_16_CHARS_UC = "0123456789ABCDEF"
BASE_16_BYTES_UC = set(BASE_16_CHARS_UC.encode("utf-8"))
BASE_16_BYTES_LC = set(BASE_16_CHARS_UC.lower().encode("utf-8"))
BASE_16_BYTES_MC = BASE_16_BYTES_UC | BASE_16_BYTES_LC

#                   00000000011111111112222222222333
#                   12345678901234567890123456789012
BASE_32_CHARS_UC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
BASE_32_BYTES_UC = set(BASE_32_CHARS_UC.encode("utf-8"))
BASE_32_BYTES_LC = set(BASE_32_CHARS_UC.lower().encode("utf-8"))
BASE_32_BYTES_MC = BASE_32_BYTES_UC | BASE_32_BYTES_LC

#                00000000011111111112222222222333333333344444444445555555555666666
#                12345678901234567890123456789012345678901234567890123456789012345
BASE_64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
BASE_64_BYTES = set(BASE_64_CHARS.encode("utf-8"))

#                    0000000001111111111222222222233333333334444444444555555555566666
#                    1234567890123456789012345678901234567890123456789012345678901234
BASE_64_URL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
BASE_64_URL_BYTES = set(BASE_64_URL_CHARS.encode("utf-8"))

#                0000000001111111111222222222233333333334444444444555555555566666666667777777777888888
#                1234567890123456789012345678901234567890123456789012345678901234567890123456789012345
BASE_85_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"
BASE_85_BYTES = set(BASE_85_CHARS.encode("utf-8"))


@contextmanager
def smart_open(filename, mode="rb") -> Union[BinaryIO, TextIO]:
    """opens the given filename, if "-" will be stdin or stdout depending on the mode"""
    if filename == "-":
        if mode is None or mode == "" or "r" in mode:
            file_handle = sys.stdin.buffer if "b" in mode else sys.stdin
        else:
            file_handle = sys.stdout.buffer if "b" in mode else sys.stdout
    else:
        file_handle = (
            # pylint: disable=unspecified-encoding
            open(filename, mode)
            if "b" in mode
            else open(filename, mode, encoding="utf-8")
        )
    try:
        yield file_handle
    finally:
        if filename != "-":
            file_handle.close()


def crc16_xmodem(data: bytes, initial_value: Optional[int] = None) -> int:
    """crc16 generates a 2-byte checksum"""
    return fast_crc16.xmodem(data, initial=initial_value)


def gen_random_data(nbytes: int) -> bytes:
    """generate a random byte-string containing the given number of bytes, plus 2 (for checksum)"""
    data = secrets.token_bytes(nbytes)
    return data + crc16_xmodem(data).to_bytes(2, CSUM_ENDIANESS)


def verify_data(data: bytes) -> bool:
    """verify data created by generate_data"""
    return data[-2:] == crc16_xmodem(data[:-2]).to_bytes(2, CSUM_ENDIANESS)


def validate_encoded(
    encoded_string: bytes,
    threshold: int,
    decode_func: Callable[[bytes], bytes],
    error_correction: Optional[Callable[[bytes], bytes]] = None,
) -> bool:
    """return True if the given baseXX string is a valid find and False otherwise"""
    while len(encoded_string) >= threshold:
        try:
            decoded: bytes = decode_func(encoded_string)
            if verify_data(decoded):
                return True
            logging.debug("FAILED: %s", encoded_string.decode("utf-8"))
            break
        except ValueError:
            if error_correction:
                encoded_string = error_correction(encoded_string)
            else:
                encoded_string = encoded_string[:-1]
            continue
    return False


def find_encoded_data(
    input_file: IO,
    threshold: int,
    valid_byte_set: set[int],
    decode_func: Callable[[bytes], bytes],
    error_correction: Optional[Callable[[bytes], bytes]] = None,
) -> Iterator[tuple[int, bytearray]]:
    """Yield encoded data as they are found."""
    encoded_bytes = bytearray()
    file_offset = -1
    found_data_offset = -1
    while True:
        read_buffer = input_file.read(1024 * 8)
        if not read_buffer:
            break
        for byte in read_buffer:
            file_offset += 1
            if byte in valid_byte_set:
                if found_data_offset == -1:
                    found_data_offset = file_offset
                encoded_bytes += byte.to_bytes(1, sys.byteorder)
                continue
            if validate_encoded(
                encoded_bytes, threshold, decode_func, error_correction
            ):
                yield found_data_offset, encoded_bytes
            encoded_bytes.clear()
            found_data_offset = -1
    if validate_encoded(encoded_bytes, threshold, decode_func, error_correction):
        yield found_data_offset, encoded_bytes
