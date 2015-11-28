from bct30 import bct30

from astropy import units as u
from astropy.coordinates import SkyCoord

class pmc():

	def __init__(self, conf_fn='tcc.conf'):
		self.bct = bct30()
		self.conf = self._read_conf(conf_fn)

	def slew(self, coords_dict):
		coords = SkyCoord(ra=coords_dict['ra'],
				dec=coords_dict['dec'],
				frame='icrs',
				unit='deg')
		# check epoch
		# coords visible?
		# convert to alt, az
		# test against conf limits
		# call bct30 slew

	def track(self):
		None
		# check soft limits in conf to stop tracking when alt < conf limit
		# find polar axis soft limit, RA, limit on non-setting stars
		# find declination wrap limit (RA +/- 10hrs)
		# call bct30 track

	def focus(self):
		None

	def offset(self):
		# use Jog
		None

	def _read_conf(self, conf_fn):
		conf = dict()
		f = open(conf_fn, 'r')
		for line in f:
			a, b = line.split('\t')
			conf[a] = b
		return conf
