"""
Guess the data kind of a directory of files
"""
import json
import os
import sys
from typing import Union

import magic

import hex_hunter


def data_kind(directory: str) -> list[dict[str, Union[str, int]]]:
    """Guess the data kind of a directory of files"""
    result = []
    for file in sorted(os.listdir(directory)):
        file_path = os.path.realpath(os.path.join(directory, file))
        file_size = os.path.getsize(file_path)
        with open(file_path, "rb") as data_file:
            data = data_file.read(file_size)
        result.append(
            {
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": magic.from_buffer(data, mime=True),
                "crc16_xmodem": hex_hunter.crc16_xmodem(data),
            }
        )
    return result


def main() -> int:
    """main function"""
    result = data_kind(os.path.join("test", "data"))
    print(json.dumps(result, indent=4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
