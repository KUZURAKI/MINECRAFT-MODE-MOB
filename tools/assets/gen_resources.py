import json, os, zlib, struct

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src', 'main', 'resources')
A = os.path.join(ROOT, 'assets', 'modehud')
D = os.path.join(ROOT, 'data', 'modehud')


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


SLABS = {
    'grass_slab': ('grass_block', 'grass_block_top', 'grass_block_side', 'dirt'),
    'dirt_slab': ('dirt', 'dirt', 'dirt', 'dirt'),
    'coarse_dirt_slab': ('coarse_dirt', 'coarse_dirt', 'coarse_dirt', 'coarse_dirt'),
    'podzol_slab': ('podzol', 'podzol_top', 'podzol_side', 'dirt'),
    'mycelium_slab': ('mycelium', 'mycelium_top', 'mycelium_side', 'dirt'),
    'sand_slab': ('sand', 'sand', 'sand', 'sand'),
    'red_sand_slab': ('red_sand', 'red_sand', 'red_sand', 'red_sand'),
    'gravel_slab': ('gravel', 'gravel', 'gravel', 'gravel'),
    'mud_slab': ('mud', 'mud', 'mud', 'mud'),
    'rough_stone_slab': ('stone', 'stone', 'stone', 'stone'),
    'clay_slab': ('clay', 'clay', 'clay', 'clay'),
}
SHOVEL = {'grass_slab', 'dirt_slab', 'coarse_dirt_slab', 'podzol_slab', 'mycelium_slab', 'sand_slab', 'red_sand_slab', 'gravel_slab', 'mud_slab', 'clay_slab'}


def face(tex, uv, tint=False, cull=None):
    f = {'uv': uv, 'texture': tex}
    if cull:
        f['cullface'] = cull
    if tint:
        f['tintindex'] = 0
    return f


def elements(y0, y1, grass):
    sv = [0, 8, 16, 16] if y0 == 0 else [0, 0, 16, 8]
    side = lambda c: face('#side', sv, cull=c)
    els = [{
        'from': [0, y0, 0], 'to': [16, y1, 16],
        'faces': {
            'down': face('#bottom', [0, 0, 16, 16], cull='down' if y0 == 0 else None),
            'up': face('#top', [0, 0, 16, 16], tint=grass, cull='up' if y1 == 16 else None),
            'north': side('north'), 'south': side('south'), 'west': side('west'), 'east': side('east'),
        }}]
    if grass:
        ov = lambda c: face('#overlay', sv, tint=True, cull=c)
        els.append({
            'from': [0, y0, 0], 'to': [16, y1, 16],
            'faces': {'north': ov('north'), 'south': ov('south'), 'west': ov('west'), 'east': ov('east')}})
    return els


for name, (parent, top, side, bottom) in SLABS.items():
    grass = name == 'grass_slab'
    tex = {'top': 'minecraft:block/' + top, 'side': 'minecraft:block/' + side,
           'bottom': 'minecraft:block/' + bottom, 'particle': 'minecraft:block/' + side}
    if grass:
        tex['overlay'] = 'minecraft:block/grass_block_side_overlay'
    for part, (y0, y1) in (('', (0, 8)), ('_top', (8, 16))):
        w(os.path.join(A, 'models', 'block', name + part + '.json'),
          {'textures': tex, 'elements': elements(y0, y1, grass)})
    double = 'minecraft:block/' + parent
    w(os.path.join(A, 'blockstates', name + '.json'), {'variants': {
        'type=bottom': {'model': 'modehud:block/' + name},
        'type=top': {'model': 'modehud:block/' + name + '_top'},
        'type=double': {'model': double}}})
    w(os.path.join(A, 'models', 'item', name + '.json'), {'parent': 'modehud:block/' + name})
    w(os.path.join(D, 'loot_table', 'blocks', name + '.json'), {
        'type': 'minecraft:block',
        'pools': [{'rolls': 1.0, 'entries': [{
            'type': 'minecraft:item', 'name': 'modehud:' + name,
            'functions': [{'function': 'minecraft:set_count', 'count': 2.0, 'add': False,
                           'conditions': [{'condition': 'minecraft:block_state_property', 'block': 'modehud:' + name,
                                           'properties': {'type': 'double'}}]},
                          {'function': 'minecraft:explosion_decay'}]}]}]})
    base = 'minecraft:' + parent
    recipe = {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['PPP'],
              'key': {'P': {'item': base}}, 'result': {'id': 'modehud:' + name, 'count': 6}}
    w(os.path.join(D, 'recipe', name + '.json'), recipe)

