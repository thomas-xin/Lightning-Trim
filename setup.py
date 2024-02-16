from distutils.core import setup
import py2exe

setup(
	options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
	console = [{'script': 'lightning.py'}],
	requires = ["easygui", "subprocess", "os", "sys", "ast"],
	packages = [],
	zipfile = None,
)