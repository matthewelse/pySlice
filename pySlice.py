#!/usr/bin/python

"""
The MIT License (MIT)

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
from stl import Surface, Vertex, Normal


resolution = 0.1 # mms
scale = 10
model_file = 'models/yoda.stl'

f = open(model_file, 'rb')
stlobj = None

stlobj = Surface(f)

for result in stlobj.processfacets:
	pass

stats = stlobj.stats()
print(stats)

sub_vertex = Vertex(stats['extents']['x']['lower'], stats['extents']['y']['lower'], stats['extents']['z']['lower'])
add_vertex = Vertex(0.5,0.5,0.5)

for facet in stlobj.facets:
	facet.v[0] -= sub_vertex
	facet.v[1] -= sub_vertex
	facet.v[2] -= sub_vertex

	# The lines above have no effect on the normal.

	facet.v[0] = (facet.v[0] * scale) + add_vertex
	facet.v[1] = (facet.v[1] * scale) + add_vertex
	facet.v[2] = (facet.v[2] * scale) + add_vertex

	facet.v[0].integerise()
	facet.v[1].integerise()
	facet.v[2].integerise()

	# Recalculate the facet normal

	u = stlobj.facets[0].v[1] - stlobj.facets[0].v[0]
	v = stlobj.facets[0].v[2] - stlobj.facets[0].v[0]

	facet.n = Normal((u.y * v.z)-(u.z*v.y), (u.z*v.x)-(u.x*v.z), (u.x*v.y)-(u.y*v.x))

# So now, we have all of the points as integers...

interval = scale * resolution

targetz = 240

for facet in stlobj.facets:
    	
    if (facet.v[0].z > targetz and facet.v[1].z < targetz) or (facet.v[0].z < targetz and facet.v[1].z > targetz):
        # Calculate the coordinates of one segment at z = 240 (between v[0] and v[1])

    	A = (facet.v[0].x, facet.v[0].y, facet.v[0].z)
    	B = (facet.v[1].x, facet.v[1].y, facet.v[1].z)

    	# Find the vector between the two...

    	V = (float(B[0]-A[0]), float(B[1]-A[1]), float(B[2]-A[2]))

    	# Therefore the interpolated point = ('some n' * V)+A

    	# ( x )   
    	# ( y ) = n*V + A 
    	# (240)

    	refz = targetz - A[2]

    	# ( x  )
    	# ( y  ) = nV
    	# (refz)

    	n = float(refz/V[2])

    	coords = (n * V[0] + A[0], n * V[1] + A[1])

    	print coords

    elif (facet.v[0].z > targetz and facet.v[2].z < targetz) or (facet.v[0].z < targetz and facet.v[2].z > targetz):
        # Calculate the coordinates of one segment at z = 240 (between v[0] and v[2])

        A = (facet.v[0].x, facet.v[0].y, facet.v[0].z)
        B = (facet.v[2].x, facet.v[2].y, facet.v[2].z)

        # Find the vector between the two...

        V = (float(B[0]-A[0]), float(B[1]-A[1]), float(B[2]-A[2]))

        # Therefore the interpolated point = ('some n' * V)+A

        # ( x )   
        # ( y ) = n*V + A 
        # (240)

        refz = targetz - A[2]

        # ( x  )
        # ( y  ) = nV
        # (refz)

        n = float(refz/V[2])

        coords = (n * V[0] + A[0], n * V[1] + A[1])

        print coords

    elif (facet.v[1].z > targetz and facet.v[2].z < targetz) or (facet.v[1].z < targetz and facet.v[2].z > targetz):
        # Calculate the coordinates of one segment at z = 240 (between v[1] and v[2])

        A = (facet.v[1].x, facet.v[1].y, facet.v[1].z)
        B = (facet.v[2].x, facet.v[2].y, facet.v[2].z)

        # Find the vector between the two...

        V = (float(B[0]-A[0]), float(B[1]-A[1]), float(B[2]-A[2]))

        # Therefore the interpolated point = ('some n' * V)+A

        # ( x )   
        # ( y ) = n*V + A 
        # (240)

        refz = targetz - A[2]

        # ( x  )
        # ( y  ) = nV
        # (refz)

        n = float(refz/V[2])

        coords = (n * V[0] + A[0], n * V[1] + A[1])

        print coords
