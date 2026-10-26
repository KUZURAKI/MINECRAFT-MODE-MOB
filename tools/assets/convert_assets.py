import base64, json, math, os, shutil, sys, zipfile

import gltf_tools as G

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(PROJ, 'src', 'main', 'resources', 'assets', 'modehud')
DL = 'C:/Users/Zedkodex/Downloads'
GEO = os.path.join(ASSETS, 'geo')
TEX = os.path.join(ASSETS, 'textures', 'entity')
os.makedirs(GEO, exist_ok=True)
os.makedirs(TEX, exist_ok=True)


def subtree(kids, i):
    out = [i]
    for c in kids.get(i, []):
        out += subtree(kids, c)
    return out


def embedded_png(js, bufs, out_path):
    img = js['images'][0]
    if 'uri' in img and img['uri'].startswith('data:'):
        data = base64.b64decode(img['uri'].split(',', 1)[1])
    else:
        bv = js['bufferViews'][img['bufferView']]
        data = bufs[bv['buffer']][bv.get('byteOffset', 0): bv.get('byteOffset', 0) + bv['byteLength']]
    open(out_path, 'wb').write(data)


def node_tris(js, bufs, W, i, nodes):
    out = []
    for pr in G.mesh_prims(js, bufs, nodes[i]['mesh']):
        for (a, b, c) in pr['tris']:
            for k in (a, b, c):
                out.append((pr['pos'][k], pr['uv'][k]))
    return out


