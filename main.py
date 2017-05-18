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

def findNeighbors(mesh):
    # Extract vertices
    name, range = mesh[0].split('.vtx')
    start, stop = range.split(':')
    start = start.split('[')[1]
    stop = stop.split(']')[0]
    # Print the name, and the first and last vertices
    print name
    print start
    print stop
    # Initialize graph
    row = []
    graph = []
    i = int(start)
    while i <= int(stop):
        row = []
        j = int(start)
        while j <= int(stop):
            row.append( 0 )
            j = j + 1
        graph.append( row )
        i = i + 1
    # Fill graph with vertices
    i = int(start)
    while i <= int(stop):
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
        i = i + 1
    cmds.select( mesh )
    return graph

# Display menu window
displayWindow()

# Transfer the selected vertices into a graph
mesh = cmds.ls( selection=True )
print mesh
graph = findNeighbors(mesh)
print graph

