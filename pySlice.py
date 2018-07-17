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
from sympy import Plane, Point3D, Line

import sys

#@profile
def slice_file(image_position_patient_array,
			   image_orientation_patient,
			   output_path=None,
			   input_path=None):
	print("Status: Loading File.")

	model = STLModel(input_path)
	stats = model.stats()

	print(stats)

	print("Status: Calculating Slices")

	v1 = Point3D(image_orientation_patient[0][0],
				 image_orientation_patient[0][1],
				 image_orientation_patient[0][2])
	v2 = Point3D(image_orientation_patient[1][0],
				 image_orientation_patient[1][1],
				 image_orientation_patient[1][2])
	org = Point3D(0, 0, 0) 
	
	for i, slice_loc in enumerate(image_position_patient_array):
		slice_loc = Point3D(slice_loc[0], slice_loc[1], slice_loc[2])

		dwg = Drawing(output_path + str(i) + '.svg', profile='tiny')
		plane = Plane(v1 + slice_loc,
					  v2 + slice_loc,
					  org + slice_loc)
		x_axis = Line(org + slice_loc, v1 + slice_loc)
		y_axis = Line(org + slice_loc, v2 + slice_loc)
		pairs = model.slice_at_plane(plane, x_axis, y_axis)
		for pair in pairs:
			dwg.add(dwg.line(pair[0], pair[1], stroke=rgb(0, 0, 0, "%")))
		dwg.save()

	print("Status: Finished Outputting Slices")
