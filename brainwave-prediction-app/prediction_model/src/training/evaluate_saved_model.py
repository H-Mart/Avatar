import pickle

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss, confusion_matrix

from compile_sklearn_model import ready_data, load_model
from ..data_processing import config


def load_models():
    models = [load_model(p) for p in config.model_save_dir_path.iterdir()]
    return models


def evaluate_model(model: RandomForestClassifier, data):
    config.model_plots_path.mkdir(parents=True, exist_ok=True)

    estimator_counts = model.get_params()['n_estimators']
    y_pred = model.predict(data.X_test)
    y_proba = model.predict_proba(data.X_test)

    accuracy = accuracy_score(data.y_test, y_pred)




def evaluate():
    models = load_models()
    estimator_counts = [model.get_params()['n_estimators'] for model in models]
    accuracies = []
    losses = []
    label_accuracies = []

    data = ready_data()

    # Calculate accuracies and losses
    for model in models:
        y_pred = model.predict(data.X_test)
        y_proba = model.predict_proba(data.X_test)
        accuracies.append(accuracy_score(data.y_test, y_pred))
        losses.append(log_loss(data.y_test, y_proba))

    # Plot Accuracy vs. Estimator Count
    plt.figure(figsize=(10, 5))
    plt.plot(estimator_counts, accuracies, marker='o', label='Accuracy')
    plt.title('Accuracy vs Number of Estimators')
    plt.xlabel('Number of Estimators')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.savefig('model_plots/accuracy.png')

    # Plot Loss vs. Estimator Count
    plt.figure(figsize=(10, 5))
    plt.plot(estimator_counts, losses, marker='o', color='red', label='Log Loss')
    plt.title('Loss vs Number of Estimators')
    plt.xlabel('Number of Estimators')
    plt.ylabel('Log Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig('model_plots/loss.png')

    for model in models:
        # Accuracy by Label (Assuming binary classification for simplicity)
        # Extend this as needed for multi-class classification by iterating over classes
        e = model.get_params()['n_estimators']
        cm = confusion_matrix(y_test, model.predict(X_test))  # Using the last model as example
        label_accuracies = cm.diagonal() / cm.sum(axis=1)
        labels = [class_map[l] for l in np.unique(y_test)]

        plt.figure(figsize=(10, 5))
        plt.bar(labels, label_accuracies, color='green')
        plt.title(f'Accuracy by Label For {e} Estimators')
        plt.xlabel('Label')
        plt.ylabel('Accuracy')
        plt.xticks(labels)
        plt.grid(axis='y')
        # plt.show()

        plt.savefig(f'model_plots/confusion_matrix_{e}.png')


if __name__ == '__main__':
    evaluate()
