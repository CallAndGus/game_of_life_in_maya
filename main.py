import maya.cmds as cmds
from functools import partial

##########################
## Game logic functions ##
##########################

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
    for i in range ( int(start), int(stop) + 1 ):
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
    for i in range ( 0, numVerts + 1 ):
        graph.append( [] )
    # Fill graph with vertices
    for i in range ( int(start), int(stop) + 1 ):
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
    for i in range ( int(start), int(stop) + 1 ):
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
            #print 'Current Vertex: {0}'.format( i )
            #print 'Found Neighbor: {0}'.format( k )
            for j in graph[k]:
                cmds.select( '{0}.e[{1}]'.format( name, j ) )
                found = cmds.polyInfo( ev=True )
                tokens = found[0].split( ' ' )
                #print tokens
                current = -1
                # Skip over non-alphanumeric strings
                for t in tokens:
                    tmp = '{0}'.format( t )
                    if (tmp.isalnum() == True) and (tmp != 'EDGE') and (int(tmp) != k) and (int(tmp) != i):
                        current = int(tmp)
                #print 'Current: {0}'.format( current )
                # Find n's neighbors and compare with k's neighbors
                for n in neighbors[i]:
                    if (n == k) or (current == -1):
                        continue
                    #print 'n: {0}'.format( n )
                    for m in graph[n]:
                        cmds.select( '{0}.e[{1}]'.format( name, m ) )
                        found = cmds.polyInfo( ev=True )
                        tokens = found[0].split( ' ' )
                        # Skip over non-alphanumeric strings
                        for t in tokens:
                            tmp = '{0}'.format( t )
                            if (tmp.isalnum() == True) and (tmp != 'EDGE') and (int(tmp) != n):
                                #print 'Shared: ' + tmp
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

# Create and display menu system
def displayWindow():
    menu = cmds.window( title="Game Of Life Tool", iconName='GOLTool', widthHeight=(350, 400) )
    scrollLayout = cmds.scrollLayout( verticalScrollBarThickness=16 )
    cmds.flowLayout( columnSpacing=10 )
    cmds.columnLayout( cat=('both', 25), rs=10, cw=340 )
    cmds.text( l="\nThis is the \"Game of Life Tool\"! Use this tool to run Conway's Game of Life on a the surface of a selected polygonal object [input] given a starting seed pattern of selected vertices [selection]. A polygon object and seed vertices are needed.\n\n", ww=True, al="left" )
    cmds.text( l="To run:\n1) Select the reference vertices for the seed.\n2) Input the information in the fields below.\n3) Click \"Run\".", al="left" )
    cmds.text( label='Enter the time at which to start the animation:', al='left', ww=True )
    startTimeField = cmds.textField()
    cmds.text( label='Enter the time at which to end the animation:', al='left', ww=True )
    endTimeField = cmds.textField()
    cmds.text( label='Enter the step time (this affects the speed of the animation):', al='left', ww=True )
    stepTimeField = cmds.textField()
    cmds.button( label='Run', command=partial( startGame, menu, startTimeField, endTimeField, stepTimeField ) )
    cmds.text( l="\n", al='left' )
    cmds.showWindow( menu )

def startGame( menu, startTimeField, endTimeField, stepTimeField, *args ):
    # Grab user input
    seed = cmds.ls( selection=True )   
    if (len( seed ) == 0):
        print 'ERROR: Please load a seed pattern by selecting vertices on a (single) mesh.\n'
        # Delete menu window
        cmds.deleteUI( menu, window=True )
        displayWindow()
        return
    name = seed[0].split('.vtx')[0]
    startTime = cmds.textField(startTimeField, q=True, tx=True )
    if (startTime == ''):
        print 'ERROR: Please enter a starting time.\n'
        # Delete menu window
        cmds.deleteUI( menu, window=True )
        displayWindow()
        return
    endTime = cmds.textField(endTimeField, q=True, tx=True )
    if (endTime == ''):
        print 'ERROR: Please enter an ending time.\n'
        # Delete menu window
        cmds.deleteUI( menu, window=True )
        displayWindow()
        return
    stepTime = cmds.textField(stepTimeField, q=True, tx=True )
    if (stepTime == ''):
        print 'ERROR: Please enter a step time.\n'
        # Delete menu window
        cmds.deleteUI( menu, window=True )
        displayWindow()
        return
    # Delete menu window
    cmds.deleteUI( menu, window=True )
       
    # Initialize pixels for rendering
    cmds.select( name )
    
    # Extract vertices
    numVerts = cmds.polyEvaluate( v=True )
    mesh = ['{0}.vtx[{1}:{2}]'.format( name, 0, numVerts - 1 )]
    objGroup = 'objGroup'
    objMap = initLife(mesh, name, objGroup)
    
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
        
    cmds.xform( objMap[65][0], s=factorEmph )
    print '{0}: {1}'.format( 65, neighbors[65] )
    for i in neighbors[65]:
        cmds.xform( objMap[i][0], s=factorAlive )
        
    cmds.xform( objMap[211][0], s=factorEmph )
    print '{0}: {1}'.format( 211, neighbors[211] )
    for i in neighbors[211]:
        cmds.xform( objMap[i][0], s=factorAlive )
    
    # Load seed pattern

##########################
####### Run Script #######
##########################

# Display window
displayWindow()

