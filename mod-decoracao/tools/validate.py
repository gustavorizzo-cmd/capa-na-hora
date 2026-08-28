#!/usr/bin/env python3
"""Confere o add-on antes de empacotar.

Verifica: JSON valido, manifests coerentes, e que toda textura/modelo citado
por um bloco realmente existe no resource pack.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BP = os.path.join(ROOT, "behavior_pack")
RP = os.path.join(ROOT, "resource_pack")

errors = []
warnings = []


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        errors.append(f"JSON invalido em {os.path.relpath(path, ROOT)}: {exc}")
        return None


def main():
    # ---- manifests
    bp = load(os.path.join(BP, "manifest.json"))
    rp = load(os.path.join(RP, "manifest.json"))
    if bp and rp:
        dep = [d["uuid"] for d in bp.get("dependencies", [])]
        if rp["header"]["uuid"] not in dep:
            errors.append("O behavior pack nao depende do UUID do resource pack.")
        uuids = [bp["header"]["uuid"], rp["header"]["uuid"]]
        uuids += [m["uuid"] for m in bp["modules"] + rp["modules"]]
        if len(set(uuids)) != len(uuids):
            errors.append("Ha UUIDs repetidos entre header/modules.")

    for pack in (BP, RP):
        if not os.path.exists(os.path.join(pack, "pack_icon.png")):
            warnings.append(f"Sem pack_icon.png em {os.path.basename(pack)}")

    # ---- texturas registradas
    tt = load(os.path.join(RP, "textures", "terrain_texture.json")) or {}
    registered = tt.get("texture_data", {})
    for key, val in registered.items():
        rel = val["textures"] + ".png"
        if not os.path.exists(os.path.join(RP, rel)):
            errors.append(f"terrain_texture.json aponta para {rel}, que nao existe.")

    # ---- modelos disponiveis
    geos = {"minecraft:geometry.full_block"}
    mdir = os.path.join(RP, "models", "blocks")
    for name in os.listdir(mdir):
        data = load(os.path.join(mdir, name)) or {}
        for geo in data.get("minecraft:geometry", []):
            geos.add(geo["description"]["identifier"])

    # ---- blocos
    ids = set()
    bdir = os.path.join(BP, "blocks")
    files = sorted(os.listdir(bdir))
    for name in files:
        data = load(os.path.join(bdir, name))
        if not data:
            continue
        block = data.get("minecraft:block", {})
        desc = block.get("description", {})
        comp = block.get("components", {})
        ident = desc.get("identifier", "")
        if not ident.startswith("deco:"):
            errors.append(f"{name}: identifier ausente ou fora do namespace deco.")
        if ident in ids:
            errors.append(f"{name}: identifier duplicado {ident}")
        ids.add(ident)

        geo = comp.get("minecraft:geometry")
        geo_id = geo if isinstance(geo, str) else (geo or {}).get("identifier")
        if geo_id not in geos:
            errors.append(f"{name}: geometria '{geo_id}' nao encontrada.")

        for face, inst in comp.get("minecraft:material_instances", {}).items():
            tex = inst.get("texture")
            if tex not in registered:
                errors.append(f"{name}: textura '{tex}' nao esta no terrain_texture.json.")

        if "minecraft:display_name" not in comp:
            warnings.append(f"{name}: sem minecraft:display_name.")

    # ---- traducoes
    lang = os.path.join(RP, "texts", "pt_BR.lang")
    text = open(lang, encoding="utf-8").read() if os.path.exists(lang) else ""
    for ident in sorted(ids):
        if f"tile.{ident}.name=" not in text:
            warnings.append(f"pt_BR.lang sem traducao para {ident}")

    print(f"{len(files)} blocos, {len(registered)} texturas, {len(geos) - 1} modelos.")
    for w in warnings:
        print("AVISO:", w)
    for e in errors:
        print("ERRO:", e)
    if errors:
        sys.exit(1)
    print("OK - add-on valido.")


if __name__ == "__main__":
    main()
