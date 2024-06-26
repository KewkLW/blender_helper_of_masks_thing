import bpy
import random
from bpy_extras.object_utils import world_to_camera_view
import mathutils

bl_info = {
    "name": "Random Duplicate Objects with Extended Features",
    "Author": "Kewk",
    "blender": (3, 3, 0),
    "category": "Object",
    "version": (1, 8, 0),
    "location": "View3D > Tool > Kewky ComfyUI Tools",
    "description": "Create random duplicates, split faces, assign materials, manage object origins, and set render properties",
    "warning": "If you stare at the sun, you will burn your retinas",
    "tracker_url": "https://github.com/KewkLW/blender_helper_of_masks_thing",
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
        links = material.node_tree.links
        
        # Clear default nodes
        for node in nodes:
            nodes.remove(node)
        
        # Create emission shader
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Color'].default_value = color
        emission.inputs['Strength'].default_value = 1
        
        # Create material output
        material_output = nodes.new(type='ShaderNodeOutputMaterial')
        material_output.location = (200, 0)
        
        # Link emission to material output
        links.new(emission.outputs['Emission'], material_output.inputs['Surface'])
        
        # Assign the material to the object
        if len(obj.data.materials) > 0:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
        
        print(f"Added {color_name} material with emission to {obj.name}")

class OBJECT_OT_random_duplicate(bpy.types.Operator):
    bl_idname = "object.random_duplicate"
    bl_label = "Random Duplicate"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.random_duplicate_props
        selected_objects = context.selected_objects
        num_duplicates = props.num_duplicates

        for obj in selected_objects:
            for _ in range(num_duplicates):
                obj_copy = obj.copy()
                obj_copy.data = obj_copy.data.copy()
                context.collection.objects.link(obj_copy)

                random_x = random.uniform(-props.x_range, props.x_range) if props.use_x_range else 0
                random_y = random.uniform(-props.y_range, props.y_range) if props.use_y_range else 0
                random_z = random.uniform(-props.z_range, props.z_range) if props.use_z_range else 0
                obj_copy.location += mathutils.Vector((random_x, random_y, random_z))

        self.report({'INFO'}, f"Duplicated {len(selected_objects)} object(s) {num_duplicates} times")
        return {'FINISHED'}

class ANIM_OT_remove_past_keyframes(bpy.types.Operator):
    bl_idname = "anim.remove_past_keyframes"
    bl_label = "Remove Past Keyframes"
    bl_description = "Remove all keyframes before the current frame for the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.animation_data is None or obj.animation_data.action is None:
            self.report({'ERROR'}, "No active object with animation data selected")
            return {'CANCELLED'}

        current_frame = context.scene.frame_current
        action = obj.animation_data.action
        total_removed = 0

        for fcurve in action.fcurves:
            keyframes_to_keep = [kf for kf in fcurve.keyframe_points if kf.co.x >= current_frame]
            total_removed += len(fcurve.keyframe_points) - len(keyframes_to_keep)
            fcurve.keyframe_points.clear()
            for kf in keyframes_to_keep:
                fcurve.keyframe_points.insert(frame=kf.co.x, value=kf.co.y)
            fcurve.update()

        action.update_tag()
        context.scene.frame_set(current_frame)
        self.report({'INFO'}, f"Removed {total_removed} past keyframes for {obj.name}")
        return {'FINISHED'}

class ANIM_OT_remove_future_keyframes(bpy.types.Operator):
    bl_idname = "anim.remove_future_keyframes"
    bl_label = "Remove Future Keyframes"
    bl_description = "Remove all keyframes after the current frame for the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.animation_data is None or obj.animation_data.action is None:
            self.report({'ERROR'}, "No active object with animation data selected")
            return {'CANCELLED'}

        current_frame = context.scene.frame_current
        action = obj.animation_data.action
        total_removed = 0

        for fcurve in action.fcurves:
            keyframes_to_keep = [kf for kf in fcurve.keyframe_points if kf.co.x <= current_frame]
            total_removed += len(fcurve.keyframe_points) - len(keyframes_to_keep)
            fcurve.keyframe_points.clear()
            for kf in keyframes_to_keep:
                fcurve.keyframe_points.insert(frame=kf.co.x, value=kf.co.y)
            fcurve.update()

        action.update_tag()
        context.scene.frame_set(current_frame)
        self.report({'INFO'}, f"Removed {total_removed} future keyframes for {obj.name}")
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
        if not selected_objects:
            # If no objects are selected, find and select objects with the specified color
            for obj in context.view_layer.objects:
                if obj.type == 'MESH' and obj.data.materials and self.is_object_visible(obj, context):
                    for material in obj.data.materials:
                        if self.check_material_color(material):
                            obj.select_set(True)
                            selected_objects.append(obj)
                            break  # Stop checking other materials for this object
            
            if selected_objects:
                context.view_layer.objects.active = selected_objects[0]
                self.report({'INFO'}, f"Selected {len(selected_objects)} object(s) with {self.color_name} material")
            else:
                self.report({'WARNING'}, f"No visible objects found with {self.color_name} material")
        else:
            # Apply the material to selected objects as before
            for obj in selected_objects:
                if obj.type == 'MESH':
                    add_material_with_emission(obj, self.color, self.color_name)
            self.report({'INFO'}, f"Applied {self.color_name} material to {len(selected_objects)} object(s)")
        
        return {'FINISHED'}

    def check_material_color(self, material):
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'EMISSION':
                    node_color = node.inputs['Color'].default_value
                    if self.compare_colors(node_color, self.color):
                        return True
                elif node.type == 'BSDF_PRINCIPLED':
                    node_color = node.inputs['Base Color'].default_value
                    if self.compare_colors(node_color, self.color):
                        return True
        return False

    def compare_colors(self, color1, color2, tolerance=0.01):
        return all(abs(c1 - c2) < tolerance for c1, c2 in zip(color1[:3], color2[:3]))

    def is_object_visible(self, obj, context):
        # Check if the object is visible in the viewport and not hidden
        return obj.visible_get() and not obj.hide_viewport and not obj.hide_render

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

class OBJECT_OT_random_resize(bpy.types.Operator):
    bl_idname = "object.random_resize"
    bl_label = "Random Resize"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.random_duplicate_props
        selected_objects = context.selected_objects
        
        for obj in selected_objects:
            random_scale = random.uniform(props.scale_min, props.scale_max)
            obj.scale = (random_scale, random_scale, random_scale)
        
        self.report({'INFO'}, f"Randomly resized {len(selected_objects)} object(s)")
        return {'FINISHED'}

class OBJECT_OT_randomize_location(bpy.types.Operator):
    bl_idname = "object.randomize_location"
    bl_label = "Randomize Location"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.random_duplicate_props
        selected_objects = context.selected_objects
        
        for obj in selected_objects:
            random_x = random.uniform(-props.x_range, props.x_range) if props.use_x_range else obj.location.x
            random_y = random.uniform(-props.y_range, props.y_range) if props.use_y_range else obj.location.y
            random_z = random.uniform(-props.z_range, props.z_range) if props.use_z_range else obj.location.z
            
            obj.location = (random_x, random_y, random_z)
        
        self.report({'INFO'}, f"Randomized location for {len(selected_objects)} object(s)")
        return {'FINISHED'}

class OBJECT_OT_select_all_in_groups(bpy.types.Operator):
    bl_idname = "object.select_all_in_groups"
    bl_label = "Select All In Groups"
    bl_description = "Toggle selecting all objects in a group by clicking on it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.select_all_in_groups = not context.scene.select_all_in_groups
        return {'FINISHED'}

def select_group_objects(self, context):
    if context.scene.select_all_in_groups:
        if self.bl_space_type == 'OUTLINER':
            active_object = context.active_object
            if active_object and active_object.users_collection:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in active_object.users_collection[0].objects:
                    obj.select_set(True)
                context.view_layer.objects.active = active_object
    return None

class OUTLINER_OT_select_group_objects(bpy.types.Operator):
    bl_idname = "outliner.select_group_objects"
    bl_label = "Select All Objects in Group"
    bl_description = "Select all objects in the clicked group"
    bl_options = {'REGISTER', 'UNDO'}

    group_name: bpy.props.StringProperty()

    def execute(self, context):
        if context.scene.select_all_in_groups:
            collection = bpy.data.collections.get(self.group_name)
            if collection:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in collection.objects:
                    obj.select_set(True)
                if collection.objects:
                    context.view_layer.objects.active = collection.objects[0]
        return {'FINISHED'}

def draw_outliner_group_menu(self, context):
    layout = self.layout
    layout.operator(OUTLINER_OT_select_group_objects.bl_idname, text="Select All Objects").group_name = context.collection.name

class OBJECT_PT_random_duplicate_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_random_duplicate_panel"
    bl_label = "Random Duplicate Objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Kewky ComfyUI Tools'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.random_duplicate_props
        
        # Random Duplicate Objects
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "show_random_duplicate", icon="TRIA_DOWN" if context.scene.show_random_duplicate else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Random Duplicate Objects")
        if context.scene.show_random_duplicate:
            box.prop(props, "num_duplicates")
            
            row = box.row(align=True)
            row.prop(props, "use_x_range", text="")
            sub = row.row()
            sub.enabled = props.use_x_range
            sub.prop(props, "x_range")
            
            row = box.row(align=True)
            row.prop(props, "use_y_range", text="")
            sub = row.row()
            sub.enabled = props.use_y_range
            sub.prop(props, "y_range")
            
            row = box.row(align=True)
            row.prop(props, "use_z_range", text="")
            sub = row.row()
            sub.enabled = props.use_z_range
            sub.prop(props, "z_range")
            
            box.prop(props, "group_name")
            box.operator("object.random_duplicate")
        
        # Utils
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "show_utils", icon="TRIA_DOWN" if context.scene.show_utils else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Utils")
        if context.scene.show_utils:
            box.operator("object.randomize_location")
            box.operator("object.split_faces")
            box.operator("object.set_new_origin")
            box.operator("object.move_to_origin")
            box.prop(context.scene, "select_all_in_groups", text="Select All In Groups")
        
        # Random Object Size
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "show_random_size", icon="TRIA_DOWN" if context.scene.show_random_size else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Random Object Size")
        if context.scene.show_random_size:
            box.prop(props, "scale_min")
            box.prop(props, "scale_max")
            box.operator("object.random_resize")
        
        # Random Render Settings
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "show_render_settings", icon="TRIA_DOWN" if context.scene.show_render_settings else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Random Render Settings")
        if context.scene.show_render_settings:
            row = box.row(align=True)
            row.operator("render.set_resolution", text="512x512").resolution = 512
            row.operator("render.set_resolution", text="1024x1024").resolution = 1024
            box.operator("render.fix_color", text="Fix Color")
        
        # Set Material
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "show_set_material", icon="TRIA_DOWN" if context.scene.show_set_material else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Set Material")
        if context.scene.show_set_material:
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
            
            col = box.column(align=True)
            for i in range(0, len(colors), 3):
                row = col.row(align=True)
                for j in range(3):
                    if i + j < len(colors):
                        color_name, color_value = colors[i + j]
                        op = row.operator("object.add_material_with_emission", text=color_name, icon='MATERIAL')
                        op.color = color_value
                        op.color_name = color_name
            
            box.operator("object.add_random_material_with_emission", text="Random Color", icon='COLOR')
        
        # Keyframe Management
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "show_keyframe_management", icon="TRIA_DOWN" if context.scene.show_keyframe_management else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Keyframe Management")
        if context.scene.show_keyframe_management:
            row = box.row(align=True)
            row.operator("anim.remove_past_keyframes", text="Remove Past")
            row.operator("anim.remove_future_keyframes", text="Remove Future")

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
    use_x_range: bpy.props.BoolProperty(
        name="Use X Range",
        default=True
    )
    use_y_range: bpy.props.BoolProperty(
        name="Use Y Range",
        default=True
    )
    use_z_range: bpy.props.BoolProperty(
        name="Use Z Range",
        default=True
    )
    
    # Add new properties for the collapsible sections
    show_random_duplicate: bpy.props.BoolProperty(default=True)
    show_random_size: bpy.props.BoolProperty(default=True)
    show_render_settings: bpy.props.BoolProperty(default=True)
    show_set_material: bpy.props.BoolProperty(default=True)
    show_keyframe_management: bpy.props.BoolProperty(default=True)
    show_utils: bpy.props.BoolProperty(default=True)  

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
    ANIM_OT_remove_past_keyframes,
    ANIM_OT_remove_future_keyframes,
    OBJECT_OT_random_resize,
    OBJECT_OT_select_all_in_groups,
    OUTLINER_OT_select_group_objects,
    OBJECT_PT_random_duplicate_panel,
    RandomDuplicateProperties
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.random_duplicate_props = bpy.props.PointerProperty(type=RandomDuplicateProperties)
    bpy.types.Scene.show_random_duplicate = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.show_random_size = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.show_render_settings = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.show_set_material = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.show_keyframe_management = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.show_utils = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.select_all_in_groups = bpy.props.BoolProperty(
        name="Select All In Groups",
        description="When enabled, clicking on a group in the outliner selects all objects in that group",
        default=False
    )
    bpy.types.OUTLINER_HT_header.append(select_group_objects)
    bpy.types.OUTLINER_MT_collection.append(draw_outliner_group_menu)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.random_duplicate_props
    del bpy.types.Scene.show_random_duplicate
    del bpy.types.Scene.show_random_size
    del bpy.types.Scene.show_render_settings
    del bpy.types.Scene.show_set_material
    del bpy.types.Scene.show_keyframe_management
    del bpy.types.Scene.show_utils
    del bpy.types.Scene.select_all_in_groups
    bpy.types.OUTLINER_HT_header.remove(select_group_objects)
    bpy.types.OUTLINER_MT_collection.remove(draw_outliner_group_menu)

if __name__ == "__main__":
    register()
