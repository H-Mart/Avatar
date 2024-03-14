# Authors: Brady Theisen
import pandas as pd
import os
from concurrent.futures import ProcessPoolExecutor


def convert_txt_to_csv(file_path):
    try:
        # Skip the first four header lines
        df = pd.read_csv(file_path, sep=",", skiprows=4, on_bad_lines='skip')

        # Convert to CSV format and save
        csv_file_path = file_path.rsplit('.', 1)[0] + '.csv'
        df.to_csv(csv_file_path, index=False)

        # Remove original txt file
        os.remove(file_path)

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def get_all_txt_files(directory):
    for dirpath, dirnames, files in os.walk(directory):
        # Check if there are any txt files in the directory
        txt_files = [f for f in files if f.endswith('.txt')]
        if txt_files:
            for file_name in txt_files:
                file_path = os.path.join(dirpath, file_name)
                yield file_path


def run(directory):
    with ProcessPoolExecutor() as executor:
        executor.map(convert_txt_to_csv, get_all_txt_files(directory))


if __name__ == "__main__":
    run('data/')
