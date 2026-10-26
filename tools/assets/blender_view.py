import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
opts = dict(a.split('=', 1) for a in argv)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=opts['file'])
hide = [h for h in opts.get('hide', '').split(',') if h]
for o in list(scene.objects):
    if any(o.name.startswith(h) for h in hide):
        bpy.data.objects.remove(o, do_unlink=True)
objs = [o for o in scene.objects if o.type == 'MESH']
for o in objs:
    for m in o.data.materials:
        if m and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE':
                    n.interpolation = 'Closest'
mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
for o in objs:
    for c in o.bound_box:
        v = o.matrix_world @ Vector(c)
        for i in range(3):
            mins[i] = min(mins[i], v[i]); maxs[i] = max(maxs[i], v[i])
center = (mins + maxs) / 2
size = max((maxs - mins))
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.55, 1)
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.0
so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-60))
scene.collection.objects.link(so)
cam = bpy.data.cameras.new('cam'); cam.lens = 45
co = bpy.data.objects.new('cam', cam); scene.collection.objects.link(co); scene.camera = co
d = size * 2.2
angles = {'a': (35, 35), 'b': (215, 30), 'c': (90, 5), 'd': (0, 80)}
az, el = angles[opts.get('view', 'a')]
pos = center + Vector((d * math.cos(math.radians(el)) * math.sin(math.radians(az)),
                       -d * math.cos(math.radians(el)) * math.cos(math.radians(az)),
                       d * math.sin(math.radians(el))))
co.location = pos
co.rotation_euler = (center - pos).to_track_quat('-Z', 'Y').to_euler()
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
scene.render.resolution_x = 700
scene.render.resolution_y = 500
scene.render.filepath = opts['out']
bpy.ops.render.render(write_still=True)
