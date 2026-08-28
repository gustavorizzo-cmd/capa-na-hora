#!/usr/bin/env python3
"""Gera os modelos (.geo.json) dos blocos do add-on Decoracao+.

Cada modelo usa uma unica textura 32x32 dividida em 4 regioes de 16x16
(A/B/C/D). Cada face de cada cubo aponta para uma regiao inteira, entao o
padrao da regiao aparece esticado na face - o que funciona bem porque todas
as regioes sao padroes uniformes.

Espaco do modelo: X e Z de -8 a 8, Y de 0 a 16 (o cubo do bloco).
"""
import json, os, re

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "resource_pack", "models", "blocks")

REG = {"A": [0, 0], "B": [16, 0], "C": [0, 16], "D": [16, 16]}
FACES = ("north", "south", "east", "west", "up", "down")


def cube(origin, size, region="A", faces=None, rotation=None, pivot=None):
    """faces: dict opcional {'up':'B', ...} sobrescrevendo a regiao padrao."""
    faces = faces or {}
    uv = {}
    for f in FACES:
        uv[f] = {"uv": list(REG[faces.get(f, region)]), "uv_size": [16, 16]}
    c = {"origin": list(origin), "size": list(size), "uv": uv}
    if rotation:
        c["rotation"] = list(rotation)
        c["pivot"] = list(pivot or [0, 0, 0])
    return c


def model(identifier, cubes, bounds_w=1.6, bounds_h=1.6, bounds_off=(0, 0.6, 0)):
    return {
        "description": {
            "identifier": identifier,
            "texture_width": 32,
            "texture_height": 32,
            "visible_bounds_width": bounds_w,
            "visible_bounds_height": bounds_h,
            "visible_bounds_offset": list(bounds_off),
        },
        "bones": [{"name": "root", "pivot": [0, 0, 0], "cubes": cubes}],
    }


MODELS = {}

# ------------------------------------------------------------------- vaso
MODELS["deco_vaso"] = model("geometry.deco_vaso", [
    # corpo do vaso (A), boca do vaso mostrando a terra (B) no topo
    cube([-4, 0, -4], [8, 7, 8], "A"),
    cube([-5, 7, -5], [10, 2, 10], "A", faces={"up": "B"}),
    # planta em cruz (C, com transparencia)
    cube([-6, 8, 0], [12, 8, 0], "C", rotation=[0, 45, 0], pivot=[0, 8, 0]),
    cube([-6, 8, 0], [12, 8, 0], "C", rotation=[0, -45, 0], pivot=[0, 8, 0]),
], 1.4, 1.4, (0, 0.6, 0))

# ------------------------------------------------------------- luminaria
MODELS["deco_luminaria"] = model("geometry.deco_luminaria", [
    cube([-1, 13, -1], [2, 3, 2], "A"),                       # fio/haste
    cube([-6, 9, -6], [12, 3, 12], "B", faces={"down": "C"}),  # cupula
    cube([-4, 12, -4], [8, 1, 8], "B"),                        # topo da cupula
    cube([-3, 7, -3], [6, 2, 6], "C"),                         # lampada acesa
], 1.4, 1.4, (0, 0.7, 0))

# ---------------------------------------------------------------- abajur
MODELS["deco_abajur"] = model("geometry.deco_abajur", [
    cube([-3, 0, -3], [6, 1, 6], "D"),   # base
    cube([-1, 1, -1], [2, 5, 2], "A"),   # haste
    cube([-3, 5, -3], [6, 1, 6], "C"),   # lampada
    cube([-4, 6, -4], [8, 5, 8], "B", faces={"up": "C"}),  # cupula
], 1.2, 1.2, (0, 0.4, 0))

# ------------------------------------------------------------------ mesa
MODELS["deco_mesa"] = model("geometry.deco_mesa", [
    cube([-8, 7, -8], [16, 2, 16], "B", faces={"up": "A"}),
    cube([-7, 0, -7], [2, 7, 2], "D"),
    cube([5, 0, -7], [2, 7, 2], "D"),
    cube([-7, 0, 5], [2, 7, 2], "D"),
    cube([5, 0, 5], [2, 7, 2], "D"),
], 1.2, 1.0, (0, 0.3, 0))

# -------------------------------------------------------------- almofada
MODELS["deco_almofada"] = model("geometry.deco_almofada", [
    cube([-6, 0, -6], [12, 4, 12], "B", faces={"up": "A", "down": "D"}),
    cube([-5, 4, -5], [10, 1, 10], "A"),
], 1.0, 0.6, (0, 0.2, 0))

# ---------------------------------------------------------------- tapete
MODELS["deco_tapete"] = model("geometry.deco_tapete", [
    cube([-8, 0, -8], [16, 1, 16], "B", faces={"up": "A", "down": "B"}),
], 1.2, 0.4, (0, 0.05, 0))

# ----------------------------------------------------------------- pilar
MODELS["deco_pilar"] = model("geometry.deco_pilar", [
    cube([-7, 0, -7], [14, 2, 14], "B"),
    cube([-5, 2, -5], [10, 12, 10], "A", faces={"up": "B", "down": "B"}),
    cube([-7, 14, -7], [14, 2, 14], "B"),
], 1.2, 1.2, (0, 0.5, 0))


def dumps(data):
    """JSON identado, mas com listas de numeros em uma linha so."""
    text = json.dumps(data, indent=2, ensure_ascii=False)
    return re.sub(r"\[\s*(-?[\d.]+(?:,\s*-?[\d.]+)*)\s*\]",
                  lambda m: "[" + ", ".join(m.group(1).split()).replace(",,", ",") + "]",
                  text)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, geo in MODELS.items():
        path = os.path.join(OUT, f"{name}.geo.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(dumps({"format_version": "1.12.0", "minecraft:geometry": [geo]}) + "\n")
        print("  ", os.path.basename(path))
    print("OK - modelos gerados em", OUT)


if __name__ == "__main__":
    main()
