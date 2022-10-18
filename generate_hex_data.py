import secrets
import sys
from base64 import b64encode
from typing import IO

import hex_hunter


def encode(data: bytes, encoding: str, answer_file: IO) -> bytes:
    if encoding == "hex":
        enc = hex_hunter.encode_hex(data)
        answer_file.write(enc.decode('utf-8'))
        answer_file.write("\n")
        return enc
    elif encoding == "base64":
        enc = b64encode(data)
        answer_file.write(enc.decode('utf-8'))
        answer_file.write("\n")
        return enc
    else:
        raise ValueError


def gen_rand_hex_data_helper(config: dict, output_file: IO, answer_file: IO):
    for i in range(0, config["num_encoded_sequences"]):
        output_file.buffer.write(
            secrets.token_bytes(
                secrets.choice(
                    range(
                        config["random_sequence"]["length_min"],
                        config["random_sequence"]["length_max"],
                    )
                )
            )
        )
        s = hex_hunter.gen_random_data(
            secrets.choice(
                range(
                    config["random_encoded_sequence"]["length_min"],
                    config["random_encoded_sequence"]["length_max"],
                )
            )
        )
        if not hex_hunter.verify_data(s):
            return -1
        output_file.buffer.write(encode(s, config["encoding"], answer_file))
        output_file.flush()

    output_file.buffer.write(
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
    with open(config["answer_filename"], "w") as answer_file:
        if config["output_filename"] is None or config["output_filename"] == "-":
            return gen_rand_hex_data_helper(config, sys.stdout, answer_file)
        else:
            with open(config["output_filename"], "w") as output_file:
                return gen_rand_hex_data_helper(config, output_file, answer_file)


if __name__ == "__main__":
    config: dict = {
        "encoding": "hex",  # "hex" or "base64"
        "random_sequence": {"length_min": 4, "length_max": 1024},
        "random_encoded_sequence": {"length_min": 8, "length_max": 1024},
        "num_encoded_sequences": 1000,
        "answer_filename": "answer_key",
        "output_filename": None,  # "-" or None for stdout, any other string for a filename
    }
    sys.exit(gen_data(config))
