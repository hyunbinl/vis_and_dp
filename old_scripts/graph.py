#this short script is created for creating plots for 20160613's loo_*.png

from numpy import arange
import matplotlib.pyplot as plt

x = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]

# these results are printed from script
y1 = [3639,3639,3639,3639,3639,3638,2035,1672,1672,0]
y2 = [429,429,429,429,429,428,377,372,370,130]
y3 = [561,561,561,561,561,561,480,456,455,341]

plt.plot(x,y1)
plt.xlabel("RGB Sq.Root Dist")
plt.ylabel("# of different heatmaps")
plt.title("Residential")
plt.show()

plt.plot(x,y2)
plt.xlabel("RGB Sq.Root Dist")
plt.ylabel("# of different heatmaps")
plt.title("SME")
plt.show()

plt.plot(x,y3)
plt.xlabel("RGB Sq.Root Dist")
plt.ylabel("# of different heatmaps")
plt.title("Others")
plt.show()