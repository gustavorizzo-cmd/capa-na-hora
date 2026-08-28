#!/usr/bin/env python3
"""Gera o pack_icon.png (128x128) usado pelos dois pacotes do add-on."""
import os, sys, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_textures import write_png, canvas, put, rect, mix, shade  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scene():
    rng = random.Random(4242)
    W = H = 32
    img = canvas(W, H, (0, 0, 0, 255))

    wall_a, wall_b = (96, 136, 194, 255), (58, 92, 148, 255)
    stripe = (46, 74, 124, 255)
    motif = (206, 224, 248, 255)
    for y in range(24):
        for x in range(W):
            img[y][x] = mix(wall_a, wall_b, y / 24)
            if x % 4 == 0:
                img[y][x] = mix(img[y][x], stripe, 0.5)
    for cx, cy in ((4, 5), (12, 5), (20, 5), (28, 5), (8, 14), (16, 14), (24, 14)):
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)):
            put(img, cx + dx, cy + dy, motif)

    floor = (150, 108, 66, 255)
    for y in range(24, H):
        for x in range(W):
            img[y][x] = shade(floor, 1 + rng.uniform(-0.08, 0.08))
        if y in (26, 29):
            for x in range(W):
                img[y][x] = shade(floor, 0.75)

    rug, gold = (150, 40, 44, 255), (214, 176, 84, 255)
    rect(img, 5, 27, 22, 5, rug)
    for x in range(5, 27):
        put(img, x, 27, gold); put(img, x, 31, gold)
    for y in range(27, 32):
        put(img, 5, y, gold); put(img, 26, y, gold)
    for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        put(img, 15 + dx, 29 + dy, gold)

    # vaso com planta
    pot = (176, 96, 62, 255)
    rect(img, 5, 20, 7, 5, pot)
    rect(img, 4, 18, 9, 2, shade(pot, 1.15))
    rect(img, 5, 18, 7, 1, (74, 52, 36, 255))
    for cx, cy, r in ((8, 13, 4), (5, 15, 3), (11, 15, 3), (8, 9, 3)):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    put(img, x, y, rng.choice([(58, 140, 60, 255), (86, 176, 76, 255),
                                               (36, 100, 46, 255)]))

    # abajur com luz
    lamp_glow = (255, 238, 176, 255)
    for y in range(10, 26):
        for x in range(17, 30):
            d = ((x - 23.5) ** 2 + (y - 16) ** 2) ** .5
            if d < 8:
                img[y][x] = mix(img[y][x], lamp_glow, max(0, (8 - d) / 8) * 0.45)
    rect(img, 21, 23, 5, 2, (126, 88, 52, 255))
    rect(img, 23, 18, 1, 5, (126, 88, 52, 255))
    rect(img, 20, 13, 7, 5, (238, 224, 190, 255))
    rect(img, 20, 17, 7, 1, lamp_glow)
    rect(img, 21, 12, 5, 1, (206, 182, 138, 255))

    # moldura
    for i in range(W):
        img[0][i] = (32, 32, 38, 255); img[H - 1][i] = (32, 32, 38, 255)
        img[i][0] = (32, 32, 38, 255); img[i][W - 1] = (32, 32, 38, 255)
    return img


def main():
    small = scene()
    S = 4
    big = canvas(32 * S, 32 * S)
    for y in range(32 * S):
        for x in range(32 * S):
            big[y][x] = small[y // S][x // S]
    for p in ("behavior_pack", "resource_pack"):
        write_png(os.path.join(ROOT, p, "pack_icon.png"), big)
    print("OK - icones gerados")


if __name__ == "__main__":
    main()
