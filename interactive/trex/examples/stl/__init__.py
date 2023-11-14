# allow import of stl_path from same directory

try:
	from trex.examples.stl import stl_path

	import sys
	sys.modules['stl_path'] = stl_path
except Exception as e:
	pass
