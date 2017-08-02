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

import sys
import importlib

bl_info = {
    "name": "Regular Polylinks",
    "author": "Shengyi Wang",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds Regular Polylinks",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }

if __name__ != "polylink":
    sys.modules["polylink"] = sys.modules[__name__]

imported_modules = []
root_modules = ["Polylink", "add_mesh_polylink"]


def import_modules(modules, base, im_list):
    for m in modules:
        im = importlib.import_module('.{}'.format(m), base)
        im_list.append(im)


import_modules(root_modules, "polylink", imported_modules)

if "bpy" in locals():
    for im in imported_modules:
        importlib.reload(im)


import bpy


class INFO_MT_mesh_polylink_add(bpy.types.Menu):
    # Define the "Math Function" menu
    bl_idname = "INFO_MT_mesh_polylink_add"
    bl_label = "Regular Polylink"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_torus_polylink",
                        text="Torus Polylink")
        layout.operator("mesh.primitive_torus_knot_polylink",
                        text="Torus Knot Polylink")


def menu_func(self, context):
    lay_out = self.layout
    lay_out.operator_context = 'INVOKE_REGION_WIN'
    lay_out.menu("INFO_MT_mesh_polylink_add", text="Polylink",
                 icon="MESH_ICOSPHERE")


def register():
    if __name__ != "polylink":
        bpy.utils.register_module("polylink")
    bpy.utils.register_module(__name__)
    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_module(__name__)
    if __name__ != "polylink":
        bpy.utils.unregister_module("polylink")


if __name__ == "__main__":
    register()
