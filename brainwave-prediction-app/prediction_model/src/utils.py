import shutil

from collections import deque
from typing import Iterator
from pathlib import Path


def wait_no_ret(x: Iterator):
    """Consumes an iterator without returning results."""
    deque(x, maxlen=0)


def move(file: Path, dst: Path, overwrite=True) -> Path:
    """Move a file to a new destination, with optional overwriting."""
    if dst.is_dir():
        dst = dst / file.name
    if overwrite and dst.exists():
        dst.unlink()
    return Path(shutil.move(str(file), str(dst)))
