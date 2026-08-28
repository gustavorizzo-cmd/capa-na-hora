#!/usr/bin/env python3
"""Gera todas as texturas PNG do add-on Decoracao+ (sem dependencias externas).

Texturas de bloco cheio: 16x16.
Texturas de blocos com modelo proprio: 32x32, divididas em 4 regioes de 16x16:
    A = (0,0)   B = (16,0)
    C = (0,16)  D = (16,16)
O gerador de modelos (gen_models.py) mapeia cada face de cada cubo em uma
dessas regioes, entao qualquer padrao uniforme dentro da regiao fica correto.
"""
import os, math, random, zlib, struct

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "resource_pack", "textures", "blocks")


# ---------------------------------------------------------------- PNG writer
def write_png(path, px):
    h = len(px)
    w = len(px[0])
    raw = b"".join(b"\x00" + bytes(v for p in row for v in p) for row in px)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    print("  ", os.path.basename(path), f"{w}x{h}")


def canvas(w, h, color=(0, 0, 0, 0)):
    return [[color for _ in range(w)] for _ in range(h)]


def put(img, x, y, c):
    if 0 <= y < len(img) and 0 <= x < len(img[0]):
        img[y][x] = c


def rect(img, x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(img, x, y, c)


def shade(c, f):
    r, g, b, a = c
    return (max(0, min(255, int(r * f))), max(0, min(255, int(g * f))),
            max(0, min(255, int(b * f))), a)


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def noise(img, x0, y0, w, h, rng, amount=0.06):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            c = img[y][x]
            if c[3] == 0:
                continue
            img[y][x] = shade(c, 1 + rng.uniform(-amount, amount))


# ------------------------------------------------------------ block textures
def marble(base, vein, dark, seed):
    rng = random.Random(seed)
    img = canvas(16, 16, base)
    for y in range(16):
        for x in range(16):
            img[y][x] = shade(base, 1 + rng.uniform(-0.025, 0.025))
    # veios diagonais
    for k in range(3):
        x = rng.randint(-6, 14)
        y = 0
        while y < 16:
            put(img, x, y, vein)
            if rng.random() < 0.45:
                put(img, x + 1, y, mix(vein, base, 0.55))
            if rng.random() < 0.3:
                put(img, x - 1, y, mix(vein, base, 0.7))
            x += rng.choice([0, 1, 1, 2])
            y += 1
    for _ in range(10):
        put(img, rng.randint(0, 15), rng.randint(0, 15), mix(base, dark, 0.35))
    return img


def wallpaper(top, bottom, stripe, motif, seed):
    rng = random.Random(seed)
    img = canvas(16, 16)
    for y in range(16):
        for x in range(16):
            img[y][x] = mix(top, bottom, y / 15)
    # listras verticais
    for x in range(0, 16, 4):
        for y in range(16):
            img[y][x] = mix(img[y][x], stripe, 0.55)
            img[y][(x + 1) % 16] = mix(img[y][(x + 1) % 16], stripe, 0.18)
    # motivo damasco simples
    for cx, cy in ((2, 3), (10, 3), (6, 11), (14, 11)):
        for dx, dy, t in ((0, -2, .9), (0, 2, .9), (-2, 0, .9), (2, 0, .9),
                          (0, -1, 1), (0, 1, 1), (-1, 0, 1), (1, 0, 1), (0, 0, 1),
                          (-1, -1, .5), (1, -1, .5), (-1, 1, .5), (1, 1, .5)):
            x, y = (cx + dx) % 16, (cy + dy) % 16
            img[y][x] = mix(img[y][x], motif, t)
    noise(img, 0, 0, 16, 16, rng, 0.035)
    return img


def bookshelf():
    rng = random.Random(77)
    wood = (110, 78, 46, 255)
    img = canvas(16, 16, wood)
    noise(img, 0, 0, 16, 16, rng, 0.09)
    rect(img, 0, 0, 16, 2, shade(wood, 0.8))
    rect(img, 0, 14, 16, 2, shade(wood, 0.8))
    rect(img, 0, 7, 16, 2, shade(wood, 0.72))
    colors = [(168, 48, 48, 255), (52, 96, 168, 255), (58, 138, 70, 255),
              (176, 138, 48, 255), (128, 60, 150, 255), (196, 196, 190, 255),
              (150, 84, 40, 255), (40, 130, 140, 255)]
    for shelf_y in (2, 9):
        x = 1
        while x < 15:
            w = rng.choice([1, 1, 2])
            if x + w > 15:
                w = 15 - x
            c = colors[rng.randrange(len(colors))]
            hgt = 5 - rng.choice([0, 0, 1])
            rect(img, x, shelf_y + (5 - hgt), w, hgt, c)
            put(img, x, shelf_y + (5 - hgt), shade(c, 1.25))
            if w == 2:
                put(img, x + 1, shelf_y + (5 - hgt), shade(c, 1.25))
            rect(img, x, shelf_y + 4, w, 1, shade(c, 0.7))
            x += w + rng.choice([0, 0, 1])
    return img


def crystal():
    rng = random.Random(9)
    base = (126, 92, 210, 255)
    img = canvas(16, 16, base)
    for y in range(16):
        for x in range(16):
            d = abs(x - 8) + abs(y - 8)
            img[y][x] = mix((228, 214, 255, 255), (86, 52, 168, 255), min(1, d / 14))
    # facetas
    for k in range(5):
        x0 = rng.randint(0, 15)
        y = 0
        x = x0
        while y < 16:
            put(img, x % 16, y, mix(img[y][x % 16], (255, 250, 255, 255), 0.55))
            x += rng.choice([0, 1])
            y += 1
    for _ in range(14):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        put(img, x, y, (255, 255, 255, 255))
    noise(img, 0, 0, 16, 16, rng, 0.05)
    return img


def aquarium():
    rng = random.Random(31)
    img = canvas(16, 16)
    for y in range(16):
        for x in range(16):
            img[y][x] = mix((92, 190, 226, 190), (24, 96, 168, 205), y / 15)
    # areia no fundo
    for y in range(13, 16):
        for x in range(16):
            img[y][x] = mix((214, 196, 148, 255), (176, 156, 112, 255), rng.random())
    # plantas
    for x in (3, 4, 11):
        h = rng.randint(4, 7)
        for i in range(h):
            put(img, x + (i % 2), 13 - i, (48, 138, 64, 255))
    # peixinho
    fish = (240, 156, 52, 255)
    for dx, dy in ((0, 0), (1, 0), (2, 0), (1, -1), (2, -1), (3, 0), (0, -1)):
        put(img, 7 + dx, 6 + dy, fish)
    put(img, 6, 6, shade(fish, 0.75))
    put(img, 6, 5, shade(fish, 0.75))
    put(img, 10, 5, (20, 20, 20, 255))
    # bolhas
    for x, y in ((12, 4), (13, 8), (12, 11), (2, 3)):
        put(img, x, y, (226, 246, 255, 225))
    # moldura de vidro
    for i in range(16):
        img[0][i] = mix(img[0][i], (236, 250, 255, 235), 0.7)
        img[15][i] = mix(img[15][i], (120, 130, 140, 255), 0.5)
        img[i][0] = mix(img[i][0], (236, 250, 255, 235), 0.6)
        img[i][15] = mix(img[i][15], (236, 250, 255, 235), 0.6)
    return img


# ------------------------------------------- texturas 32x32 (4 regioes 16x16)
REG = {"A": (0, 0), "B": (16, 0), "C": (0, 16), "D": (16, 16)}


def atlas():
    return canvas(32, 32)


def fill_region(img, key, fn):
    ox, oy = REG[key]
    tile = fn()
    for y in range(16):
        for x in range(16):
            img[oy + y][ox + x] = tile[y][x]


def flat(color, seed=1, amount=0.07, edge=None):
    def f():
        rng = random.Random(seed)
        img = canvas(16, 16, color)
        noise(img, 0, 0, 16, 16, rng, amount)
        if edge:
            for i in range(16):
                img[0][i] = edge
                img[15][i] = shade(edge, 0.8)
        return img
    return f


def planks(color, seed=2):
    def f():
        rng = random.Random(seed)
        img = canvas(16, 16, color)
        noise(img, 0, 0, 16, 16, rng, 0.08)
        for y in (0, 5, 10, 15):
            for x in range(16):
                img[y][x] = shade(color, 0.72)
        for _ in range(18):
            x, y = rng.randint(0, 15), rng.randint(0, 15)
            img[y][x] = shade(color, rng.choice([0.85, 1.14]))
        return img
    return f


def terracotta(seed=3):
    def f():
        rng = random.Random(seed)
        base = (176, 96, 62, 255)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, rng, 0.1)
        for y in range(16):
            for x in range(16):
                img[y][x] = mix(img[y][x], shade(base, 0.72), (x / 15) * 0.35)
        for x in range(16):
            img[0][x] = shade(base, 1.2)
            img[1][x] = shade(base, 1.1)
        for _ in range(12):
            put(img, rng.randint(0, 15), rng.randint(2, 15), shade(base, 0.8))
        return img
    return f


