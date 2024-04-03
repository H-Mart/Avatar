from flask import Flask, render_template, request
import pandas as pd
import json
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

prediction_cache = []
labels = ['backward', 'down', 'forward',
          'land', 'left', 'right', 'takeoff', 'up']
app = Flask(__name__)

with open(f'sklearn_naive.skl_model', 'rb') as f:
    model = pickle.load(f)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/eegrandomforestprediction', methods=['POST'])
def eegprediction():
    if request.data is None:
        return {'error': 'No data provided'}

    # import and process the data to feed to ML model
    data_dict = request.get_json()

    df = pd.DataFrame.from_dict(data_dict, orient='index')
    np_df = df.to_numpy(dtype=np.float64)[:, 1:17]

    # Give to model for it to predict
    prediction = model.predict(np_df)
    pred_labels, pred_label_count = np.unique(prediction, return_counts=True)
    predicted_label = pred_labels[np.argmax(pred_label_count)]

    return {'prediction_label': predicted_label, 'prediction_count': len(prediction_cache)}


if __name__ == '__main__':
    app.run(host='0.0.0.0')
