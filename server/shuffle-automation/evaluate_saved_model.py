import tensorflow as tf
from sklearn.model_selection import train_test_split
import tensorflow_decision_forests as tfdf
import pyspark
from delta import *

print(tf.version.VERSION)
print(tf.config.list_physical_devices('GPU'))

# Set up the SparkSession

builder = pyspark.sql.SparkSession.builder.appName("MyApp") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config('spark.network.timeout', '800s') \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

print('Data saved to Delta Lake')

print('Loading data from Delta Lake')

# Read the data from Delta Lake
df1 = spark.read.format("delta").load("deltalake-table")

print('Data loaded from Delta Lake')

print('Converting to Pandas DataFrame')

pdf = df1.toPandas()
print(pdf.dtypes)

print('Data converted to Pandas DataFrame')

train, test = train_test_split(pdf, test_size=0.1)  # , stratify=pdf['label'])

print('converting to TensorFlow DataFrames')

train_ds = tfdf.keras.pd_dataframe_to_tf_dataset(train, label="label", batch_size=1000)
test_ds = tfdf.keras.pd_dataframe_to_tf_dataset(test, label="label", batch_size=1000)

del train
del test

print('Training model')

model = tfdf.keras.RandomForestModel()
history = model.fit(train_ds)

print('Model trained')

print(model.summary())

print('Evaluating model')

evaluation = model.evaluate(test_ds)

print('Model evaluated')
