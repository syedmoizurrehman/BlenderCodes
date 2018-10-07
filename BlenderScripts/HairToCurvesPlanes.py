import bpy
import bmesh

def PrintMatrix(Matrix, Rows, Columns):
     for i in range(0, Rows):
          for j in range(0, Columns):
               print(Matrix[i][j], end = " ")
          print("")

def GetLength():

    obj_name_original = bpy.context.active_object.name
    bpy.ops.object.duplicate_move()
       
    # the duplicate is active, apply all transforms to get global coordinates
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # convert to mesh
    bpy.ops.object.convert(target='MESH', keep_original=False)
    
    _data = bpy.context.active_object.data
    
    edge_length = 0
    for edge in _data.edges:
        vert0 = _data.vertices[edge.vertices[0]].co
        vert1 = _data.vertices[edge.vertices[1]].co
        edge_length += (vert0-vert1).length
    
    # deal with trailing float smear
    #edge_length = '{:.6f}'.format(edge_length)
    #print(edge_length)
    
    # stick into clipboard
    #bpy.context.window_manager.clipboard = edge_length
    
    bpy.ops.object.delete()
    bpy.context.scene.objects.active = bpy.context.scene.objects[obj_name_original]
    bpy.context.object.select = True
    return edge_length


def Main():
     bpy.ops.object.modifier_convert(modifier="ParticleSystem 1")
     bpy.ops.object.editmode_toggle()             # Enter edit mode
     bpy.ops.mesh.select_all(action='SELECT')     # Select everything
     bpy.ops.mesh.separate(type='LOOSE')          # Separate by lose
     bpy.ops.object.editmode_toggle()             # Exit edit mode
     bpy.ops.object.convert(target='CURVE')       # Convert all mesh curves to curve objects
     # TODO: Convert all curves to be not flat
     bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

SharedMeshData = None

for i, CurveObject in enumerate(bpy.context.selected_objects):
     # Name the curve object
     CurveObject.name = "C" + str(i)

     bpy.ops.object.select_all(action='DESELECT')                # Deselect all curves
     CurveObject.select = True                                   # Select CurveObject curve
     bpy.context.scene.objects.active = CurveObject

     # Get this CureObject's length
     Length = GetLength()
     print(Length)

     CurveWorldTransformation = CurveObject.matrix_world
     #coord = CurveWorldTransformation * VertexData.co
     
     # Get vertex data of first vertex
     CurveVertexData =  CurveObject.data.splines[0].points[0]
     
     # Get first vertex's global location
     CurveOrigin = (CurveVertexData.co.x, CurveVertexData.co.y, CurveVertexData.co.z)
     
     # Set 3D cursor's location to CurveOrigin
     bpy.context.scene.cursor_location = CurveOrigin
     
     # Set CurveObject's origin to 3D cursor
     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')                       

     # Add a plane for this curve's hair strand
     bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=CurveOrigin, layers=(False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
     
     # Move the plane to align with the CurveObject according to Curve's length
     bpy.ops.transform.translate(value=(Length, 0, 0), constraint_axis=(True, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

     # Scale plane to be rectangular
     #bpy.ops.transform.resize(value=(2, 1, 1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
     #bpy.ops.transform.resize(value=(1, 0.3, 1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
     bpy.context.object.scale[0] = 2
     bpy.context.object.scale[1] = 0.3

     # Name the plane
     bpy.context.object.name = "P" + str(i)

     #if (i == 0):
     #     SharedMeshData = bpy.context.object.data
     #else:
     #     bpy.context.object.data = SharedMeshData
     
     # Enter edit mode
     bpy.ops.object.editmode_toggle()

     # Get Bmesh data of this plane
     SharedMeshData = bpy.context.object.data
     Mesh = bmesh.from_edit_mesh(SharedMeshData)
     
     # Deselect all
     bpy.ops.mesh.select_all(action='DESELECT')
     
     # This must be called before indexing
     Mesh.verts.ensure_lookup_table()
     

     # Get two vertices on one of the smaller edges of the rectangular plane
     PlaneFirstVertex = Mesh.verts[0]
     PlaneSecondVertex = Mesh.verts[1]
     
     # Store the mid point of these two vertices as plane's origin location 
     PlaneOriginLocation = (abs(PlaneFirstVertex.co.x - PlaneSecondVertex.co.x), abs(PlaneFirstVertex.co.y - PlaneSecondVertex.co.y), abs(PlaneFirstVertex.co.z - PlaneSecondVertex.co.z))
     
     # Subdivide the plane
     for i in range(1, 4, 2):
          Mesh.edges.ensure_lookup_table()
          
          # Select two long edges
          LongEdge = Mesh.edges[i]
          LongEdge.select = True

     # Subdivide the two selected edges
     bpy.ops.mesh.subdivide(number_cuts=12, smoothness=0)

     # Exit edit mode
     bpy.ops.object.editmode_toggle()

     # Set 3D cursor's location to plane's first two vertices's midpoint
     bpy.context.scene.cursor_location = PlaneOriginLocation

     # Set plane's origin to 3D cursor
     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')        
     
     # Add Curve modifier to plane and set target to CurveObject
     bpy.ops.object.modifier_add(type='CURVE')
     bpy.context.object.modifiers["Curve"].object = CurveObject

     # Clear Plane's location
     bpy.ops.object.location_clear(clear_delta=False)
