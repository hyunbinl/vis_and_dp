#script used for generating heatmaps

import numpy as np
import math
import sys

from parser import parse_h5f, parse_type
from printer import draw_plot
from aggregator import sum_rows, convert_to_matrix
from diffp import compute_deltas, add_noise_simple

default_wks = 75
hf_hrs = 336
s_delta = 0.00001 #temporary delta for now

users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)
deltas = compute_deltas()

aggregate = [None, None, None]

for i in range(0,3):
    aggregate[i] = sum_rows(meter_matrix[i])
    aggregate[i].resize((default_wks,hf_hrs))

weeks = 75
k = weeks * hf_hrs
temp = aggregate[0][:weeks,:]
temp_delt = deltas[0][:k]

eps = 0.00125
eps_prime = math.sqrt(2 * k * np.log(1/s_delta)) * eps + k * eps * (math.exp(eps) - 1)
mats = add_noise_simple(temp,eps,temp_delt)

title = "epsilon="+str(eps_prime)
draw_plot(mats,title,title+".png")

eps = 0.017
eps_prime = math.sqrt(2 * k * np.log(1/s_delta)) * eps + k * eps * (math.exp(eps) - 1)
mats = add_noise_simple(temp,eps,temp_delt)

title = "epsilon="+str(eps_prime)
draw_plot(mats,title,title+".png")