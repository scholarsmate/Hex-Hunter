"""
hex_hunter module
"""
from contextlib import contextmanager
import secrets
import sys
from typing import Optional, BinaryIO, TextIO, Union

from fastcrc import crc16 as fast_crc16

__all__ = [
    "crc16_xmodem",
    "gen_random_data",
    "verify_data",
    "is_hex_char",
    "is_hex_char_upper",
    "is_hex_char_lower",
    "is_base64_char",
    "encode_hex",
]

CSUM_ENDIANESS = sys.byteorder


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
    """verify data created by gen_random_data"""
    return data[-2:] == crc16_xmodem(data[:-2]).to_bytes(2, CSUM_ENDIANESS)


def is_hex_char(byte: bytes) -> bool:
    """return True if the given byte is a hex character"""
    return byte in "0123456789abcdefABCDEF".encode("utf-8")


def is_hex_char_upper(byte: bytes) -> bool:
    """return True if the given byte is an uppercase hex character"""
    return byte in "0123456789ABCDEF".encode("utf-8")


def is_hex_char_lower(byte: bytes) -> bool:
    """return True if the given byte is a lowercase hex character"""
    return byte in "0123456789abcdef".encode("utf-8")


def is_base64_char(byte: bytes) -> bool:
    """return True if the given byte is a base64 character"""
    return (
        byte
        #   00000000011111111112222222222333333333344444444445555555555666666
        #   12345678901234567890123456789012345678901234567890123456789012345
        in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=".encode(
            "utf-8"
        )
    )


def encode_hex(byte: bytes) -> bytes:
    """return hex encoded version of the given bytes"""
    return byte.hex().encode("utf-8")
