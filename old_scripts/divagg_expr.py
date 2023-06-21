import math
import sys
import numpy as np

from parser import parse_h5f, parse_type
from printer import draw_plot, draw_plot_norm
from aggregator import sum_rows, convert_to_matrix

from div_agg import divide_aggregate
from diffp import compute_deltas, add_noise_simple, eps_prime


users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)
delta = compute_deltas()

residential = meter_matrix[0]
residential = residential[:,:336*52]
tot_agg = sum_rows(residential)
tot_agg.resize((52,336))

x = 2
y = 4
t = 800

a, budget = divide_aggregate(tot_agg, residential, x, y, t, 0.008)
print eps_prime(budget, 0.00001, 0.008)
draw_plot(a,"budget="+str(budget)+",e'="+str(eps_prime(budget, 0.00001, 0.008)), None)