import maya.cmds as cmds

# Game logic functions
def displayWindow():
    if( cmds.window( "Game Of Life Tool", exists=True ) ) :
        cmds.deleteUI( "Game Of Life Tool" )
    window = cmds.window( title="Game Of Life Tool", iconName='GOLTool', widthHeight=(200, 55) )
    cmds.columnLayout( adjustableColumn=True )
    cmds.button( label='Blank' )
    cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True )') )
    cmds.setParent( '..' )
    cmds.showWindow( window )

def createGraph(mesh, name):
    start, stop = (mesh[0].split('.vtx')[1]).split(':')
    start = start.split('[')[1]
    stop = stop.split(']')[0]
    cmds.select( name )
    # Extract edges
    numEdges = cmds.polyEvaluate( e=True )
    print numEdges
    # Extract vertices
    numVerts = cmds.polyEvaluate( v=True )
    print numVerts
    # Initialize graph
    graph = []
    for i in range ( 0, numVerts ):
        row = []
        for j in range ( 0, numEdges ):
            row.append( 0 )
        graph.append( row )
    print graph
    # Fill graph with vertices
    for i in range ( int(start), int(stop) ):
        cmds.select( '{0}.vtx[{1}]'.format( name, i ) )
        found = cmds.polyInfo( ve=True )
        print found
        tokens = found[0].split( ' ' )
        # Skip over non-alphanumeric strings
        for t in tokens:
            tmp = '{0}'.format( t )
            if (tmp.isalnum() == True) and (tmp != 'VERTEX'):
                # Add each alphanumeric string to the graph
                graph[i][int(tmp)] = 1
    cmds.select( mesh )
    return graph

def initLife(mesh, name, id):
    matrix = cmds.group( em=True, n='group{0}'.format(id) )
    start, stop = (mesh[0].split('.vtx')[1]).split(':')
    start = start.split('[')[1]
    stop = stop.split(']')[0]
    for i in range( int(start), int(stop) ):
        # Find the coordinates of each vertex
        trans = cmds.pointPosition( '{0}.vtx[{1}]'.format( name, i ) )
        # Create a cube at each vertex
        obj = cmds.polyCube()
        cmds.parent( obj, matrix )
        cmds.xform( obj, t=(trans[0], trans[1], trans[2]) )
    return matrix

def scaleMatrix(matrix, factor):
    children = cmds.listRelatives( matrix, c=True )
    for obj in children:
        cmds.xform( obj, s=(factor[0], factor[1], factor[2]) )

##########################
### Main Functionality ###
##########################

# Display menu window
displayWindow()

# Store mesh variables
mesh = cmds.ls( selection=True )
name = mesh[0].split('.vtx')[0]

# Transfer the selected vertices into a graph
graph = createGraph(mesh, name)
for i in graph:
    print i
    
# Initialize rendering
matrixA = initLife(mesh, name, 'MatrixA')
matrixB = initLife(mesh, name, 'MatrixB')

# Scale both matrices to 0
factorDead = (0.0, 0.0, 0.0)
factorAlive = (1.0, 1.0, 1.0)
scaleMatrix(matrixA, factorDead)
scaleMatrix(matrixB, factorDead)

# Load seed pattern

