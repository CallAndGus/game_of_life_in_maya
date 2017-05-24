import maya.cmds as cmds
import maya.OpenMaya as om
import numpy as np
print np.__version__
from functools import partial

##########################
## Game logic functions ##
##########################

# Initialize groups of cubes that will be rendered
def initLife(mesh, name, id, neighbors):
    print 'Initializing objects...'
    group = cmds.group( em=True, n=id )
    jointGroup = cmds.group( em=True, n='jointGroup' )
    cmds.select( name )
    # Extract vertices
    numVerts = cmds.polyEvaluate( v=True )
    map = []
    for i in range ( 0, numVerts ):
        row = ''
        map.append( row )
    for i in range ( 0, numVerts ):
        # Find the coordinates of each vertex
        trans = cmds.pointPosition( '{0}.vtx[{1}]'.format( name, i ) )
        currVector = om.MVector( trans[0], trans[1], trans[2] )
        currVector.normalize()
        neighborVectors = []
        # Find the vectors from each vertex to each neighbor
        for n in neighbors[i]:
            if i == 0:
                print '{0}: {1}'.format( i, n )
            vector = om.MVector()
            coord = cmds.pointPosition( '{0}.vtx[{1}]'.format( name, n ) )
            vector.x = coord[0] - trans[0]
            vector.y = coord[1] - trans[1]
            vector.z = coord[2] - trans[2]
            neighborVectors.append( vector )
        # Find the normal
        normVector = om.MVector( 0, 0, 0 )
        for vector in neighborVectors:
            normVector = normVector + vector
        normVector.normalize()
        normVector.x = trans[0] - normVector.x
        normVector.y = trans[1] - normVector.y
        normVector.z = trans[2] - normVector.z
        normVector.normalize()
        # Create joint in order to test the calculated normal
        newJoint = cmds.joint()
        cmds.parent( newJoint, jointGroup )
        cmds.xform( newJoint, t=(trans[0] + normVector.x, trans[1] + normVector.y, trans[2] + normVector.z) )
        # Create an object and add to the group
        obj = cmds.polyCone()
        map = createObjMap(map, i, obj)
        cmds.parent( obj[0], group )
        # Rotate the object so the y-axis aligns with the normal
        epsilon = 0.001
        delta = 0.05
        x = 0.0
        y = 0.0
        z = 0.0
        xRot = om.MEulerRotation(np.deg2rad(delta), 0.0, 0.0)
        zRot = om.MEulerRotation(0.0, 0.0, np.deg2rad(delta))
        # Setup planes to compare against
        xCross = normVector ^ om.MVector( 1.0, 0.0, 0.0 )
        zCross = normVector ^ om.MVector( 0.0, 0.0, 1.0 )
        # Initialize comparison vectors
        xDot = currVector * xCross
        zDot = currVector * zCross
        # X-axis match rotation
        while (xDot < -epsilon) or (xDot > epsilon):
            currVector = currVector.rotateBy( xRot )
            x = x + delta
            #print 'Norm: {0}, {1}, {2}'.format( normVector.x, normVector.y, normVector.z )
            #print 'X Transformed: {0}, {1}, {2}'.format( currVector.x, currVector.y, currVector.z )
            xDot = currVector * xCross
            #print 'x = {0}, dot = {1}'.format( x, xDot )
        # Z-axis match rotation
        while (zDot < -epsilon) or (zDot > epsilon):
            currVector = currVector.rotateBy( zRot )
            z = z + delta
            #print 'Norm: {0}, {1}, {2}'.format( normVector.x, normVector.y, normVector.z )
            #print 'Z Transformed: {0}, {1}, {2}'.format( currVector.x, currVector.y, currVector.z )
            zDot = currVector * zCross
            #print 'z = {0}, dot = {1}'.format( z, zDot )
        # Correct z-axis reflections
        if normVector.z < 0:
            if currVector.z > 0:
                currVector.z = -currVector.z
                z = z + 180
        else:
            if currVector.z < 0:
                currVector.z = -currVector.z
                z = z + 180
        # Correct y-axis reflections
        if normVector.y < 0:
            if currVector.y > 0:
                currVector.y = -currVector.y
                y = 180
        else:
            if currVector.y < 0:
                currVector.y = -currVector.y
                y = 180
                # Correct x-axis reflections
        if normVector.x < 0:
            if currVector.x > 0:
                currVector.x = -currVector.x
                x = x + 180
        else:
            if currVector.x < 0:
                currVector.x = -currVector.x
                x = x + 180
        print '{0} ...'.format( i )
        print 'Norm: {0}, {1}, {2}'.format( normVector.x, normVector.y, normVector.z )
        print 'Transformed: {0}, {1}, {2}'.format( currVector.x, currVector.y, currVector.z )
        print 'x = {0}, y = {1}, z = {2}'.format( x, y, z )
        # Perform rotation
        cmds.xform( obj, r=True, ro=(x, y, z) )
        # Translate object to vertex
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
    print 'Creating graph...'
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
    for i in range ( 0, numVerts ):
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
    print 'Finding neighbors...'
    # Initialize neighbors array
    neighbors = []
    cmds.select( name )
    # Extract vertices
    numVerts = cmds.polyEvaluate( v=True )
    for i in range ( 0, numVerts ):
        neighbors.append( [] )
    for i in range ( 0, numVerts ):
        print '... pass {0} out of {1}'.format( i, numVerts - 1 )
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

