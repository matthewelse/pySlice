from hashlib import md5
from struct import unpack
from math import fabs, sqrt

# This is the difference between points, below which we can consider them equal.
DIFFERENCE_LIMIT = 1e-7

class Vector3(object):
	'''Class for a 3D Cartesian Point'''

	def __init__(self, x, y, z):
		'''Creates a 3D Vector from the given coordinates'''
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)

		key_string = '(%f, %f, %f)' % (self.x, self.y, self.z)
		key_string = key_string.encode('utf-8')
		self.hash = md5(key_string).hexdigest()

	def __add__(self, other):
		'''Return the sum of the two points as a new Vector3'''
		return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		'''Return the difference between two points as a new Vector3'''
		return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

	def __str__(self):
		return '(%f, %f, %f)' % (self.x, self.y, self.z)

	def __eq__(self, other):
		if other == None:
			return False
		if (fabs(self.x - other.x) < DIFFERENCE_LIMIT and
			fabs(self.y - other.y) < DIFFERENCE_LIMIT and
			fabs(self.z - other.z) < DIFFERENCE_LIMIT):
			return True
		else:
			return False

	def __mul__(self, multi):
		return Vector3(self.x * multi, self.y * multi, self.z * multi)

	def length(self):
		'''Direct distance between point and the origin'''
		return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

	def cross(self, other):
		'''Calculate the cross product of self and other'''
		return Vector3(self.y*other.z-self.z*other.y,
						self.z*other.x-self.x*other.z,
						self.x*other.y-self.y*other.x)

class Normal(Vector3):
	'''Class for a 3D Normal Vector in Cartesian Space'''

	def __init__(self, dx, dy, dz):
		dx = float(dx)
		dy = float(dy)
		dz = float(dz)

		l = sqrt(dx*dx+dy*dy+dz*dz)

		if l == 0.0:
			raise ValueError("Length of Vector is 0")

		super(Normal, self).__init__(dx, dy, dz)

	def __str__(self):
		return 'Normal: (%f, %f, %f)' % (dx, dy, dz)

class Edge(object):
	'''Class representing the edge of a Facet, a line segment between two
	vertices.'''

	def __init__(self, start, end, f=None):
		'''Create the edge of a Facet.
		
		start, end -- points of the line segment
		f   -- facet that the line segment belongs to.'''
		assert isinstance(start, Vector3), "Start point of edge is not a Vertex"
		assert isinstance(end, Vector3), "End point of edge is not a Vertex"
		self.p = [start, end]
		self.refs = []
		if f:
			assert isinstance(f, Facet), "Reference is not a Facet."
			self.refs.append(f)

	def __eq__(self, other):
		'''If both self and other contain the same endpoints, they're equal,
		irrespective of the direction of the edge.'''
		assert isinstance(Edge, other), "Trying to compare a non-Edge."
		if self.p[0] == other.p[0] and self.p[1] == other.p[1]:
			return True
		if self.p[0] == other.p[1] and self.p[1] == other.p[0]:
			return True
		return False

	def __str__(self):
		s = 'Edge from ({}, {}, {}) to ({}, {}, {}) ({} refs)'
		return s.format(self.p[0].x, self.p[0].y, self.p[0].z, 
						self.p[1].x, self.p[1].y, self.p[1].z,
						len(self.refs))

	def fits(self, index, other):
		'''Checks if another Edge fits onto this one.

		index -- end of the Edge to test, either 1 (start) or 2 (end).
		other -- Edge to test.

		Returns a tuple of the new end edge and its free point.'''
		index = int(index)
		assert index < 0 or index > 2, "Index out of bounds"
		assert isinstance(Edge, other), "Trying to fit a non-Edge."
		if self.p[index-1] == other.p[0]:
			return (other, 1)
		if self.p[index-1] == other.p[1]:
			return (other, 2)
		return (self, index) # Doesn't fit

	def contains(self, point):
		'''Checks if a Vertex lies on the egde.

		point -- Vertex to test.

		Returns True if the point is on the Edge, false otherwise.'''
		d1 = self.p[1] - self.p[0]
		d2 = point - self.p[0]
		xp = d1.cross(d2)
		if xp.length() == 0.0 and (0.0 <= d2.length() <= 1.0):
			return True
		return False

	def addref(self, f):
		'''Add another Facet to the list of references.'''
		assert isinstance(f, Facet), "Reference is not a Facet."
		self.refs.append(f)

	def key(self):
		'''Return a unique key for the edge so we can put it in a
		dictionary. The key is derived from the keys of the Edge's
		Vertices.'''
		k1 = self.p[0].key()
		k2 = self.p[1].key()
		if k2 < k1:
			return k2+k1
		return k1+k2

