import pandas as pd


data = pd.read_csv("student-dataset.csv")
print(data.head())
data.info()



data_json = pd.read_json("student-data.json")

print(data_json.head())

#converting data from csv to json

data.to_json("student-data-converted.json", orient="records", lines=True)
