"""
Guess the data kind of a directory of files
"""
import json
import os
import sys

import magic

BUFFER_SIZE = 4096  # consider up to the first 4K of the data to determine the data kind


def data_kind(directory):
    """Guess the data kind of a directory of files"""
    result = []
    for file in sorted(os.listdir(directory)):
        filename = os.path.realpath(os.path.join(directory, file))
        file_size = os.path.getsize(filename)
        with open(filename, "rb") as data_file:
            mime_type = magic.from_buffer(data_file.read(BUFFER_SIZE), mime=True)
            result.append({"filename": filename, "size": file_size, "mime": mime_type})
    return result


def main():
    """main function"""
    result = data_kind(os.path.join("test", "data"))
    print(json.dumps(result, indent=4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
