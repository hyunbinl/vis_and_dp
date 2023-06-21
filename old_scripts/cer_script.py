import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import pandas as pd
import h5py

base = '/home/hyunbinl/smartgrid/'
h5f = h5py.File(base+'cer_parsed_data/Consumer_data_new.h5','r')
xl = pd.ExcelFile(base+'cer_original/CER Electricity Revised March 2012/SME and Residential allocations.xlsx')
df = xl.parse('Sheet1')
d = dict(zip(df['ID'],df['Code']))
b = h5f['dataset'][...]

aggregate = [None, None, None]
title = ["Residential", "SME", "Others"]
day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]
c = range(0,25202) #range of each dataset
col_range = []

i = 1 #first occurance of the frame
j = 48 #width of the frame (must be <= 48)
folder_name = "diffp" #name of folder where plots will be saved at

while i < 25201:
    col_range = col_range + c[i:i+j]
    i += 48 # one day = 48 half hours

num_col = int(len(col_range)/75)

for row in b:
    id = row[0]
    type = d[id]

    temp = np.array(row[1:25201])
    data = np.array([temp[y-1] for y in col_range])
    data.resize((75,num_col))
    

    if aggregate[type-1] is None:
        aggregate[type-1] = data
    else:
        aggregate[type-1] = aggregate[type-1] + data        

#create heatmaps
for i in range(0,4):
    if i != 3:
        a = aggregate[i]
        t = title[i]
    else:
        a = aggregate[0] + aggregate[1] + aggregate[2]
        t = "Total"

    fig = plt.figure()
    mapable = plt.imshow(a, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9,aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Aggregate Consumption")
    plt.xlabel("Half-hour Index of Week")
    plt.xticks([w * j for w in range(0,num_col)], day)
    plt.ylabel("Week Index (0 to 74)")
    plt.autoscale(tight=True)
    plt.title(t)
    fig.savefig("plots/"+folder_name+"/"+t+".png")

h5f.close()