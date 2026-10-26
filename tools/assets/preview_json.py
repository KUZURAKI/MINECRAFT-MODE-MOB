import bpy, json, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
opts = dict(a.split('=', 1) for a in argv)
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
name = opts['name']
data = json.load(open(os.path.join(PROJ, 'src', 'main', 'resources', 'assets', 'modehud', 'geo', name + '.json')))
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
img = bpy.data.images.load(os.path.join(PROJ, 'src', 'main', 'resources', 'assets', 'modehud', 'textures', 'entity', name + '.png'))
img.pack()
mat = bpy.data.materials.new('m'); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes.get('Principled BSDF')
tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img; tn.interpolation = 'Closest'
nt.links.new(tn.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(tn.outputs['Alpha'], bsdf.inputs['Alpha'])
to_b = lambda x, y, z: (x, z, y)
allv = []
for part in data['parts']:
    v = part['v']
    verts, faces, uvs = [], [], []
    for t in range(len(v) // 15):
        base = len(verts)
        for k in range(3):
            o = t * 15 + k * 5
            verts.append(to_b(v[o], v[o + 1], v[o + 2]))
            uvs.append((v[o + 3], 1 - v[o + 4]))
        faces.append((base, base + 1, base + 2))
    allv += verts
    mesh = bpy.data.meshes.new(part['name'])
    mesh.from_pydata(verts, [], faces)
    uvl = mesh.uv_layers.new(name='uv')
    for poly in mesh.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uvl.data[li].uv = uvs[vi]
    mesh.materials.append(mat)
    scene.collection.objects.link(bpy.data.objects.new(part['name'], mesh))
mn = Vector([min(p[i] for p in allv) for i in range(3)]); mx = Vector([max(p[i] for p in allv) for i in range(3)])
center = (mn + mx) / 2; size = max(mx - mn)
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.55, 1)
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.0
so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-60)); scene.collection.objects.link(so)
cam = bpy.data.cameras.new('cam'); cam.lens = 45
co = bpy.data.objects.new('cam', cam); scene.collection.objects.link(co); scene.camera = co
az, el = [(35, 35), (215, 30), (0, 85), (90, 5)][int(opts.get('view', '0'))]
d = size * 2.0
pos = center + Vector((d * math.cos(math.radians(el)) * math.sin(math.radians(az)), -d * math.cos(math.radians(el)) * math.cos(math.radians(az)), d * math.sin(math.radians(el))))
co.location = pos; co.rotation_euler = (center - pos).to_track_quat('-Z', 'Y').to_euler()
engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
scene.render.resolution_x = 700; scene.render.resolution_y = 500
scene.render.filepath = opts['out']
bpy.ops.render.render(write_still=True)