# Create and initialize a matrix used for rendering
def createMatrix(name, factor):
    cmds.select( name )
    # Extract vertices
    numVerts = cmds.polyEvaluate( v=True )
    matrix = []
    for i in range ( 0, numVerts ):
        matrix.append( factor )
    return matrix

# Loads the list of vertices into a matrix
def loadPattern(matrix, pattern, factor):
    for i in range ( 0, len( matrix ) ):
        if i in pattern:
            matrix[i] = factor
    return matrix

# Breaks the initial seed selection into a list of vertices
def enumerateSeed(seed):
    pattern = []
    count = 0
    for s in seed:
        if ':' not in seed[count].split('.vtx')[1]:
            start = seed[count].split('.vtx')[1]
            start = start.split('[')[1]
            start = start.split(']')[0]
            stop = ''
        else:
            start, stop = (seed[count].split('.vtx')[1]).split(':')
            start = start.split('[')[1]
            stop = stop.split(']')[0]
        if start != '' and stop != '':
            for i in range ( int(start), int(stop) + 1 ):
                pattern.append( i )
        elif start != '':
            pattern.append( int(start) )
        elif stop != '':
            pattern.append( int(stop) )
        count = count + 1
    return pattern

# Render the found matrix transforms
def renderLife(objMap, curr, next, stepTime):
    i = 0
    if stepTime < 2:
        for obj in objMap:
            cmds.setAttr( '{0}.scaleX'.format( obj[0] ), next[i][0] )
            cmds.setAttr( '{0}.scaleY'.format( obj[0] ), next[i][1] )
            cmds.setAttr( '{0}.scaleZ'.format( obj[0] ), next[i][2] )
            cmds.setKeyframe( '{0}.sx'.format( obj[0] ) )
            cmds.setKeyframe( '{0}.sy'.format( obj[0] ) )
            cmds.setKeyframe( '{0}.sz'.format( obj[0] ) )
            i = i + 1
    else:
        for obj in objMap:
            if curr[i] != next[i][0]:
                cmds.setKeyframe( '{0}.sx'.format( obj[0] ) )
                cmds.setKeyframe( '{0}.sy'.format( obj[0] ) )
                cmds.setKeyframe( '{0}.sz'.format( obj[0] ) )
                currTime = cmds.currentTime( q=True )
                cmds.currentTime( currTime + stepTime - 1, edit=True )
                cmds.setKeyframe( '{0}.sx'.format( obj[0] ) )
                cmds.setKeyframe( '{0}.sy'.format( obj[0] ) )
                cmds.setKeyframe( '{0}.sz'.format( obj[0] ) )
                cmds.currentTime( currTime + stepTime, edit=True )
                cmds.setAttr( '{0}.scaleX'.format( obj[0] ), next[i][0] )
                cmds.setAttr( '{0}.scaleY'.format( obj[0] ), next[i][1] )
                cmds.setAttr( '{0}.scaleZ'.format( obj[0] ), next[i][2] )
                cmds.setKeyframe( '{0}.sx'.format( obj[0] ) )
                cmds.setKeyframe( '{0}.sy'.format( obj[0] ) )
                cmds.setKeyframe( '{0}.sz'.format( obj[0] ) )
                cmds.currentTime( currTime, edit=True )
            i = i + 1
    cmds.currentTime( currTime + stepTime, edit=True )

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
    # Transfer the mesh into a graph of V x E
    graph = createGraph(mesh, name)
    # Find neighbors for each vertex
    neighbors = findNeighbors(graph, mesh, name)
    objGroup = 'lifeObjGroup'
    objMap = initLife(mesh, name, objGroup, neighbors)
    return
    
    # Scale object matrix to 'dead' state
    factorDead = (0.0, 0.0, 0.0)
    factorAlive = (0.5, 0.1, 0.5)
    factorEmph = (2.0, 2.0, 2.0)
    scaleObjGroup(objGroup, factorDead)
    
    # Create storage matrices
    matrixA = createMatrix(name, factorDead)
    matrixB = createMatrix(name, factorDead)
    
    # Load seed pattern
    pattern = enumerateSeed(seed)
    matrixA = loadPattern(matrixA, pattern, factorAlive)
    
    print matrixA
    
    # Render first frame
    cmds.currentTime( int(startTime), edit=True )
    renderLife(objMap, matrixA, 0)
    
    # Run the Game of Life on the mesh
    currTime = int(startTime)
    while currTime < int(endTime):
        # Create matrix B from matrix A
        for i in range ( 0, numVerts ):
            count = 0
            for n in neighbors[i]:
                if matrixA[n] == factorAlive:
                    count = count + 1
            if count == 2:
                matrixB[i] = matrixA[i]
            if count == 3:
                matrixB[i] = factorAlive
            if count < 2 or count > 3:
                matrixB[i] = factorDead
        for i in range ( 0, numVerts ):
            matrixA[i] = matrixB[i]
        renderLife(objMap, matrixA, int(stepTime))
        currTime = currTime + int(stepTime)

##########################
####### Run Script #######
##########################

# Display window
displayWindow()

