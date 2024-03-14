# import tensorflow as tf
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
# import tensorflow_decision_forests as tfdf
import pyspark
from delta import *
import pathlib

import os

# Modelling
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint

# Tree Visualisation
# from sklearn.tree import export_graphviz
# from IPython.display import Image

# Keep using Keras 2
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import numpy as np
import pandas as pd
# import tf_keras
import math

# from load_and_save_data import load_and_save_data

# load_and_save_data()

# Set up the SparkSession
from ..data_processing import config

print(config.processed_dir_path)

exit(0)

DRIVER_MEMORY = "8g"
EXECUTOR_MEMORY = "8g"

builder = pyspark.sql.SparkSession.builder.appName("MyApp") \
    .config_obj("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config_obj("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config_obj('spark.network.timeout', '800s') \
    .config_obj("spark.executor.memory", EXECUTOR_MEMORY) \
    .config_obj("spark.driver.memory", DRIVER_MEMORY)

spark = configure_spark_with_delta_pip(builder).getOrCreate()

print('Loading data from Delta Lake')

# Read the data from Delta Lake
df1 = spark.read.format("delta").load("deltalake-table")

print('Data loaded from Delta Lake')

print('Converting to Pandas DataFrame')

pdf = df1.toPandas()

print('Data converted to Pandas DataFrame')

label = 'label'

classes = pdf[label].unique().tolist()
print(classes)
pdf['label'] = pdf['label'].map(classes.index)

X = pdf.drop(columns=[label, 'filename'])
y = pdf[label]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

# param_dist = {'n_estimators': [1, 10, 15, 25, 50, 100]}
# 'max_depth': [10, 16, 20, None]}


# Create a random forest classifier
# rf = RandomForestClassifier(n_jobs=-1, verbose=2)

# Use random search to find the best hyperparameters
# model_1 = RandomizedSearchCV(rf,
#                              param_distributions=param_dist,
#                              n_iter=1,
#                              cv=None)
estimators = [1, 5, 10, 20, 50, 100]
import pickle

for e in estimators:
    model_1 = RandomForestClassifier(n_estimators=e, max_depth=16, n_jobs=-1, verbose=2)
    # train_flag = True

    model_path = pathlib.Path(f'models/model_{e}_estimators')
    if not model_path.exists():
        model_1.fit(X_train, y_train)

        with model_path.open('wb') as f:
            pickle.dump(model_1, f)
    else:
        with model_path.open('rb') as f:
            model_1 = pickle.load(f)

    y_pred = model_1.predict(X_test)
    print(model_1.score(X_test, y_test))
    accuracy = sklearn.metrics.accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")

    # Create the confusion matrix
    # cm = confusion_matrix(y_test, y_pred)

    # ConfusionMatrixDisplay(confusion_matrix=cm).plot()

    # Generate predictions with the best model
