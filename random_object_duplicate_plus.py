import bpy
import random
from bpy_extras.object_utils import world_to_camera_view
import mathutils

bl_info = {
    "name": "Random Duplicate Objects with Extended Features",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 7, 0),
    "location": "View3D > Tool > Random Duplicate Objects",
    "description": "Create random duplicates, split faces, assign materials, manage object origins, and set render properties",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
}

def is_object_visible(obj, camera, scene):
    """Check if the object is visible in the camera's view."""
    for corner in obj.bound_box:
        world_corner = obj.matrix_world @ mathutils.Vector(corner)
        co_ndc = world_to_camera_view(scene, camera, world_corner)
        if 0.0 <= co_ndc.x <= 1.0 and 0.0 <= co_ndc.y <= 1.0 and 0.0 <= co_ndc.z <= 1.0:
            return True
    return False

def add_material_with_emission(obj, color, color_name):
    if obj.type == 'MESH':
        material = bpy.data.materials.new(name=f"{color_name}Material")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        for node in nodes:
            nodes.remove(node)
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        bsdf.inputs['Base Color'].default_value = color
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, -200)
        emission.inputs['Color'].default_value = color
        emission.inputs['Strength'].default_value = 1
        add_shader = nodes.new(type='ShaderNodeAddShader')
        add_shader.location = (200, 0)
        material_output = nodes.new(type='ShaderNodeOutputMaterial')
        material_output.location = (400, 0)
        material.node_tree.links.new(bsdf.outputs['BSDF'], add_shader.inputs[0])
        material.node_tree.links.new(emission.outputs['Emission'], add_shader.inputs[1])
        material.node_tree.links.new(add_shader.outputs['Shader'], material_output.inputs['Surface'])
        if len(obj.data.materials) > 0:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
        print(f"Added {color_name} material with emission to {obj.name}")

class OBJECT_OT_random_duplicate(bpy.types.Operator):
    bl_idname = "object.random_duplicate"
    bl_label = "Random Duplicate"
    bl_description = "Create random duplicates of the selected object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        props = context.scene.random_duplicate_props
        
        if obj is None:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        
        group_name = props.group_name
        collection = bpy.data.collections.get(group_name)
        
        if collection is None:
            collection = bpy.data.collections.new(group_name)
            context.scene.collection.children.link(collection)
        
        for _ in range(props.num_duplicates):
            duplicate = obj.copy()
            duplicate.data = obj.data.copy()
            duplicate.location = (
                obj.location.x + random.uniform(-props.x_range, props.x_range),
                obj.location.y + random.uniform(-props.y_range, props.y_range),
                obj.location.z + random.uniform(-props.z_range, props.z_range),
            )
            scale_factor = random.uniform(props.scale_min, props.scale_max)
            duplicate.scale = (scale_factor, scale_factor, scale_factor)
            collection.objects.link(duplicate)
        
        return {'FINISHED'}

class OBJECT_OT_randomize_location(bpy.types.Operator):
    bl_idname = "object.randomize_location"
    bl_label = "Randomize Location"
    bl_description = "Randomize the location of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.random_duplicate_props
        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
        
        for obj in selected_objects:
            obj.location = (
                obj.location.x + random.uniform(-props.x_range, props.x_range),
                obj.location.y + random.uniform(-props.y_range, props.y_range),
                obj.location.z + random.uniform(-props.z_range, props.z_range)
            )
        
        self.report({'INFO'}, f"Randomized locations of {len(selected_objects)} object(s)")
        return {'FINISHED'}

class OBJECT_OT_split_faces(bpy.types.Operator):
    bl_idname = "object.split_faces"
    bl_label = "Split Faces"
    bl_description = "Split faces, separate by loose parts, set origin to geometry, and record original location"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_split(type='EDGE')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.mesh.separate(type='LOOSE')
        
        for obj in context.selected_objects:
            context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            obj["original_location"] = obj.location.copy()
        
        self.report({'INFO'}, f"Split faces and recorded original locations for {len(context.selected_objects)} object(s)")
        return {'FINISHED'}

class OBJECT_OT_move_to_origin(bpy.types.Operator):
    bl_idname = "object.move_to_origin"
    bl_label = "Move to Origin"
    bl_description = "Move selected objects back to their original locations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        moved_count = 0
        for obj in context.selected_objects:
            if "original_location" in obj:
                obj.location = obj["original_location"]
                moved_count += 1
        
        if moved_count > 0:
            self.report({'INFO'}, f"Moved {moved_count} object(s) to their original locations")
        else:
            self.report({'WARNING'}, "No objects with recorded original locations were selected")
        return {'FINISHED'}

class OBJECT_OT_set_origin(bpy.types.Operator):
    bl_idname = "object.set_new_origin"
    bl_label = "Set Origin"
    bl_description = "Set the current location as the new origin for selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            obj["original_location"] = obj.location.copy()
        
        self.report({'INFO'}, f"Set new origin for {len(context.selected_objects)} object(s)")
        return {'FINISHED'}

class OBJECT_OT_add_material_with_emission(bpy.types.Operator):
    bl_idname = "object.add_material_with_emission"
    bl_label = "Add Material with Emission"
    bl_options = {'REGISTER', 'UNDO'}

    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 0.0, 0.0, 1.0)
    )
    color_name: bpy.props.StringProperty(
        name="Color Name",
        default="Red"
    )

    def execute(self, context):
        selected_objects = context.selected_objects
        if selected_objects:
            for obj in selected_objects:
                if obj.type == 'MESH':
                    add_material_with_emission(obj, self.color, self.color_name)
            self.report({'INFO'}, f"Applied {self.color_name} material to {len(selected_objects)} object(s)")
        else:
            self.report({'WARNING'}, "No objects selected")
        return {'FINISHED'}

