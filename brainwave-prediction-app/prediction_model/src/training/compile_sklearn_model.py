from ..data_processing import config

if config.use_intelex:
    from sklearnex import patch_sklearn

    patch_sklearn()

import pickle

from pathlib import Path
from dataclasses import dataclass
from typing import Any

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from ..data_processing import delta_lake_ops
import numpy as np


@dataclass
class TrainTestData:
    X_train: Any
    X_test: Any
    y_train: Any
    y_test: Any
    label_map: Any


def ready_data(table_path: Path = config.deltalake_table_path) -> TrainTestData:
    df1 = delta_lake_ops.load_table(table_path)
    pdf = df1.toPandas()
    label = 'label'
    classes = pdf[label].unique().tolist()
    pdf[label] = pdf[label].map(classes.index)  # .astype(np.float64)

    X = pdf.drop(columns=[label, 'filename'])
    y = pdf[label]

    label_map = {classes.index(c): c for c in classes}

    return TrainTestData(*train_test_split(X, y, test_size=0.2), label_map)


def save_model(model: RandomForestClassifier, save_path: Path):
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with save_path.open('wb') as f:
        pickle.dump(model, f)


def load_model(save_path: Path) -> RandomForestClassifier:
    with save_path.open('rb') as f:
        return pickle.load(f)


def train_model(data: TrainTestData, n_estimators=100, max_depth=16, criterion='gini', save=True, save_name=None,
                jobs=-1):
    model = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth, criterion=criterion,
        n_jobs=jobs, verbose=2)

    model.fit(data.X_train, data.y_train)

    if save:
        save_name = save_name or f'{n_estimators}_estimators_{max_depth}_depth_{criterion}.model'
        save_model(model, config.model_save_dir_path / save_name)

    return model
