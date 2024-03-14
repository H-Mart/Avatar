import pickle

from pathlib import Path
from dataclasses import dataclass
from typing import Any

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split

from ..data_processing import config, delta_lake_ops


@dataclass
class TrainTestData:
    X_train: Any
    X_test: Any
    y_train: Any
    y_test: Any


def ready_data() -> TrainTestData:
    df1 = delta_lake_ops.load_table()
    pdf = df1.toPandas()
    label = 'label'
    classes = pdf[label].unique().tolist()
    pdf[label] = pdf[label].map(classes.index)

    X = pdf.drop(columns=[label, 'filename'])
    y = pdf[label]

    return TrainTestData(*train_test_split(X, y, test_size=0.2))


def save_model(model: RandomForestClassifier, save_path: Path):
    with save_path.open('wb') as f:
        pickle.dump(model, f)


def load_model(save_path: Path) -> RandomForestClassifier:
    with save_path.open('rb') as f:
        return pickle.load(f)


def train_model(data: TrainTestData, n_estimators=100, max_depth=16, save=True, save_name=None):
    model = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth,
        n_jobs=-1, verbose=2)

    model.fit(data.X_train, data.y_train)

    if save:
        save_name = save_name or f'{n_estimators}_estimators_{max_depth}_depth.model'
        save_model(model, config.model_save_dir_path / save_name)

    return model


def main():
    estimators = [1, 5, 10, 20, 50, 100]
    data = ready_data()
    for e in estimators:
        model = train_model(data, e)


if __name__ == '__main__':
    main()
