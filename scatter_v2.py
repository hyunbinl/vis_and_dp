import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl

from parser import parse_h5f, parse_type
from printer import draw_plot, draw_plot_norm, draw_1d_plot, draw_scatter, draw_2d_hist
from aggregator import sum_rows, convert_to_matrix

from diffp import compute_deltas, add_noise_simple, eps_prime, lap_sample

from random import randint, uniform

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
    the_x = min(the_x, num - 1)
    the_y = min(the_y, num - 1)
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

x = []
y = []

x2 = []
y2 = []

c = 0

tot_min = 0
tot_max = 0
the_min = 0
the_max = 0
mindiff = 0
maxdiff = 0
total = 0

day1 = 0
day2 = 1

days = ["18th","25th"]

for res_i in residential:
    total = total + 1
    entry_i = res_i[21*336:22*336]
    entry_j = res_i[22*336:23*336]
    # entry_a = sum(entry_i[4 * 48:5 * 48])/48
    # entry_b = sum(entry_j[4 * 48:5 * 48])/48
    entry_a = entry_i[218]
    entry_b = entry_j[218]

    min_i = entry_a
    max_i = entry_b

    x.append(min_i)
    y.append(max_i)
    tot_max = tot_max + max_i
    tot_min = tot_min + min_i
    if the_min < min_i:
        mindiff = min_i - the_min
        the_min = min_i
    if the_max < max_i:
        maxdiff = max_i - the_max
        the_max = max_i

# x_avg = tot_min/len(x)
# y_avg = tot_max/len(y)
# x_std = np.std(x)
# y_std = np.std(y)

m = int(math.sqrt(float(1 * len(x))/10)) + 1

print m
print sum(y)

dist_mat = np.zeros((m,m))

print the_min
print the_max

while True:
    newmin = the_min + abs(lap_sample(None, mindiff/0.25))
    newmax = the_max + abs(lap_sample(None, maxdiff/0.25))
    if float(abs(the_min - newmin))/the_min < 0.1 and float(abs(the_max - newmax))/the_max < 0.1:
        the_min = newmin
        the_max = newmax
        break
    #endif
#endwhile

print the_min
print the_max

xp = []
yp = []

for i in range(0,len(x)):
    (yi,xi) = compute_index(x[i],y[i],the_min,the_max,m)
    dist_mat[xi][yi] = dist_mat[xi][yi] + 1
    if y[i] < 0.5:
        continue
    else:
        xp.append(x[i])
        yp.append(y[i])

#poly = np.polyfit(xp,yp,1)
poly = np.polyfit(x,y,1)
print "y = "+str(poly[0])+"x + "+str(poly[1])
poly_obj = np.poly1d(poly)

draw_scatter(x,y,the_min,the_max,days[day1],days[day2],poly_obj, "Consumption during 1300 to 1330 for Dec "+days[day1]+" and "+days[day2],"raw_scatter.jpg")
draw_2d_hist(dist_mat,the_min,the_max,m,days[day1],days[day2],"raw 2d histogram m="+str(m), "raw_hist.jpg")


v = m
a = np.zeros((v,v))
for i in range(0,v):
    for j in range(0,v):
        a[i][j] = int(dist_mat[i][j] + lap_sample(None, 1/0.5))
        a[i][j] = max(a[i][j] ,0)

draw_2d_hist(a, the_min,the_max,m,days[day1],days[day2], "2d histogram with 1-DP", "hist_dp.jpg")

new_x = []
new_y = []
for i in range(0,v):
    for j in range(0,v):
        if a[i][j] != 0:
            for l in range(0, int(a[i][j])):
                x_i, y_i = generate_new_point(j,i,the_min,the_max,m)
                new_x.append(x_i)
                new_y.append(y_i)
            #endfor
        #endif
    #endfor
#endfor

poly = np.polyfit(new_x,new_y,1)
poly_obj = np.poly1d(poly)

draw_scatter(new_x,new_y,the_min,the_max,days[day1],days[day2],poly_obj,"1-DP scatterplot","dp_scatter.jpg")

# tot_max = 0
# tot_min = 0
# for i in range(0, len(new_x)):
#     tot_min = tot_min + new_x[i]
#     tot_max = tot_max + new_y[i]

# x_avg = tot_min/len(new_x)
# y_avg = tot_max/len(new_y)
# x_std = np.std(new_x)
# y_std = np.std(new_y)

# new_x2 = []
# new_y2 = []

# for i in range(0,len(new_x)):
#     min_i = new_x[i]
#     max_i = new_y[i]

#     if x_avg + 2 * x_std < min_i or x_avg - 2 * x_std > min_i:
#         continue
#     if y_avg + 2 * y_std < max_i or y_avg - 2 * y_std > max_i:
#         continue
#     if max_i > 0 and min_i > 0:
#         new_x2.append(min_i)
#         new_y2.append(max_i)

# poly = np.polyfit(new_x2,new_y2,1)
# poly_obj = np.poly1d(poly)
# draw_scatter(new_x2, new_y2, the_min, the_max,days[day1],days[day2],poly_obj,"1-DP scatterplot_noo","dp_scatter_noo.jpg")