class Triangle(object):
	'''Class to represent a triangle in 3D Space.'''

	def __init__(self, p1, p2, p3, norm):

		assert isinstance(p1, Vector3), "p1 is not a Vector3"
		assert isinstance(p2, Vector3), "p2 is not a Vector3"
		assert isinstance(p3, Vector3), "p3 is not a Vector3"

		if p1 == p2 or p1 == p3:
			raise ValueError("Degenerate Facet; Coincident Points")

		edge = Edge(p1, p2)
		if edge.contains(p3):
			raise ValueError("Degenerate Facet; Colinear Points")

		del edge

		self.vertices = [p1, p2, p3]

		if isinstance(norm, Normal):
			self.norm = norm
		else:
			d1 = p2 - p1
			d2 = p3 - p2
			xp = d1.cross(d2)
			self.norm = Normal(xp.x, xp.y, xp.z)

	def __str__(self):
		return 'Triangle: %s, %s, %s' % (self.vertices[0], self.vertices[1], self.vertices[2])

	#@profile
	def findInterpolatedPoint(self, A, B, targetz):
		# Find the vector between the two...

		V = (B[0]-A[0], B[1]-A[1], B[2]-A[2])

		# Therefore the interpolated point = ('some n' * V)+A

		# ( x )   
		# ( y ) = n*V + A 
		# (240)

		refz = targetz - A[2]

		# ( x  )
		# ( y  ) = nV
		# (refz)

		n = refz/V[2]

		coords = (n * V[0] + A[0], n * V[1] + A[1])

		return (coords)

	#@profile
	def find_interpolated_points_at_z(self, targetz):
		pair = []

		if (self.vertices[0].z > targetz and self.vertices[1].z < targetz) or (self.vertices[0].z < targetz and self.vertices[1].z > targetz):
			# Calculate the coordinates of one segment at z = targetz (between v[0] and v[1])

			A = (self.vertices[0].x, self.vertices[0].y, self.vertices[0].z)
			B = (self.vertices[1].x, self.vertices[1].y, self.vertices[1].z)

			pair.append(self.findInterpolatedPoint(A, B, targetz))

		if (self.vertices[0].z > targetz and self.vertices[2].z < targetz) or (self.vertices[0].z < targetz and self.vertices[2].z > targetz):
			# Calculate the coordinates of one segment at z = targetz (between v[0] and v[2])

			A = (self.vertices[0].x, self.vertices[0].y, self.vertices[0].z)
			B = (self.vertices[2].x, self.vertices[2].y, self.vertices[2].z)

			pair.append(self.findInterpolatedPoint(A, B, targetz))

		if (self.vertices[1].z > targetz and self.vertices[2].z < targetz) or (self.vertices[1].z < targetz and self.vertices[2].z > targetz):
			# Calculate the coordinates of one segment at z = targetz (between v[1] and v[2])

			A = (self.vertices[1].x, self.vertices[1].y, self.vertices[1].z)
			B = (self.vertices[2].x, self.vertices[2].y, self.vertices[2].z)

			pair.append(self.findInterpolatedPoint(A, B, targetz))

		if self.vertices[0].z == targetz:
			pair.append((self.vertices[0].x, self.vertices[0].y))
		elif self.vertices[1].z == targetz:
			pair.append((self.vertices[1].x, self.vertices[1].y))
		elif self.vertices[2].z == targetz:
			pair.append((self.vertices[2].x, self.vertices[2].y))

		return pair