def ceramic(seed=4):
    def f():
        rng = random.Random(seed)
        base = (232, 232, 226, 255)
        blue = (74, 112, 176, 255)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, rng, 0.03)
        for x in range(16):
            img[4][x] = blue
            img[5][x] = mix(blue, base, 0.55)
            img[11][x] = mix(blue, base, 0.55)
        for x in range(0, 16, 4):
            put(img, x, 8, blue)
            put(img, x + 1, 9, blue)
            put(img, x + 2, 8, blue)
        return img
    return f


def soil(seed=5):
    def f():
        rng = random.Random(seed)
        base = (74, 52, 36, 255)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, rng, 0.16)
        for _ in range(10):
            put(img, rng.randint(0, 15), rng.randint(0, 15), (52, 36, 24, 255))
        return img
    return f


def leaves(seed=6):
    """Folhagem com fundo transparente (usa alpha_test)."""
    def f():
        rng = random.Random(seed)
        img = canvas(16, 16)
        g1, g2, g3 = (58, 140, 60, 255), (86, 176, 76, 255), (36, 100, 46, 255)
        stem = (72, 108, 48, 255)
        for y in range(4, 16):
            put(img, 7, y, stem)
            put(img, 8, y, shade(stem, 0.85))
        blobs = [(4, 6, 3), (11, 5, 3), (7, 2, 3), (3, 10, 2), (12, 10, 2), (8, 8, 3)]
        for cx, cy, r in blobs:
            for y in range(cy - r, cy + r + 1):
                for x in range(cx - r, cx + r + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 1:
                        c = rng.choice([g1, g1, g2, g3])
                        put(img, x, y, c)
        for _ in range(16):
            x, y = rng.randint(0, 15), rng.randint(0, 15)
            if img[y][x][3]:
                img[y][x] = shade(img[y][x], rng.choice([0.85, 1.15]))
        return img
    return f


def flowers(seed=7):
    def f():
        rng = random.Random(seed)
        img = leaves(seed + 1)()
        petals = [(236, 128, 172, 255), (244, 176, 200, 255), (250, 222, 120, 255)]
        for cx, cy in ((4, 5), (11, 4), (8, 9), (13, 9)):
            p = rng.choice(petals)
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                put(img, cx + dx, cy + dy, p)
            put(img, cx, cy, (252, 226, 120, 255))
        return img
    return f


def glow(c1=(255, 244, 186, 255), c2=(255, 214, 118, 255), seed=8):
    def f():
        rng = random.Random(seed)
        img = canvas(16, 16)
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - 7.5, y - 7.5) / 11
                img[y][x] = mix(c1, c2, min(1, d))
        for _ in range(8):
            put(img, rng.randint(0, 15), rng.randint(0, 15), (255, 255, 236, 255))
        return img
    return f


