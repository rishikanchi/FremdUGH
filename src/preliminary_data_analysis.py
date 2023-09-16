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
