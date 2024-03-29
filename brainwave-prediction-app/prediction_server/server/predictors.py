import tensorflow as tf
import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from tensorflow_decision_forests.keras import RandomForestModel
from abc import ABC, abstractmethod

"""
This module contains classes that define an interface for predictors, to be used by the server.
The interface is defined by the abstract class BasePredictor, which has three abstract methods:
- load_model: loads a model from a file
- preprocess: preprocesses data before prediction
- predict: makes a prediction on the preprocessed data

The data that is passed to preprocess is expected to be in the form that the brainflow library outputs
Then the preprocess method should convert this data into the same format as the data that the model was trained on
"""

labels = ['left', 'right', 'takeoff', 'land', 'forward', 'backward']

data_channel_columns = np.arange(1, 17)
data_sample_index_column = 0
data_timestamp_column = 30
data_accelerometer_columns = np.arange(17, 20)


class BasePredictor(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def load_model(self, model_path: Path):
        raise NotImplementedError

    @abstractmethod
    def preprocess(self, data):
        raise NotImplementedError

    @abstractmethod
    def predict(self, data):
        raise NotImplementedError


class SciKitPredictor(BasePredictor):
    def __init__(self):
        super().__init__()
        self.model: RandomForestClassifier | None = None

    def load_model(self, model_path):
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    def preprocess(self, data: np.ndarray):
        processed_data = data[:, data_channel_columns]
        return processed_data

    def predict(self, processed_data):
        return self.model.predict(processed_data)

    def evaluate(self, data, data_labels):
        return self.model.score(data, data_labels)


class TensorFlowPredictor(BasePredictor):
    def __init__(self):
        super().__init__()
        self.model = None

    def load_model(self, model_path):
        # with open(model_path, 'rb') as f:
        #     self.model = pickle.load(f)
        self.model = tf.keras.models.load_model(str(model_path))

    def preprocess(self, data: np.ndarray):
        # np.sort(data, axis=data_timestamp_column)
        data = data[data[:, data_timestamp_column].argsort()]
        processed_data = data[:, data_channel_columns].astype(np.float64)

        processed_data = tf.data.Dataset.from_tensor_slices(processed_data).batch(100)

        return processed_data

    def predict(self, data):
        return self.model.predict(data)

    def evaluate(self, data, labels):
        predictions = self.model.predict(data)
        accuracy = tf.keras.metrics.Accuracy()
        return accuracy(labels, predictions)


if __name__ == '__main__':
    from random import shuffle
    import pandas as pd

    test_data = Path('/home/henry/School/csci495/bci_data/brainwave_processed')
    left_data = list((test_data / 'left').iterdir())
    shuffle(left_data)
    right_data = list((test_data / 'right').iterdir())
    shuffle(right_data)
    takeoff_data = list((test_data / 'takeoff').iterdir())
    shuffle(takeoff_data)
    land_data = list((test_data / 'land').iterdir())
    shuffle(land_data)
    forward_data = list((test_data / 'forward').iterdir())
    shuffle(forward_data)
    backward_data = list((test_data / 'backward').iterdir())
    shuffle(backward_data)

    test_df = [
        pd.read_csv(left_data[0]).sort_values(by=[' Timestamp']),
        pd.read_csv(right_data[0]).sort_values(by=[' Timestamp']),
        pd.read_csv(takeoff_data[0]).sort_values(by=[' Timestamp']),
        pd.read_csv(land_data[0]).sort_values(by=[' Timestamp']),
        pd.read_csv(forward_data[0]).sort_values(by=[' Timestamp']),
        pd.read_csv(backward_data[0]).sort_values(by=[' Timestamp']),
    ]

    test_channel_data = [df.to_numpy()[:, :32].astype(np.float64) for df in test_df]
    test_label_data = [df.to_numpy()[:, -1] for df in test_df]

    scikit_predictor = SciKitPredictor()
    scikit_predictor.load_model(Path('../models/sklearn_naive.skl_model'))

    tensorflow_predictor = TensorFlowPredictor()
    tensorflow_predictor.load_model(Path('../models/tensorflow_naive.keras'))

    for dt, label in zip(test_channel_data, test_label_data):
        processed_data_sk = scikit_predictor.preprocess(dt)
        print(f'Scikit: {scikit_predictor.evaluate(processed_data_sk, label)}')

    for test_label_np in test_label_data:
        for i, l in enumerate(labels):
            test_label_np[test_label_np == l] = i

    for dt, label in zip(test_channel_data, test_label_data):
        # processed_data_tf = tf.data.Dataset.from_tensor_slices((dt, label.astype(np.float64))).batch(100)
        processed_data_tf = tensorflow_predictor.preprocess(dt)
        print(f'Tensorflow: {tensorflow_predictor.evaluate(processed_data_tf, label.astype(np.float64))}')
