#functions which used to belong to diffp
#these functions only work for SVD decomposition related uses
#TODO: make sure the transportation worked properly

from colormapper import create_rgba, split_rgb
from diffp import lap_sample

base = '/home/hyunbinl/smartgrid/'

def find_agg_sens_svd(k, aggregate, users, categories):
    """ 
    TODO: combine this with find_rgb_sensitivity
    fix this so that it works with any size matrix
    """

    #initialize arrays
    max_U = np.zeros((75,k))
    max_s = np.zeros((k,))
    max_V = np.zeros((k,336))
    min_U = np.full((75,k),np.inf)
    min_s = np.full((k,),np.inf)
    min_V = np.full((k,336),np.inf)

    ctr = 0
    for row in users:
        id = row[0]
        case = categories[id] - 1
        
        #let's only focus on residential for now
        if case != 0:
            continue

        data = np.array(row[1:25201])
        data.resize((75,336))

        loo_mat = aggregate[case] - data
        U_l, s_l, V_l = np.linalg.svd(loo_mat)
        U_k = U_l[:,0:k]
        s_k = s_l[0:k]
        V_k = V_l[0:k,:]

        # U is 75 by k matrix
        for i in range(0,75):
            for j in range(0,k):
                max_U[i][j] = max(max_U[i][j], U_k[i][j])
                min_U[i][j] = min(min_U[i][j], U_k[i][j])

        # Sigma has k singular values
        for i in range(0,k):
            max_s[i] = max(max_s[i],s_k[i])
            min_s[i] = min(min_s[i],s_k[i])

        # V is k by 336 matrix 
        for i in range(0,k):
            for j in range(0,336):
                max_V[i][j] = max(max_V[i][j], V_k[i][j])
                min_V[i][j] = min(min_V[i][j], V_k[i][j])

        ctr = ctr + 1
        if ctr % 100 == 0:
            print ctr

    max_mins = [max_U, max_s, max_V, min_U, min_s, min_V]
    return max_mins

def find_agg_deltas_svd(max_mins):
    """
    TODO
    """

    max_U = max_mins[0]
    max_s = max_mins[1]
    max_V = max_mins[2]
    min_U = max_mins[3]
    min_s = max_mins[4]
    min_V = max_mins[5]

    delta_U = max_U - min_U
    delta_s = max_s - min_s
    delta_V = max_V - min_V

    return [delta_U, delta_s, delta_V]

def add_agg_noise_svd(k, U_k, s_k, V_k, epsilon, deltas, budget):
    """
    TODO
    fix so that this works with any matrix
    """

    e_prime = epsilon/budget
    U_noise = np.zeros((75,k))
    s_noise = np.zeros((k,))
    V_noise = np.zeros((k,336))

    for i in range(0,75):
        for j in range(0,k):
            U_noise[i][j] = lap_sample(None, deltas[0][i][j]/e_prime)

    for i in range(0,k):
        s_noise[i] = lap_sample(None, deltas[1][i]/e_prime)

    for i in range(0,k):
        for j in range(0,336):
            V_noise[i][j] = lap_sample(None, deltas[2][i][j]/e_prime)

    diff_U = U_k + U_noise
    diff_s = s_k + s_noise
    diff_V = V_k + V_noise

    retval = [diff_U, diff_s, diff_V]
    return retval

def find_rgb_sens_svd(k, aggregate, users, categories):
    """ 
    function which attempts to find sensitivity of matrix U, Sig, and V using LOO
    Note: This function only deals with residential data for now

    @param k                the SVD compression rate (1 <= k <= 75) 
    @param aggregate        the meter aggregate matrix
    @param users            rows of meter readings from Anupam's h5f
    @param categories       category of each meter based on provided xls file

    @return a matrix of max and mins for U, Sig and V
    """

    #initialize arrays
    max_U = np.zeros((75,k))
    max_s = np.zeros((k,))
    max_V = np.zeros((k,1008))
    min_U = np.full((75,k),np.inf)
    min_s = np.full((k,),np.inf)
    min_V = np.full((k,1008),np.inf)

    ctr = 0
    for row in users:
        id = row[0]
        case = categories[id] - 1
        
        #let's only focus on residential for now
        if case != 0:
            continue

        data = np.array(row[1:25201])
        data.resize((75,336))

        loo_mat = aggregate[case] - data
        rgba_loo = create_rgba(loo_mat)
        loo_A = split_rgb(rgba_loo)
        U_l, s_l, V_l = np.linalg.svd(loo_A)
        U_k = U_l[:,0:k]
        s_k = s_l[0:k]
        V_k = V_l[0:k,:]

        # U is 75 by k matrix
        for i in range(0,75):
            for j in range(0,k):
                max_U[i][j] = max(max_U[i][j], U_k[i][j])
                min_U[i][j] = min(min_U[i][j], U_k[i][j])

        # Sigma has k singular values
        for i in range(0,k):
            max_s[i] = max(max_s[i],s_k[i])
            min_s[i] = min(min_s[i],s_k[i])

        # V is k by 1008 matrix 
        for i in range(0,k):
            for j in range(0,1008):
                max_V[i][j] = max(max_V[i][j], V_k[i][j])
                min_V[i][j] = min(min_V[i][j], V_k[i][j])

        ctr = ctr + 1
        if ctr % 100 == 0:
            print ctr

    max_mins = [max_U, max_s, max_V, min_U, min_s, min_V]
    return max_mins

def find_rgb_deltas_svd(max_mins):
    """
    a simple function which finds delta for S, V and Sigma

    @param max_mins     max,min matrices created from find_rgb_sens_svd

    @return a set of delta matrices
    """

    max_U = max_mins[0]
    max_s = max_mins[1]
    max_V = max_mins[2]
    min_U = max_mins[3]
    min_s = max_mins[4]
    min_V = max_mins[5]

    delta_U = max_U - min_U
    delta_s = max_s - min_s
    delta_V = max_V - min_V

    return [delta_U, delta_s, delta_V]

def add_rgb_noise_svd(k, U_k, s_k, V_k, epsilon, deltas, budget):
    """
    this function adds laplacian noise to each matrix

    @param k        the SVD compression rate (1 <= k <= 75)
    @param U_k      U matrix after decomposition with factor k
    @param s_k      k sigular values created by SVD decomposition
    @param V_k      V matrix after decomposition with factor k
    @param epsilon
    @param deltas   sensitivity created by find_rgb_deltas
    @param budget   the number of budgets that epsilon must be divided onto

    @return U, s, V with noise added
    """

    e_prime = epsilon/budget
    U_noise = np.zeros((75,k))
    s_noise = np.zeros((k,))
    V_noise = np.zeros((k,1008))

    for i in range(0,75):
        for j in range(0,k):
            U_noise[i][j] = lap_sample(None, deltas[0][i][j]/e_prime)

    for i in range(0,k):
        s_noise[i] = lap_sample(None, deltas[1][i]/e_prime)

    for i in range(0,k):
        for j in range(0,1008):
            V_noise[i][j] = lap_sample(None, deltas[2][i][j]/e_prime)

    diff_U = U_k + U_noise
    diff_s = s_k + s_noise
    diff_V = V_k + V_noise

    retval = [diff_U, diff_s, diff_V]
    return retval    
