#!/usr/bin/python

"""
The MIT License (MIT)

pySlice.py
Copyright (c) 2013 Matthew Else

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from Model3D import STLModel, Vector3, Normal
from svgwrite import Drawing, rgb
import sys, os
import numpy as np

#@profile
def slice_file(f=None, resolution=0.1):
	print("Status: Loading File.")

	model = STLModel(f)
	scale = 10
	stats = model.stats()

	sub_vertex = Vector3(stats['extents']['x']['lower'], stats['extents']['y']['lower'], stats['extents']['z']['lower'])
	add_vertex = Vector3(0.5,0.5,0.5)

	model.xmin = model.xmax = None
	model.ymin = model.ymax = None
	model.zmin = model.zmax = None

	print("Status: Scaling Triangles.")

	for triangle in model.triangles:
		triangle.vertices[0] -= sub_vertex
		triangle.vertices[1] -= sub_vertex
		triangle.vertices[2] -= sub_vertex

		# The lines above have no effect on the normal.

		triangle.vertices[0] = (triangle.vertices[0] * scale) + add_vertex
		triangle.vertices[1] = (triangle.vertices[1] * scale) + add_vertex
		triangle.vertices[2] = (triangle.vertices[2] * scale) + add_vertex

		# Recalculate the triangle normal

		u = model.triangles[0].vertices[1] - model.triangles[0].vertices[0]
		v = model.triangles[0].vertices[2] - model.triangles[0].vertices[0]

		triangle.n = Normal((u.y * v.z)-(u.z*v.y), (u.z*v.x)-(u.x*v.z), (u.x*v.y)-(u.y*v.x))
		model.update_extents(triangle)

	print("Status: Calculating Slices")

	interval = scale * resolution
	stats = model.stats()
	print(stats)

	for index, targetz in enumerate(np.arange(0, stats['extents']['z']['upper'], interval)):
		dwg = Drawing('outputs/svg/'+str(index)+'.svg', profile='tiny')
		pairs = model.slice_at_z(targetz)
		for pair in pairs:
			dwg.add(dwg.line(pair[0], pair[1], stroke=rgb(0, 0, 0, "%")))
		dwg.save()

	print("Status: Finished Outputting Slices")


if __name__ == '__main__':
	# Run as a command line program.

	import argparse
	parser = argparse.ArgumentParser(
						description='Takes a 3D Model, and slices it at regular intervals')
	parser.add_argument('file',
						metavar='FILE',
						help='File to be sliced',
						nargs='?',
						default='models/yoda.stl',
						type=argparse.FileType('rb'))
	parser.add_argument('-r', '--resolution', type=float,
						default=0.01,
						help='The Z-Axis resolution of the printer, in mms')
	parser.add_argument('-d', '--dirs', type=str,
						default='./outputs/svg',
						help='The path to the output directory')
	args = parser.parse_args()
 
	if not os.path.exists(args.dirs):
		os.makedirs(args.dirs)
	slice_file(args.file, args.resolution)