def build_parts(name, path, scale, remove, parts_spec, anchors, origin_mode='center', rotate_y=0.0, front_flip=False):
    js, bufs = G.load(path)
    W, parent = G.world_matrices(js)
    nodes = js['nodes']
    kids = {}
    for c, p in parent.items():
        kids.setdefault(p, []).append(c)

    removed = set()
    for i, n in enumerate(nodes):
        if remove(i, n):
            removed.update(subtree(kids, i))

    part_of = {}
    for pname, roots in parts_spec.items():
        for r in roots:
            for j in subtree(kids, r):
                part_of[j] = pname

    verts = {}
    for i, n in enumerate(nodes):
        if 'mesh' not in n or i in removed:
            continue
        pname = part_of.get(i, 'static')
        for p, uv in node_tris(js, bufs, W, i, nodes):
            w = G.apply(W[i], p)
            verts.setdefault(pname, []).append((w, uv))

    allp = [w for v in verts.values() for (w, _) in v]
    mn = [min(p[k] for p in allp) for k in range(3)]
    mx = [max(p[k] for p in allp) for k in range(3)]
    cx = (mn[0] + mx[0]) / 2
    cz = (mn[2] + mx[2]) / 2
    ox, oy, oz = cx, mn[1], cz
    if origin_mode == 'front':
        oz = mn[2]
    c, s = math.cos(math.radians(rotate_y)), math.sin(math.radians(rotate_y))

    def tf(p):
        x, y, z = (p[0] - ox) * scale, (p[1] - oy) * scale, (p[2] - oz) * scale
        return [round(x * c + z * s, 5), round(y, 5), round(-x * s + z * c, 5)]

    out_parts = []
    for pname, vs in verts.items():
        flat = []
        pts = [tf(w) for (w, _) in vs]
        for (w, uv), q in zip(vs, pts):
            flat += [q[0], q[1], q[2], round(uv[0], 6), round(uv[1], 6)]
        pivot = [round(sum(p[k] for p in pts) / len(pts), 5) for k in range(3)]
        out_parts.append({'name': pname, 'pivot': pivot, 'v': flat})

    out = {'parts': out_parts,
           'anchors': {k: tf(v) for k, v in anchors.items()},
           'size': [round((mx[0] - mn[0]) * scale, 3), round((mx[1] - mn[1]) * scale, 3), round((mx[2] - mn[2]) * scale, 3)]}
    json.dump(out, open(os.path.join(GEO, name + '.json'), 'w'), separators=(',', ':'))
    embedded_png(js, bufs, os.path.join(TEX, name + '.png'))
    print(name, 'parts', [(p['name'], len(p['v']) // 15) for p in out_parts], 'size', out['size'], 'anchors', out['anchors'])


def build_rig(name, path, scale, anim_names):
    js, bufs = G.load(path)
    nodes = js['nodes']
    W, parent = G.world_matrices(js)
    allp = []
    for i, n in enumerate(nodes):
        if 'mesh' in n:
            for pr in G.mesh_prims(js, bufs, n['mesh']):
                allp += [G.apply(W[i], p) for p in pr['pos']]
    mn = [min(p[k] for p in allp) for k in range(3)]
    mx = [max(p[k] for p in allp) for k in range(3)]
    ox, oy, oz = (mn[0] + mx[0]) / 2, mn[1], (mn[2] + mx[2]) / 2

    out_nodes = []
    for i, n in enumerate(nodes):
        node = {'name': n.get('name', ''), 'parent': parent.get(i, -1),
                't': [round(v, 6) for v in n.get('translation', [0, 0, 0])],
                'r': [round(v, 6) for v in n.get('rotation', [0, 0, 0, 1])],
                's': [round(v, 6) for v in n.get('scale', [1, 1, 1])]}
        if 'matrix' in n:
            m = G.node_matrix(n)
            node['m'] = [round(m[r][cc], 6) for cc in range(4) for r in range(4)]
        if 'mesh' in n:
            flat = []
            for p, uv in node_tris(js, bufs, W, i, nodes):
                flat += [round(p[0], 5), round(p[1], 5), round(p[2], 5), round(uv[0], 6), round(uv[1], 6)]
            node['v'] = flat
        out_nodes.append(node)

    anims = {}
    for ai, a in enumerate(js.get('animations', [])):
        key = anim_names[ai] if ai < len(anim_names) else a.get('name', str(ai))
        length = 0.0
        chans = []
        for ch in a['channels']:
            tgt = ch['target']
            if 'node' not in tgt or tgt['path'] not in ('translation', 'rotation', 'scale'):
                continue
            sm = a['samplers'][ch['sampler']]
            times = G.accessor(js, bufs, sm['input'])
            vals = G.accessor(js, bufs, sm['output'])
            if sm.get('interpolation', 'LINEAR') == 'CUBICSPLINE':
                vals = vals[1::3]
            length = max(length, max(times))
            flat = []
            for v in vals:
                flat += [round(x, 6) for x in (v if isinstance(v, tuple) else (v,))]
            chans.append({'node': tgt['node'], 'path': {'translation': 't', 'rotation': 'r', 'scale': 's'}[tgt['path']],
                          'times': [round(t, 5) for t in times], 'vals': flat})
        anims[key] = {'len': round(length, 5), 'ch': chans}
    out = {'scale': scale, 'origin': [ox, oy, oz], 'nodes': out_nodes, 'anims': anims,
           'size': [round((mx[k] - mn[k]) * scale, 3) for k in range(3)]}
    json.dump(out, open(os.path.join(GEO, name + '.json'), 'w'), separators=(',', ':'))
    embedded_png(js, bufs, os.path.join(TEX, name + '.png'))
    print(name, 'nodes', len(out_nodes), 'anims', {k: (v['len'], len(v['ch'])) for k, v in anims.items()}, 'size', out['size'], 'origin', [round(v, 2) for v in out['origin']])


PILOT = {'head', 'rightArm', 'leftArm', 'rightLeg', 'leftLeg', 'body', 'b3', 'b4'}

if __name__ == '__main__':
    which = set(sys.argv[1:]) or {'backpack', 'car', 'fighter', 'bomber', 'tarantula'}
    if 'backpack' in which:
        keep = {1, 2, 3, 4, 5, 6}
        js0, _ = G.load(DL + '/back/source/model.gltf')
        build_parts('backpack', DL + '/back/source/model.gltf', 1.0,
                    lambda i, n: ('mesh' in n and i not in keep) or (n.get('name') in ('left_arm', 'right_arm', 'left_leg', 'right_leg')),
                    {}, {}, origin_mode='front')
    if 'car' in which:
        build_parts('car', DL + '/car/source/model.gltf', 0.045, lambda i, n: False,
                    {'wheel_fl': [161], 'wheel_fr': [173], 'wheel_rl': [147], 'wheel_rr': [135]},
                    {'seat0': (-10.5, 8, 2.5), 'seat1': (10.5, 8, 2.5)})
    if 'fighter' in which:
        build_parts('fighter', DL + '/plain/1/source/model.gltf', 1.3,
                    lambda i, n: n.get('name') in PILOT,
                    {}, {'seat': (0, 0.7, 0.35), 'gun_l': (-0.5, 0.75, -1.4), 'gun_r': (0.5, 0.75, -1.4),
                         'pylon_l': (-1.6, 0.7, 2.6), 'pylon_r': (1.6, 0.7, 2.6)})
    if 'bomber' in which:
        build_parts('bomber', DL + '/plain/2/source/model.gltf', 0.06, lambda i, n: False,
                    {}, {'seat': (2.3, 24, -20), 'bay': (2.3, 12, 10)})
    if 'tarantula' in which:
        zp = zipfile.ZipFile(DL + '/tarant/source/Mutant_Spider.zip')
        zp.extract('mutant_spider.glb', os.path.join(HERE, 'tmp'))
        build_rig('tarantula', os.path.join(HERE, 'tmp', 'mutant_spider.glb'), 1.3, ['idle', 'walk', 'attack'])
