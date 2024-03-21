from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes
import pandas as pd
from pathlib import Path
import logging


def apply_filters(df: pd.DataFrame,
                  sampling_rate=125, low_cutoff=5, high_cutoff=50,
                  filter_order=4, filter_type=FilterTypes.BUTTERWORTH) -> pd.DataFrame:
    def do_filter(series: pd.Series):
        series_np = series.to_numpy()
        DataFilter.remove_environmental_noise(series_np, sampling_rate, NoiseTypes.FIFTY_AND_SIXTY.value)
        DataFilter.perform_bandpass(series_np, sampling_rate, low_cutoff, high_cutoff, filter_order,
                                    filter_type, 0)
        return pd.Series(series_np)

    df_copy = df.copy()
    cols1 = [str(x) for x in df_copy.columns if x.startswith(' EXG')]
    cols_df = df_copy[cols1]
    cols_df.apply(do_filter)
    df_copy[cols1] = cols_df

    return df_copy


def filter_file(data_path: Path, save_path: Path):
    logging.debug(f"Filtering data from {data_path} to {save_path}")
    df = pd.read_csv(data_path, index_col=None, header=0)

    # sort so that the data is in order when applying the filters
    df.sort_values(by=' Timestamp', inplace=True)
    filtered_data = apply_filters(df)
    filtered_data.to_csv(save_path, index=False)
