from src.data_processing import config, spark_ops, delta_lake_ops, process_raw_data
from itertools import product
from pathlib import Path
import logging


def train_models(data):
    # estimators = [20, 50, 75, 100, 200, 400, 800]
    estimators = [100, 200, 500]
    # depth = [16, 20, 24, 28, 32, 64, 128, None]
    depth = [32, 64, None]
    c = 'gini'
    for e, d in product(estimators, depth):
        if Path(config.model_save_dir_path / f"{e}_estimators_{d}_depth_{c}.model").exists():
            print(f"Model with {e} estimators, {d} depth, and {c} criteria already exists")
            continue
        print(f"Training model with {e} estimators, {d} depth, and {c} criteria")
        logging.info(f"Training model with {e} estimators, {d} depth, and {c} criteria")
        compile_sklearn_model.train_model(data, e, d, c, jobs=-1)
        print(f"Model with {e} estimators, {d} depth, and {c} criteria trained")
        logging.info(f"Model with {e} estimators, {d} depth, and {c} criteria trained")


if __name__ == '__main__':
    config.use_intelex = False

    from src.training import compile_sklearn_model

    percent_set_aside = 40

    process_raw_data.run(percent_set_aside / 100)
    df = spark_ops.df_from_csvs(config.processed_minus_set_aside)

    temp_delta_lake_path = Path('test_delta_lake_tables') / f'set_aside_{percent_set_aside}_percent.model'
    temp_delta_lake_path.parent.mkdir(parents=True, exist_ok=True)

    delta_lake_ops.save_table(df, temp_delta_lake_path)

    data = compile_sklearn_model.ready_data(temp_delta_lake_path)

    compile_sklearn_model.train_model(data, 100, 32, 'gini',
                                      jobs=-1, save=True,
                                      save_name=f'intelex_{config.use_intelex}_{percent_set_aside}_percent_set_aside.model')
    # evaluate_models.evaluate(data)
    # evaluate_models.plot_heatmaps()