class Model3D(object):
	'''Abstract Class to represent 3D objects. Cannot usually be used '''

	def __init__(self, f=None):
		'''Initialise the 3D object'''

		if f is None:
			raise ValueError("You must provide a file.")

		self.triangles = []
		self.vertices = {}
		self.normals = {}

		self.name = ""

		self.xmin = self.xmax = None
		self.ymin = self.ymax = None
		self.zmin = self.zmax = None

		# Not the means :D
		self.mx = self.my = self.mz = 0.0

	def __str__(self):
		return "3D Model: %s" % self.name

	def __len__(self):
		return len(self.triangles)

	def __iter__(self):
		for t in self.triangles:
			yield t

	def add_triangle(self, v1, v2, v3, norm):
		'''Add the specified vertices and possibly a normal vector into the
		object'''

		hash_1 = v1.hash

		if hash_1 not in self.vertices:
			self.vertices[hash_1] = v1

		hash_2 = v2.hash

		if hash_2 not in self.vertices:
			self.vertices[hash_2] = v2

		hash_3 = v3.hash

		if hash_3 not in self.vertices:
			self.vertices[hash_3] = v3

		triangle = Triangle(self.vertices[hash_1], 
							self.vertices[hash_2], 
							self.vertices[hash_3],
							norm)

		if not isinstance(norm, Normal):
			norm = triangle.norm

		normal_hash = norm.hash

		if normal_hash not in self.normals:
			self.normals[normal_hash] = norm
		else:
			triangle.norm = self.normals[normal_hash]

		self.triangles.append(triangle)
		self.update_extents(triangle)

	def extents(self):
		return ((self.xmin, self.xmax),
				(self.ymin, self.ymax),
				(self.zmin, self.zmax))

	def centre(self):
		return ((self.xmin+self.xmax)/2,
				(self.ymin+self.ymax)/2,
				(self.zmin+self.zmax)/2)

	def mean_point(self):
		c = 3 * len(self.triangles)
		return (self.mx/c, self.my/c, self.mz/c)

	def update_extents(self, triangle):
		'''Update the extents of the model, based on Triangle t'''

		if self.xmin == None:
			self.xmin = self.xmax = triangle.vertices[0].x
			self.ymin = self.ymax = triangle.vertices[0].y
			self.zmin = self.zmax = triangle.vertices[0].z

			self.mx = 0.0
			self.my = 0.0
			self.mz = 0.0

		self.mx += (triangle.vertices[0].x +
					triangle.vertices[1].x +
					triangle.vertices[2].x)
		self.my += (triangle.vertices[0].y +
					triangle.vertices[1].y +
					triangle.vertices[2].y)
		self.mz += (triangle.vertices[0].z +
					triangle.vertices[1].z +
					triangle.vertices[2].z)

		for vertex in triangle.vertices:
			if vertex.x < self.xmin:
				self.xmin = vertex.x
			elif vertex.x > self.xmax:
				self.xmax = vertex.x

			if vertex.y < self.ymin:
				self.ymin = vertex.y
			elif vertex.y > self.ymax:
				self.ymax = vertex.y

			if vertex.z < self.zmin:
				self.zmin = vertex.z
			elif vertex.z > self.zmax:
				self.zmax = vertex.z

	def stats(self):
		out = {
			'name': self.name,
			'facets': len(self.triangles),
			'vertices': len(self.vertices),
			'normals': len(self.normals),
			'extents': {
				'x': {
					'lower': self.xmin,
					'upper': self.xmax,
				},
				'y': {
					'lower': self.ymin,
					'upper': self.ymax,
				},
				'z': {
					'lower': self.zmin,
					'upper': self.zmax,
				}
			},
			'centre': self.centre(),
			'meanpoint': self.mean_point()
		}

		return out

	#@profile
	def slice_at_z(self, targetz):
		'''Function to slice the model at a certain z coordinate. Returns
		an array of tuples, describing the various lines between points.'''
		output = []

		for triangle in self.triangles:
			points = triangle.find_interpolated_points_at_z(targetz)

			if len(points) == 2:
				output.append((points[0], points[1]))

		return output

class STLModel(Model3D):

	def __init__(self, f=None):
		super(STLModel, self).__init__(f)

		contents = f.read()
		f.close()

		if contents.find(b"vertex", 80) == -1:
			# File is a binary STL file.
			self.process_bin(contents)
		else:
			self.process_text(contents)

	def process_bin(self, contents=None):
		self.name, num_facets_1 = unpack(b"=80sI", contents[:84])

		self.name = self.name.replace(b"solid", b"")
		self.name = self.name.strip(b'\x00 \t\n\r')

		if len(self.name) == 0:
			self.name = b"Unkown"

		contents = contents[84:]
		facetsz = len(contents)

		num_facets_2 = facetsz / 50

		if num_facets_1 != num_facets_2:
			raise ValueError("Incorrect number of facets.")

		items = [contents[n:n+50] for n in range(0, facetsz, 50)]
		del contents

		for i in items:
			nx, ny, nz, f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
				unpack(b"=ffffffffffffxx", i)
			v1 = Vector3(f1x, f1y, f1z)
			v2 = Vector3(f2x, f2y, f2z)
			v3 = Vector3(f3x, f3y, f3z)
			try:
				norm = Normal(nx, ny, nz)
			except ValueError:
				norm = None
			
			self.add_triangle(v1, v2, v3, norm)

	def process_text(self, contents=None):
		'''Process the contents of a text file as a generator.'''
		items = contents.split()
		del contents
		items = [s.strip() for s in items]
		try:
			sn = items.index("solid")+1
			en = items.index("facet")
		except:
			raise ValueError("Not an STL file.")
		if sn == en:
			self.name = "unknown"
		else:
			self.name = ' '.join(items[sn:en])
		nf1 = items.count('facet')
		del items[0:en]
		# Items now begins with "facet"
		while items[0] == "facet":
			v1 = Vector3(items[8], items[9], items[10])
			v2 = Vector3(items[12], items[13], items[14])
			v3 = Vector3(items[16], items[17], items[18])
			try:
				norm = Normal(items[2], items[3], items[4])
			except ValueError:
				norm = None
			
			self.add_triangle(v1, v2, v3, norm)
			del items[:21]
