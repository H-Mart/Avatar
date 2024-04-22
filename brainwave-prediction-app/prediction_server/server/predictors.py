import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
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
