#!/usr/bin/env python

import codecs
from datetime import datetime as dt, timedelta as td
from jinja2 import FileSystemLoader, Environment

from settings.common import basepath
from current_fc import get_current_plotted_fc as get_ec_initdate
from current_fc_arome import get_current_plotted_fc_arome as get_no_initdate

from collections import namedtuple, OrderedDict
Conf = namedtuple('Conf', 'plotpath')
#conf = Conf(plotpath='/data/sci/devel/prj/iveret/web/plots')
conf = Conf(plotpath='/share/web/plots')


ec_leads = list(range(0,72,6))
ec_leads.extend(range(72,180,12))
ec_initdate = get_ec_initdate()
ec_fcdates = [ec_initdate + lead*td(0,3600) for lead in ec_leads]
#ec_fcdates = [ec_initdate + lead*td(0,3600) for lead in ec_leads[:3]]

no_initdate = get_no_initdate()
no_fcdates = [no_initdate + lead*td(0,3600) for lead in range(0,67,6)]
#no_fcdates = [no_initdate + lead*td(0,3600) for lead in range(0,7,3)]

no_arctic_initdate = no_initdate
no_arctic_fcdates = [no_initdate + lead*td(0,3600) for lead in range(0,67,6)]
#no_arctic_fcdates = [no_initdate + lead*td(0,3600) for lead in range(0,7,3)]

print('Creating loop based on')
print(' - EC forecasts from %s' % ec_initdate.strftime('%d.%m.%Y, %H UTC'))
print(' - AROME forecasts from %s' % no_initdate.strftime('%d.%m.%Y, %H UTC'))
print(' - AROME Arctic forecasts from %s' % no_arctic_initdate.strftime('%d.%m.%Y, %H UTC'))

file_fmt = '%Y%m%d%H'
display_fmt = '%a, %d %b %Y, %HZ'

publoop = OrderedDict([
	('ECMWF forecast 1/3: 500 hPa Geopotential and SLP', ('EC z500', 'ec_for_z500_msl', ec_initdate, ec_fcdates)),
	('ECMWF forecast 2/3: Total column water vapour, fluxes and precip.', ('EC tcwv', 'ec_for_tcwv', ec_initdate, ec_fcdates)),
	('ECMWF forecast 3/3: 850 hPa Temperature, SLP and wind barbs', ('EC t850', 'ec_for_t850_msl', ec_initdate, ec_fcdates)),
	('AROME forecast 1/2', ('AROME t2m', {
		'2m Temperature and SLP': 'no_for_full_t2m_msl',
		'2m Relative humidity and precipitation': 'no_for_full_rh2m_tp'},
			no_initdate, no_fcdates)),
	('AROME forecast 2/2', ('AROME ff10', {
		'10 m Wind speed and direction': 'no_for_full_ff10_wind',
		'2m Relative humidity and precipitation': 'no_for_full_rh2m_tp'}, 
			no_initdate, no_fcdates)),
	('AROME Arctic forecast 1/2', ('Arctic ff10', {
		'10 m Wind speed and direction': 'no_for_arctic_t2m_msl', 
		'2m Relative humidity and precipitation': 'no_for_arctic_rh2m_tp'}, 
			no_arctic_initdate, no_arctic_fcdates)),
	('AROME Arctic forecast 2/2', ('Arctic sfx', {
		'Surface fluxes, 10m winds, SSTs, and MIZ': 'no_for_arctic_shf_winds', 
		'2m Relative humidity and precipitation': 'no_for_arctic_rh2m_tp'}, 
			no_arctic_initdate, no_arctic_fcdates)),
])
units = {
		'ec_for_z500_msl': 'gpdm',
		'ec_for_tcwv': 'kg/m²',
		'ec_for_t850_msl': '°C',
		'no_for_full_t2m_msl': '°C',
		'no_for_full_rh2m_tp': 'mm/h',
		'no_for_full_ff10_wind': 'm/s',
		'no_for_arctic_t2m_msl': '°C',
		'no_for_arctic_rh2m_tp': 'mm/h',
		'no_for_arctic_shf_winds': 'W/m²',
}	

def mk_slide_panel(paneltitle, fileseg, init, valid):
	return {'paneltitle': paneltitle, 
		'fname': '%s_from_%s_for_%s.png' % (fileseg, init.strftime(file_fmt), valid.strftime(file_fmt)),
		'cbar': 'cbar_%s.png' % fileseg,
		'units': units[fileseg],
	}

def mk_slide_singlepanel(fileseg, init, valid):
	return {'panels': [mk_slide_panel(None, fileseg, init, valid)],
		'init': init.strftime(display_fmt),
		'valid': valid.strftime(display_fmt),
		'lead': (valid-init).total_seconds()//3600,
	}

def mk_slide_multipanel(filesegs, init, valid):
	return {'panels': [mk_slide_panel(paneltitle, fileseg, init, valid) for paneltitle, fileseg in filesegs.items()],
		'init': init.strftime(display_fmt),
		'valid': valid.strftime(display_fmt),
		'lead': (valid-init).total_seconds()//3600,
	}

def mk_chapter(idx, title, brief, size_fraction):
	return {'idx': idx, 'title': title, 'brief': brief, 'width': float(size_fraction)}

slides = []
chapters = []
curidx = 0
for title, (brief, fileseg, init, valids) in publoop.items():
	chapters.append(mk_chapter(curidx, title, brief, len(valids)))
	if type(fileseg) == str:
		for valid in valids:
			slides.append(mk_slide_singlepanel(fileseg, init, valid))
	elif type(fileseg) == dict:
		for valid in valids:
			slides.append(mk_slide_multipanel(fileseg, init, valid))
	else:
		raise ValueError('fileseg values must be either str or dict, got %s' % type(fileseg))
	
	curidx += len(valids)

print('Total %d slides' % curidx)
for chapter in chapters:
	chapter['width'] = (chapter['width']*10000//curidx)/100 # floor to 2 decimal places

# Where to save the weather map; 
filepath = conf.plotpath+'/../publoop.html'

env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web'))

t = env.get_template('template_publoop.html')
c = {
	'chapters': chapters, 
	'slides': slides,
	'firsttitle': chapters[0]['title'],
	'first': slides[0],
	'fstpanel': slides[0]['panels'][0],
	'sndpanel': slides[0]['panels'][1] if len(slides[0]['panels']) > 1 else None,
	'plotdir': 'http://iveret.gfi.uib.no/plots',
}

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(**c))
f.close()


# C'est le fin
