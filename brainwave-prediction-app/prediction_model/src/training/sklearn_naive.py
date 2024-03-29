from ..data_processing import load_data, process_raw_data
from ..data_processing.config import processed_dir_path
from time import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# process_raw_data.run()

start = time()
df = load_data.load_csvs(processed_dir_path)
print(f"Time to load data: {time() - start}")
df.sort_values(by=['session', 'trial', ' Timestamp'], inplace=True)
cols = [str(x) for x in df.columns if x.startswith(' EXG')]
labels = ['left', 'right', 'takeoff', 'land', 'forward', 'backward']

channel_data = df[cols]
assert channel_data.shape[1] == 16
label_data = df['label']

channel_data = channel_data.to_numpy()
label_data = label_data.to_numpy()

X = channel_data[:, :17]
y = label_data

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

clf = RandomForestClassifier(n_estimators=100, max_depth=32, n_jobs=-1, verbose=2)
clf.fit(X_train, y_train)

print(f"Training accuracy: {clf.score(X_train, y_train)}")
print(f"Testing accuracy: {clf.score(X_test, y_test)}")

# Save the model
import pickle

with open('../../../prediction_server/models/sklearn_naive.skl_model', 'wb') as f:
    pickle.dump(clf, f)
