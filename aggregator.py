# functions which deal with creating a aggregate power consumption matrix

import numpy as np

def convert_to_matrix(users,categories):
    """
    convert meter array into three matricies of different categories

    @param users        unprocessed meter readings with meter ids from Anupam's h5f
    @param categories   a dictionary which stores category for each meter
                        1   residential
                        2   SME
                        3   others

    @return a set of power consumption arrays for each category
    """

    retval = [None, None, None]
    ctr = [0,0,0] #a counter for row "shallow copying"
    c = [0,0,0] #counts # of meters in each category

    for row in users:
        id = row[0]
        case = categories[id] - 1 #since array begins with index 0
        c[case] = c[case] + 1

    for i in range(0,3):
        row_size = c[i]
        retval[i] = np.zeros((row_size,25200)) #bad way of initializing
        #TODO: change this initialization

    for row in users:
        id = row[0]
        case = categories[id] - 1
        data = np.array(row[1:25201])

        i = ctr[case]

        retval[case][i] = data
        ctr[case] = ctr[case] + 1

    return retval

def sum_rows(m):
    """
    sum all rows of matrix m
    
    @param m        input matrix to be summed        
    @return a row which is sum of all rows
    """

    retval = None
    (row_num, col_num) = m.shape

    for i in range(0, row_num):
        #print row_num
        if retval is None:
            retval = m[i]
        else:
            retval = retval + m[i]

    return retval