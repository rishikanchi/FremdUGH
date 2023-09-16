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

pal = sns.color_palette("viridis", 10)
fig, ax = pyplot.subplots(figsize=(20, 5))
sns.barplot(y=df["Travel Relative To Employment and Population"], x=df["District Name"], palette=pal)

transport_bus_routes = data["/content/drive/MyDrive/UberData/bus_stops.csv"].groupby("District.Name")["District.Name"].count()
fig, ax = pyplot.subplots(figsize=(20, 5))
sns.barplot(y=transport_bus_routes.values, x=df["District Name"], palette=pal)

from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import folium

bus_stop_locations = data["/content/drive/MyDrive/UberData/bus_stops.csv"]
transport_locations = data["/content/drive/MyDrive/UberData/transports.csv"]

geometry = [Point(xy) for xy in zip(bus_stop_locations['Longitude'], bus_stop_locations['Latitude'])]

gdf = GeoDataFrame(bus_stop_locations, geometry=geometry)   

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gdf.plot(ax=world.plot(figsize=(10, 6)), marker='o', color='red', markersize=15)

color_point_maps = {
    "Underground" : "#967D69",
    "Tram" : "#92B9BD",
    "Railway (FGC)" : "#A8D4AD",
    "RENFE" : "#F2F79E",
    "Maritime station" : "#E8EC67",
    "Airport train" : "#D6D6B1",
    "Funiculur" : "#878472",
    "Cableway" : "#De541E",
}

barcelona_map = folium.Map([41.3947,2.1557], zoom_start=12.4, tiles='cartodbpositron')

def plotDot(lat_pt, long_pt, color):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    folium.CircleMarker(location=[long_pt, lat_pt],
                        radius=2,
                        color=color,
                        weight=5).add_to(barcelona_map)

specific_loc_data = transport_locations[transport_locations["District.Name"]=="Eixample"]

for transport_type in color_point_maps.keys():
    
    transport_df = transport_locations[transport_locations["Transport"]==transport_type]
    for long_pt, lat_pt in transport_df[["Longitude", "Latitude"]].values:
        plotDot(long_pt, lat_pt, color_point_maps[transport_type])
