import os
import random


def generate_file(filename, size):
    with open(filename, "wb") as f:
        f.write(os.urandom(size))


def create_1kb_file(filename, size=1024):
    with open(filename, "wb") as f:
        f.write(bytes(chr(random.randint(0, 128)), "ascii") * size)


if __name__ == "__main__":
    generate_file("test_for_curl2.txt", 1024 * 500)

    create_1kb_file("1KB", 1024)
