import numpy as np
from diffp import add_noise_simple, lap_sample

def compute_loo(m, samples):
    num, att = samples.shape
    row, col = m.shape

    retval = []

    for i in range(0, num):
        curr = samples[i]
        curr.resize((row,col))
        retval.append(m - curr)

    return retval

def compute_group_loc_sen(loo_m):
    delta = 0
    l_max = 0
    l_min = np.inf
    row = 0
    col = 0

    for curr in loo_m:
        row, col = curr.shape
        val = 0
        
        for i in range(0, row):
            for j in range(0, col):
                val = val + curr[i][j]

        l_max = max(l_max,val)
        l_min = min(l_min,val)

    return (l_max - l_min)/(row * col)

def compute_loc_sen(loo_m):
    num_samples, row, col = loo_m.shape

    l_max = np.zeros((row, col))
    l_min = np.zeros((row, col))
    l_min.fill(np.inf)

    for curr in loo_m:
        for i in range(0, row):
            for j in range(0, col):
                l_max[i][j] = max(l_max[i][j], curr[i][j])
                l_min[i][j] = min(l_min[i][j], curr[i][j])

    return l_max - l_min


def divide_aggregate(m, samples, x, y, t, eps):
    """
    @param m        row by col input matrix m 
    @param x        
    @param y        
    @param samples    
    @param t        absolute threshold

    @return new_m
    @return new_delta
    @return budget
    """

    loo_m = compute_loo(m, samples)
    print np.array(loo_m).shape

    return rec_divide_aggregate(m, np.array(loo_m), x, y, t, eps)

def rec_divide_aggregate(m, loo_m, x, y, t, eps):
    """
    @param m        row by col input matrix m 
    @param x        
    @param y        
    @param loo_m    
    @param t        absolute threshold

    @return new_m
    @return budget
    """

    (row,col) = m.shape

    #base case
    if row <= y and col <= x:
        deltas = compute_loc_sen(loo_m)
        deltas.resize((row*col,))
        a, noises = add_noise_simple(m, eps, deltas)
        return a, (row * col)

    mean = 0
    for i in range(0, row):
        for j in range(0, col):
            mean = mean + m[i][j]

    #see if any |mean - m_ij| > t
    mean = mean/(row * col)
    can_agg = True

    for i in range(0, row):
        for j in range(0, col):
            diff = abs(mean - m[i][j])
            if diff > t:
                can_agg = False
                break

    if can_agg is True:
        new_m = np.zeros((row,col))

        loc_sen = compute_group_loc_sen(loo_m)       
        mean = min(max(mean + lap_sample(None, loc_sen/eps), 0), 5000)

        for i in range(0, row):
            for j in range(0, col):
                new_m[i][j] = mean

        return new_m, 1

    else:
        budget = 0
        if row > y and col > x:
            new_row = row/2
            new_col = col/2
            
            m_lt = m[:new_row,:new_col]
            m_rt = m[:new_row,new_col:col]
            m_lb = m[new_row:row,:new_col]
            m_rb = m[new_row:row,new_col:col]

            loo_lt = []
            loo_rt = []
            loo_lb = []
            loo_rb = []

            for curr in loo_m:
                loo_lt.append(curr[:new_row,:new_col])
                loo_rt.append(curr[:new_row,new_col:col])
                loo_lb.append(curr[new_row:row,:new_col])
                loo_rb.append(curr[new_row:row,new_col:col])

            p_lt, b_lt = rec_divide_aggregate(m_lt, np.array(loo_lt), x, y, t, eps)
            p_rt, b_rt = rec_divide_aggregate(m_rt, np.array(loo_rt), x, y, t, eps)
            p_lb, b_lb = rec_divide_aggregate(m_lb, np.array(loo_lb), x, y, t, eps)
            p_rb, b_rb = rec_divide_aggregate(m_rb, np.array(loo_rb), x, y, t, eps)

            budget = b_lt + b_rt + b_lb + b_rb
            processed = np.vstack((np.hstack((p_lt,p_rt)), np.hstack((p_lb, p_rb))))

            return processed, budget

        elif row > y:
            new_row = row/2
            
            m_t = m[:new_row,:]
            m_b = m[new_row:row,:]
            
            loo_t = []
            loo_b = []

            for curr in loo_m:
                loo_t.append(curr[:new_row,:])
                loo_b.append(curr[:new_row:row,:])

            p_t, b_t = rec_divide_aggregate(m_t, np.array(loo_t), x, y, t, eps)
            p_b, b_b = rec_divide_aggregate(m_b, np.array(loo_b), x, y, t, eps)

            budget = b_t + b_b
            processed = np.vstack((p_t,p_b))

            return processed, budget 

        else: #col > x
            new_col = col/2

            m_l = m[:,:new_col]
            m_r = m[:,new_col:col]
            
            loo_l = []
            loo_r = []
            
            for curr in loo_m:
                loo_l.append(curr[:,:new_col])
                loo_r.append(curr[:,new_col:col])

            p_l, b_l = rec_divide_aggregate(m_l, np.array(loo_l), x, y, t, eps)
            p_r, b_r = rec_divide_aggregate(m_r, np.array(loo_r), x, y, t, eps)

            budget = b_l + b_r

            processed = np.hstack((p_l,p_r))

            return processed, budget