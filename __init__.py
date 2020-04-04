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

import bpy
from . add_mesh_polylink import AddTorusPolylink, AddTorusKnotPolylink

bl_info = {
    "name": "Regular Polylinks",
    "author": "Shengyi Wang",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds Regular Polylinks",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }


def add_polylink_buttons(self, context):
    self.layout.operator(
        AddTorusPolylink.bl_idname,
        text="Torus Polylink",
        icon="MESH_ICOSPHERE")
    self.layout.operator(
        AddTorusKnotPolylink.bl_idname,
        text="Torus Knot Polylink",
        icon="MESH_ICOSPHERE")


def register():
    bpy.utils.register_class(AddTorusPolylink)
    bpy.utils.register_class(AddTorusKnotPolylink)
    bpy.types.VIEW3D_MT_mesh_add.append(add_polylink_buttons)


def unregister():
    bpy.utils.unregister_class(AddTorusPolylink)
    bpy.utils.unregister_class(AddTorusKnotPolylink)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_polylink_buttons)


if __name__ == "__main__":
    register()
