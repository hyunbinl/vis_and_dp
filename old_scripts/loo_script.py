#script used for generating heatmaps

import pylab as pl
import numpy as np
import math
import sys
import time

from parser import parse_h5f, parse_type
from printer import draw_plot, draw_plot_rgb, draw_lin_plot
from aggregator import sum_rows, convert_to_matrix
from diffp import find_agg_sensitivity, find_agg_deltas, add_agg_noise

#main
users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)

aggregate = [None,None,None]
rgba = [None,None,None]
comp_rgba = [None,None,None]
k = 5
budget = 75 * k + k + 336 * k

for i in range(0,3):
    aggregate[i] = sum_rows(meter_matrix[i])
    aggregate[i].resize((75,336))

max_mins = find_agg_sensitivity(k, aggregate, users, categories)
deltas = find_agg_deltas(max_mins)

A = aggregate[0]
U, s, V = np.linalg.svd(A)

U_k = U[:,0:k]
s_k = s[0:k,]
V_k = V[0:k,:]

epsilons = [0.1,0.5,1.0,2.0,4.0,16.0,100.0,1000.0] 

for epsilon in epsilons:
    new_U, new_s, new_V = add_agg_noise(k, U_k, s_k, V_k, epsilon, deltas, budget)
    new_S = np.diag(new_s)
    temp = np.dot(new_U[:,0:k], np.dot(new_S[0:k,0:k] ,new_V[0:k,:]))
    draw_plot(temp,"e="+str(epsilon),None)