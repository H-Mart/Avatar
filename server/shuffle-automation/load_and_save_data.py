import pyspark
from delta import *
from pyspark.sql.functions import lit

# Set up the SparkSession

builder = pyspark.sql.SparkSession.builder.appName("MyApp") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config('spark.network.timeout', '800s') \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

print('SparkSession created')

# Load the data

print('Loading data')

pathGlobFilter = '*.csv'

all_columns = ['Sample Index', ' EXG Channel 0', ' EXG Channel 1', ' EXG Channel 2',
               ' EXG Channel 3', ' EXG Channel 4', ' EXG Channel 5', ' EXG Channel 6',
               ' EXG Channel 7', ' EXG Channel 8', ' EXG Channel 9', ' EXG Channel 10',
               ' EXG Channel 11', ' EXG Channel 12', ' EXG Channel 13',
               ' EXG Channel 14', ' EXG Channel 15', ' Accel Channel 0',
               ' Accel Channel 1', ' Accel Channel 2', ' Other', ' Other.1',
               ' Other.2', ' Other.3', ' Other.4', ' Other.5', ' Other.6',
               ' Analog Channel 0', ' Analog Channel 1', ' Analog Channel 2',
               ' Timestamp', ' Other.7', ' Timestamp (Formatted)']

unused_columns = [' Other', ' Other.1', ' Other.2', ' Other.3', ' Other.4', ' Other.5', ' Other.6',
                  ' Analog Channel 0', ' Analog Channel 1', ' Analog Channel 2', ' Other.7', ' Timestamp (Formatted)']

used_columns = [column for column in all_columns if column not in unused_columns]

takeoff = spark.read.options(delimiter=',').csv(
    "data/takeoff", inferSchema=True, pathGlobFilter=pathGlobFilter, header=True)
landdf = spark.read.options(delimiter=',').csv(
    "data/land", inferSchema=True, pathGlobFilter=pathGlobFilter, header=True)
leftdf = spark.read.options(delimiter=',').csv(
    "data/left", inferSchema=True, pathGlobFilter=pathGlobFilter, header=True)
rightdf = spark.read.options(delimiter=',').csv(
    "data/right", inferSchema=True, pathGlobFilter=pathGlobFilter, header=True)
forward = spark.read.options(delimiter=',').csv(
    "data/forward", inferSchema=True, pathGlobFilter=pathGlobFilter, header=True)
backward = spark.read.options(delimiter=',').csv(
    "data/backward", inferSchema=True, pathGlobFilter=pathGlobFilter, header=True)

# Add labels to the data

labels = ['takeoff', 'land', 'left', 'right', 'forward', 'backward']

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

df = df.drop(*unused_columns)

print('Data loaded')

# Save the data to Delta Lake

print('Saving data to Delta Lake')

df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .option("delta.columnMapping.mode", "name") \
    .save("deltalake-table")
