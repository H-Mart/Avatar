from flask import Flask, render_template, request
import pandas as pd
import json
import numpy as np
import pickle
from pathlib import Path

prediction_cache = []
labels = ['backward', 'down', 'forward',
          'land', 'left', 'right', 'takeoff', 'up']
app = Flask(__name__)

with open(f'models/sklearn_naive.skl_model', 'rb') as f:
    model = pickle.load(f)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/eegrandomforestprediction', methods=['POST'])
def eegprediction():
    # import and process the data to feed to ML model
    data = request.data
    data_dict = json.loads(data)

    df = pd.DataFrame.from_dict(data_dict).to_numpy(dtype=np.float64)
    df = np.transpose(df)[:, 1:17]

    # Give to model for it to predict
    prediction = model.predict(df)
    pred_labels, pred_label_count = np.unique(prediction, return_counts=True)
    predicted_label = pred_labels[np.argmax(pred_label_count)]

    return {"prediction_label": predicted_label, "prediction_count": len(prediction_cache)}


if __name__ == '__main__':
    app.run(host='0.0.0.0')
