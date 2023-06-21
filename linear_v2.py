
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl

from parser import parse_h5f, parse_type
from printer import draw_plot, draw_plot_norm, draw_lin_plot, draw_lin_plot_ns
from aggregator import sum_rows, convert_to_matrix
from diffp import compute_deltas, add_noise_simple, eps_prime, lap_sample

from random import randint, uniform
from scipy.signal import savgol_filter

YSCALE = 6000

users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)
delta = compute_deltas()

residential = meter_matrix[0]
sme = meter_matrix[1]
others = meter_matrix[2]

def compute_index(x,y,minx,maxy,num):
    the_x = int(x/(minx/num))
    the_y = int(y/(maxy/num))
    return the_x,the_y
#enddef

def generate_new_point(x,y,minx,maxy,num):
    x1 = float(x)/num * minx
    x2 = float(x+1)/num * minx
    y1 = float(y)/num * maxy
    y2 = float(y+1)/num * maxy

    the_x = uniform(x1, x2)
    the_y = uniform(y1, y2)
    return the_x, the_y
#enddef

residential = residential[:,:52*336]
num_sample, queries = residential.shape

tot_agg = sum_rows(residential)
tot_agg.resize((52,336))
res_deltas = np.array(delta[0])
res_deltas.resize((75,336))
res_deltas = res_deltas[:52,:]
res_deltas.resize((52*336,))

xmas_week = tot_agg[22:23]
xmas_delta = res_deltas[22*336:23*336]

print xmas_delta.shape

eps = 0.01
noise,k = add_noise_simple(xmas_week,eps,xmas_delta)

eps_p = eps_prime(336, 0.000001, eps)
print eps_p

draw_lin_plot(xmas_week, "linear_raw",YSCALE,"l0.png")

days = np.zeros((7,48))
day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

two_days = [3,4]

for i in range(0,7):
    days[i] = xmas_week[:,(48*i):(48*i + 48)]
    plt.plot(days[i])

plt.title("linear_plot_daily_raw")
axes = plt.gca()
axes.set_ylim([0,YSCALE])
plt.xlabel("Half-Hour index")
plt.ylabel("Aggregate Consumption (kWh)")
plt.legend(day,loc='upper left')
plt.savefig('linear_rainbow_raw.jpg')
plt.close()

for i in two_days:
    days[i] = xmas_week[:,(48*i):(48*i + 48)]
    plt.plot(days[i])

plt.title("linear_plot_daily_raw")
axes = plt.gca()
axes.set_ylim([0,YSCALE])
plt.xlabel("Half-Hour index")
plt.ylabel("Aggregate Consumption (kWh)")
plt.legend(['24th','25th'],loc='upper left')
plt.savefig('linear_two_raw.jpg')
plt.close()


draw_lin_plot_ns(noise,"linear_noise","l1.png")

for i in range(0,7):
    days[i] = noise[:,(48*i):(48*i + 48)]
    plt.plot(days[i])

plt.title("linear_plot_daily_noise")
plt.xlabel("Half-Hour index")
plt.ylabel("Aggregate Consumption (kWh)")
plt.legend(day,loc='upper left')
plt.savefig('linear_rainbow_noise.jpg')
plt.close()

for i in two_days:
    days[i] = noise[:,(48*i):(48*i + 48)]
    plt.plot(days[i])

plt.title("linear_plot_daily_noise")
plt.xlabel("Half-Hour index")
plt.ylabel("Aggregate Consumption (kWh)")
plt.legend(['24th','25th'],loc='upper left')
plt.savefig('linear_two_noise.jpg')
plt.close()

noise = savgol_filter(noise,31,5)

draw_lin_plot(noise,"linear_noise_savgol",YSCALE,"l2.png")

for i in range(0,7):
    days[i] = noise[:,(48*i):(48*i + 48)]
    plt.plot(days[i])

plt.title("linear_plot_daily_savgol")
axes = plt.gca()
axes.set_ylim([0,YSCALE])
plt.xlabel("Half-Hour index")
plt.ylabel("Aggregate Consumption (kWh)")
plt.legend(day,loc='upper left')
plt.savefig('linear_rainbow_savgol.jpg')
plt.close()

for i in two_days:
    days[i] = noise[:,(48*i):(48*i + 48)]
    plt.plot(days[i])

plt.title("linear_plot_daily_savgol")
axes = plt.gca()
axes.set_ylim([0,YSCALE])
plt.xlabel("Half-Hour index")
plt.ylabel("Aggregate Consumption (kWh)")
plt.legend(['24th','25th'],loc='upper left')
plt.savefig('linear_two_savgol.jpg')
plt.close()

xmas_week.resize((336,))
noise.resize((336,))
plt.plot(xmas_week)
plt.plot(noise)
axes = plt.gca()
axes.set_ylim([0,YSCALE])
plt.title("comparing raw and processed")
plt.xlabel("Half-Hour index")
plt.ylabel("Aggregate Consumption (kWh)")
plt.legend(['raw','processed'],loc='upper left')
plt.savefig('raw_and_savgol.jpg')
plt.close()

diff = (xmas_week - noise)/xmas_week
diff = [abs(i) for i in diff]
plt.plot(diff)
plt.title("relative error")
plt.xlabel("Half-Hour index")
plt.ylabel("Relative error")
plt.savefig('relerror.jpg')
plt.close()