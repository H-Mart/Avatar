from pyspark.sql.functions import lit, input_file_name

from .config import processed_dir_path, deltalake_table_path
from .spark_ops import build_spark_session


def load_and_save_data():
    spark = build_spark_session()
    path_glob_filter = '*.csv'

    all_columns = ['Sample Index', ' EXG Channel 0', ' EXG Channel 1', ' EXG Channel 2',
                   ' EXG Channel 3', ' EXG Channel 4', ' EXG Channel 5', ' EXG Channel 6',
                   ' EXG Channel 7', ' EXG Channel 8', ' EXG Channel 9', ' EXG Channel 10',
                   ' EXG Channel 11', ' EXG Channel 12', ' EXG Channel 13',
                   ' EXG Channel 14', ' EXG Channel 15', ' Accel Channel 0',
                   ' Accel Channel 1', ' Accel Channel 2', ' Other', ' Other.1',
                   ' Other.2', ' Other.3', ' Other.4', ' Other.5', ' Other.6',
                   ' Analog Channel 0', ' Analog Channel 1', ' Analog Channel 2', ' Other.7', ' Timestamp (Formatted)']

    unused_columns = [' Other', ' Other.1', ' Other.2', ' Other.3', ' Other.4', ' Other.5', ' Other.6',
                      ' Analog Channel 0', ' Analog Channel 1', ' Analog Channel 2', ' Other.7',
                      ' Timestamp (Formatted)']

    takeoff = spark.read.options(delimiter=',').csv(
        str(processed_dir_path / "takeoff"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    land_df = spark.read.options(delimiter=',').csv(
        str(processed_dir_path / "land"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    left_df = spark.read.options(delimiter=',').csv(
        str(processed_dir_path / "left"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    right_df = spark.read.options(delimiter=',').csv(
        str(processed_dir_path / "right"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    forward = spark.read.options(delimiter=',').csv(
        str(processed_dir_path / "forward"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)
    backward = spark.read.options(delimiter=',').csv(
        str(processed_dir_path / "backward"), inferSchema=True, pathGlobFilter=path_glob_filter, header=True)

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

    print('Data loaded')

    # Save the data to Delta Lake

    print('Saving data to Delta Lake')

    df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .option("delta.columnMapping.mode", "name") \
        .save(str(deltalake_table_path.absolute()))


if __name__ == "__main__":
    load_and_save_data()
