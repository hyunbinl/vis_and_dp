#functions dealing with heatmap generation

from numpy import arange
import matplotlib.pyplot as plt
import pylab as pl
import numpy as np

def draw_plot(m,t,dir):
    """
    plot heatmaps with matrix m and title t
    """

    weeks, hf_hrs = m.shape
    hhpd = hf_hrs/7
    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

    fig = plt.figure()
    mapable = plt.imshow(m, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9, aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Aggregate Consumption")
    plt.xlabel("Half-Hour index")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("Weekly index")

    plt.autoscale(tight=True)
    plt.title(t)

    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
#enddef

def draw_plot_cm(m,t,cm,dir):
    """
    plot heatmaps with matrix m and title t
    """

    weeks, hf_hrs = m.shape
    hhpd = hf_hrs/7
    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

    fig = plt.figure()
    mapable = plt.imshow(m, interpolation="nearest", cmap=plt.get_cmap(cm), alpha=0.9, aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Aggregate Consumption")
    plt.xlabel("Half-Hour index")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("Weekly index")

    plt.autoscale(tight=True)
    plt.title(t)

    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
#enddef

def draw_plot_cm_v2(m,t,cm,cm_tag,dir):
    """
    plot heatmaps with matrix m and title t
    """

    weeks, hf_hrs = m.shape
    hhpd = hf_hrs/7
    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

    fig = plt.figure()
    mapable = plt.imshow(m, interpolation="nearest", cmap=plt.get_cmap(cm), alpha=0.9, aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label(cm_tag)
    plt.xlabel("Half-Hour index")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("Weekly index")

    plt.autoscale(tight=True)
    plt.title(t)

    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
#enddef

def draw_plot_norm(m,t,n,dir):
    """
    plot heatmaps with matrix m and title t
    """

    weeks, hf_hrs = m.shape
    hhpd = hf_hrs/7
    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

    fig = plt.figure()
    mapable = plt.imshow(m, interpolation="nearest",cmap=pl.cm.spectral, norm=n, alpha=0.9, aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Aggregate Consumption (kWh)")
    plt.xlabel("Half-Hour index")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("Weekly index")
    plt.autoscale(tight=True)
    plt.title(t)
    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
#enddef

def draw_1d_plot(m,t,dir):
    """
    563 project
    plot 1d-heatmaps with matrix m and title t
    """

    weeks, hf_hrs = m.shape
    hhpd = hf_hrs/7
    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

    fig = plt.figure(figsize=(10,3))
    mapable = plt.imshow(m, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9, aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Aggregate Consumption (kWh)")
    plt.xlabel("Half-Hour index")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("Weekly index")

    plt.autoscale(tight=True)
    plt.title(t)

    frame1 = plt.gca()
    frame1.axes.get_yaxis().set_visible(False)

    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
#enddef

def draw_lin_plot_ns(m,t,dir):
    """
    563 project & ms_thesis
    """
    a, b= m.shape
    hhpd = b/7
    m.resize((b,a))
    plt.plot(m)

    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]
    plt.title(t)
    plt.xlabel("Half-Hour index")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("Aggregate Consumption (kWh)")

    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
    m.resize((a,b))
#enddef

def draw_lin_plot(m,t,yscale,dir):
    """
    563 project & ms_thesis
    """
    a, b= m.shape
    hhpd = b/7
    m.resize((b,a))
    plt.plot(m)

    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]
    plt.title(t)
    axes = plt.gca()
    axes.set_ylim([0,yscale])
    plt.xlabel("Half-Hour index")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("Aggregate Consumption (kWh)")

    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
    m.resize((a,b))
#enddef

def draw_scatter(x,y,dpx,dpy,day1,day2,poly,title,filename):
    """
    563 project
    """
    plt.scatter(x,y)

    xp = np.linspace(0,dpx,100)
    #plt.plot(xp,poly(xp),'-',color='red')

    plt.autoscale(tight=True)
    plt.xlabel("Consumption during "+day1+" (kWh)")
    plt.ylabel("Consumption during "+day2+" (kWh)")
    plt.xlim([0,dpx])
    plt.ylim([0,dpy])
    plt.title(title)
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename)
    plt.close()
#enddef

def draw_2d_hist(m,dpx,dpy,u,day1,day2,title,filename):
    """
    563
    """
    fig = plt.figure()
    mapable = plt.imshow(m, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9, aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("freq")
    plt.xlabel("Consumption during "+day1+" (kWh)")
    plt.ylabel("Consumption during "+day2+" (kWh)")
    arrs = arange(0,u,float(u)/6)
    plt.xticks(arrs,[float("{0:.2f}".format(i * dpx/u)) for i in arrs])
    plt.yticks(arrs,[float("{0:.2f}".format(i * dpy/u)) for i in arrs])
    plt.gca().invert_yaxis()
    plt.autoscale(tight=True)
    plt.title(title)
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename)
    plt.close()
#enddef

def draw_hm_temp(m,a,b,t,dir):
    """
    563
    """
    m.resize((a,b))

    fig = plt.figure()
    mapable = plt.imshow(m, interpolation="nearest", cmap=pl.cm.spectral, alpha=0.9, aspect='auto')
    cbar = fig.colorbar(mapable)
    cbar.set_label("Aggregate Consumption")
    plt.xlabel("Half-Hour index")
    plt.ylabel("Daily index")
    plt.autoscale(tight=True)
    plt.title(t)

    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()

    plt.close()
    m.resize((1,a*b))
#enddef

def draw_plot_rgb(c,t,dir):
    """
    TODO: fix so that this can account for general cases like draw_plot

    plot heatmaps with colormapped matrix c and title t
    """

    print c.shape
    weeks, hf_hrs, tup = c.shape
    hhpd = hf_hrs/7
    day = ["Mon","Tue","Wed","Thr","Fri","Sat","Sun"]

    fig = plt.figure()
    plt.imshow(c, interpolation="nearest")
    plt.xlabel("x")
    plt.xticks([w * hhpd for w in range(0,7)], day)
    plt.ylabel("y")
    plt.autoscale(tight=True)
    plt.title(t)
    if dir is not None:
        plt.savefig(dir)
    else:
        plt.show()
        
    plt.close()
