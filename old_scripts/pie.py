import matplotlib.pyplot as plt
import numpy as np
import sys

from parser import parse_h5f, parse_type
from aggregator import sum_rows, convert_to_matrix
from diffp import compute_deltas, add_noise_simple, eps_prime, lap_sample


def import_from_credc(i,j):
    users = parse_h5f() #parse h5f dataset
    categories = parse_type() #get xls file for user types
    meter_matrix = convert_to_matrix(users,categories)
    delta = compute_deltas()

    residential = meter_matrix[0]
    residential = residential[:,:52*336]
    num_sample, queries = residential.shape

    tot_agg = sum_rows(residential)
    tot_agg.resize((52,336))
    res_deltas = np.array(delta[0])
    res_deltas.resize((75,336))
    res_deltas = res_deltas[:52,:]
    res_deltas.resize((52*336,))

    xmas_week = tot_agg[i:j]
    xmas_delta = res_deltas[i*336:j*336]

    return xmas_week, xmas_delta
#enddef

def make_autopct(values):
    """
    http://stackoverflow.com/questions/6170246/how-do-i-use-matplotlib-autopct
    """
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:.8f})'.format(p=pct,v=val)
    return my_autopct
#enddef

#main

xmas_week, xmas_delta = import_from_credc(22,23)
xmas_week.resize((336,))
xmas_delta.resize((336,))

# k = 0
# daily_tot = np.zeros((7,))
# daily_max = np.zeros((7,))
# daily_min = np.zeros((7,))

# for i in range(0,7):
#     for j in range(0,48):
#         daily_tot[i] = daily_tot[i] + xmas_week[i*48 + j]
#         if daily_min[i] == 0 and xmas_week[i*48 + j] != 0:
#             daily_min[i] = xmas_week[i*48 + j]
#         elif daily_min[i] > xmas_week[i*48 + j]:
#             daily_min[i] = xmas_week[i*48 + j]
#         if daily_max[i] < xmas_week[i*48 + j]:
#             daily_max[i] = xmas_week[i*48 + j]

# # The slices will be ordered and plotted counter-clockwise.
# labels = 'Mon', 'Tue', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'
# colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'purple', 'white', 'red']
# explode = (0, 0, 0, 0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

# sizes = daily_tot
# fig = plt.figure()
# plt.pie(sizes, explode=explode, labels=labels, colors=colors,
#         autopct='%1.1f%%', shadow=True, startangle=90)
# # Set aspect ratio to be equal so that pie is drawn as a circle.
# plt.axis('equal')
# plt.title('weekly_average')
# plt.close()

# sizes = daily_max
# fig = plt.figure()
# plt.pie(sizes, explode=explode, labels=labels, colors=colors,
#         autopct='%1.1f%%', shadow=True, startangle=90)
# # Set aspect ratio to be equal so that pie is drawn as a circle.
# plt.axis('equal')
# plt.title('weekly_max')
# plt.show()
# plt.close()

# sizes = daily_min
# fig = plt.figure()
# plt.pie(sizes, explode=explode, labels=labels, colors=colors,
#         autopct='%1.1f%%', shadow=True, startangle=90)
# # Set aspect ratio to be equal so that pie is drawn as a circle.
# plt.axis('equal')
# plt.title('weekly_min')
# plt.show()
# plt.close()


