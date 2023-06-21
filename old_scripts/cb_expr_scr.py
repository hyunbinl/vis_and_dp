import math
import sys
import numpy as np

from parser import parse_h5f, parse_type
from printer import draw_plot
from aggregator import sum_rows, convert_to_matrix

from div_agg import divide_aggregate
from diffp import compute_deltas, add_noise_simple, eps_prime

users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)
delta = compute_deltas()

residential = meter_matrix[0]
sme = meter_matrix[1]
others = meter_matrix[2]

sample_size, t_size = residential.shape

new_mat = np.zeros((25200,))

for i in range(0,t_size):
    maxi = 0
    mini = np.inf

    for j in range(0,sample_size):
        maxi = max(maxi, residential[j][i])
        mini = min(mini, residential[j][i])

    diff = maxi - mini
    bins = np.zeros((9,))
    counts = np.zeros((10,))

    for k in range(0,9):
        bins[k] = mini + (k + 1) * diff/10

    for j in range(0,sample_size):
        isMax = True
        for k in range(0,9):
            if residential[j][i] < bins[k]:
                counts[k] = counts[k] + 1
                isMax = False
                break 
            if isMax is True:
                counts[9] = counts[9] + 1

    total = 0
    for j in range(0,10):
            if counts[j] < 360:
                counts[j] = 0
            else:
                total = total + counts[j]
    
    aver = 0
    aver_tot = 0
    for j in range(0,10):
        aver = mini + (2 * j + 1) * diff/20
        aver_tot = aver_tot + aver * counts[j]

    aver_tot = aver_tot/total
    new_mat[i] = aver_tot

new_mat.resize((75,336))

draw_plot(new_mat,"k=360 Crowd-Blending Private",None)