import maya.cmds as cmds

##########################
## Game logic functions ##
##########################

# Create and display menu system
def displayWindow():
    if( cmds.window( "Game Of Life Tool", exists=True ) ) :
        cmds.deleteUI( "Game Of Life Tool" )
    window = cmds.window( title="Game Of Life Tool", iconName='GOLTool', widthHeight=(200, 55) )
    cmds.columnLayout( adjustableColumn=True )
    cmds.button( label='Blank' )
    cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True )') )
    cmds.setParent( '..' )
    cmds.showWindow( window )

# Initialize groups of cubes that will be rendered
def initLife(mesh, name, id):
    group = cmds.group( em=True, n=id )
    start, stop = (mesh[0].split('.vtx')[1]).split(':')
    start = start.split('[')[1]
    stop = stop.split(']')[0]
    cmds.select( name )
    # Extract vertices
    numVerts = cmds.polyEvaluate( v=True )
    map = []
    for i in range ( 0, numVerts ):
        row = ''
        map.append( row )
    for i in range ( int(start), int(stop) ):
        # Find the coordinates of each vertex
        trans = cmds.pointPosition( '{0}.vtx[{1}]'.format( name, i ) )
        # Create a cube at each vertex
        obj = cmds.polyCube()
        map = createObjMap(map, i, obj)
        cmds.parent( obj, group )
        cmds.xform( obj, t=(trans[0], trans[1], trans[2]) )
    cmds.select( mesh )
    return map

# Scales an object group to a certain factor
def scaleObjGroup(objGroup, factor):
    children = cmds.listRelatives( objGroup, c=True )
    for obj in children:
        cmds.xform( obj, s=(factor[0], factor[1], factor[2]) )

# Create graph, V x E
def createGraph(mesh, name):
    start, stop = (mesh[0].split('.vtx')[1]).split(':')
    start = start.split('[')[1]
    stop = stop.split(']')[0]
    cmds.select( name )
    # Extract edges
    numEdges = cmds.polyEvaluate( e=True )
    # Extract vertices
    numVerts = cmds.polyEvaluate( v=True )
    # Initialize graph
    graph = []
    for i in range ( 0, numVerts ):
        graph.append( [] )
    # Fill graph with vertices
    for i in range ( int(start), int(stop) ):
        cmds.select( '{0}.vtx[{1}]'.format( name, i ) )
        found = cmds.polyInfo( ve=True )
        #print found
        tokens = found[0].split( ' ' )
        # Skip over non-alphanumeric strings
        for t in tokens:
            tmp = '{0}'.format( t )
            if (tmp.isalnum() == True) and (tmp != 'VERTEX'):
                # Add each alphanumeric string to the graph
                graph[i].append( int(tmp) )
    cmds.select( mesh )
    return graph

# Creates a map between vertex number (key) and object name (value)
def createObjMap(map, key, value):
    if map[key] == '':
        map[key] = value
    else:
        print( 'ERROR: map already has a value at the given key!' )
    return map

# Creates a 2D array listing all neighbors of a given index
def findNeighbors(graph, mesh, name):
    start, stop = (mesh[0].split('.vtx')[1]).split(':')
    start = start.split('[')[1]
    stop = stop.split(']')[0]
    # Initialize neighbors array
    neighbors = []
    for i in range ( 0, len( graph ) - 1 ):
        neighbors.append( [] )
    for i in range ( int(start), int(stop) ):
        # Find 1st level neighbors
        for j in graph[i]:
            cmds.select( '{0}.e[{1}]'.format( name, j ) )
            found = cmds.polyInfo( ev=True )
            tokens = found[0].split( ' ' )
            # Skip over non-alphanumeric strings
            for t in tokens:
                tmp = '{0}'.format( t )
                if (tmp.isalnum() == True) and (tmp != 'EDGE') and (int(tmp) != i):
                    neighbors[i].append( int(tmp) )
        # Find 2nd level neighbors
        add = []
        for k in neighbors[i]:
            print 'Current Vertex: {0}'.format( i )
            print 'Found Neighbor: {0}'.format( k )
            for j in graph[k]:
                cmds.select( '{0}.e[{1}]'.format( name, j ) )
                found = cmds.polyInfo( ev=True )
                tokens = found[0].split( ' ' )
                print tokens
                current = -1
                # Skip over non-alphanumeric strings
                for t in tokens:
                    tmp = '{0}'.format( t )
                    if (tmp.isalnum() == True) and (tmp != 'EDGE') and (int(tmp) != k) and (int(tmp) != i):
                        current = int(tmp)
                print 'Current: {0}'.format( current )
                # Find n's neighbors and compare with k's neighbors
                for n in neighbors[i]:
                    if (n == k) or (current == -1):
                        continue
                    print 'n: {0}'.format( n )
                    for m in graph[n]:
                        cmds.select( '{0}.e[{1}]'.format( name, m ) )
                        found = cmds.polyInfo( ev=True )
                        tokens = found[0].split( ' ' )
                        # Skip over non-alphanumeric strings
                        for t in tokens:
                            tmp = '{0}'.format( t )
                            if (tmp.isalnum() == True) and (tmp != 'EDGE') and (int(tmp) != n):
                                print 'Shared: ' + tmp
                                if (int(tmp) == current):
                                    add.append( int(tmp) )
        for a in add:
            if a in neighbors[i]:
                continue
            neighbors[i].append( a )
    cmds.select( mesh )
    return neighbors

##########################
### Main Functionality ###
##########################

# Display menu window
displayWindow()

# Store mesh variables
mesh = cmds.ls( selection=True )
name = mesh[0].split('.vtx')[0]

# Initialize pixels for rendering
objGroup = 'objGroup'
objMap = initLife(mesh, name, objGroup)
count = 0
for obj in objMap:
    print '{0}: {1}'.format( count, obj )
    count = count + 1

# Scale object matrix to 'dead' state
factorDead = (0.0, 0.0, 0.0)
factorAlive = (1.0, 1.0, 1.0)
factorEmph = (2.0, 2.0, 2.0)
scaleObjGroup(objGroup, factorDead)

# Transfer the selected vertices into a graph
graph = createGraph(mesh, name)

# Find neighbors for each vertex
neighbors = findNeighbors(graph, mesh, name)
cmds.xform( objMap[0][0], s=factorEmph )
print '{0}: {1}'.format( 0, neighbors[0] )
for i in neighbors[0]:
    cmds.xform( objMap[i][0], s=factorAlive )
    
cmds.xform( objMap[45][0], s=factorEmph )
print '{0}: {1}'.format( 45, neighbors[45] )
for i in neighbors[45]:
    cmds.xform( objMap[i][0], s=factorAlive )
    
cmds.xform( objMap[90][0], s=factorEmph )
print '{0}: {1}'.format( 90, neighbors[90] )
for i in neighbors[90]:
    cmds.xform( objMap[i][0], s=factorAlive )

count = 0
for g in graph:
    print '{0}: {1}'.format( count, g )
    count = count + 1

# Load seed pattern

