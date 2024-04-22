import os
import pandas as pd
from pathlib import Path


def load_and_process_csv(filename):
    # Load the CSV file, skipping the first 4 lines
    with open(filename, 'r') as file:
        header_lines = [next(file) for _ in range(4)]  # Read the first 4 lines
        data = pd.read_csv(file)  # Read the rest of the data as a DataFrame

    # Remove the last column from the data
    data = data.iloc[:, :-1]

    # Optionally, you can save the modified dataframe to a new CSV file
    os.rename(filename, f'{filename}.bak')
    with open(filename, 'w') as output_file:
        # Write the first 4 lines unchanged
        output_file.writelines(header_lines)

        # Append the processed data, converting it back to CSV format

        data.to_csv(filename, mode='a', index=False)


def undo():
    p = Path('files_for_synthetic_run')
    for file in p.iterdir():
        if file.suffix == '.txt':
            file.unlink()

    for file in p.iterdir():
        if file.suffix == '.bak':
            os.rename(file, f'{file.name}.txt')


if __name__ == '__main__':
    # undo()
    p = Path('files_for_synthetic_run')
    for file in p.iterdir():
        load_and_process_csv(file)
