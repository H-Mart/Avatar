from ..data_processing import load_data, process_raw_data
from ..data_processing.config import processed_dir_path
from time import time
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow_decision_forests.keras import RandomForestModel
import numpy as np

# process_raw_data.run()

start = time()
df = load_data.load_csvs(processed_dir_path)
print(f"Time to load data: {time() - start}")
df.sort_values(by=['session', 'trial', ' Timestamp'], inplace=True)
cols = [str(x) for x in df.columns if x.startswith(' EXG')]
labels = ['left', 'right', 'takeoff', 'land', 'forward', 'backward']

df['label'] = df['label'].map(labels.index)
channel_data = df[cols]
assert channel_data.shape[1] == 16
label_data = df['label']
channel_data = channel_data.to_numpy()
label_data = label_data.to_numpy()

for i, label in enumerate(labels):
    label_data[label_data == label] = i

X = channel_data[:, :17].astype(np.float64)
y = label_data.astype(np.float64)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train)).batch(100)
test_dataset = tf.data.Dataset.from_tensor_slices((X_test, y_test)).batch(100)

model = RandomForestModel(num_trees=100, max_depth=32)
model.compile(metrics=["accuracy"])
model.fit(train_dataset)

print(f"Training accuracy: {model.evaluate(train_dataset)}")
print(f"Testing accuracy: {model.evaluate(test_dataset)}")

# Save the model
model.save("tensorflow_naive.keras")
