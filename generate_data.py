"""
generate test data
"""
import json
import secrets
import sys
from base64 import b64encode
from typing import IO

import hex_hunter


def encode(data: bytes, encoding: str, answer_file: IO) -> bytes:
    """encode data"""
    if encoding == "hex":
        enc = hex_hunter.encode_hex(data)
        answer_file.write(enc)
        answer_file.write("\n".encode("utf-8"))
        return enc
    if encoding == "base64":
        enc = b64encode(data)
        answer_file.write(enc)
        answer_file.write("\n".encode("utf-8"))
        return enc
    raise ValueError


def gen_rand_hex_data_helper(config: dict, output_file: IO, answer_file: IO):
    """generate random hex data helper"""
    for _ in range(0, config["num_encoded_sequences"]):
        output_file.write(
            secrets.token_bytes(
                secrets.choice(
                    range(
                        config["random_sequence"]["length_min"],
                        config["random_sequence"]["length_max"],
                    )
                )
            )
        )
        embedded_data = hex_hunter.gen_random_data(
            secrets.choice(
                range(
                    config["random_encoded_sequence"]["length_min"],
                    config["random_encoded_sequence"]["length_max"],
                )
            )
        )
        if not hex_hunter.verify_data(embedded_data):
            return -1
        output_file.write(encode(embedded_data, config["encoding"], answer_file))
        output_file.flush()

    output_file.write(
        secrets.token_bytes(
            secrets.choice(
                range(
                    config["random_sequence"]["length_min"],
                    config["random_sequence"]["length_max"],
                )
            )
        )
    )
    output_file.flush()
    return 0


def gen_data(config: dict):
    """generate test data"""
    with open(config["answer_filename"], "wb") as answer_file:
        with hex_hunter.smart_open(config["output_filename"], "wb") as output_file:
            return gen_rand_hex_data_helper(config, output_file, answer_file)


def main():
    """main"""
    with open("settings.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        sys.exit(gen_data(config))


if __name__ == "__main__":
    main()
