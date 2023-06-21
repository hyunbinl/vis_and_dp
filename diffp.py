import numpy as np
import math

base = '/home/hyunbinl/smartgrid/'

def lap_sample(u,b):
    """
    based on 
    https://en.wikipedia.org/wiki/Laplace_distribution

    @param u    a number picked from the uniform distribution
    @param b    delta/e' where e' can either be epsilon or epsilon/(# of samples)
    @return     a laplacian noise, l(delta/e')
    """
    if u is None:
        u = np.random.uniform(-0.5,0.5,size = 1)[0]

    mu = 0 # mu = 0 for this case
    return mu - b * np.sign(u) * math.log(1 - 2 * abs(u))

def eps_prime(k, s_delta, eps):
    """
    TODO: Add comment with source

    @param k
    @param s_delta
    @param eps

    @return     eps_prime for advanced composition
    """

    return math.sqrt(2 * k * np.log(1/s_delta)) * eps + k * eps * (math.exp(eps) - 1)

def compute_deltas():
    """
    computes matrix for max - min for each category

    @return     an array of three delta matricies of shape (1,25200)
    """

    stat_base = base + 'cer_parsed_data/Filter_outlier'
    types = ['/Resident/FeatureData/',
    '/SME/FeatureData/',
    '/Others/FeatureData/']
    retval = [None, None, None]

    for i in range(0,3):
        with open(stat_base+types[i]+'Min') as f:
            min = f.readline().strip().split(',') 

        with open(stat_base+types[i]+'Max') as f:
            max = f.readline().strip().split(',')

        retval[i] = [float(x) - float(y) for x,y in zip(max,min)]

    return retval

def track_outliers():
    """ returns a list of outliers """

    types = ['Others_combo',
    'Resident_combo',
    'SME_combo']
    path = base+"cer_parsed_data/outliers/"
    outliers = []

    for category in types:
        for meter_id in open(path+category,"r"):
            outliers.append([int(meter_id)])

    return outliers

def add_noise_simple(aggregate, eps, deltas):
    """
    function which adds Laplacian noise to meter matrix
    Note: This function replaced deprecated add_noise() since 2016/07/12.

    @param aggregate    a (# of weeks,# of half-hours) aggregate power consumption matrix
    @param epsilon
    @param deltas       a # of weeks * # of half-hours sensitivity list 
    
    @return     processed meter matrix and a (# of weeks,# of half-hours) noise matrix
    """

    weeks, hf_hrs = aggregate.shape
    k = weeks * hf_hrs

    if k != len(deltas):
        print len(deltas)
        print k
        print "delta and aggregate shape different"

    u_arr = (np.random.rand(1,k))[0] #samples picked from U[0,1)
    u_arr = [x - 0.5 for x in u_arr] #U[-0.5,0.5)

    noises = np.array([lap_sample(u, delta/eps) for u, delta in zip(u_arr, deltas)])
    noises.resize((weeks,hf_hrs))
    diffp_m = aggregate + noises #add two matricies
    diffp_m.resize((k,))
    a = np.array([x for x in diffp_m]) #make sure there is no "negative" consumption
    a.resize((weeks,hf_hrs))
    
    return a, noises

# def find_rgb_sens(aggregate, users, categories, scale, interp):
#     """ 
#     function which attempts to find sensitivity of compressed matrix
#     Note: This function only deals with residential data for now

#     @param aggregate        the meter aggregate matrix
#     @param users            rows of meter readings from Anupam's h5f
#     @param categories       category of each meter based on provided xls file
#     @param scale            new (width,height)
#     @param interp           Interpolation to use for re-sizing

#     @return a matrix of deltas for R, G, and B
#     """

#     (width,height) = scale

#     max_R = np.zeros(scale)
#     max_G = np.zeros(scale)
#     max_B = np.zeros(scale)
#     min_R = np.full(scale,np.inf)
#     min_G = np.full(scale,np.inf)
#     min_B = np.full(scale,np.inf)

#     ctr = 0
#     for row in users:
#         id = row[0]
#         case = categories[id] - 1
        
#         #let's only focus on residential for now
#         if case != 0:
#             continue

#         data = np.array(row[1:25201])
#         data.resize((75,336))

#         loo_mat = aggregate[case] - data
#         rgba_loo = create_rgba(loo_mat)
#         rgba_resized = imresize(rgba_loo,scale,interp)
#         (R,G,B) = split_rgb(rgba_resized)

#         for i in range(0,width):
#             for j in range(0,height):
#                 max_R[i][j] = max(max_R[i][j], R[i][j])
#                 min_R[i][j] = min(min_R[i][j], R[i][j])

#         for i in range(0,width):
#             for j in range(0,height):
#                 max_G[i][j] = max(max_G[i][j], G[i][j])
#                 min_G[i][j] = min(min_G[i][j], G[i][j])

#         for i in range(0,width):
#             for j in range(0,height):
#                 max_B[i][j] = max(max_B[i][j], B[i][j])
#                 min_B[i][j] = min(min_B[i][j], B[i][j])

#         ctr = ctr + 1
#         if ctr % 100 == 0:
#             print ctr

#     deltas = [max_R - min_R, max_G - min_G, max_B - min_B]
#     return deltas

# def add_rgb_noise(rgbmat, eps, deltas):
#     """
#     this function adds laplacian noise to rgbmat

#     @param rgb
#     @param epsilon
#     @param deltas   sensitivity created by find_rgb_deltas
#     """

#     (w,h,t) = rgbmat.shape
#     noise_mat = np.zeros((w,h,t))

#     for i in range(0,w):
#         for j in range(0,h):
#             noise_mat[i][j][0] = lap_sample(None, deltas[0][i][j]/eps)
#             noise_mat[i][j][1] = lap_sample(None, deltas[1][i][j]/eps)
#             noise_mat[i][j][2] = lap_sample(None, deltas[2][i][j]/eps)
    
#     for i in range(0,w):
#         for j in range(0,h):
#             rgbmat[i][j][0] = min(max(noise_mat[i][j][0] + rgbmat[i][j][0],0),255)
#             rgbmat[i][j][1] = min(max(noise_mat[i][j][1] + rgbmat[i][j][1],0),255)
#             rgbmat[i][j][2] = min(max(noise_mat[i][j][2] + rgbmat[i][j][2],0),255)