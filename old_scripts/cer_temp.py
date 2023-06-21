import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import pandas as pd
import math
import h5py
import sys

base = '/home/hyunbinl/smartgrid/'

def lap_sample(u,b):
    """
    @param u    a number picked from the uniform distribution
    @param b    delta/e' where e' can either be epsilon or epsilon/(# of samples)
    @return     a laplacian noise, l(delta/e')
    """

    mu = 0 # mu = 0 for this case
    return mu - b * np.sign(u) * math.log(1 - 2 * abs(u))

def parse_h5f():
    """
    @return     a matrix dataset with shape (4629, 25201)
    """

    dir = base+'cer_parsed_data/Consumer_data_new.h5'
    h5f = h5py.File(dir,'r')
    retval = h5f['dataset'][...]
    h5f.close()
    return retval

def parse_type():
    """
    1 = residential
    2 = SME
    3 = others

    @return     a dictionary for (user, category) as (key,value)
    """

    dir = base+'cer_original/CER Electricity Revised March 2012/SME and Residential allocations.xlsx'
    xl = pd.ExcelFile(dir)
    df = xl.parse('Sheet1')
    return dict(zip(df['ID'],df['Code']))

def compute_deltas():
    """
    computes matrix for max - min for each category

    @return     an array of three delta matricies of shape (1,25200)
    """

    stat_base = base + 'cer_parsed_data/30mins'
    types = ['/Acrossuser_resident/FeatureData/',
    '/Acrossuser_SME/FeatureData/',
    '/Acrossuser_others/FeatureData/']
    retval = [None, None, None]

    for i in range(0,3):
        with open(stat_base+types[i]+'Min') as f:
            min = f.readline().strip().split(',') 

        with open(stat_base+types[i]+'Max') as f:
            max = f.readline().strip().split(',')

        retval[i] = [float(x) - float(y) for x,y in zip(max,min)]

    return retval

def draw_plot(m,t,dir):
    """
    plot heatmaps based on matrix m

    @param m    a matrix to be plotted
    @param t    title of the plot
    @param dir  a directory for the plot
    """

    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

    fig = plt.figure()
    mapable = plt.imshow(m, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9,aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Aggregate Consumption")
    plt.xlabel("Half-hour Index of Week")
    plt.xticks([w * 48 for w in range(0,336)], day)
    plt.ylabel("Week Index (0 to 74)")
    plt.autoscale(tight=True)
    plt.title(t)
    fig.savefig(dir)
    plt.close()

def add_noise(aggregate, case_num, epsilons):
    """
    this function will not only apply diff. privacy onto aggregate matrix
    but also will plot the matrices as heatmaps

    @param aggregate    a (75,336) aggregate power consumption matrix
    @param case_num     0: no noise 
                        1: sequential composition e' = e/(# of samples)
                        2: parallel composition e' = e
    @param epsilons           
    """

    category = ["Residential", "SME", "Others"]
    folder_names = ["diffp/case_0/",
    "diffp/case_1/",
    "diffp/case_2/"]

    folder_name = folder_names[case_num]

    if case_num == 0:
        for i in range(0,3):
            draw_plot(aggregate[i],category[i],"plots/"+folder_name+category[i]+".png")
    else:
        laps = dict()

        #lets create a noise matrices
        for epsilon in epsilons:
            laps[epsilon] = [None,None,None]
            noises = laps[epsilon] #initialize array of noises

            for i in range(0,3):
                if case_num == 1:
                    e_prime = epsilon/25200
                else:
                    e_prime = epsilon

                u_arr = (np.random.rand(1,25200))[0] #25200 samples picked from U[0,1)
                u_arr = [x - 0.5 for x in u_arr]
                noises[i] = np.array([lap_sample(u, delta/e_prime) for u, delta in zip(u_arr, deltas[i])])
                noises[i].resize((75,336))

        #create heatmaps
        for epsilon in epsilons:
            noises = laps[epsilon]
            for i in range(0,3):
                diffp_m = aggregate[i] + noises[i] #add two matricies
                diffp_m.resize((25200,))
                a = np.array([max(x,0) for x in diffp_m]) #make sure there is no "negative" consumption
                a.resize((75,336))
                t = category[i]+"_epsilon"+str(epsilon)
                draw_plot(a,t,"plots/"+folder_name+t+".png")


#main

day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]
aggregate = [None, None, None] #each element is a (75,336) matrix for each category
count = [0,0,0] #array for keeping track of # of users for each category

users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
deltas = compute_deltas() #read csv files to grab max and min matrix

for row in users:
    id = row[0]
    type = categories[id]

    data = np.array(row[1:25201])
    data.resize((75,336))
    count[type-1] = count[type-1] + 1
    
    if aggregate[type-1] is None:
        aggregate[type-1] = data
    else:
        aggregate[type-1] = aggregate[type-1] + data        


plt.plot(np.arange(336),aggregate[0][0])
plt.plot(np.arange(336),aggregate[0][20])
plt.xlabel("Half hour index of week (0-335)")
plt.xticks([w * 48 for w in range(0,336)], day)
plt.ylabel("Aggregate Electricity consumption (kWh)")
plt.autoscale(tight=True)
plt.title("Electricity consumption in Week 1 (Blue) and Week 21 (Green)")
plt.show()