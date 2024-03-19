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


def load_set_aside():
    sa_df = spark_ops.df_from_csvs(config.set_aside_path)
    return sa_df


def get_real_accuracy(set_aside_df, model, label_map):
    df1 = set_aside_df
    pdf = df1.toPandas()

    label = 'label'
    pdf[label] = pdf[label].map(label_map)  # .astype(np.float64)
    pdf[' Timestamp'] = 0

    X = pdf.drop(columns=[label, 'filename'])
    y = pdf[label].to_numpy()

    y_pred = model.predict(X)
    print('actual', y[:10])
    print('predict', y_pred[:10])
    return accuracy_score(y, y_pred)


if __name__ == '__main__':
    config.use_intelex = False

    from src.training import compile_sklearn_model
    from sklearn.metrics import accuracy_score

    percent_set_aside = 20

    # process_raw_data.run(percent_set_aside / 100)
    # df = spark_ops.df_from_csvs(config.processed_minus_set_aside)

    temp_delta_lake_path = Path('test_delta_lake_tables') / f'data_not_set_aside-{percent_set_aside}.delta-lake'
    temp_delta_lake_path.parent.mkdir(parents=True, exist_ok=True)

    set_aside_dt = temp_delta_lake_path.parent / f'data_set_aside-{percent_set_aside}.delta-lake'
    set_aside_dt.parent.mkdir(parents=True, exist_ok=True)

    # delta_lake_ops.save_table(df, temp_delta_lake_path)
    # delta_lake_ops.save_table(load_set_aside(), set_aside_dt)

    temp_model_path = Path('test_models') / f'set_aside_{percent_set_aside}_percent.model'
    temp_model_path.parent.mkdir(parents=True, exist_ok=True)

    data = compile_sklearn_model.ready_data(temp_delta_lake_path)
    sa_dt = delta_lake_ops.load_table(set_aside_dt)

    exit()

    model_name = f'intelex_{config.use_intelex}_{percent_set_aside}_percent_set_aside.model'
    model = compile_sklearn_model.train_model(data, 100, 16, 'gini',
                                              jobs=-1, save=True,
                                              save_name=model_name,
                                              save_path=temp_model_path)

    print(f"Model: {model_name} trained with {percent_set_aside}% set aside")
    print(f'Accuracy on test data: {accuracy_score(data.y_test, model.predict(data.X_test))}')
    print(f"Accuracy on set aside data: {get_real_accuracy(sa_dt, model, data.class_to_int_map)}")
    # evaluate_models.evaluate(data)
    # evaluate_models.plot_heatmaps()
