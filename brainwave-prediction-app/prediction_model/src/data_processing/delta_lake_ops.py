from .spark_ops import SparkSessionManager
from .config import deltalake_table_path

import pyspark


def load_table() -> pyspark.sql.DataFrame:
    spark = SparkSessionManager().spark_session
    return spark.read.format("delta").load(str(deltalake_table_path.absolute()))


def save_table(df: pyspark.sql.DataFrame):
    df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .option("delta.columnMapping.mode", "name") \
        .save(str(deltalake_table_path.absolute()))


if __name__ == '__main__':
    df = load_table()
    print(df.schema)
    df.summary().show()