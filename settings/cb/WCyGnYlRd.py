#!/usr/bin/env python
# -*- encoding: utf-8

from matplotlib.colors import LinearSegmentedColormap
from numpy import nan, inf

cm_data = {'red': ((0.0, 1.0, 1.0),
		   (0.125, 0.4, 0.4),
		   (0.25, 0.1, 0.1),
		   (0.4, 0.9, 0.9),
		   (0.8, 1.0, 1.0),
		   (1.0, 0.5, 0.5)),

	 'green': ((0.0, 1.0, 1.0),
		   (0.1, 1.0, 1.0),
		   (0.25, 0.7, 0.7), 
		   (0.4, 0.9, 0.9),
		   (0.8, 0.1, 0.1),
		   (1.0, 0.1, 0.1)),

	 'blue':  ((0.0, 1.0, 1.0),
		   (0.1, 1.0, 1.0),
		   (0.25, 0.1, 0.1),
		   (0.4, 0.1, 0.1),
		   (0.8, 0.1, 0.1),
		   (1.0, 0.2, 0.2))
}

test_cm = LinearSegmentedColormap(__file__, cm_data)


if __name__ == "__main__":
	import matplotlib.pyplot as plt
	import numpy as np

	try:
		from pycam02ucs.cm.viscm import viscm
		viscm(test_cm)
	except ImportError:
		print("pycam02ucs not found, falling back on simple display")
		plt.imshow(np.linspace(0, 100, 256)[None, :], aspect='auto',
				   cmap=test_cm)
	plt.show()

# the end
