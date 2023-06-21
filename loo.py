import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import pylab as pl

from parser import parse_h5f, parse_type
from printer import draw_plot_rgb, draw_plot_cm, draw_plot_cm_v2
from aggregator import sum_rows, convert_to_matrix
from diffp import compute_deltas, add_noise_simple, eps_prime, lap_sample
from random import randint, uniform

from colormapper import create_rgba

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)
delta = compute_deltas()

residential = meter_matrix[0]
sme = meter_matrix[1]
others = meter_matrix[2]

residential = residential[:,:52*336]
num_sample, queries = residential.shape
a = sum_rows(residential)
# a.resize((52,336))
res_deltas = np.array(delta[0])
res_deltas.resize((75,336))
res_deltas = res_deltas[:52,:]
res_deltas.resize((52*336,))

tot_del = 0
for ct in range(0,10):
    i = 0
    j = 0
    while i == j:
        i = randint(0, 3638)
        j = randint(0, 3638)
    r = residential[i]
    t = residential[j]
    ar = a - r
    at = a - t  
    cmap = plt.get_cmap("spectral")
    norm = pl.Normalize(a.min(),a.max())

    arr = []
    for k in range(0,len(ar)):
        car = cmap(norm(ar[k]))
        cat = cmap(norm(at[k]))
        
        color1_rgb = sRGBColor(car[0], car[1], car[2]);
        color2_rgb = sRGBColor(cat[0], cat[1], cat[2]); 
        color1_lab = convert_color(color1_rgb, LabColor); 
        color2_lab = convert_color(color2_rgb, LabColor); 
        delta_e = delta_e_cie2000(color1_lab, color2_lab);
        arr.append(delta_e)

    arr = np.array(arr)
    ar.resize((52,336))
    at.resize((52,336))
    arr.resize((52,336))
    draw_plot_cm(ar, str(i), "spectral", str(i)+".jpg")
    draw_plot_cm(at, str(j), "spectral", str(j)+".jpg")
    draw_plot_cm_v2(arr, str(i)+"_"+str(j)+"_diff", "binary", "delta_e", str(ct)+"_diff.jpg")


    ct = ct + 1
    if ct == 10:
        break

# ctrs = dict()
# for t in range(0, 100):
#     i = randint(0, 51)
#     j = randint(0, 335)

#     #print "week="+str(i)+" day="+str(j/48)+" hhour="+str(j%48)
#     defc = a[i][j]
#     c = sorted(m for m in plt.cm.datad if not m.endswith("_r"))
#     for cm in c:
#         #draw_plot_cm(a,cm,cm,"20170223/colormaps/"+cm+".jpg")


#         cmap = plt.get_cmap(cm)
#         norm = pl.Normalize(a.min(),a.max())
#         color_prev = cmap(norm(defc))
#         counter = 0
#         the_delta = 1.0
#         eps = 1.0

#         for k in range(0, 100):
#             noise = lap_sample(None, res_deltas[i * 336 + j]/eps)
#             color_ite = cmap(norm(defc + noise))

#             r1 = color_prev[0]
#             g1 = color_prev[1]
#             b1 = color_prev[2]

#             r2 = color_ite[0]
#             g2 = color_ite[1]
#             b2 = color_ite[2]

#             color1_rgb = sRGBColor(r1, g1, b1);
#             color2_rgb = sRGBColor(r2, g2, b2); 

#             color1_lab = convert_color(color1_rgb, LabColor); 
#             color2_lab = convert_color(color2_rgb, LabColor); 
#             delta_e = delta_e_cie2000(color1_lab, color2_lab);

#             if delta_e > the_delta:
#                 counter = counter + 1
#         if t == 0:
#             ctrs[cm] = counter
#         else:
#             ctrs[cm] = ctrs[cm] + counter
#         #print cm+": "+str(counter)

# for cm in c:
#     print cm+": "+str(ctrs[cm])

    # carr = []

    # ite = a.min()
    # while ite < a.max():
    #     prev = ite
    #     ite = ite + 50
    #     color_prev = cmap(norm(prev))
    #     color_ite = cmap(norm(ite))

    #     r1 = color_prev[0]
    #     g1 = color_prev[1]
    #     b1 = color_prev[2]

    #     r2 = color_ite[0]
    #     g2 = color_ite[1]
    #     b2 = color_ite[2]

    #     color1_rgb = sRGBColor(r1, g1, b1);
    #     color2_rgb = sRGBColor(r2, g2, b2); 

    #     color1_lab = convert_color(color1_rgb, LabColor); 
    #     color2_lab = convert_color(color2_rgb, LabColor); 
    #     delta_e = delta_e_cie2000(color1_lab, color2_lab);
    #     carr.append(delta_e)

    # fig = plt.figure()
    # plt.plot(np.arange(a.min(),ite,50), carr)
    # plt.title("consumption vs delta_e")
    # plt.xlabel("agg. consumption")
    # plt.ylabel("delta_e")
    # plt.savefig("20170223/colormaps/e_deltas/"+cm+".jpg")
    # plt.close()




# arr = []

# for i in range(0,336):
#     r1 = ca[0][i][0]
#     g1 = ca[0][i][1]
#     b1 = ca[0][i][2]

#     r2 = ca[1][i][0]
#     g2 = ca[1][i][1]
#     b2 = ca[1][i][2]

#     color1_rgb = sRGBColor(r1, g1, b1);
#     color2_rgb = sRGBColor(r2, g2, b2); 

#     color1_lab = convert_color(color1_rgb, LabColor); 
#     color2_lab = convert_color(color2_rgb, LabColor); 
#     delta_e = delta_e_cie2000(color1_lab, color2_lab);

#     #print "The difference between the 2 color = ", delta_e

#     arr.append(delta_e)