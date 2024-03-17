# Authors: Brady Theisen
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import time


def convert_txt_to_csv(file_path: Path):
    try:
        # Skip the first four header lines
        df = pd.read_csv(file_path, sep=",", skiprows=4, on_bad_lines='skip')
        df.to_csv(file_path.with_suffix('.csv'), index=False)
        file_path.unlink()

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def run(directory: Path):
    print(f"Converting files to csv in {directory}")
    start = time()
    with ProcessPoolExecutor() as executor:
        executor.map(convert_txt_to_csv, directory.rglob('*.txt'))
    print(f"Conversion took {time() - start:.2f} seconds")


if __name__ == "__main__":
    run('data/')
