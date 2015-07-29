#!/usr/bin/env python
# -*- encoding: utf-8

from reverse import reverse_cm
from matplotlib.colors import LinearSegmentedColormap
from numpy import nan, inf

cm_data = {'red':   ((0.0, 0.0, 0.0), (1.0, 0.8, 0.8)),
	   'green': ((0.0, 0.0, 0.0), (1.0, 0.5, 0.5)),
	   'blue':  ((0.0, 0.0, 0.0), (1.0, 0.2, 0.2))  }

KOr = LinearSegmentedColormap(__file__, cm_data)
KOr_r = LinearSegmentedColormap(__file__, reverse_cm(cm_data))

# Make a clean "from <colormap> import *"
__all__ = ['KOr', 'KOr_r']

# For use with viscm
test_cm = KOr

# the end