w(os.path.join(D, 'tags', 'block', 'mineable', 'shovel.json'), {'replace': False, 'values': ['modehud:' + n for n in SLABS if n in SHOVEL]})
w(os.path.join(D, 'tags', 'block', 'mineable', 'pickaxe.json'), {'replace': False, 'values': ['modehud:rough_stone_slab']})
w(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block', 'slabs.json'), {'replace': False, 'values': ['modehud:' + n for n in SLABS]})
w(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'item', 'slabs.json'), {'replace': False, 'values': ['modehud:' + n for n in SLABS]})

w(os.path.join(D, 'worldgen', 'configured_feature', 'smooth_terrain.json'), {'type': 'modehud:smooth_terrain', 'config': {}})
w(os.path.join(D, 'worldgen', 'placed_feature', 'smooth_terrain.json'), {'feature': 'modehud:smooth_terrain', 'placement': []})
w(os.path.join(D, 'neoforge', 'biome_modifier', 'smooth_terrain.json'), {
    'type': 'neoforge:add_features', 'biomes': '#minecraft:is_overworld',
    'features': 'modehud:smooth_terrain', 'step': 'top_layer_modification'})
w(os.path.join(D, 'neoforge', 'biome_modifier', 'tarantula_spawn.json'), {
    'type': 'neoforge:add_spawns', 'biomes': '#minecraft:is_overworld',
    'spawners': {'type': 'modehud:tarantula', 'weight': 2, 'minCount': 1, 'maxCount': 1}})

