# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#
#  Contributor: Shengyi Wang
#  Contact:     txyyss@gmail.com
#

from polylink.Polylink import trigPolylink, torusKnotPolylink
import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty


def create_mesh_object(context, verts, edges, faces, name):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, edges, faces)
    me.update()

    from bpy_extras import object_utils
    return object_utils.object_data_add(context, me, operator=None)


class AddTorusPolylink(bpy.types.Operator):
    """Add a surface defined by torus-based polylinks"""
    bl_idname = "mesh.primitive_torus_polylink"
    bl_label = "Add Torus Polylink"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    source = EnumProperty(
        items=[("TETRAHEDRON", "Tetrahedron", "", 1),
               ("CUBE", "Cube", "", 2),
               ("OCTAHEDRON", "Octahedron", "", 3),
               ("DODECAHEDRON", "Dodecahedron", "", 4),
               ("ICOSAHEDRON", "Icosahedron", "", 5)],
        name="Source",
        description="Starting point of your polylink")

    rot = FloatProperty(
        name="Rotation",
        description="Rotation around the face normals",
        min=0.00, max=360,
        step=10,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION")

    faceDis = FloatProperty(
        name="Distance",
        description="Distance from the center to each face",
        min=0.00, max=10,
        default=1.0,
        unit="LENGTH")

    majorRadius = FloatProperty(
        name="Major Radius",
        description=("Max distance from the face " +
                     "center to the center of the tube"),
        min=0.01, max=10,
        default=3.0,
        unit="LENGTH")

    tubeRadius = FloatProperty(
        name="Tube Radius",
        description="The radius of the tube",
        min=0.01, max=10,
        default=0.5,
        unit="LENGTH")

    amplitude = FloatProperty(
        name="Amplitude",
        description="Amplitude of the wave",
        min=0.01, max=10,
        default=1.0,
        unit="LENGTH")

    factor = IntProperty(
        name="Factor",
        description="Times of the frequency",
        min=1, max=10,
        default=1)

    initAng = FloatProperty(
        name="Initial Angle",
        description="Initial angle of tube segments",
        min=0.00, max=360,
        step=10,
        default=0.0,
        subtype="ANGLE")

    uSeg = IntProperty(
        name="u segments",
        description="Number of segments in radial direction",
        min=3, max=50,
        default=10)

    vSeg = IntProperty(
        name="v segments",
        description="Number of segments in axial direction",
        min=10, max=300,
        default=40)

    def execute(self, context):
        pmesh = trigPolylink(self.source, self.rot, self.faceDis,
                             self.majorRadius, self.amplitude,
                             self.tubeRadius, self.factor,
                             self.initAng, self.vSeg, self.uSeg)
        create_mesh_object(context, pmesh.vertices, [],
                           pmesh.faces, "Polylink")
        return {'FINISHED'}


class AddTorusKnotPolylink(bpy.types.Operator):
    """Add a surface defined by torus-based polylinks"""
    bl_idname = "mesh.primitive_torus_knot_polylink"
    bl_label = "Add Torus Knot Polylink"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    source = EnumProperty(
        items=[("TETRAHEDRON", "Tetrahedron", "", 1),
               ("CUBE", "Cube", "", 2),
               ("OCTAHEDRON", "Octahedron", "", 3),
               ("DODECAHEDRON", "Dodecahedron", "", 4),
               ("ICOSAHEDRON", "Icosahedron", "", 5)],
        name="Source",
        description="Starting point of your polylink")

    rot = FloatProperty(
        name="Rotation",
        description="Rotation around the face normals",
        min=0.00, max=360,
        step=10,
        default=0.0,
        subtype="ANGLE",
        unit="ROTATION")

    faceDis = FloatProperty(
        name="Distance",
        description="Distance from the center to each face",
        min=0.00, max=10,
        default=1.0,
        unit="LENGTH")

    majorRadius = FloatProperty(
        name="Major Radius",
        description="Major radius of the torus knot",
        min=0.01, max=10,
        default=3.0,
        unit="LENGTH")

    minorRadius = FloatProperty(
        name="Minor Radius",
        description="Minor radius of the torus knot",
        min=0.01, max=10,
        default=1,
        unit="LENGTH")

    p = IntProperty(
        name="p",
        description="p times around its axis of rotational symmetry",
        min=1, max=50,
        default=1)

    qFac = IntProperty(
        name="Factor of q",
        description="q times around a circle in the interior of the torus",
        min=1, max=50,
        default=1)

    tubeRadius = FloatProperty(
        name="Tube Radius",
        description="Radius of the tube",
        min=0.01, max=10,
        default=0.5,
        unit="LENGTH")

    initAng = FloatProperty(
        name="Initial Angle",
        description="Initial angle of tube segments",
        min=0.00, max=360,
        step=10,
        default=0.0,
        subtype="ANGLE")

    uSeg = IntProperty(
        name="u segments",
        description="Number of segments in radial direction",
        min=3, max=50,
        default=10)

    vSeg = IntProperty(
        name="v segments",
        description="Number of segments in axial direction",
        min=10, max=300,
        default=40)

    def execute(self, context):
        pmesh = torusKnotPolylink(self.source, self.rot, self.faceDis,
                                  self.majorRadius, self.minorRadius,
                                  self.p, self.qFac, self.tubeRadius,
                                  self.initAng, self.uSeg, self.vSeg)
        create_mesh_object(context, pmesh.vertices, [],
                           pmesh.faces, "Polylink")
        return {'FINISHED'}
