"""
generate test data

This script generates test data by encoding it in various encoding formats (base85, base64, base32, or base16) and
writing this data, along with other metadata about the encoded data, to an output file and an answer file.

Here's a breakdown of the functions:

1. `encode`: This function takes bytes of data, an encoding type, and an optional answer file. The encoding type can be
'random' to select a random encoding or one of 'base85', 'base64', 'base32', or 'base16'. The data is then encoded in
the selected format. If an answer file is provided, it also writes metadata about the encoded data to the answer file.
This metadata includes information like the encoding used, the mime type and extension of the data, and a checksum.

2. `gen_rand_hex_data_helper`: This function takes a configuration dictionary, an output file, and an answer file. It
generates random data, encodes it, and writes it to the output file. It also writes metadata about the encoded data to
the answer file. The function works with two types of data:
   - One sourced from existing files in a specified directory. The number of sequences to generate from these files i
     given in the configuration.
   - Another type is randomly generated sequences. The number and lengths of these sequences are also given in the
     configuration.

3. `gen_data`: This function opens the output and answer files and calls `gen_rand_hex_data_helper` to generate and
write the data.

4. `main`: This function reads a configuration from a file called 'settings.json' and calls `gen_data` with the
configuration.

The code is intended to be run as a script. When it's run, it calls the `main` function.
"""

import json
import os
import random
import secrets
import sys
from base64 import b64encode, b16encode, b32encode, b85encode
from typing import IO, Optional

import mimetypes

import magic

import hex_hunter


def encode(data: bytes, encoding: str, answer_file: Optional[IO] = None) -> bytes:
    """encode data"""
    encoded_data: bytes

    if encoding == "random":
        # randomly select an encoding to use from this set
        encoding = secrets.choice(["base85", "base64", "base32", "base16"])

    # handle the encoding
    if encoding == "base85":
        encoded_data = b85encode(data)
    elif encoding == "base64":
        encoded_data = b64encode(data)
    elif encoding == "base32":
        encoded_data = b32encode(data)
    elif encoding == "base16":
        encoded_data = b16encode(data)
    else:
        raise ValueError

    if answer_file:
        guessed_mimetype = magic.from_buffer(data, mime=True)
        answer_record = {
            "encoding": encoding,
            "guessed_content_kind": magic.from_buffer(data),
            "guessed_mime_type": guessed_mimetype,
            "guessed_extension": mimetypes.guess_extension(guessed_mimetype),
            "offset": answer_file.tell(),
            "encoded_length": len(encoded_data),
            "decoded_length": len(data),
            "crc16_xmodem": hex_hunter.crc16_xmodem(data),
        }
        answer_file.write(json.dumps(answer_record).encode("utf-8"))
        answer_file.write("\n".encode("utf-8"))
    return encoded_data


def gen_rand_hex_data_helper(config: dict, output_file: IO, answer_file: IO):
    """generate random hex data helper"""
    rand_shuffle = []
    while len(rand_shuffle) < config["encoded_sequence"]["num_sequences"]:
        for file_name in os.listdir(config["encoded_sequence"]["source_directory"]):
            rand_shuffle.append(
                os.path.join(config["encoded_sequence"]["source_directory"], file_name)
            )
            if len(rand_shuffle) == config["encoded_sequence"]["num_sequences"]:
                break
    rand_shuffle.extend([None] * config["random_encoded_sequence"]["num_sequences"])
    random.shuffle(rand_shuffle)
    for item in rand_shuffle:
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
        if item is None:
            embedded_data = hex_hunter.gen_random_data(
                secrets.choice(
                    range(
                        config["random_encoded_sequence"]["length_min"],
                        config["random_encoded_sequence"]["length_max"],
                    )
                )
            )
        else:
            with open(item, "rb") as data_file:
                embedded_data = data_file.read(os.path.getsize(item))
            embedded_data += hex_hunter.crc16_xmodem(embedded_data).to_bytes(
                2, hex_hunter.CSUM_ENDIANESS
            )
        if not hex_hunter.verify_data(embedded_data):
            return -1
        output_file.write(encode(embedded_data, config["encoding"], answer_file))

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
        return gen_data(config)


if __name__ == "__main__":
    sys.exit(main())
