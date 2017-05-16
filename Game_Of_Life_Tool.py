import maya.cmds as cmds

def create(tx, ty, tz):
    body = cmds.polyPlane(w=4, h=2)
    group = cmds.group(body)
    cmds.select(clear=True)
    cmds.setAttr("[0].translate".format(group), tx, ty, tz)
    
    return group

obj1 = create(1, 3, 5)
obj2 = create(3, 1, 5)
obj3 = create(4, 1, 2)