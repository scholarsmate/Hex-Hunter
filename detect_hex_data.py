import sys
import hex_hunter


def main():
    threshold = 10
    hex_string = bytes()
    found = 0
    while True:
        buffer = sys.stdin.buffer.read(1024)
        if not buffer:
            break
        for b in buffer:
            b = b.to_bytes(1, sys.byteorder)  # byte order doesn't matter for 1 byte
            if hex_hunter.is_hex_lower(b):
                hex_string += b
            else:
                while len(hex_string) > threshold:
                    try:
                        data = bytes.fromhex(hex_string.decode("utf-8"))
                        if hex_hunter.verify_data(data):
                            found += 1
                            print(
                                f'data[{found}] ({len(data)}): {hex_string.decode("utf-8")}'
                            )
                        else:
                            print(f"**FAILED ({len(data)}): {hex_string.decode('utf-8')}")
                    except ValueError as e:
                        print(f"**ERROR {e}: {hex_string.decode('utf-8')}")
                        hex_string = hex_string[:-1]
                        continue
                    break
                hex_string = bytes()


if __name__ == "__main__":
    main()
