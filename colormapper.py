#these functions deal with RGB matrix related operations

import matplotlib.pyplot as plt
import pylab as pl
import numpy as np

def create_rgba(arr, cm):
    """
    convert meter reading matrix arr into rgb matrix

    @param arr: a meter matrix
    @return a rgba matrix
    """
    cmap = plt.get_cmap(cm)
    norm = pl.Normalize(arr.min(),arr.max())
    retval = cmap(norm(arr))
    return retval

def split_rgb(a):
    """
    split rgb component so that SVD decomposition can be used

    @param a        a rgba matrix with size (width, height)
    @return a matrix with size (width,height * 3) where first third is R matrix,
            second third is G matrix, and last third is B matrix
    """

    w,h,t = a.shape


    a.resize((w * h,4,))
    red = np.array([r for (r,g,b,al) in a])
    green = np.array([g for (r,g,b,al) in a])
    blue = np.array([b for (r,g,b,al) in a])
    a.resize((w,h,4)) #restore a to original shape

    red.resize((w,h))
    green.resize((w,h))
    blue.resize((w,h))

    return (red, green, blue)

def combine_rgb(a):
    """
    combine a matrix created from above into a rgb matrix

    @param a        a matrix with size  (w,3 * h) where R, G and B are separated
    @return a rgba matrix with size (w,h)
    """

    (red,green,blue) = a
    print red
    w,h = red.shape    
    retval = np.zeros((w,h,4))


    for i in range(0,w):
        for j in range(0,h):
            r = min(225,max(0,red[i][j]))
            g = min(225,max(0,green[i][j]))
            b = min(225,max(0,blue[i][j]))

            retval[i][j] = (r,g,b,225) #lets stick alpha with 1

    return retval