labels = '0~4', '4~8', '8~12', '12~16', '16~20', '20~24'
colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'purple', 'white']
explode = (0, 0, 0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

hr_tot = np.zeros((6,))
hr_max = np.zeros((6,))
hr_min = np.zeros((6,))
hr_delta = np.zeros((6,))
hr_noise = np.zeros((6,))

cr_tot = np.zeros((6,))
cr_max = np.zeros((6,))
cr_min = np.zeros((6,))
cr_delta = np.zeros((6,))
cr_noise = np.zeros((6,))

for i in range(0,7):
    for j in range(0,6):
        for k in range(0,8):
            hr_tot[j] = hr_tot[j] + xmas_week[i*48 + j*8 + k]
            hr_delta[j] = hr_delta[j] + xmas_delta[i*48 + j*8 + k]
            if hr_min[j] == 0 and xmas_week[i*48 + j*8 + k] != 0:
                hr_min[j] = xmas_week[i*48 + j*8 + k]
            elif hr_min[j] > xmas_week[i*48 + j*8 + k]:
                hr_min[j] = xmas_week[i*48 + j*8 + k]
            if hr_max[j] < xmas_week[i*48 + j*8 + k]:
                hr_max[j] = xmas_week[i*48 + j*8 + k]

            if i == 4:
                cr_tot[j] = cr_tot[j] + xmas_week[i*48 + j*8 + k]
                cr_delta[j] = cr_delta[j] + xmas_delta[i*48 + j*8 + k]
                if cr_min[j] == 0 and xmas_week[i*48 + j*8 + k] != 0:
                    cr_min[j] = xmas_week[i*48 + j*8 + k]
                elif cr_min[j] > xmas_week[i*48 + j*8 + k]:
                    cr_min[j] = xmas_week[i*48 + j*8 + k]
                if cr_max[j] < xmas_week[i*48 + j*8 + k]:
                    cr_max[j] = xmas_week[i*48 + j*8 + k]
            #endif
        #endfor
    #endfor
#endfor

for i in range(0,6):
    hr_noise[i] = hr_tot[i] + lap_sample(None, hr_delta[i]/6)
    cr_noise[i] = cr_tot[i] + lap_sample(None, cr_delta[i]/6)
#endfor

width = 0.75

sizes = hr_tot
fig = plt.figure()
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%.2f', shadow=True, startangle=90)
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')
plt.suptitle('daily_average', x = .15, y = .99)
plt.savefig('pie_daily_raw.jpg')
plt.close()

for i in range(0, len(sizes)):
    sizes[i] = sizes[i]/(3639 * 8)

fig = plt.figure()
plt.bar(np.arange(6), sizes, width)
plt.ylabel("Average Consumption (kWh)")
plt.title('daily_average')
plt.xticks([i + width/2 for i in np.arange(6)], labels)
plt.savefig('bar_daily_raw.jpg')
plt.close()

sizes = cr_tot
fig = plt.figure()
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%.2f', shadow=True, startangle=90)
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')
plt.suptitle('christmas_average', x = .15, y = .99)
plt.savefig('pie_xmas_raw.jpg')
plt.close()

for i in range(0, len(sizes)):
    sizes[i] = sizes[i]/(3639 * 8)

fig = plt.figure()
plt.bar(np.arange(6), sizes, width)
plt.ylabel("Average Consumption (kWh)")
plt.title('christmas_average')
plt.xticks([i + width/2 for i in np.arange(6)], labels)
plt.savefig('bar_xmas_raw.jpg')
plt.close()

sizes = hr_noise
fig = plt.figure()
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%.2f', shadow=True, startangle=90)
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')
plt.suptitle('daily_average_1-DP', x = .15, y = .99)
plt.savefig('pie_daily_noise.jpg')
plt.close()

for i in range(0, len(sizes)):
    sizes[i] = sizes[i]/(3639 * 8)

fig = plt.figure()
plt.bar(np.arange(6), sizes, width)
plt.ylabel("Average Consumption (kWh)")
plt.title('daily_average_1-DP')
plt.xticks([i + width/2 for i in np.arange(6)], labels)
plt.savefig('bar_daily_noise.jpg')
plt.close()

sizes = cr_noise
fig = plt.figure()
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%.2f', shadow=True, startangle=90)
# Set aspect ratio to be equal so that pie is drawn as a circle.
plt.axis('equal')
plt.suptitle('christmas_average_1-DP', x = .15, y = .99)
plt.savefig('pie_xmas_noise.jpg')
plt.close()

for i in range(0, len(sizes)):
    sizes[i] = sizes[i]/(3639 * 8)

fig = plt.figure()
plt.bar(np.arange(6), sizes, width)
plt.ylabel("Average Consumption (kWh)")
plt.title('christmas_average_1-DP')
plt.xticks([i + width/2 for i in np.arange(6)], labels)
plt.savefig('bar_xmas_noise.jpg')
plt.close()
