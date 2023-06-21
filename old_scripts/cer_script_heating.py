import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import pandas as pd
import h5py

q474 = 'Question 4704: Which of the following best describes how you cook in your home'

h5f = h5py.File('Consumer_data_new.h5','r')
xl = pd.ExcelFile('/home/hyunbinl/smartgrid/cer_original/CER Electricity Revised March 2012/Survey data - Excel format/Smart meters Residential pre-trial survey data.xlsx')
df = xl.parse('Sheet1')
d_i = dict(zip(df['ID'],df[q474]))
b = h5f['dataset'][...]
title = ['Electric cooker',
'Gas cooker',
'Oil fired cooker',
'Solid fuel cooker']

aggregate = [None, None, None, None]
day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]
count = [0,0,0,0]

c = range(0,25202)
col_range = []

i = 1 #first occurance of this data
j = 48 #width of occurance in one day

while i < 25201:
    col_range = col_range + c[i:i+j]
    i += 48 # one day = 48 half hours

num_col = int(len(col_range)/75)

for row in b:
    id = int(row[0])
    temp = np.array(row[1:25201])
    data = np.array([temp[y-1] for y in col_range])
    data.resize((75,num_col))
    if id in d_i:
        i = d_i[id]-1
        count[i] = count[i] + 1
        if aggregate[i] is None:
            aggregate[i] = data
        else:
            aggregate[i] = aggregate[i] + data   

for i in range(0,4):
    print count[i]
    if count[i] == 0:
        continue
    a = aggregate[i]/count[i]
    t = title[i]

    fig = plt.figure()
    mapable = plt.imshow(a, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9,aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Average Consumption")
    plt.xlabel("Half-hour Index of Week")
    plt.xticks([w * j for w in range(0,num_col)], day)
    plt.ylabel("Week Index (0 to 74)")
    plt.autoscale(tight=True)
    plt.title(t)
    fig.savefig("plots/cooking/"+t+".png")

aa = aggregate[0]/count[0] - (aggregate[1]+aggregate[2]+aggregate[3])/(count[1]+count[2]+count[3])
tt = 'Electricity-Others'

fig = plt.figure()
mapable = plt.imshow(aa, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9,aspect='auto')
cbar = fig.colorbar(mapable)
cbar.set_label("Average Consumption")
plt.xlabel("Half-hour Index of Week")
plt.xticks([w * j for w in range(0,num_col)], day)
plt.ylabel("Week Index (0 to 74)")
plt.autoscale(tight=True)
plt.title(tt)
fig.savefig("plots/cooking/"+tt+".png")


h5f.close()
