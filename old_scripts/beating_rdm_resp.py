import math
import sys
import numpy as np

from parser import parse_h5f, parse_type
from printer import draw_plot
from aggregator import sum_rows, convert_to_matrix

users = parse_h5f() #parse h5f dataset
categories = parse_type() #get xls file for user types
meter_matrix = convert_to_matrix(users,categories)

residential = meter_matrix[0]
row,col = residential.shape

k = 100
eps = 1.0
delta = 0.0001

omega = np.random.normal(0,1,(col,k))

print omega.shape

Y = np.dot(residential, omega)

####1

# rou = 2 * (1/eps) * math.sqrt(2 * k * math.log(float(4 * k)/delta))
# rou_sq = math.pow(rou,2)
# N = np.random.normal(0,rou_sq,(row,k))
# Y = Y + N

####1

W, r = np.linalg.qr(Y)

temp_r, temp_c = W.shape

W_T = np.matrix.transpose(W)

####2

# wr, wc = W.shape

# alphas = np.zeros((wc,1))

# for i in range(0,wc):
#     for j in range(0,wr):
#         alphas[i] = max(alphas[i],W[j][i])

# print alphas.shape

# N_2 = np.zeros((k,col))

# rou = 2 * (1/eps) * math.sqrt(8 * k * math.log(4.0 * k/delta) * math.log(2.0/delta))
# rou_sq = math.pow(rou,2)

# for i in range(0,k):
#     for j in range(0,col):
#         std = math.pow(alphas[i],2) * rou_sq
#         N_2[i][j] = np.random.normal(0,std)

# B = np.dot(W_T, residential) + N_2
# B = np.dot(W,B)

####2

B = np.dot(W_T,residential)

brow,bcol = B.shape

for i in range(0,brow):
    for j in range(0,bcol):
        B[i][j] = max(B[i][j],0)

aggregate = sum_rows(B)
aggregate.resize((75,336))

draw_plot(aggregate, "k="+str(k), None)