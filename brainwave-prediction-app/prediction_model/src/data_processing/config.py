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

spark_config: dict = config_obj['spark']
spark_executor_memory: str = spark_config['executor_memory']
spark_driver_memory: str = spark_config['driver_memory']
spark_timeout: str = spark_config['timeout']

model_save_dir_path = Path(config_obj['models']['save_directory'])
model_plots_path = Path(config_obj['models']['metric_plots'])

logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
