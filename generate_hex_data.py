import secrets
import sys
import hex_hunter


def main():
    with open("answer_key", "w") as answers:
        for i in range(0, 1000):
            r = secrets.token_bytes(secrets.choice(range(4, 1024)))
            s = hex_hunter.gen_random_data(
                secrets.choice(range(8, 1024))
            )  # with 2-byte checksum length range is 10 - 1026
            sys.stdout.buffer.write(r)
            sys.stdout.buffer.write(s.hex().encode("utf-8"))
            sys.stdout.flush()
            print(f"data[{i}]: {s.hex()}", file=answers)
            if not hex_hunter.verify_data(s):
                return -1
        return 0


if __name__ == "__main__":
    sys.exit(main())