class OBJECT_OT_add_random_material_with_emission(bpy.types.Operator):
    bl_idname = "object.add_random_material_with_emission"
    bl_label = "Random Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        colors = [
            ("Red", (1.0, 0.0, 0.0, 1.0)),
            ("Green", (0.0, 1.0, 0.0, 1.0)),
            ("Blue", (0.0, 0.0, 1.0, 1.0)),
            ("Cyan", (0.0, 1.0, 1.0, 1.0)),
            ("Magenta", (1.0, 0.0, 1.0, 1.0)),
            ("Yellow", (1.0, 1.0, 0.0, 1.0)),
            ("Black", (0.0, 0.0, 0.0, 1.0)),
            ("White", (1.0, 1.0, 1.0, 1.0))
        ]
        selected_objects = context.selected_objects
        if selected_objects:
            for obj in selected_objects:
                if obj.type == 'MESH':
                    color_name, color = random.choice(colors)
                    add_material_with_emission(obj, color, color_name)
            self.report({'INFO'}, f"Applied random colors to {len(selected_objects)} object(s)")
        else:
            self.report({'WARNING'}, "No objects selected")
        return {'FINISHED'}

class RENDER_OT_set_resolution(bpy.types.Operator):
    bl_idname = "render.set_resolution"
    bl_label = "Set Render Resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.IntProperty(
        name="Resolution",
        default=512,
        min=1
    )

    def execute(self, context):
        context.scene.render.resolution_x = self.resolution
        context.scene.render.resolution_y = self.resolution
        self.report({'INFO'}, f"Set render resolution to {self.resolution}x{self.resolution}")
        return {'FINISHED'}

class RENDER_OT_fix_color(bpy.types.Operator):
    bl_idname = "render.fix_color"
    bl_label = "Fix Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.view_settings.view_transform = 'Standard'
        self.report({'INFO'}, "Set color view transform to 'Standard'")
        return {'FINISHED'}

class OBJECT_PT_random_duplicate_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_random_duplicate_panel"
    bl_label = "Random Duplicate Objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Random Duplicates'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.random_duplicate_props
        
        layout.prop(props, "num_duplicates")
        layout.prop(props, "x_range")
        layout.prop(props, "y_range")
        layout.prop(props, "z_range")
        layout.prop(props, "scale_min")
        layout.prop(props, "scale_max")
        layout.prop(props, "group_name")
        layout.operator("object.random_duplicate")
        
        layout.separator()
        
        layout.prop(props, "loc_range")
        layout.operator("object.randomize_location")
        
        layout.separator()
        
        layout.operator("object.split_faces")
        layout.operator("object.move_to_origin")
        layout.operator("object.set_new_origin")
        
        layout.separator()
        
        layout.label(text="Render Settings:")
        row = layout.row(align=True)
        row.operator("render.set_resolution", text="512x512").resolution = 512
        row.operator("render.set_resolution", text="1024x1024").resolution = 1024
        layout.operator("render.fix_color", text="Fix Color")
        
        layout.separator()
        
        layout.label(text="Add Material with Emission:")
        
        colors = [
            ("Red", (1.0, 0.0, 0.0, 1.0)),
            ("Green", (0.0, 1.0, 0.0, 1.0)),
            ("Blue", (0.0, 0.0, 1.0, 1.0)),
            ("Cyan", (0.0, 1.0, 1.0, 1.0)),
            ("Magenta", (1.0, 0.0, 1.0, 1.0)),
            ("Yellow", (1.0, 1.0, 0.0, 1.0)),
            ("Black", (0.0, 0.0, 0.0, 1.0)),
            ("White", (1.0, 1.0, 1.0, 1.0))
        ]
        
        col = layout.column(align=True)
        for i in range(0, len(colors), 3):
            row = col.row(align=True)
            for j in range(3):
                if i + j < len(colors):
                    color_name, color_value = colors[i + j]
                    op = row.operator("object.add_material_with_emission", text=color_name, icon='MATERIAL')
                    op.color = color_value
                    op.color_name = color_name
        
        layout.operator("object.add_random_material_with_emission", text="Random Color", icon='COLOR')

class RandomDuplicateProperties(bpy.types.PropertyGroup):
    num_duplicates: bpy.props.IntProperty(
        name="Number of Duplicates",
        default=10,
        min=1
    )
    x_range: bpy.props.FloatProperty(
        name="X Range",
        default=5.0,
        min=0.0
    )
    y_range: bpy.props.FloatProperty(
        name="Y Range",
        default=5.0,
        min=0.0
    )
    z_range: bpy.props.FloatProperty(
        name="Z Range",
        default=5.0,
        min=0.0
    )
    scale_min: bpy.props.FloatProperty(
        name="Minimum Scale",
        default=0.5,
        min=0.0
    )
    scale_max: bpy.props.FloatProperty(
        name="Maximum Scale",
        default=2.0,
        min=0.0
    )
    group_name: bpy.props.StringProperty(
        name="Group Name",
        default="RandomDuplicates"
    )
    loc_range: bpy.props.FloatProperty(
        name="Location Range",
        default=1.0,
        min=0.0
    )

classes = (
    OBJECT_OT_random_duplicate,
    OBJECT_OT_randomize_location,
    OBJECT_OT_split_faces,
    OBJECT_OT_add_material_with_emission,
    OBJECT_OT_add_random_material_with_emission,
    OBJECT_OT_move_to_origin,
    OBJECT_OT_set_origin,
    RENDER_OT_set_resolution,
    RENDER_OT_fix_color,
    OBJECT_PT_random_duplicate_panel,
    RandomDuplicateProperties
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.random_duplicate_props = bpy.props.PointerProperty(type=RandomDuplicateProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.random_duplicate_props

if __name__ == "__main__":
    register()
