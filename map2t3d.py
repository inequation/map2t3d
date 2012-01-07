#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from math import *

def print_help():
	print("Usage: %s <infile> <outfile>\n" % sys.argv[0])
	
def fetch_line(f):
	s = [f.readline(), '']
	s[1] = s[0].strip()
	return s
	
def vec_add(v1, v2):
	return (v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2])
	
def vec_sub(v1, v2):
	return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])
	
def vec_mult(v, s):
	return (v[0] * s, v[1] * s, v[2] * s)
	
def vec_div(v, s):
	return (v[0] / s, v[1] / s, v[2] / s)

def vec_cross(v1, v2):
	return (v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0])

def vec_dot(v1, v2):
	return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def vec_length_squared(v):
	return vec_dot(v, v)

def vec_length(v):
	return sqrt(vec_length_squared(v))
	
def vec_normalize(v):
	l = 1.0 / vec_length(v)
	return (v[0] * l, v[1] * l, v[2] * l)

def point_inside_brush(point, brush):
	for p in brush:
		if (vec_dot(point, p[0]) - p[1] >= 0):
			return True
	return False
	
def point_in_set(point, vertices):
	for p in vertices:
		if (vec_length(vec_sub(p, point)) < 0.01):
			return True
	return False

def get_tangent_binormal(normal):
	# work around silly python limitations
	b = [normal[0], normal[1], normal[2]]
	maxc = 0
	minc = 0
	# find the largest and smallest (by magnitude) components of the vector
	for i in range(1, len(b)):
		if (abs(b[i]) > abs(b[maxc])):
			maxc = i
		elif (abs(b[i]) < abs(b[minc])):
			minc = i
	# set the max and min elements to exaggerated values to get a vector that
	# stands a chance to be perpendicular to the normal
	b[minc] = 1.0
	b[maxc] = 0.0
	binormal = (b[0], b[1], b[2])
	# perpendicularize it!
	dot = vec_dot(binormal, normal)
	if (abs(dot) > 0.01):
		binormal = vec_normalize(vec_sub(binormal, vec_mult(normal, dot)))
	# find a vector perpendicular to the other two
	tangent = vec_normalize(vec_cross(binormal, normal))
	# cross again to ensure perpendicularity
	binormal = vec_normalize(vec_cross(normal, tangent))
	return [tangent, binormal]
	
# =============================================================================

if (len(sys.argv) != 3):
	print_help()
	exit()

# load brushwork from the .map file
infile = open(sys.argv[1], 'r')
depth = int(0)
state = ["foo", ""]
brush = []
brushes = []
while (state[0] != ''):
	state = fetch_line(infile)
	# skip comment lines
	if (state[1].startswith('//')):
		continue
	#print str(depth) + ": " + state[1]
	if (depth == 0):
		# global level
		if (state[1].startswith('{')):
			depth = depth + 1
			continue
		elif (state[1].startswith('}')):
			print('Successful parsing!')
			exit()
	elif (depth == 1):
		# entity level
		if (state[1].startswith('{')):
			depth = depth + 1
			# clear the brush
			brush = []
			continue
		elif (state[1].startswith('}')):
			depth = depth - 1
			continue
		elif (state[1].startswith('\"')):
			continue
	elif (depth == 2):
		# brush level
		if (state[1].lower().startswith('terraindef') or state[1].lower().startswith('patchdef')):
			# skip the entire block
			while (not state[1].startswith('{')):
				state = fetch_line(infile)
			skipdepth = 1
			while (skipdepth > 0):
				state = fetch_line(infile)
				if (state[1].startswith('{')):
					skipdepth = skipdepth + 1
				elif (state[1].startswith('}')):
					skipdepth = skipdepth - 1
				if (skipdepth == 0):
					break
			continue
		elif (state[1].startswith('}')):
			if (len(brush) > 0):
				brushes.append(brush)
			depth = depth - 1
			continue
		elif (state[1].startswith('(')):
			# brush definition starts
			tokens = state[1].split()
			# plane points
			p1 = (float(tokens[1]), float(tokens[2]), float(tokens[3]))
			p2 = (float(tokens[6]), float(tokens[7]), float(tokens[8]))
			p3 = (float(tokens[11]), float(tokens[12]), float(tokens[13]))
			# calculate plane
			v1 = vec_sub(p2, p1)
			v2 = vec_sub(p2, p3)
			normal = vec_normalize(vec_cross(v1, v2))
			plane = [normal, vec_dot(p1, normal)]
			brush.append(plane)

# start the output
outfile = open(sys.argv[2], 'w')
fname = sys.argv[1][sys.argv[1].rfind('/') + 1 : len(sys.argv[1])]
dot = fname.rfind('.')
if (dot >= 0):
	fname = fname[0 : dot]
outfile.write('Begin Map Name=' + fname + '\r\n' \
		+ '   Begin Level NAME=PersistentLevel\r\n')

