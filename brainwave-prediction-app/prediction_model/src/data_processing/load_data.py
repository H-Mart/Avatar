import pandas as pd
from pathlib import Path

from concurrent.futures import ProcessPoolExecutor


def load_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)


def load_csvs(file_path: Path) -> pd.DataFrame:
    files = [f for f in file_path.rglob('*.csv')]
    with ProcessPoolExecutor() as executor:
        master_df = pd.concat(list(executor.map(load_data, files)), ignore_index=True)
    return master_df
