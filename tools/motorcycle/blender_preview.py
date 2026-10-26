import bpy, math, os, sys
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
opts = dict(a.split('=', 1) for a in argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.wm.obj_import(filepath=os.path.join(HERE, 'z50', 'model.obj'), forward_axis='NEGATIVE_Z', up_axis='Y')

img = bpy.data.images.load(os.path.join(HERE, 'z50', 'z50_motorbike.png'))
img.pack()
glow = bpy.data.images.load(os.path.join(HERE, 'z50', 'z50_motorbike_glow.png'))
glow.pack()
mat = bpy.data.materials.new('z50')
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes.get('Principled BSDF')
tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img; tn.interpolation = 'Closest'
gn = nt.nodes.new('ShaderNodeTexImage'); gn.image = glow; gn.interpolation = 'Closest'
nt.links.new(tn.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(tn.outputs['Alpha'], bsdf.inputs['Alpha'])
nt.links.new(gn.outputs['Color'], bsdf.inputs['Emission Color'])
bsdf.inputs['Emission Strength'].default_value = 2.0
bsdf.inputs['Roughness'].default_value = 0.85
for o in scene.objects:
    if o.type == 'MESH':
        o.data.materials.clear()
        o.data.materials.append(mat)

world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.40, 0.30, 0.26, 1)
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5
so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-60))
scene.collection.objects.link(so)
cam = bpy.data.cameras.new('cam'); cam.lens = 50
co = bpy.data.objects.new('cam', cam); scene.collection.objects.link(co); scene.camera = co
view = opts.get('view', 'ref')
target = Vector((0, 0.1, 0.7))
pos = {'side': Vector((-7.5, 0.1, 1.2)), 'ref': Vector((-5.5, -4.6, 2.6)), 'front': Vector((-3.0, -6.5, 2.0)), 'icon': Vector((-5.5, -4.2, 2.8))}[view]
co.location = pos
co.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
icon = view == 'icon'
scene.render.resolution_x = 256 if icon else 1000
scene.render.resolution_y = 256 if icon else 640
scene.render.film_transparent = icon
if 'out' in opts:
    scene.render.filepath = opts['out']
    bpy.ops.render.render(write_still=True)
if 'blend' in opts:
    bpy.ops.wm.save_as_mainfile(filepath=opts['blend'])
