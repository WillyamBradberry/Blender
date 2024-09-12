bl_info = {
    "name": "Quick Sets Manager",
    "blender": (3, 6, 7),
    "category": "Object",
    "description": "Creates a list of selected objects to quick access, instead of searching them in outliner, also add PIE menu (Shift+E) to get quick access",
    "author": "Youtube: @WillFalcon | www.vitaliy-sokol.com",
    "version": (1, 0, 5),
}

import bpy
from bpy.types import Panel, Operator, UIList, Menu, PropertyGroup
from bpy.props import StringProperty, CollectionProperty, IntProperty, PointerProperty

separator = " :: "


# --- Define Custom List Items ---
class ObjectItem(bpy.types.PropertyGroup):
    name: StringProperty(name="Object Name", default="Unnamed Object")
    object_ref: bpy.props.PointerProperty(type=bpy.types.Object)  # Указатель на объект вместо имени


class ObjectSetItem(bpy.types.PropertyGroup):
    name: StringProperty(name="Set Name", default="New Set")
    objects: CollectionProperty(type=ObjectItem)


# --- Panel UI ---
def getMyObjectName(obj):
    names = obj.name  # .split(separator)
    return names


class OBJECT_PT_set_manager(Panel):
    bl_label = "Quick Sets v1 [Shift+E]"
    bl_idname = "OBJECT_PT_set_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    name: StringProperty()

    def update():
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        wm = context.window_manager

        row = layout.row()
        row.template_list("OBJECT_UL_sets", "", wm, "object_sets", wm, "object_set_index", rows=2)

        #        row = layout.row()

        col = row.column(align=True)
        col.operator("object_set.add_set", text="", icon="ADD")
        col.operator("object_set.remove_set", text="", icon="REMOVE")
        col.separator(factor=1)
        col.separator(factor=1)
        col.separator(factor=1)

        col.operator("object_set.select_all", text="", icon="RESTRICT_SELECT_OFF")
        col.operator("object_set.add_objects", text="", icon="PLUS")
        layout.label(text="Add / Remove objects to Set")
        row = layout.row()
        #        row.operator("object_set.remove_objects", text="", icon="X")
        row.operator("object_set.add_objects", text="Add ", icon="ADD")
        row.operator("object_set.remove_objects", text="Remove", icon="X")

        # Show objects in the active set
        if wm.object_sets:
            active_set = wm.object_sets[wm.object_set_index]
            layout.separator()
            layout.label(text="Click to select object:")
            for obj in active_set.objects:
                orig_names = getMyObjectName(obj)

                layout.operator("object_set.select_object", text=orig_names,
                                icon="OBJECT_DATA").object_name = orig_names

        layout.separator(factor=1)


class OBJECT_UL_sets(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="Set", emboss=False)


# --- Operator to Add/Remove Sets ---
def add_Objects_Func(wm, self, context):
    indx = wm.object_set_index
    active_set = wm.object_sets[indx]

    for obj in context.selected_objects:
        if not any(o.name == obj.name for o in active_set.objects):
            new_object = active_set.objects.add()
            new_object.name = obj.name


class OBJECT_OT_add_set(Operator):
    bl_idname = "object_set.add_set"
    bl_label = "Add Object Set"

    def execute(self, context):
        wm = context.window_manager
        new_set = wm.object_sets.add()

        set_len = len(wm.object_sets)

        new_set.name = "Quick List #" + str(set_len)

        wm.object_set_index = set_len - 1
        # Check if there are no sets, create a default one
        if not wm.object_sets:
            new_set = wm.object_sets.add()
            new_set.name = "Default Set"
            wm.object_set_index = 0

        # Add selected objects to the active set
        add_Objects_Func(wm, self, context)

        return {'FINISHED'}


class OBJECT_OT_remove_set(Operator):
    bl_idname = "object_set.remove_set"
    bl_label = "Remove Object Set"

    def execute(self, context):
        wm = context.window_manager
        wm.object_sets.remove(wm.object_set_index)
        wm.object_set_index = max(0, wm.object_set_index - 1)
        return {'FINISHED'}


# --- Operator to Add/Remove Objects ---

class OBJECT_OT_add_objects(Operator):
    bl_idname = "object_set.add_objects"
    bl_label = "Add Selected Objects to Set"

    def execute(self, context):
        wm = context.window_manager

        # Check if there are no sets, create a default one
        if not wm.object_sets:
            new_set = wm.object_sets.add()
            new_set.name = "Default Set"
            wm.object_set_index = 0

        add_Objects_Func(wm, self, context)
        return {'FINISHED'}


class OBJECT_OT_remove_objects(Operator):
    bl_idname = "object_set.remove_objects"
    bl_label = "Remove Selected Objects from Set"

    def execute(self, context):
        wm = context.window_manager
        if wm.object_sets:
            active_set = wm.object_sets[wm.object_set_index]
            selected_objects = [obj.name for obj in context.selected_objects]

            # Loop through the collection in reverse and remove matching objects
            for obj_item in reversed(active_set.objects):
                if obj_item.name in selected_objects:
                    active_set.objects.remove(active_set.objects.find(obj_item.name))

        return {'FINISHED'}


