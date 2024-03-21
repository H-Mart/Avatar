# Authors: Brady Theisen
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, wait
from pathlib import Path
from time import time


def convert_txt_to_csv_with_mapping(file_path: Path, session, trial, label):
    try:
        # Skip the first four header lines
        df = pd.read_csv(file_path, sep=",", skiprows=4, on_bad_lines='skip')
        df['session'] = session
        df['trial'] = trial
        df['label'] = label
        df.to_csv(file_path.with_suffix('.csv'), index=False)
        file_path.unlink()

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def convert_txt_to_csv(file_path: Path):
    try:
        # Skip the first four header lines
        df = pd.read_csv(file_path, sep=",", skiprows=4, on_bad_lines='skip')
        df.to_csv(file_path.with_suffix('.csv'), index=False)
        file_path.unlink()

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def run_with_mapping(directory: Path, file_mapping):
    print(f"Converting files to csv in {directory}")
    start = time()
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(convert_txt_to_csv_with_mapping, f, s, t, l)
                   for f, (s, t, l) in file_mapping.items()]
        wait(futures)
    print(f"Conversion took {time() - start:.2f} seconds")


def run(directory: Path):
    print(f"Converting files to csv in {directory}")
    start = time()
    with ProcessPoolExecutor() as executor:
        executor.map(convert_txt_to_csv, directory.rglob('*.txt'))
    print(f"Conversion took {time() - start:.2f} seconds")


if __name__ == "__main__":
    run('data/')
