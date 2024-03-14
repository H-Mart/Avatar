import subprocess
import zipfile
import json
from pathlib import Path
import os
import logging
import sys

sys.path.append('..')
import convert_files_to_csv
import data_preprocessing
from config import extract_dir_path, processed_dir_path, filtered_dir_path

base_path = Path(__file__).parent
config_path = base_path / 'training_config.json'

# make sure base_path is correct
assert config_path.exists(), f'Config file not found at {config_path}'


def extract_zip(zip_path: Path, extract_path: Path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)


def process_files(raw_path: Path, processed_path: Path):
    actual_raw_path = raw_path / 'brainwave_rawdata'

    # make sure the directory is correct
    assert (actual_raw_path / 'left').exists(), f'left data not found at {actual_raw_path}'
    assert (actual_raw_path / 'right').exists(), f'right data not found at {actual_raw_path}'
    assert (actual_raw_path / 'forward').exists(), f'forward data not found at {actual_raw_path}'
    assert (actual_raw_path / 'backward').exists(), f'backward data not found at {actual_raw_path}'
    assert (actual_raw_path / 'takeoff').exists(), f'takeoff data not found at {actual_raw_path}'
    assert (actual_raw_path / 'land').exists(), f'land data not found at {actual_raw_path}'

    print(f'Processing raw data at {actual_raw_path}')

    print('Renaming files')
    shell_script_path = base_path / 'rename_files.sh'
    subprocess.run((shell_script_path.absolute(), actual_raw_path.absolute()))

    print('Converting files to CSV')
    convert_files_to_csv.run(actual_raw_path.absolute())

    print(f'Moving processed data to {processed_path}')
    for category in actual_raw_path.iterdir():
        logging.debug(f'Moving {category.name} to {processed_path / category.name}')
        category.rename(processed_path / category.name)

    print('Finished processing raw data, removing extracted directory')
    # purposefully not checking files to remove, since all files should have been moved
    for root, dirs, files in os.walk(raw_path, topdown=False):
        for name in dirs:
            logging.debug(f'Removing directory {os.path.join(root, name)}')
            os.rmdir(os.path.join(root, name))
    logging.debug(f'Removing directory {raw_path}')
    raw_path.rmdir()


def filter_files(processed_path: Path, filtered_path: Path):
    for category in processed_path.iterdir():
        for file in category.iterdir():
            filtered_file_path = filtered_path / category.name / file.name
            filtered_file_path.parent.mkdir(parents=True, exist_ok=True)
            data_preprocessing.filter_file(file, filtered_file_path)


def clear_directory(directory: Path):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def remove_non_txt_files(directory: Path):
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            if not name.endswith('.txt'):
                os.remove(os.path.join(root, name))


def main():
    with config_path.open() as f:
        data_paths = json.load(f)['data_paths']

    zip_path = Path(data_paths['compressed_raw'])

    # base_data_path = Path(data_paths['base'])
    # extract_dir_path = base_data_path / Path(data_paths['raw'])
    # processed_dir_path = base_data_path / Path(data_paths['processed'])
    # filtered_dir_path = base_data_path / Path(data_paths['filtered'])

    extract_dir_path.mkdir(parents=True, exist_ok=True)
    processed_dir_path.mkdir(parents=True, exist_ok=True)
    filtered_dir_path.mkdir(parents=True, exist_ok=True)

    print('Clearing directories')
    clear_directory(extract_dir_path)
    clear_directory(processed_dir_path)
    clear_directory(filtered_dir_path)
    print('Directories cleared')

    extract_zip(zip_path, extract_dir_path)
    remove_non_txt_files(extract_dir_path)
    process_files(extract_dir_path, processed_dir_path)
    filter_files(processed_dir_path, filtered_dir_path)


if __name__ == "__main__":
    main()
