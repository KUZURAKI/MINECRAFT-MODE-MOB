import json, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(PROJ, 'src', 'main', 'resources', 'assets', 'modehud')

V, VT, groups, order, cur = [], [], {}, [], None
for line in open(os.path.join(HERE, 'z50', 'model.obj')):
    p = line.split()
    if not p:
        continue
    if p[0] == 'o':
        cur = p[1]
        if cur not in groups:
            groups[cur] = []
            order.append(cur)
    elif p[0] == 'v':
        V.append([float(x) for x in p[1:4]])
    elif p[0] == 'vt':
        VT.append([float(x) for x in p[1:3]])
    elif p[0] == 'f':
        idx = [tuple(int(i) - 1 for i in c.split('/')[:2]) for c in p[1:]]
        for k in range(1, len(idx) - 1):
            for vi, ti in (idx[0], idx[k], idx[k + 1]):
                x, y, z = V[vi]
                u, v = VT[ti]
                groups[cur].extend([round(x, 5), round(y, 5), round(z, 5), round(u, 6), round(1 - v, 6)])

def bbox(name):
    d = groups[name]
    xs, ys, zs = d[0::5], d[1::5], d[2::5]
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]

def center(name):
    a, b = bbox(name)
    return [(a[i] + b[i]) / 2 for i in range(3)]

allv = [c for g in groups.values() for c in g]
min_y = min(allv[1::5])
h0, h1 = center('handle0'), center('handle1')
top = [(h0[i] + h1[i]) / 2 for i in range(3)]
axle = center('wheel0')
out = {
    'ground': -min_y,
    'steer': {'groups': ['front_part', 'handle0', 'handle1', 'wheel0'], 'top': top, 'bottom': axle},
    'wheels': {'wheel0': center('wheel0'), 'wheel1': center('wheel1')},
    'groups': [{'name': n, 'v': groups[n]} for n in order],
}
os.makedirs(os.path.join(ASSETS, 'geo'), exist_ok=True)
json.dump(out, open(os.path.join(ASSETS, 'geo', 'motorcycle.json'), 'w'), separators=(',', ':'))
shutil.copy(os.path.join(HERE, 'z50', 'z50_motorbike.png'), os.path.join(ASSETS, 'textures', 'entity', 'motorcycle.png'))
shutil.copy(os.path.join(HERE, 'z50', 'z50_motorbike_glow.png'), os.path.join(ASSETS, 'textures', 'entity', 'motorcycle_glow.png'))
print('groups', order, 'tris', len(allv) // 15, 'ground', round(-min_y, 3), 'top', [round(t, 3) for t in top], 'axle', [round(a, 3) for a in axle])
