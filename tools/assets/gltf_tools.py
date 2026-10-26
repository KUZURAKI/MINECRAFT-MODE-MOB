import base64, json, math, os, struct

CT = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def load(path):
    if path.lower().endswith('.glb'):
        data = open(path, 'rb').read()
        magic, ver, length = struct.unpack('<4sII', data[:12])
        off, js, binchunk = 12, None, None
        while off < len(data):
            cl, ct = struct.unpack('<II', data[off:off + 8])
            chunk = data[off + 8: off + 8 + cl]
            if ct == 0x4E4F534A:
                js = json.loads(chunk.decode('utf8'))
            elif ct == 0x004E4942:
                binchunk = chunk
            off += 8 + cl
        return js, [binchunk]
    js = json.load(open(path, encoding='utf8'))
    bufs = []
    for b in js['buffers']:
        uri = b.get('uri', '')
        if uri.startswith('data:'):
            bufs.append(base64.b64decode(uri.split(',', 1)[1]))
        else:
            bufs.append(open(os.path.join(os.path.dirname(path), uri), 'rb').read())
    return js, bufs


def accessor(js, bufs, idx):
    a = js['accessors'][idx]
    bv = js['bufferViews'][a['bufferView']]
    fmt, size = CT[a['componentType']]
    n = NC[a['type']]
    stride = bv.get('byteStride') or size * n
    base = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    buf = bufs[bv['buffer']]
    out = []
    for i in range(a['count']):
        o = base + i * stride
        vals = struct.unpack_from('<' + fmt * n, buf, o)
        if a.get('normalized'):
            div = {'b': 127.0, 'B': 255.0, 'h': 32767.0, 'H': 65535.0}[fmt]
            vals = tuple(v / div for v in vals)
        out.append(vals if n > 1 else vals[0])
    return out


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def identity():
    return [[1 if i == j else 0 for j in range(4)] for i in range(4)]


def node_matrix(n):
    if 'matrix' in n:
        m = n['matrix']
        return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    t = n.get('translation', [0, 0, 0])
    q = n.get('rotation', [0, 0, 0, 1])
    s = n.get('scale', [1, 1, 1])
    x, y, z, w = q
    r = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    m = identity()
    for i in range(3):
        for j in range(3):
            m[i][j] = r[i][j] * s[j]
        m[i][3] = t[i]
    return m


def world_matrices(js):
    nodes = js['nodes']
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []):
            parent[c] = i
    cache = {}

    def wm(i):
        if i in cache:
            return cache[i]
        m = node_matrix(nodes[i])
        if i in parent:
            m = mat_mul(wm(parent[i]), m)
        cache[i] = m
        return m
    return [wm(i) for i in range(len(nodes))], parent


def apply(m, p):
    return [m[0][0] * p[0] + m[0][1] * p[1] + m[0][2] * p[2] + m[0][3],
            m[1][0] * p[0] + m[1][1] * p[1] + m[1][2] * p[2] + m[1][3],
            m[2][0] * p[0] + m[2][1] * p[1] + m[2][2] * p[2] + m[2][3]]


def mesh_prims(js, bufs, mesh_idx):
    out = []
    for prim in js['meshes'][mesh_idx]['primitives']:
        at = prim['attributes']
        pos = accessor(js, bufs, at['POSITION'])
        uv = accessor(js, bufs, at['TEXCOORD_0']) if 'TEXCOORD_0' in at else [(0, 0)] * len(pos)
        idx = accessor(js, bufs, prim['indices']) if 'indices' in prim else list(range(len(pos)))
        mode = prim.get('mode', 4)
        tris = []
        if mode == 4:
            tris = [(idx[i], idx[i + 1], idx[i + 2]) for i in range(0, len(idx) - 2, 3)]
        out.append({'pos': pos, 'uv': uv, 'tris': tris,
                    'joints': accessor(js, bufs, at['JOINTS_0']) if 'JOINTS_0' in at else None,
                    'weights': accessor(js, bufs, at['WEIGHTS_0']) if 'WEIGHTS_0' in at else None})
    return out
