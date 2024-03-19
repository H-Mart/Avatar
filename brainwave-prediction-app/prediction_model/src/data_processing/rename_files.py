import shutil
import random
import os
import sys

from datetime import datetime, timedelta
from pathlib import Path
from functools import partial

import concurrent.futures

from ..utils import wait_no_ret, move

categories = ["backward", "forward", "land", "left", "right", "takeoff"]


def rand_time_past(days=10) -> datetime:
    """Generate a random datetime in the past within a given day range."""
    return datetime.now() - timedelta(days=random.randint(0, days),
                                      hours=random.randint(0, 23),
                                      minutes=random.randint(0, 59))


def change_timestamp(file_path: Path, max_days_past=10) -> Path:
    """Change the timestamp of a file to a random time in the past."""
    t = rand_time_past(max_days_past).timestamp()
    os.utime(file_path, (t, t))
    return file_path


def process_category(category, base_dir, executor: concurrent.futures.ThreadPoolExecutor):
    """Process csv files in a given category: move, rename, and change timestamps."""
    category_dir = base_dir / category

    # Move all files to the category directory
    files = category_dir.rglob('*.csv')
    files = list(executor.map(lambda f: move(f, category_dir), files))

    # Remove any subdirectories
    wait_no_ret(executor.map(shutil.rmtree, [p for p in category_dir.iterdir() if p.is_dir()]))

    # Temporarily rename files to avoid name conflicts
    files = list(executor.map(lambda x: move(x[1], x[1].with_name(f'{x[0]}temp.csv')), enumerate(files, start=1)))

    # Rename files to a random number between 1 and the number of files
    random.shuffle(files)
    files = list(executor.map(lambda x: move(x[1], x[1].with_name(f'{x[0]}.csv')), enumerate(files, start=1)))

    # Record then change timestamps of files
    original_timestamps = list(executor.map(lambda x: x.stat().st_mtime, files))
    wait_no_ret(executor.map(change_timestamp, files))
    modified_timestamps = list(executor.map(lambda x: x.stat().st_mtime, files))

    for file, orig, mod in zip(files, original_timestamps, modified_timestamps):
        pass
        # print(f"Original timestamp of {file.relative_to(category_dir)}: {datetime.fromtimestamp(orig)}")
        # print(f"Modified timestamp of {file.relative_to(category_dir)}: {datetime.fromtimestamp(mod)}")


def run(directory: Path):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Use threading to process each category in parallel
        wait_no_ret(executor.map(partial(process_category, base_dir=directory, executor=executor), categories))


if __name__ == '__main__':
    base_dir = Path(sys.argv[1])
    run(base_dir)