def metal(base=(62, 62, 72, 255), seed=9):
    def f():
        rng = random.Random(seed)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, rng, 0.12)
        for x in range(16):
            img[0][x] = shade(base, 1.35)
            img[15][x] = shade(base, 0.7)
        for y in range(2, 15, 4):
            for x in range(16):
                img[y][x] = shade(base, 1.15)
        return img
    return f


def fabric(base, stripe, seed=10, diag=False):
    def f():
        rng = random.Random(seed)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, rng, 0.05)
        if diag:
            for y in range(16):
                for x in range(16):
                    if (x + y) % 6 < 2:
                        img[y][x] = mix(img[y][x], stripe, 0.6)
        else:
            for x in range(0, 16, 5):
                for y in range(16):
                    img[y][x] = mix(img[y][x], stripe, 0.7)
        return img
    return f


def rug_top(seed=11):
    def f():
        rng = random.Random(seed)
        base = (150, 40, 44, 255)
        gold = (214, 176, 84, 255)
        cream = (238, 226, 200, 255)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, rng, 0.05)
        for i in range(16):
            img[0][i] = gold; img[15][i] = gold
            img[i][0] = gold; img[i][15] = gold
            img[1][i] = mix(base, gold, 0.25); img[14][i] = mix(base, gold, 0.25)
            img[i][1] = mix(base, gold, 0.25); img[i][14] = mix(base, gold, 0.25)
        for i in range(3, 13):
            img[3][i] = cream; img[12][i] = cream
            img[i][3] = cream; img[i][12] = cream
        for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0), (0, -1), (0, 1),
                       (-1, 0), (1, 0), (0, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            put(img, 7 + dx, 7 + dy, gold)
        put(img, 7, 7, cream)
        return img
    return f


def rug_side(seed=12):
    def f():
        base = (120, 32, 36, 255)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, random.Random(seed), 0.08)
        for x in range(0, 16, 2):
            for y in range(0, 5):
                put(img, x, y, (222, 208, 176, 255))
        return img
    return f


