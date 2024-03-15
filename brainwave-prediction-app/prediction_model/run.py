from src.training import compile_sklearn_model, evaluate_models
from src.data_processing import config
from itertools import product
from pathlib import Path
import logging


def train_models(data):
    estimators = [20, 50, 75, 100, 200, 400, 800]
    depth = [16, 20, 24, 28, 32, 64, 128, None]
    criteria = ['gini', 'entropy', 'log_loss']
    for e, d, c in product(estimators, depth, criteria):
        if Path(config.model_save_dir_path / f"{e}_estimators_{d}_depth_{c}.model").exists():
            print(f"Model with {e} estimators, {d} depth, and {c} criteria already exists")
            continue
        print(f"Training model with {e} estimators, {d} depth, and {c} criteria")
        logging.info(f"Training model with {e} estimators, {d} depth, and {c} criteria")
        compile_sklearn_model.train_model(data, e, d, c, jobs=-1)
        print(f"Model with {e} estimators, {d} depth, and {c} criteria trained")
        logging.info(f"Model with {e} estimators, {d} depth, and {c} criteria trained")


if __name__ == '__main__':
    data = compile_sklearn_model.ready_data()

    train_models(data)
    evaluate_models.evaluate(data)
    evaluate_models.plot_heatmaps()
