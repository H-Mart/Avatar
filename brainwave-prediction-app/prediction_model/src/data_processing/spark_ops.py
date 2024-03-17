import pathlib

import pyspark
from delta import configure_spark_with_delta_pip
from pyspark.sql.functions import lit, input_file_name

from .config import spark_timeout, spark_driver_memory, spark_executor_memory, processed_dir_path


def build_spark_session() -> pyspark.sql.SparkSession:
    builder = pyspark.sql.SparkSession.builder.appName("MyApp") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config('spark.network.timeout', spark_timeout) \
        .config("spark.executor.memory", spark_executor_memory) \
        .config("spark.driver.memory", spark_driver_memory)

    return configure_spark_with_delta_pip(builder).getOrCreate()


class SparkSessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SparkSessionManager, cls).__new__(cls)
            cls._instance._spark_session = build_spark_session()
        return cls._instance

    @property
    def spark_session(self) -> pyspark.sql.SparkSession:
        return self._instance._spark_session

    def reset_session(self) -> pyspark.sql.SparkSession:
        self._instance._spark_session = build_spark_session()
        return self._instance._spark_session


def df_from_csvs(base_path: pathlib.Path = processed_dir_path) -> pyspark.sql.DataFrame:
    spark = SparkSessionManager().spark_session
    path_glob_filter = '*.csv'

    unused_columns = [' Other', ' Other.1', ' Other.2', ' Other.3', ' Other.4', ' Other.5', ' Other.6',
                      ' Analog Channel 0', ' Analog Channel 1', ' Analog Channel 2', ' Other.7',
                      ' Timestamp (Formatted)']

    takeoff = spark.read.options(delimiter=',').csv(
        str(base_path / "takeoff"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    land_df = spark.read.options(delimiter=',').csv(
        str(base_path / "land"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    left_df = spark.read.options(delimiter=',').csv(
        str(base_path / "left"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    right_df = spark.read.options(delimiter=',').csv(
        str(base_path / "right"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    forward = spark.read.options(delimiter=',').csv(
        str(base_path / "forward"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    backward = spark.read.options(delimiter=',').csv(
        str(base_path / "backward"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)

    # Add labels to the data
    labels = ['takeoff', 'land', 'left', 'right', 'forward', 'backward']

    takeoff = takeoff.withColumn("label", lit("takeoff"))
    land_df = land_df.withColumn("label", lit("land"))
    left_df = left_df.withColumn("label", lit("left"))
    right_df = right_df.withColumn("label", lit("right"))
    forward = forward.withColumn("label", lit("forward"))
    backward = backward.withColumn("label", lit("backward"))

    df = takeoff.union(land_df)
    df = df.union(left_df)
    df = df.union(right_df)
    df = df.union(forward)
    df = df.union(backward)

    df = df.withColumn('filename', input_file_name())

    df = df.drop(*unused_columns)

    return df