def marble_col(seed=13):
    def f():
        rng = random.Random(seed)
        base = (238, 236, 228, 255)
        img = canvas(16, 16, base)
        noise(img, 0, 0, 16, 16, rng, 0.03)
        for x in range(0, 16, 3):
            for y in range(16):
                img[y][x] = shade(base, 0.86)
                if x + 1 < 16:
                    img[y][x + 1] = shade(base, 1.03)
        for k in range(2):
            x = rng.randint(0, 15)
            for y in range(16):
                img[y][x % 16] = mix(img[y][x % 16], (178, 176, 170, 255), 0.5)
                x += rng.choice([0, 0, 1])
        return img
    return f


# ---------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    print("Texturas de bloco cheio (16x16):")
    write_png(f"{OUT}/deco_marmore_polido.png",
              marble((240, 238, 231, 255), (188, 186, 180, 255), (140, 138, 132, 255), 1))
    write_png(f"{OUT}/deco_marmore_preto.png",
              marble((44, 44, 52, 255), (122, 122, 138, 255), (20, 20, 26, 255), 2))
    write_png(f"{OUT}/deco_marmore_dourado.png",
              marble((246, 240, 226, 255), (212, 175, 55, 255), (168, 132, 40, 255), 3))
    write_png(f"{OUT}/deco_papel_azul.png",
              wallpaper((92, 132, 190, 255), (58, 92, 148, 255), (46, 74, 124, 255),
                        (206, 224, 248, 255), 4))
    write_png(f"{OUT}/deco_papel_rosa.png",
              wallpaper((216, 152, 176, 255), (176, 108, 138, 255), (150, 84, 116, 255),
                        (250, 226, 236, 255), 5))
    write_png(f"{OUT}/deco_papel_verde.png",
              wallpaper((104, 150, 108, 255), (66, 108, 74, 255), (52, 88, 60, 255),
                        (222, 240, 214, 255), 6))
    write_png(f"{OUT}/deco_estante.png", bookshelf())
    write_png(f"{OUT}/deco_cristal.png", crystal())
    write_png(f"{OUT}/deco_aquario.png", aquarium())

    print("Texturas de modelos (32x32, regioes A/B/C/D):")

    def build(name, a, b, c, d):
        img = atlas()
        for key, fn in (("A", a), ("B", b), ("C", c), ("D", d)):
            fill_region(img, key, fn)
        write_png(f"{OUT}/{name}.png", img)

    build("deco_vaso_planta", terracotta(), soil(), leaves(), flat((150, 80, 52, 255), 21))
    build("deco_vaso_flor", ceramic(), soil(9), flowers(), flat((190, 200, 214, 255), 22))
    build("deco_luminaria", metal((52, 52, 60, 255)), metal((92, 76, 44, 255), 14),
          glow(), flat((36, 36, 42, 255), 23))
    build("deco_abajur", planks((126, 88, 52, 255)), fabric((238, 224, 190, 255),
          (206, 182, 138, 255), 15), glow((255, 238, 196, 255), (250, 206, 132, 255)),
          flat((92, 64, 40, 255), 24))
    build("deco_mesa", planks((160, 116, 70, 255), 16), planks((124, 86, 50, 255), 17),
          planks((104, 72, 42, 255), 18), flat((96, 66, 38, 255), 25))
    build("deco_almofada", fabric((186, 92, 108, 255), (146, 62, 82, 255), 19, diag=True),
          fabric((156, 70, 88, 255), (120, 48, 66, 255), 20), flat((210, 120, 134, 255), 26),
          flat((120, 48, 66, 255), 27))
    build("deco_tapete", rug_top(), rug_side(), rug_top(28), rug_side(29))
    build("deco_pilar", marble_col(), flat((222, 220, 212, 255), 30, 0.03),
          marble_col(31), flat((208, 206, 198, 255), 32, 0.03))

    print("OK - texturas geradas em", OUT)


if __name__ == "__main__":
    main()
