"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app -p wx
"""

from setuptools import setup

APP = ['tccv3.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': False,
	  'packages':'wx',
          'site_packages':True,
	  'plist': {
		'CFBundleName':'TCC GUI',
		'CFBundleShortVersionString':'3.0',
		},
	   }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