def select_all():
    wm = bpy.context.window_manager
    if wm.object_sets:
        active_set = wm.object_sets[wm.object_set_index]
        bpy.ops.object.select_all(action='DESELECT')

        for obj_item in active_set.objects:
            myname = getMyObjectName(obj_item)
            obj = bpy.data.objects.get(myname)
            try:
                if obj:
                    obj.select_set(True)

            except Exception as err:
                print("Something went wrong when opening the file:", err)

    return {'FINISHED'}


class OBJECT_OT_select_all(Operator):
    bl_idname = "object_set.select_all"
    bl_label = "Select All Objects in Set"

    def execute(self, context):
        select_all()
        return {'FINISHED'}


class OBJECT_OT_select_object(Operator):
    bl_idname = "object_set.select_object"
    bl_label = "Select Object from Set"

    object_name: StringProperty()

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        print("object_name: ", self.object_name)
        obj = bpy.data.objects.get(self.object_name)
        if obj:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
        return {'FINISHED'}


# PIE menu ----------------------------------------------------


class OBJECT_MT_pie_menu(Menu):
    bl_label = "Pie Menu"
    bl_idname = "OBJECT_MT_pie_menu"

    def draw(self, context):
        self.report("Report OBJECT_MT_pie_menu")
        return {'FINISHED'}


class OBJECT_OT_select_set(Operator):
    bl_idname = "object_set.select_set"
    bl_label = "Select Object Set"

    set_index: IntProperty()
    index: IntProperty()

    def execute(self, context):
        wm = context.window_manager
        self.set_index = self.index
        wm.object_set_index = self.index
        #        print("Select set operator: ", wm.object_set_index)
        if wm.object_sets:
            active_set = wm.object_sets[self.set_index]
            #            bpy.ops.object.select_all(action='DESELECT')
            OBJECT_PT_set_manager.update()
        return {'FINISHED'}


class CUSTOM_MT_menu(Menu):
    bl_label = ""
    bl_idname = "CUSTOM_MT_menu"

    def draw(self, context):
        pie = self.layout.menu_pie()
        wm = context.window_manager

        layout = self.layout
        row = layout.row()
        box = layout.box()
        #        box_row = box.row()
        #        box_row.alignment = 'LEFT'
        #        row.separator(factor=1.0, type="LINE")

        # Ensure a set is selected
        icons = ["KEYFRAME", "KEYFRAME_HLT"]
        if wm.object_sets:
            active_set = wm.object_sets[wm.object_set_index]

            print("OBJECT_UL_sets:", active_set.name)

            row.label(text=f"Select set: [ {active_set.name} ] ", icon="TRIA_DOWN")
            #            row.alignment = 'RIGH'

            for index, x in enumerate(wm.object_sets):
                row = layout.row()
                layout.operator("object_set.select_set", text="Set:" + x.name, icon=icons[wm.object_set_index == index],
                                emboss=True, depress=(wm.object_set_index == index)).index = index
            row = layout.row()
            row.separator(factor=1.0)

            row = layout.row()
            row.separator()

            row.label(text="Select object in set", icon="TRIA_DOWN")
            row = layout.row()
            # Display the objects from the active set
            for obj_item in active_set.objects:
                obj = bpy.data.objects.get(obj_item.name)
                if obj:
                    #                    pie = box.row()
                    row = layout.row()
                    row.operator("object_set.select_object", text=obj.name,
                                 icon="OBJECT_DATA").object_name = obj_item.name

            row = layout.row()
            layout.label(text="Action", icon="TRIA_DOWN")
            layout.operator("object_set.select_all", text="Select All", icon="RESTRICT_SELECT_OFF")
            layout.operator("object_set.add_objects", text="Add Selected", icon="ADD")
            layout.operator("object_set.remove_objects", text="Remove From Set", icon="X")
            row.separator()
        else:
            pie.label(text="No sets available")


class CUSTOM_OT_operator(Operator):
    bl_idname = "object.custom_operator"
    bl_label = "Test Operator"

    relations_expand: bpy.props.BoolProperty(default=True)
    display_expand: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout


class Context(dict):
    def __init__(self, context=None, **kwargs):
        super().__init__()
        self.__dict__ = self

        if context is not None:
            self.update(context.copy())
        self.update(**kwargs)


class Layout:
    def __init__(self, layout):
        self.layout = layout


# register, unregister = bpy.utils.register_classes_factory(classes)

# --- Register ---
classes = [
    ObjectItem,
    ObjectSetItem,
    OBJECT_PT_set_manager,
    OBJECT_UL_sets,
    OBJECT_OT_add_set,
    OBJECT_OT_remove_set,
    OBJECT_OT_add_objects,
    OBJECT_OT_remove_objects,
    OBJECT_OT_select_all,
    OBJECT_OT_select_object,
    OBJECT_OT_select_set,
    OBJECT_MT_pie_menu,
    CUSTOM_MT_menu,
    CUSTOM_OT_operator,

]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.object_sets = CollectionProperty(type=ObjectSetItem)
    bpy.types.WindowManager.object_set_index = IntProperty()

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("wm.call_menu", 'E', 'PRESS', shift=True)
    #    kmi = km.keymap_items.new("wm.call_menu_pie", 'E', 'PRESS', shift=True)
    kmi.properties.name = "CUSTOM_MT_menu"


#    kmi.properties.name = "OBJECT_MT_pie_menu"


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.object_sets
    del bpy.types.WindowManager.object_set_index

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.get('3D View')
    if km:
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu':
                km.keymap_items.remove(kmi)


if __name__ == "__main__":
    register()

