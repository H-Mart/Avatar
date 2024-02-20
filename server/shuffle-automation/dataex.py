import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pyspark
from delta import *
from pyspark.sql.functions import lit

builder = pyspark.sql.SparkSession.builder.appName("MyApp") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config('spark.network.timeout', '800s') \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

df1 = spark.read.format("delta").load("deltalake-table")
# %%
pdf = df1.toPandas()

# Assuming 'pdf' is your pandas DataFrame
num_columns = len(pdf.columns)
n_rows = int(np.ceil(num_columns / 2))  # Adjust the layout here, 2 columns per row
fig, axes = plt.subplots(n_rows, 2, figsize=(15, n_rows * 4))  # Adjust figure size as needed
fig.tight_layout(pad=5.0)  # Adjust spacing between plots

for i, column in enumerate(pdf.columns):
    ax = axes.flatten()[i]
    if pd.api.types.is_numeric_dtype(pdf[column]):
        # Plot histogram for numeric columns
        ax.hist(pdf[column].dropna(), bins=30)  # Adjust the number of bins as necessary
        ax.set_title(f'Histogram of {column}')
    else:
        # For non-numeric data, plot value counts as a bar chart
        value_counts = pdf[column].dropna().value_counts()
        value_counts.plot(kind='bar', ax=ax)
        ax.set_title(f'Bar Chart of {column}')
    ax.set_xlabel(column)
    ax.set_ylabel('Count')
    ax.grid(False)

# Adjust layout if the number of columns is odd
if num_columns % 2 != 0:
    fig.delaxes(axes.flatten()[-1])  # Remove last subplot if unused

plt.show()
