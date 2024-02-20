import pandas as pd

df = pd.read_csv('data/backward/1.csv')
data = df[' EXG Channel 0']

print(data.head())
