#!python

import json
from pathlib import Path
import logging
from os import PathLike
from typing import Final
import argparse


def refresh_config():
    config_path = Path(__file__).parent / Path('training_config.json')
    config_obj = json.load(config_path.open())

    globals()['data_paths'] = config_obj['data_paths']
    globals()['base_data_path'] = Path(data_paths['base'])
    globals()['extract_dir_path'] = base_data_path / Path(data_paths['raw'])
    globals()['processed_dir_path'] = base_data_path / Path(data_paths['processed'])
    globals()['filtered_dir_path'] = base_data_path / Path(data_paths['filtered'])
    globals()['deltalake_table_path'] = base_data_path / Path(data_paths['deltalake_table'])
    globals()['set_aside_path'] = base_data_path / Path(data_paths['set_aside'])
    globals()['processed_minus_set_aside'] = base_data_path / Path(data_paths['processed_minus_set_aside'])

    globals()['spark_config'] = config_obj['spark']
    globals()['spark_executor_memory'] = spark_config['executor_memory']
    globals()['spark_driver_memory'] = spark_config['driver_memory']
    globals()['spark_timeout'] = spark_config['timeout']

    globals()['model_save_dir_path'] = Final[Path](config_obj['models']['save_directory'])
    globals()['model_stats_path'] = Final[Path](config_obj['models']['stats'])

    globals()['headset_streaming_host'] = config_obj['headset_streaming']['host']
    globals()['headset_streaming_port'] = config_obj['headset_streaming']['port']
    globals()['brainflow_batch_size'] = config_obj['headset_streaming']['batch_size']

    globals()['use_intelex'] = config_obj['training']['use_intelex']


def save_config_and_refresh(f):
    f()
    with config_path.open('w') as f:
        json.dump(config_obj, f)
    refresh_config()


@save_config_and_refresh
def set_base_data_path(path: PathLike):
    config_obj['data_paths']['base'] = path


@save_config_and_refresh
def set_model_save_dir_path(path: PathLike):
    config_obj['models']['save_directory'] = path


@save_config_and_refresh
def set_model_stats_path(path: PathLike):
    config_obj['models']['stats'] = path


config_path = Path(__file__).parent / Path('training_config.json')
config_obj = json.load(config_path.open())

data_paths: Final[dict] = config_obj['data_paths']
base_data_path: Final[Path] = Path(data_paths['base'])
extract_dir_path: Final[Path] = base_data_path / Path(data_paths['raw'])
processed_dir_path: Final[Path] = base_data_path / Path(data_paths['processed'])
filtered_dir_path: Final[Path] = base_data_path / Path(data_paths['filtered'])
deltalake_table_path: Final[Path] = base_data_path / Path(data_paths['deltalake_table'])
set_aside_path: Final[Path] = base_data_path / Path(data_paths['set_aside'])
processed_minus_set_aside: Final[Path] = base_data_path / Path(data_paths['processed_minus_set_aside'])

spark_config: Final[dict] = config_obj['spark']
spark_executor_memory: Final[str] = spark_config['executor_memory']
spark_driver_memory: Final[str] = spark_config['driver_memory']
spark_timeout: Final[str] = spark_config['timeout']

model_save_dir_path: Final[Path] = Path(config_obj['models']['save_directory'])
model_stats_path: Final[Path] = Path(config_obj['models']['stats'])

headset_streaming_host: Final[str] = config_obj['headset_streaming']['host']
headset_streaming_port: Final[int] = config_obj['headset_streaming']['port']
brainflow_batch_size: Final[int] = config_obj['headset_streaming']['batch_size']

use_intelex: bool = config_obj['training']['use_intelex']

logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Methods to set and get configuration values')
    set_parser = parser.add_subparsers().add_parser('set', help='Set a configuration value')
    set_parser.add_argument('option', type=str, help='Which key to set',
                            choices=['base_data_path', 'model_save_dir_path', 'model_stats_path'])
    set_parser.add_argument('value', type=Path, help='Value to set')

    args = parser.parse_args()

    match args.option:
        case 'base_data_path':
            set_base_data_path(args.value)
        case 'model_save_dir_path':
            set_model_save_dir_path(args.value)
        case 'model_stats_path':
            set_model_stats_path(args.value)
        case _:
            raise ValueError('Invalid option')
