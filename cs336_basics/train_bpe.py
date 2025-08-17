import sys
import regex as re
import os
from typing import BinaryIO
from collections import defaultdict


def split(file: BinaryIO, chunk_num, split_special_token):
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    chunk_size = file_size // chunk_num
    CHUNK_SIZE = 4096
    boundaries = [chunk_size * i for i in range(chunk_num + 1)]
    boundaries[-1] = file_size

    for i in range(1, chunk_num):
        file.seek(boundaries[i])  # overlap
        curr_offset = boundaries[i]
        while True:
            mini_chunk = file.read(CHUNK_SIZE)

            if mini_chunk == b"":
                boundaries[i] = file_size
                break

            found_at = mini_chunk.find(split_special_token)
            if found_at != -1:
                boundaries[i] = curr_offset + found_at
                break
            curr_offset += CHUNK_SIZE
        if boundaries[i] == file_size:
            break
    return boundaries


def pretokenization():
    pass


def train(input_path: str,
          vocab_size: int,
          special_tokens: list[str]
          ):
    with open(input_path, "rb") as f:
        boundaries = split(f, 4, b"<|endoftext|>")
        count = defaultdict(int)
        for start, end in zip(boundaries[:-1], boundaries[1:]):
            f.seek(start)
            print(start, end)
            st_pat = "|".join(map(re.escape, special_tokens))
            chunk = f.read(end - start).decode("utf-8", errors="ignore")
            chunk = "".join(re.split(st_pat, chunk))

            pat = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

            for token in re.finditer(pat, chunk):
                count[token] += 1
            print(count.keys()[:2])
        print(count)


if __name__ == "__main__":
    train(
        "/Users/runji/Interesting/CS336/data/TinyStoriesV2-GPT4-train.txt", 0, ["<|endoftext|>"])
