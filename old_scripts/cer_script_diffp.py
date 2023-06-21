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

    stat_base = base + 'cer_parsed_data/Filter_outlier'
    types = ['/Resident/FeatureData/',
    '/SME/FeatureData/',
    '/Others/FeatureData/']
    retval = [None, None, None]

    for i in range(0,3):
        with open(stat_base+types[i]+'Min') as f:
            min = f.readline().strip().split(',') 

        with open(stat_base+types[i]+'Max') as f:
            max = f.readline().strip().split(',')

        retval[i] = [float(x) - float(y) for x,y in zip(max,min)]

    return retval

def track_outliers():
    """ returns a list named outliers, a list of outliers """

    types = ['Others_combo',
    'Resident_combo',
    'SME_combo']
    path = base+"cer_parsed_data/outliers/"
    outliers = []

    for category in types:
        for meter_id in open(path+category,"r"):
            outliers.append([int(meter_id)])

    return outliers

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
    plt.xlabel("4-Hourly index")
    #plt.xticks([w * 48 for w in range(0,336)], day)
    plt.ylabel("Bi-Monthly index")
    plt.autoscale(tight=True)
    plt.title(t)
    fig.savefig(dir)
    plt.close()

def add_noise(aggregate, case_num, epsilons, deltas, pixel, count):
    """
    this function will not only apply diff. privacy onto aggregate matrix
    but also will plot the matrices as heatmaps

    @param aggregate    a (25200,) aggregate power consumption matrix
    @param case_num     0: no noise 
                        1: sequential composition e' = e/(# of samples)
                        2: parallel composition e' = e
    @param epsilons
    @param deltas
    @param pixel
    @param count           
    """

    category = ["Residential", "SME", "Others"]
    folder_names = ["diffp3/case_0/",
    "diffp3/case_1/",
    "diffp3/case_2/"]

    folder_name = folder_names[case_num]
    budget = (64 * 336 / (pixel * pixel))

    if case_num == 0:
        for i in range(0,3):
            #aggregate[i] = aggregate[i]/float(count[i])
            draw_plot(aggregate[i],category[i],"plots/"+folder_name+category[i]+".png")
    else:
        laps = dict()

        #lets create a noise matrices
        for epsilon in epsilons:
            laps[epsilon] = [None,None,None]
            noises = laps[epsilon] #initialize array of noises

            for i in range(0,3):
                if case_num == 1:
                    e_prime = epsilon/budget
                else:
                    e_prime = epsilon

                u_arr = (np.random.rand(1,budget))[0] #samples picked from U[0,1)
                u_arr = [x - 0.5 for x in u_arr]

                noises[i] = np.array([lap_sample(u, delta/e_prime) for u, delta in zip(u_arr, deltas[i])])
                noises[i].resize((64/pixel,336/pixel))

        #create heatmaps
        for epsilon in epsilons:
            noises = laps[epsilon]
            for i in range(0,3):
                diffp_m = aggregate[i] + noises[i] #add two matricies
                #diffp_m = diffp_m/float(count[i]) #normalize the sum

                diffp_m.resize((budget,))
                a = np.array([max(x,0) for x in diffp_m]) #make sure there is no "negative" consumption
                a.resize((64/pixel,336/pixel))
                t = category[i]+"_epsilon"+str(epsilon)
                draw_plot(a,t,"plots/"+folder_name+t+".png")

def merge_aggs(aggregate, pixel):
    """
    TODO: write function description

    @param aggregate
    @param pixel
    """

    temp = [None, None, None]
    new_agg = [None, None, None]

    for category in range(0,3):
        temp[category] = np.delete(aggregate[category],range(64,75),0)
        size = temp[category].shape
        new_agg[category] = np.zeros((size[0]/pixel, size[1]/pixel))

        for i in range(0,size[0]):
            for j in range(0,size[1]):
                new_agg[category][i/pixel][j/pixel] = new_agg[category][i/pixel][j/pixel] + temp[category][i][j]

    return new_agg

def merge_deltas(deltas, pixel):
    """
    TODO

    @param deltas
    @param pixel
    """

    temp = [None, None, None]
    new_d = [None, None, None]

    for category in range(0,3):
        temp[category] = np.array(deltas[category])
        temp[category].resize((75,336))
        temp[category] = np.delete(temp[category],range(64,75),0)
        size = temp[category].shape
        new_d[category] = np.zeros((size[0]/pixel, size[1]/pixel))

        for i in range(0,size[0]):
            for j in range(0,size[1]):
                if new_d[category][i/pixel][j/pixel] < temp[category][i][j]:
                    new_d[category][i/pixel][j/pixel] = temp[category][i][j]

        num = 64*336/(pixel*pixel)
        new_d[category] = np.reshape(new_d[category],num)
        print new_d[category].shape

    return new_d

#main
merged_aggs = [None, None, None]
aggregate = [None, None, None] #each element is a (75,336) matrix for each category
count = [0,0,0] #array for keeping track of # of users for each category

users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
deltas = compute_deltas() #read csv files to grab max and min matrix
outliers = track_outliers() #read outlier list from folder outliers

for row in users:
    id = row[0]

    #do not add outliers
    if id in outliers:
        continue

    type = categories[id]

    data = np.array(row[1:25201])
    data.resize((75,336))
    count[type-1] = count[type-1] + 1
    
    if aggregate[type-1] is None:
        aggregate[type-1] = data
    else:
        aggregate[type-1] = aggregate[type-1] + data        

epsilons = [0.1,0.5,1.0,2.0,4.0,16.0,100.0,1000.0] #TODO: change this if necessary

pixel = 8
aggregate = merge_aggs(aggregate, pixel)
new_deltas = merge_deltas(deltas, pixel)

for case in range(0,3):
    #for pixel in pixels:
    add_noise(aggregate,case,epsilons,new_deltas,pixel,count)