"""
Example of creating a radar chart (a.k.a. a spider or star chart) [1]_.

Although this example allows a frame of either 'circle' or 'polygon', polygon
frames don't have proper gridlines (the lines are circles instead of polygons).
It's possible to get a polygon grid by setting GRIDLINE_INTERPOLATION_STEPS in
matplotlib.axis to the desired number of vertices, but the orientation of the
polygon is not aligned with the radial axes.

.. [1] http://en.wikipedia.org/wiki/Radar_chart
"""
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

from parser import parse_h5f, parse_type
from aggregator import sum_rows, convert_to_matrix
from diffp import compute_deltas, add_noise_simple, eps_prime, lap_sample


def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts

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

def create_dp(week, delta, N, eps):
    week.resize((336,))
    weekarr = []
    weekdeltaarr = []

    for i in range(0,7):
        k = 0
        dayarr = []
        deltaarr = []
        temp = 0
        tempd = 0
        for j in range(0,48):
            temp = temp + week[48*i + j]
            tempd = tempd + delta[48*i + j]
            if k%(48/N) == (48/N - 1):
                dayarr.append(temp)
                deltaarr.append(tempd)
                k = 0
                temp = 0
                tempd = 0
            else:
                k = k + 1
        #endfor
        weekarr.append(dayarr)
        weekdeltaarr.append(deltaarr)
    #endfor
    wk = np.array(weekarr)
    wk_d = np.array(weekdeltaarr)
    wk_d.resize((7*N,))
    wk_noisy, noises = add_noise_simple(wk, eps, wk_d)
    print eps_prime(7*N, 0.000001, eps)

    return wk_noisy
#enddef

def compute_max_mins(week, delta, N, eps):
    week.resize((336,))
    weekarr = []

    for i in range(0,7):
        k = 0
        dayarr = []
        temp = 0
        for j in range(0,48):
            temp = temp + week[48*i + j]
            if k%(48/N) == (48/N - 1):
                dayarr.append(temp)
                k = 0
                temp = 0
            else:
                k = k + 1
        #endfor
        weekarr.append(dayarr)
    #endfor

    dparr = create_dp(week, delta, N, eps)
    data = [
        ('raw', weekarr),
        ('DP', dparr)
        ]

    return data 
#enddef

if __name__ == '__main__':
    N = 6
    eps = 0.023
    xmas_week, xmas_delta = import_from_credc(22,23)
    data = compute_max_mins(xmas_week, xmas_delta, N, eps)

    theta = radar_factory(N, frame='polygon')

    spoke_labels = ['0', '4', '8', '12', '16', '20']

    fig = plt.figure(figsize=(9, 9))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    # Plot the four cases from the example data on separate axes
    for n, (title, case_data) in enumerate(data):
        ax = fig.add_subplot(2, 2, n + 1, projection='radar')
        #plt.rgrids([500, 1000, 2000, 3000, 4000, 5000])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        for d, color in zip(case_data, colors):
            ax.plot(theta, d, color=color)
            ax.fill(theta, d, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    N = 8
    eps = 0.023
    xmas_week, xmas_delta = import_from_credc(22,23)
    data = compute_max_mins(xmas_week, xmas_delta, N, eps)

    theta = radar_factory(N, frame='polygon')

    spoke_labels = ['0', '3', '6', '9', '12','15', '18', '21']
    for n, (title, case_data) in enumerate(data):
        ax = fig.add_subplot(2, 2, n + 3, projection='radar')
        #plt.rgrids([500, 1000, 2000, 3000, 4000, 5000])
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                     horizontalalignment='center', verticalalignment='center')
        for d, color in zip(case_data, colors):
            ax.plot(theta, d, color=color)
            ax.fill(theta, d, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)    

    # add legend relative to top-left plot
    plt.subplot(2, 2, 1)
    labels = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    legend = plt.legend(labels, loc=(1.3, 0.85), labelspacing=0.1)
    plt.setp(legend.get_texts(), fontsize='small')

    plt.figtext(0.5, 0.965, 'radar_chart',
                ha='center', color='black', weight='bold', size='large')

    plt.show()
    plt.close()
