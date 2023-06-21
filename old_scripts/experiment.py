import matplotlib.pyplot as plt
from diffp import lap_sample

# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api

deltas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
signs = [-1,1]
z = [30, 90, 70, 50]
N = len(z)
x = range(N)
width = 1/1.5
fig = plt.figure()
axes = plt.gca()
axes.set_ylim([0,100])
plt.bar(x, z, width, color="blue")
plt.savefig("20170223/3/no_noise.jpg")
plt.close()

for d in deltas:
    for s in signs:
        y = list(z)
        y[3] = y[3] + s * d
        print y
        N = len(y)
        x = range(N)
        width = 1/1.5
        fig = plt.figure()
        axes = plt.gca()
        axes.set_ylim([0,100])
        plt.bar(x, y, width, color="blue")
        plt.savefig("20170223/3/"+str(d)+"_"+str(s)+".jpg")
        plt.close()


epss = [0.1, 0.5, 1.0]

# print "delta\tepsilon\terror_perc"

# for d in deltas:
#     for e in epss:
#         delta = d
#         counter = 0

#         for i in range(0,100000):
#             noise = lap_sample(None, 1/e)
#             if delta < noise:
#                 counter = counter + 1

#         print str(d)+"\t"+str(e)+"\t"+str(float(counter)/100000)