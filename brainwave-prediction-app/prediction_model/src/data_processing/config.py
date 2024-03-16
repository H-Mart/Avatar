import json
from pathlib import Path
import logging

config_path = Path(__file__).parent / Path('training_config.json')
config_obj = json.load(config_path.open())

data_paths: dict = config_obj['data_paths']
base_data_path = Path(data_paths['base'])
extract_dir_path = base_data_path / Path(data_paths['raw'])
processed_dir_path = base_data_path / Path(data_paths['processed'])
filtered_dir_path = base_data_path / Path(data_paths['filtered'])
deltalake_table_path = base_data_path / Path(data_paths['deltalake_table'])
set_aside_path = base_data_path / Path(data_paths['set_aside'])
processed_minus_set_aside = base_data_path / Path(data_paths['processed_minus_set_aside'])

spark_config: dict = config_obj['spark']
spark_executor_memory: str = spark_config['executor_memory']
spark_driver_memory: str = spark_config['driver_memory']
spark_timeout: str = spark_config['timeout']

model_save_dir_path = Path(config_obj['models']['save_directory'])
model_stats_path = Path(config_obj['models']['stats'])

headset_streaming_host: str = config_obj['headset_streaming']['host']
headset_streaming_port: int = config_obj['headset_streaming']['port']
brainflow_batch_size: int = config_obj['headset_streaming']['batch_size']

logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
