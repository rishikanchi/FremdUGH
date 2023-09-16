from google.colab import drive
drive.mount("/content/drive")

import pandas as pd
import numpy as np
from IPython.display import display
import glob

file_pths = glob.glob("/content/drive/MyDrive/UberData/*.csv")

data = {}

for pth in file_pths:
    print(pth)
    df = pd.read_csv(pth)
    display(df)

    data[pth] = df

month_total = np.zeros(11)
month_perc = np.zeros(11)

unemployment = data["/content/drive/MyDrive/UberData/unemployment.csv"]
population = data["/content/drive/MyDrive/UberData/population.csv"]
destination_data = data["/content/drive/MyDrive/UberData/immigrants_emigrants_by_destination.csv"]

pop_sum2 = population[population["Year"]==2017].groupby("District.Name")["Number"].sum()

for month in unemployment["Month"].unique():
    pop_sum1 = unemployment[unemployment["Year"]==2017][unemployment["Month"]==month].groupby("District Name")["Number"].sum()

    total_employed = pop_sum2 - pop_sum1
    perc_employed = total_employed / pop_sum2 * 100

    month_total += total_employed.values
    month_perc += perc_employed.values

month_total /= 12
month_perc /= 12


import math
total = 0
for value in month_total:
    if not math.isnan(value):
        total += value

df = pd.DataFrame({"District Name" : pop_sum2.keys(), 
                   "Percentage Employed" : [x for i, x in enumerate(month_perc) if i != 5], 
                   "Population Size" : pop_sum2.values, 
                   "Total Employed" : [x for i, x in enumerate(month_total) if i != 5]})

def get_num_traveled(district_name):
    immigrants_moved_from = destination_data2[destination_data2["from"] == district_name]["weight"].sum()
    immigrants_moved_to = destination_data2[destination_data2["to"] == district_name]["weight"].sum()

    return immigrants_moved_from + immigrants_moved_to

df["Number Traveled"] = df["District Name"].apply(get_num_traveled)
df["Population Weightage"] = df["Population Size"] = df["Population Size"] / df["Population Size"].max()
df["Travel Relative To Employment and Population"] = df["Number Traveled"] / df["Total Employed"] * 100 * df["Population Weightage"]

fig, ax = pyplot.subplots(figsize=(15, 5))
sns.barplot(y=df["Travel Relative To Employment and Population"], x=df["District Name"])
