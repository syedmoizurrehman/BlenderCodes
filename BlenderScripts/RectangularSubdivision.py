import bpy
import bmesh

def SelectSharpEdges():
     bpy.ops.mesh.select_all(action='SELECT')       # Select everything
     bpy.ops.mesh.dissolve_edges()                  # Remove unnecessary edges
     bpy.ops.mesh.select_all(action='TOGGLE')       # Deselect everything
     obj = bpy.context.edit_object
     me = obj.data

     bm = bmesh.from_edit_mesh(me)
     for edge in bm.edges:
          if not edge.smooth:
               edge.select = True

     bmesh.update_edit_mesh(me, False)

def RectanglularSubdivide(Divisions = 1):
     SelectSharpEdges()
     bpy.ops.mesh.subdivide(number_cuts=Divisions, smoothness=0)
     bpy.ops.mesh.select_all(action='DESELECT')      #Deselect everything
     
RectanglularSubdivide(1)