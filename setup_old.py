#! python

from distutils.core import setup, Extension

test_module = Extension('_bct30_wrap_compiled', sources=['bct30_wrap.cxx'],)

setup (name = 'test_module',
		version = '0.1',
		author = "Alex McMaster",
		)