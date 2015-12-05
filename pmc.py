from bct30 import bct30

from astropy import units as u
from astropy.coordinates import SkyCoord

class pmc():

	def __init__(self, conf_fn='tcc.conf'):
		self.bct = bct30()
		self.conf = self._read_conf(conf_fn)

	def slew(self, coords_dict):
		'''
		takes in a RA, DEC coordinates to prompt hardware to 			initiate a target slew
		arguments: coords_dict
		returns: slewing confirmation
		'''
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
		'''
		track_onoroff
		track_setrate
		track_status
		'''
		None
		#DB Does this mean tracking on or off?	

		# check soft limits in conf to stop tracking when alt < conf limit
		# find polar axis soft limit, RA, limit on non-setting stars
		# find declination wrap limit (RA +/- 10hrs)
		# call bct30 track
	
	def track_set(self,tracking=False):
		'''
		Sets tracking to be on or off
		arguments: tracking (Boolean)
		returns: confirmation of tracking preference
		'''
		None
	def track_setrate(self, RArate, DECrate):
		'''
		sets the individual tracking rates for RA and DEC
		arguments: RArate, DECrate
		returns: confirmation and set rates
		'''
		None
	def track_status(self)
		'''
		Displays status information for guider tracking
		arguments:
		returns:tracking status
		'''
		None 

	def focus(self,value=None):
		'''
		this takes in a focus value to focus the telescope
		arguments: value
		returns: focus completion status
		'''
		None

	def offset(self,RAjog=None,DECjog=None):
		'''
		alters the coordinates by an RA and DEC offset
		arguments: RAjog, DECjog
		returns: offset amount and confirmation
		'''
		# use Jog
		None

	def _read_conf(self, conf_fn):
		conf = dict()
		f = open(conf_fn, 'r')
		for line in f:
			a, b = line.split('\t')
			conf[a] = b
		return conf
