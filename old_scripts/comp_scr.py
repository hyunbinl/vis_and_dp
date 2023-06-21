import math
import sys
import numpy as np

from parser import parse_h5f, parse_type
from printer import draw_plot, draw_plot_rgb
from aggregator import sum_rows, convert_to_matrix
from diffp import compute_deltas, add_noise_simple, find_rgb_sens, add_rgb_noise
from colormapper import create_rgba, combine_rgb

w = 37 
h = 118
scale = (w, h)
interp = 'nearest'
eps = 0.002
s_delta = 0.00001 #temporary delta for now
k = w * h * 3

users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)

aggregate = [None,None,None]
rgba = [None,None,None]

for i in range(0,3):
    aggregate[i] = sum_rows(meter_matrix[i])
    aggregate[i].resize((75,336))
    rgba[i] = create_rgba(aggregate[i])

from scipy.misc import imresize, imshow

comp_rgba = imresize(rgba[0],scale,interp)
draw_plot_rgb(comp_rgba,"resized to 37 by 118","resized_37_118.png")
sys.exit(0)

eps_prime = math.sqrt(2 * k * np.log(1/s_delta)) * eps + k * eps * (math.exp(eps) - 1)
deltas = find_rgb_sens(aggregate, users, categories, scale, interp)

while eps_prime < 100:
    eps_prime = math.sqrt(2 * k * np.log(1/s_delta)) * eps + k * eps * (math.exp(eps) - 1)
    print eps_prime
    comp_rgba = imresize(rgba[0],scale,interp)
    add_rgb_noise(comp_rgba, eps, deltas)
    t = "eps'="+str(eps_prime)+"_eps="+str(eps)
    draw_plot_rgb(comp_rgba,t,t+".png")
    eps = eps + 0.001
