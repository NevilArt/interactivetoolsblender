import bpy
import bmesh


def list_intersection(a, b):
    return list(set(a) & set(b))


def list_difference(a, b):
    return list(set(a) - set(b))


def get_mode():
    mode = bpy.context.mode
    if mode == 'EDIT_MESH':
        selection_mode = (tuple(bpy.context.scene.tool_settings.mesh_select_mode))
        if selection_mode[0]:
            return 'VERT'
        elif selection_mode[1]:
            return 'EDGE'
        elif selection_mode[2]:
            return 'FACE'
    return mode


def set_mode(mode, grow=False):
    if mode == 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    elif mode == 'VERT' or mode == 'EDGE' or mode == 'FACE':
        bpy.ops.mesh.select_mode(type=mode, use_expand=grow)


def get_bmesh():
    if get_mode() in ['VERT', 'EDGE', 'FACE']:
        return bmesh.from_edit_mesh(bpy.context.edit_object.data)
    else:
        print("Must be in obj mode to get bmesh")


# Return items index for selected mesh elements or names for objects
def get_selected(mode='', item=True):
    if not mode:
        mode = get_mode()
    if mode == 'OBJECT':
        if item:
            return [obj for obj in bpy.context.selected_objects]
        else:
            return [obj.name for obj in bpy.context.selected_objects]
    elif mode in ['VERT', 'EDGE', 'FACE']:
        bm = get_bmesh()
        if item:
            if mode == 'VERT':
                return [vert for vert in bm.verts if vert.select]
            elif mode == 'EDGE':
                return [edge for edge in bm.edges if edge.select]
            elif mode == 'FACE':
                return [face for face in bm.faces if face.select]
        else:
            if mode == 'VERT':
                return [vert.index for vert in bm.verts if vert.select]
            elif mode == 'EDGE':
                return [edge.index for edge in bm.edges if edge.select]
            elif mode == 'FACE':
                return [face.index for face in bm.faces if face.select]

    elif mode == 'EDIT_CURVE':
        curves = bpy.context.active_object.data.splines
        points = []
        for curve in curves:
            if curve.type == 'BEZIER':
                points.append([point for point in curve.bezier_points if point.select_control_point])

            else:
                points.append([point for point in curve.points if point.select])

        points = [item for sublist in points for item in sublist]
        return points

    else:
        return []


# Returns active object name
def active_get(item=True):
    if item:
        return bpy.context.active_object
    else:
        return bpy.context.active_object.name


# Sets active object based on name
def active_set(obj, item=True):
    if item:
        print(obj)
        bpy.context.view_layer.objects.active = obj
    else:
        bpy.context.view_layer.objects.active = bpy.data.objects[obj]


# Make selection based on indexes for selected mesh elements or names for objects
def select(target, mode='', item=True, replace=False, deselect=False, add_to_history=False):
    if not mode:
        mode = get_mode()

    selection_value = True

    if deselect:
        selection_value = False

    if type(target) is not list:
        target = [target]

    if mode == 'OBJECT':
        if replace:
            bpy.ops.object.select_all(action='DESELECT')

        if item:
            for obj in target:
                target.select_set(selection_value)
        else:
            for obj in target:
                bpy.data.objects[obj].select_set(selection_value)

    elif mode in ['VERT', 'EDGE', 'FACE']:
        bm = get_bmesh()

        if replace:
            bpy.ops.mesh.select_all(action='DESELECT')

        if item:
            if mode == 'VERT':
                for vert in target:
                    vert.select = selection_value
                    if add_to_history:
                        bm.select_history.add(bm.verts[vert.index])

            elif mode == 'EDGE':
                for edge in target:
                    edge.select = selection_value
                    if add_to_history:
                        bm.select_history.add(bm.edges[edge.index])

            elif mode == 'FACE':
                for face in target:
                    edge.select = selection_value
                    if add_to_history:
                        bm.select_history.add(bm.faces[face.index])

        else:
            if mode == 'VERT':
                for vert in target:
                    bm.verts[vert].select = selection_value
                    if add_to_history:
                        bm.select_history.add(bm.verts[vert])

            elif mode == 'EDGE':
                for edge in target:
                    bm.edges[edge].select = selection_value
                    if add_to_history:
                        bm.select_history.add(bm.edges[edge])

            elif mode == 'FACE':
                for face in target:
                    bm.faces[face].select = selection_value
                    if add_to_history:
                        bm.select_history.add(bm.faces[face])

    elif mode == 'EDIT_CURVE':
        print("Curve")
        curves = bpy.context.active_object.data.splines
        points = []
        for curve in curves:
            if curve.type == 'BEZIER':
                for point in curve.bezier_points:
                    point.select_control_point = True
            else:
                for point in curve.points:
                    point.select = True


def update_indexes(mode=''):
    bm = get_bmesh()
    if not mode:
        print("Try to get mode")
        mode = get_mode()
        print(mode)
    if 'VERT' or 'ALL' in mode:
        bm.verts.index_update()
        bm.verts.ensure_lookup_table()
    if 'EDGE' or 'ALL' in mode:
        bm.edges.index_update()
        bm.edges.ensure_lookup_table()
    if 'FACE' or 'ALL' in mode:
        bm.faces.index_update()
        bm.faces.ensure_lookup_table()
    bmesh.update_edit_mesh(bpy.context.edit_object.data)


def remove_duplicates(target):
    return list(set(target))