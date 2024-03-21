import zipfile
import json
import logging
import random
import shutil
from time import time
from pathlib import Path
import concurrent.futures
from collections import namedtuple

from . import convert_files_to_csv, data_preprocessing, rename_files
from .config import extract_dir_path, processed_dir_path, filtered_dir_path, set_aside_path, processed_minus_set_aside
from .. import utils

base_path = Path(__file__).parent
config_path = base_path / 'training_config.json'

# make sure base_path is correct
assert config_path.exists(), f'Config file not found at {config_path}'

threadpool_executor = concurrent.futures.ThreadPoolExecutor(1000)

SessionTrialLabel = namedtuple('SessionTrialLabel', ['session', 'trial', 'label'])


def extract_zip(zip_path: Path, extract_path: Path):
    print(f'Extracting {zip_path} to {extract_path}')
    start = time()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        names = zip_ref.namelist()
        print(f'Extracting {len(names)} files')
        for name in names:
            zip_ref.extract(name, path=extract_path)
        # zip_ref.extractall(extract_path)
        # futures = [threadpool_executor.submit(zip_ref.extract, name, path=extract_path) for name in names]
        # concurrent.futures.wait(futures)

    print(f'Extraction took {time() - start:.2f} seconds')
    print(f'Extraction complete')


def check_extraction(raw_path: Path):
    actual_raw_path = raw_path / 'brainwave_rawdata'

    # make sure the directory is correct
    assert (actual_raw_path / 'left').exists(), f'left data not found at {actual_raw_path}'
    assert (actual_raw_path / 'right').exists(), f'right data not found at {actual_raw_path}'
    assert (actual_raw_path / 'forward').exists(), f'forward data not found at {actual_raw_path}'
    assert (actual_raw_path / 'backward').exists(), f'backward data not found at {actual_raw_path}'
    assert (actual_raw_path / 'takeoff').exists(), f'takeoff data not found at {actual_raw_path}'
    assert (actual_raw_path / 'land').exists(), f'land data not found at {actual_raw_path}'


def map_filenames_to_session_and_trial(raw_path: Path) -> dict[Path, SessionTrialLabel]:
    mapping: dict[Path, SessionTrialLabel] = {}
    sessions, trials = set(), set()
    for file in raw_path.rglob('*.txt'):
        sessions.add(str(file.parent.absolute()))
        trials.add(str(file.absolute()))
        label = file.parent.parent.name
        mapping[file] = SessionTrialLabel(len(sessions), len(trials), label)
    return mapping


def process_files(raw_path: Path, processed_path: Path):
    actual_raw_path = raw_path / 'brainwave_rawdata'
    check_extraction(raw_path)

    print(f'Processing raw data at {actual_raw_path}')

    file_mapping = map_filenames_to_session_and_trial(actual_raw_path)
    convert_files_to_csv.run_with_mapping(actual_raw_path.absolute(), file_mapping)

    print('Renaming files')
    rename_files.run(actual_raw_path.absolute())

    print(f'Moving processed data to {processed_path}')
    for category in actual_raw_path.iterdir():
        logging.debug(f'Moving {category.name} to {processed_path / category.name}')
        category.rename(processed_path / category.name)

    print('Finished processing raw data, removing extracted directory')
    clear_directory(raw_path)
    logging.debug(f'Removing directory {raw_path}')
    raw_path.rmdir()


def set_aside_files(raw_path: Path, set_aside_percent=0.2):
    print(f'Setting aside {set_aside_percent * 100}% of files from {raw_path}')
    actual_raw_path = raw_path / 'brainwave_rawdata'
    check_extraction(raw_path)

    to_set_aside = []
    for category in actual_raw_path.iterdir():
        to_set_aside.extend(
            random.sample(list(category.iterdir()), int(len(list(category.iterdir())) * set_aside_percent)))

    futures = [threadpool_executor.submit(utils.move, item, set_aside_path / item.parent.name / item.name)
               for item in to_set_aside]
    concurrent.futures.wait(futures)

    convert_files_to_csv.run(set_aside_path.absolute())


def filter_files(processed_path: Path, filtered_path: Path):
    print(f'Filtering files from {processed_path} to {filtered_path}')
    files = []
    for category in processed_path.iterdir():
        for file in category.iterdir():
            filtered_file_path = filtered_path / category.name / file.name
            filtered_file_path.parent.mkdir(parents=True, exist_ok=True)
            files.append((file, filtered_file_path))

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(data_preprocessing.filter_file, file, filtered_file)
                   for file, filtered_file in files]
        concurrent.futures.wait(futures)


def clear_directory(directory: Path):
    for f in directory.iterdir():
        shutil.rmtree(f)


def remove_non_txt_files(directory: Path):
    for f in directory.rglob('*'):
        if f.is_file() and f.suffix != '.txt':
            f.unlink()


def run():
    with config_path.open() as f:
        data_paths = json.load(f)['data_paths']

    zip_path = Path(data_paths['compressed_raw'])

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
    # filter_files(processed_dir_path, filtered_dir_path)


if __name__ == "__main__":
    run()
