#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from math import *

def print_help():
    print "Usage: " + sys.argv[0] + " <infile> <outfile>\n"
    
def fetch_line(f):
    s = [f.readline(), '']
    s[1] = s[0].strip()
    return s
    
def vec_sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])

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
	    print 'Successful parsing!'
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
	    #print state[1]
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
	    #print "skipped"
	    continue
	elif (state[1].startswith('}')):
	    if (len(brush) > 0):
		#print brush
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
outfile.write('Begin Map Name=' + fname + '\n' \
	    + '   Begin Level NAME=PersistentLevel\n')

# find brush vertices
index = 0
for b in brushes:
    outfile.write('      Begin Actor Class=Brush Name=Brush_' + str(index) + ' Archetype=Brush\'Engine.Default__Brush\'\n' \
		+ '         Begin Brush Name=Model_' + str(index) + '\n'                                                   \
		+ '            Begin PolyList\n')
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
		p = (detAx / detA, detAy / detA, detAz / detA)
		if (point_inside_brush(p, b) and not point_in_set(p, vertices)):
		    vertices.append(p)
    polygons = b
    a = 0
    for v in vertices:
	print a
	a = a + 1
	for p in b:
	    print str(v) + ' ' + str(p[0]) + ' ' + str(p[1]) + ' ' + str(abs(vec_dot(v, p[0]) - p[1]))
	    if (abs(vec_dot(v, p[0]) - p[1]) < 0.01):
		p.append(v)
		break
#    for p in b:
#	print "polygon " + str(p)
    outfile.write('            End PolyList\n' \
		+ '         End Brush\n' \
		+ '         Begin Object Class=BrushComponent Name=BrushComponent0 ObjName=BrushComponent_' + str(index) + ' Archetype=BrushComponent\'Engine.Default__Brush:BrushComponent0\'\n' \
		+ '            Brush=Model\'Model_' + str(index) + '\'\n' \
		+ '            ReplacementPrimitive=None\n' \
		+ '            LightingChannels=(bInitialized=True,Dynamic=True)\n' \
		+ '            Name="BrushComponent_' + str(index) + '"\n' \
		+ '            ObjectArchetype=BrushComponent\'Engine.Default__Brush:BrushComponent0\'\n' \
		+ '         End Object\n' \
		+ '         CsgOper=CSG_Add\n' \
		+ '         Brush=Model\'Model_' + str(index) + '\'\n' \
		+ '         BrushComponent=BrushComponent\'BrushComponent_' + str(index) + '\'\n' \
		+ '         Components(0)=BrushComponent\'BrushComponent_' + str(index) + '\'\n' \
		+ '         CreationTime=0.0\n' \
		+ '         Tag="Brush"\n' \
		+ '         CollisionComponent=BrushComponent\'BrushComponent_' + str(index) + '\'\n' \
		+ '         Name="Brush_' + str(index) + '"\n' \
		+ '         ObjectArchetype=Brush\'Engine.Default__Brush\'\n' \
		+ '      End Actor\n')
    index = index + 1

# finalize output
outfile.write('   End Level\n' \
	    + 'Begin Surface\n' \
	    + 'End Surface\n' \
	    + 'End Map\n')