# find brush vertices
index = 0
for b in brushes:
	outfile.write('	  Begin Actor Class=Brush Name=Brush_' + str(index + 1) + ' Archetype=Brush\'Engine.Default__Brush\'\r\n' \
		+ '		 Begin Object Class=BrushComponent Name=BrushComponent0 ObjName=BrushComponent_' + str(index) + ' Archetype=BrushComponent\'Engine.Default__Brush:BrushComponent0\'\r\n' \
		+ '			Brush=Model\'Model_' + str(index) + '\'\r\n' \
		+ '			ReplacementPrimitive=None\r\n' \
		+ '			LightingChannels=(bInitialized=True,Dynamic=True)\r\n' \
		+ '			Name="BrushComponent_' + str(index) + '"\r\n' \
		+ '			ObjectArchetype=BrushComponent\'Engine.Default__Brush:BrushComponent0\'\r\n' \
		+ '		 End Object\r\n' \
		+ '		 CsgOper=CSG_Add\r\n' \
		+ '		 Begin Brush Name=Model_' + str(index) + '\r\n' \
		+ '			Begin PolyList\r\n')
	# calculate the vertex set
	vertices = []
	for i in range(len(b) - 2):
		for j in range(1, len(b) - 1):
			for k in range(2, len(b)):
				# solve with Cramer for intersection point (i.e. vertex)
				if (i == j or j == k or i == k):
					continue
				detA = b[i][0][0] * b[j][0][1] * b[k][0][2] + b[i][0][1] * b[j][0][2] * b[k][0][0] \
					+ b[i][0][2] * b[j][0][0] * b[k][0][1] - b[i][0][0] * b[j][0][2] * b[k][0][1]  \
					- b[i][0][1] * b[j][0][0] * b[k][0][2] - b[i][0][2] * b[j][0][1] * b[k][0][0]
				if (abs(detA) < 0.001):
					continue
				detAx = b[i][1] * b[j][0][1] * b[k][0][2] + b[i][0][1] * b[j][0][2] * b[k][1] \
					+ b[i][0][2] * b[j][1] * b[k][0][1] - b[i][1] * b[j][0][2] * b[k][0][1]   \
					- b[i][0][1] * b[j][1] * b[k][0][2] - b[i][0][2] * b[j][0][1] * b[k][1]
				detAy = b[i][0][0] * b[j][1] * b[k][0][2] + b[i][1] * b[j][0][2] * b[k][0][0] \
					+ b[i][0][2] * b[j][0][0] * b[k][1] - b[i][0][0] * b[j][0][2] * b[k][1]   \
					- b[i][1] * b[j][0][0] * b[k][0][2] - b[i][0][2] * b[j][1] * b[k][0][0]
				detAz = b[i][0][0] * b[j][0][1] * b[k][1] + b[i][0][1] * b[j][1] * b[k][0][0] \
					+ b[i][1] * b[j][0][0] * b[k][0][1] - b[i][0][0] * b[j][1] * b[k][0][1]   \
					- b[i][0][1] * b[j][0][0] * b[k][1] - b[i][1] * b[j][0][1] * b[k][0][0]
				p = vec_div((detAx, detAy, detAz), detA)
				if (point_inside_brush(p, b) and not point_in_set(p, vertices)):
					vertices.append(p)
		
	for p in b:
		outfile.write('			   Begin Polygon Flags=3584\r\n')
		writtenFirst = False
		# UDK requires the the vertex sequences to be clockwise, or it doesn't
		# create the polygon
		relevant = []
		# find the polygon centre
		centre = (float(0), float(0), float(0))
		# find vertices lying on the current plane
		for v in vertices:
			if (abs(vec_dot(v, p[0]) - p[1]) < 0.01):
				centre = vec_add(centre, v)
				relevant.append(v)
		centre = vec_div(centre, len(relevant))
		# sort by angle (ensures clockwiseness)
		tb = get_tangent_binormal(p[0])
		def get_angle_key(v):
			r = vec_sub(v, centre)
			x = vec_dot(r, tb[0])
			y = vec_dot(r, tb[1])
			return atan2(y, x)
		relevant.sort(None, get_angle_key)
		# finally, dump the vertices to file
		for v in relevant:
			if (not writtenFirst):
				outfile.write('				  Origin   %(ox)0+13.6f,%(oy)0+13.6f,%(oz)0+13.6f\r\n' \
					% {'ox' : v[0], 'oy' : v[1], 'oz' : v[2]} \
							+ '				  Normal   %(nx)0+13.6f,%(ny)0+13.6f,%(nz)0+13.6f\r\n' \
					% {'nx' : p[0][0], 'ny': p[0][1], 'nz': p[0][2]} \
							+ '				  TextureU +00001.000000,+00000.000000,+00000.000000\r\n' \
							+ '				  TextureV +00000.000000,+00001.000000,+00000.000000\r\n')
				writtenFirst = True
			outfile.write('				  Vertex   %(x)0+13.6f,%(y)0+13.6f,%(z)0+13.6f\r\n' % {'x' : v[0], 'y': v[1], 'z': v[2]})
		# finalize polygon
		outfile.write('			   End Polygon\r\n')
	# finalize brush
	outfile.write('			End PolyList\r\n' \
				+ '		 End Brush\r\n' \
				+ '		 Brush=Model\'Model_' + str(index) + '\'\r\n' \
				+ '		 BrushComponent=BrushComponent\'BrushComponent_' + str(index) + '\'\r\n' \
				+ '		 Components(0)=BrushComponent\'BrushComponent_' + str(index) + '\'\r\n' \
				+ '		 CreationTime=12.345678\r\n' \
				+ '		 Tag="Brush"\r\n' \
				+ '		 CollisionComponent=BrushComponent\'BrushComponent_' + str(index) + '\'\r\n' \
				+ '		 Name="Brush_' + str(index + 1) + '"\r\n' \
				+ '		 ObjectArchetype=Brush\'Engine.Default__Brush\'\r\n' \
				+ '	  End Actor\r\n')
	index = index + 1

# finalize output
outfile.write('   End Level\r\n' \
			+ 'Begin Surface\r\n' \
			+ 'End Surface\r\n' \
			+ 'End Map\r\n')