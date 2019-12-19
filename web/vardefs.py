#!/usr/bin/env python

# Defining stuff
class variable(object):
	def __init__(self, name, units, level, addinfo=u''):
		self.name = name
		self.units = units
		self.level = level
		self.addinfo = addinfo

		#self.overlays = overlays

class plot(object):
	def __init__(self, prefix, shading, overlays=[], name=None):
		self.prefix = prefix
		self.shading = shading
		self.overlays = overlays
		
		if name:
			self.name = name
		elif self.shading.level:
			self.name = '%s on %s' % (self.shading.name, self.shading.level)
		else:
			self.name = self.shading.name

class overlay(object):
	def __init__(self, color, variable, contours):
		self.color = color
		self.var = variable
		if type(contours) == list:
			self.contours = ', '.join(map(str, contours))
		else:
			self.ci = contours
		


# Defining stuff
z500 = variable(u'Geopotential', u'gpdm', u'500 hPa')
t850 = variable(u'Temperature', u'°C', u'850 hPa')
def850 = variable(u'Deformation', '10⁻⁵/s', u'850 hPa')
ff10 = variable(u'10 m wind speed', 'm/s', u'')
tcwv = variable(u'Total column water vapour', 'kg/m²', u'')
lcc = variable(u'Low cloud cover', '', u'')
mcc = variable(u'Mid-level cloud cover', '', u'')
hcc = variable(u'High cloud cover', '', u'')
pvpt315 = variable(u'Potential vorticity', 'PVU', u'315 K')
pvpt330 = variable(u'Potential vorticity', 'PVU', u'330 K')
ptpv2 = variable(u'Potential temperature', 'K', u'PV 2')
sshff = variable(u'Surface sensible heat flux', u'W/m²', u'')
slhff = variable(u'Surface latent heat flux', u'W/m²', u'')
sthff = variable(u'Surface total heat flux', u'W/m²', u'')

tcwvp = variable(u'Total column water vapour percentiles', u'', u'', u'based on ERA-Interim 1979-2017')
tcwva = variable(u'Total column water vapour anomaly', u'', u'', u'based on ERA-Interim 1979-2017')
t850p = variable(u'Temperature percentiles', u'', u'850 hPa', u'based on ERA-Interim 1979-2017')
t850a = variable(u'Temperature anomaly', u'K', u'850 hPa', u'based on ERA-Interim 1979-2017')

msl = variable(u'Sea level pressure', 'hPa', u'')
cp = variable(u'Convective precipitation', 'mm/h', u'')
lp = variable(u'Large-scale precipitation', 'mm/h', u'')
tp = variable(u'Total precipitation', 'mm/h', u'')
sic = variable(u'Sea ice concentration', '', u'')
sst = variable(u'Sea surface temperature', '°C', u'')
frovo850 = variable(u'Frontal volumes', '', '850 hPa')
fronts850 = variable(u'Front lines', '', '850 hPa')
barbs850 = variable(u'Wind barbs', u'm/s', u'850 hPa')
barbs10 = variable(u'10 m Wind barbs', u'm/s', u'')
irbarbspt315 = variable(u'Irrot. wind barbs', u'm/s', u'315 K')
irbarbspt330 = variable(u'Irrot. wind barbs', u'm/s', u'330 K')
ffpv2 = variable(u'Wind speed', u'm/s', u'PV 2')
defang850 = variable(u'Axes of dilatation', u'', u'850 hPa')
icwvt = variable(u'Integrated column water vapour transport', u'', u'')
jetaxespv2 = variable(u'Jet axes', u'', u'PV 2')
uslope = variable(u'Average isentropic slope', u'm/km', '200-600 hPa')
lslope = variable(u'Average isentropic slope', u'm/km', '600-900 hPa')

# C'est le fin
