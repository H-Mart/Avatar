import tensorflow as tf
import pandas as pd

import pyspark
from delta import *
from pyspark.sql.functions import lit

from sklearn.model_selection import train_test_split
import tensorflow_decision_forests as tfdf

print(tf.version.VERSION)
print(tf.config.list_physical_devices('GPU'))
# Set up the SparkSession

builder = pyspark.sql.SparkSession.builder.appName("MyApp") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.network.timeout", "800") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

print('SparkSession created')

# Load the data

print('Loading data')

pathGlobFilter = '*.csv'

takeoff = spark.read.options(delimiter=',').csv(
    "data/takeoff", inferSchema='true', pathGlobFilter=pathGlobFilter, header=False)
landdf = spark.read.options(delimiter=',').csv(
    "data/land", inferSchema='true', pathGlobFilter=pathGlobFilter, header=False)
leftdf = spark.read.options(delimiter=',').csv(
    "data/left", inferSchema='true', pathGlobFilter=pathGlobFilter, header=False)
rightdf = spark.read.options(delimiter=',').csv(
    "data/right", inferSchema='true', pathGlobFilter=pathGlobFilter, header=False)
forward = spark.read.options(delimiter=',').csv(
    "data/forward", inferSchema='true', pathGlobFilter=pathGlobFilter, header=False)
backward = spark.read.options(delimiter=',').csv(
    "data/backward", inferSchema='true', pathGlobFilter=pathGlobFilter, header=False)

# Add labels to the data

takeoff = takeoff.withColumn("label", lit("takeoff"))
landdf = landdf.withColumn("label", lit("land"))
leftdf = leftdf.withColumn("label", lit("left"))
rightdf = rightdf.withColumn("label", lit("right"))
forward = forward.withColumn("label", lit("forward"))
backward = backward.withColumn("label", lit("backward"))

df = takeoff.union(landdf)
df = df.union(leftdf)
df = df.union(rightdf)
df = df.union(forward)
df = df.union(backward)

print('Data loaded')

# Save the data to Delta Lake

print('Saving data to Delta Lake')

df.write \
    .format("delta") \
    .mode("overwrite") \
    .save("deltalake-table")

print('Data saved to Delta Lake')


print('Loading data from Delta Lake')

# Read the data from Delta Lake
df1 = spark.read.format("delta").load("deltalake-table")

print('Data loaded from Delta Lake')

print('Converting to Pandas DataFrame')

pdf = df1.toPandas()

print('Data converted to Pandas DataFrame')

train, test = train_test_split(pdf, test_size=0.1)

print('converting to TensorFlow DataFrames')

train_ds = tfdf.keras.pd_dataframe_to_tf_dataset(train, label="label", batch_size=1000)
test_ds = tfdf.keras.pd_dataframe_to_tf_dataset(test, label="label", batch_size=1000)

del pdf
del train
del test

print('Training model')

model = tfdf.keras.RandomForestModel()
history = model.fit(train_ds, verbose=1)

print('Model trained')

print(model.summary())

model.save("/home/henry/Avatar/server/model")