w(os.path.join(D, 'loot_table', 'entities', 'tarantula.json'), {
    'type': 'minecraft:entity',
    'pools': [
        {'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': 'minecraft:string', 'functions': [
            {'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 4.0, 'max': 10.0}}]}]},
        {'rolls': 1.0, 'entries': [{'type': 'minecraft:item', 'name': 'minecraft:spider_eye', 'functions': [
            {'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 2.0, 'max': 5.0}}]}]}]})


def shaped(name, pattern, key, count=1, cat='misc'):
    w(os.path.join(D, 'recipe', name + '.json'), {
        'type': 'minecraft:crafting_shaped', 'category': cat, 'pattern': pattern,
        'key': {k: {'item': v} for k, v in key.items()}, 'result': {'id': 'modehud:' + name, 'count': count}})


shaped('car', ['III', 'BFB', 'WIW'], {'I': 'minecraft:iron_ingot', 'B': 'minecraft:iron_block', 'F': 'minecraft:furnace', 'W': 'minecraft:black_wool'})
shaped('fighter', ['ISI', 'BFB', 'III'], {'I': 'minecraft:iron_ingot', 'S': 'minecraft:dispenser', 'B': 'minecraft:iron_block', 'F': 'minecraft:furnace'})
shaped('bomber', ['BIB', 'IFI', 'TDT'], {'I': 'minecraft:iron_ingot', 'B': 'minecraft:iron_block', 'F': 'minecraft:furnace', 'T': 'minecraft:tnt', 'D': 'minecraft:dispenser'})
shaped('backpack', ['LSL', 'LCL', 'LLL'], {'L': 'minecraft:leather', 'S': 'minecraft:string', 'C': 'minecraft:chest'})

PALETTES = {
    'car': ((200, 40, 40), (30, 30, 30)),
    'fighter': ((70, 80, 100), (20, 25, 35)),
    'bomber': ((45, 50, 55), (15, 15, 20)),
    'backpack': ((120, 85, 50), (60, 40, 25)),
    'tarantula_spawn_egg': ((42, 34, 32), (176, 32, 32)),
}


def png(path, px, size=16):
    raw = b''.join(b'\x00' + b''.join(bytes(px[y][x]) for x in range(size)) for y in range(size))
    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b''))


def icon(name, kind):
    main, dark = PALETTES[name]
    px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    def put(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            px[y][x] = c + (255,)
    if kind == 'car':
        for x in range(2, 14):
            for y in range(7, 12):
                put(x, y, main)
        for x in range(5, 11):
            for y in range(4, 7):
                put(x, y, (150, 200, 230))
        for cx in (4, 11):
            for dx in range(3):
                for dy in range(3):
                    put(cx + dx - 1, 12 + dy, dark)
    elif kind in ('fighter', 'bomber'):
        for y in range(2, 14):
            half = 1 if kind == 'fighter' and y < 8 else (y - 3 if kind == 'fighter' else 1 + (y - 2) * 6 // 11)
            half = max(1, min(half, 7))
            for x in range(8 - half, 8 + half):
                put(x, y, main if (x + y) % 5 else dark)
        put(7, 4, (150, 200, 230)); put(8, 4, (150, 200, 230))
    elif kind == 'backpack':
        for x in range(3, 13):
            for y in range(3, 14):
                put(x, y, main)
        for x in range(3, 13):
            put(x, 3, dark); put(x, 13, dark)
        for y in range(3, 14):
            put(3, y, dark); put(12, y, dark)
        for x in range(5, 11):
            for y in range(8, 12):
                put(x, y, dark)
        for x in range(6, 10):
            put(x, 2, dark)
    else:
        for x in range(3, 13):
            for y in range(4, 13):
                if (x - 7.5) ** 2 / 25 + (y - 8.5) ** 2 / 20 <= 1:
                    put(x, y, main)
        for x in (5, 6, 9, 10):
            for y in (6, 7):
                put(x, y, dark)
    png(os.path.join(A, 'textures', 'item', name + '.png'), px)
    w(os.path.join(A, 'models', 'item', name + '.json'), {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'modehud:item/' + name}})


for n, k in (('car', 'car'), ('fighter', 'fighter'), ('bomber', 'bomber'), ('backpack', 'backpack'), ('tarantula_spawn_egg', 'egg')):
    icon(n, k)

for n, c in (('missile', (200, 200, 205)), ('bomb', (50, 50, 55)), ('web_shot', (235, 235, 235))):
    px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    for x in range(16):
        for y in range(16):
            if n == 'web_shot':
                if x == 8 or y == 8 or x == y or x + y == 15:
                    px[y][x] = c + (255,)
            elif n == 'bomb':
                if (x - 7.5) ** 2 + (y - 8.5) ** 2 <= 20:
                    px[y][x] = c + (255,)
            elif 6 <= x <= 9 and 2 <= y <= 13:
                px[y][x] = (c if y > 4 else (200, 50, 40)) + (255,)
    png(os.path.join(A, 'textures', 'item', n + '.png'), px)
    w(os.path.join(A, 'models', 'item', n + '.json'), {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'modehud:item/' + n}})

for lang, tr in (('en_us', {
    'item.modehud.car': 'Car', 'item.modehud.fighter': 'Stealth Fighter', 'item.modehud.bomber': 'Flying Wing Bomber',
    'item.modehud.backpack': 'Backpack', 'item.modehud.tarantula_spawn_egg': 'Tarantula Spawn Egg',
    'item.modehud.missile': 'Missile', 'item.modehud.bomb': 'Bomb', 'item.modehud.web_shot': 'Web Shot',
    'entity.modehud.car': 'Car', 'entity.modehud.fighter': 'Stealth Fighter', 'entity.modehud.bomber': 'Flying Wing Bomber',
    'entity.modehud.tarantula': 'Giant Tarantula', 'entity.modehud.missile': 'Missile', 'entity.modehud.bomb': 'Bomb',
    'entity.modehud.web_shot': 'Web Shot',
    'key.categories.modehud': 'Mode HUD', 'key.modehud.open_backpack': 'Open backpack',
    'key.modehud.take_off_backpack': 'Take off backpack', 'key.modehud.exit_vehicle': 'Exit vehicle',
    'message.modehud.backpack_worn': 'Backpack equipped', 'message.modehud.no_backpack': 'No backpack on your back',
    'message.modehud.land_first': 'Land before leaving the aircraft', 'message.modehud.crash': 'Crashed!',
    'block.modehud.grass_slab': 'Grass Slab', 'block.modehud.dirt_slab': 'Dirt Slab',
    'block.modehud.coarse_dirt_slab': 'Coarse Dirt Slab', 'block.modehud.podzol_slab': 'Podzol Slab',
    'block.modehud.mycelium_slab': 'Mycelium Slab', 'block.modehud.sand_slab': 'Sand Slab',
    'block.modehud.red_sand_slab': 'Red Sand Slab', 'block.modehud.gravel_slab': 'Gravel Slab',
    'block.modehud.mud_slab': 'Mud Slab', 'block.modehud.rough_stone_slab': 'Stone Terrain Slab',
    'block.modehud.clay_slab': 'Clay Slab',
}), ('ru_ru', {
    'item.modehud.car': 'Машина', 'item.modehud.fighter': 'Истребитель', 'item.modehud.bomber': 'Бомбардировщик',
    'item.modehud.backpack': 'Рюкзак', 'item.modehud.tarantula_spawn_egg': 'Яйцо призыва тарантула',
    'item.modehud.missile': 'Ракета', 'item.modehud.bomb': 'Бомба', 'item.modehud.web_shot': 'Паутина',
    'entity.modehud.car': 'Машина', 'entity.modehud.fighter': 'Истребитель', 'entity.modehud.bomber': 'Бомбардировщик',
    'entity.modehud.tarantula': 'Гигантский тарантул', 'entity.modehud.missile': 'Ракета', 'entity.modehud.bomb': 'Бомба',
    'entity.modehud.web_shot': 'Паутина',
    'key.categories.modehud': 'Mode HUD', 'key.modehud.open_backpack': 'Открыть рюкзак',
    'key.modehud.take_off_backpack': 'Снять рюкзак', 'key.modehud.exit_vehicle': 'Выйти из транспорта',
    'message.modehud.backpack_worn': 'Рюкзак надет', 'message.modehud.no_backpack': 'На спине нет рюкзака',
    'message.modehud.land_first': 'Сначала приземлитесь', 'message.modehud.crash': 'Крушение!',
    'block.modehud.grass_slab': 'Травяной полублок', 'block.modehud.dirt_slab': 'Земляной полублок',
    'block.modehud.coarse_dirt_slab': 'Полублок каменистой земли', 'block.modehud.podzol_slab': 'Полублок подзола',
    'block.modehud.mycelium_slab': 'Полублок мицелия', 'block.modehud.sand_slab': 'Песчаный полублок',
    'block.modehud.red_sand_slab': 'Полублок красного песка', 'block.modehud.gravel_slab': 'Гравийный полублок',
    'block.modehud.mud_slab': 'Грязевой полублок', 'block.modehud.rough_stone_slab': 'Каменный полублок рельефа',
    'block.modehud.clay_slab': 'Глиняный полублок',
})):
    p = os.path.join(A, 'lang', lang + '.json')
    cur = json.load(open(p, encoding='utf-8'))
    cur.update(tr)
    w(p, cur)
print('ok')
