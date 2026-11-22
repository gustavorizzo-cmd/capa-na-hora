"""Gera os assets do Mini Minecraft 2D com o Blender (por script).

Uso:
    python gerar_assets.py            (com o módulo bpy instalado: pip install bpy)
    blender -b -P gerar_assets.py     (com o Blender instalado)

Saída em ../assets/ (relativo a este arquivo).
"""
import math
import os
import random

import bpy
import bmesh
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.normpath(os.path.join(AQUI, "..", "assets"))
for sub in ("blocos", "icones", "personagem", "cenario", "fonte"):
    os.makedirs(os.path.join(SAIDA, sub), exist_ok=True)


# ---------------------------------------------------------------- utilidades
def cena_nova(res_x, res_y, amostras=48):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = amostras
    sc.cycles.use_denoising = False
    sc.cycles.filter_width = 0.8
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    mundo = bpy.data.worlds.new("Mundo")
    mundo.use_nodes = True
    fundo = mundo.node_tree.nodes.get("Background")
    fundo.inputs["Color"].default_value = (0.62, 0.78, 1.0, 1)
    fundo.inputs["Strength"].default_value = 0.55
    sc.world = mundo
    return sc


def sol(rot_graus=(50, -25, -35), forca=3.2):
    dados = bpy.data.lights.new("Sol", "SUN")
    dados.energy = forca
    dados.angle = math.radians(8)
    ob = bpy.data.objects.new("Sol", dados)
    ob.rotation_euler = [math.radians(a) for a in rot_graus]
    bpy.context.collection.objects.link(ob)
    return ob


def camera_orto(local, rot_graus, escala, ajuste="AUTO"):
    dados = bpy.data.cameras.new("Cam")
    dados.type = "ORTHO"
    dados.ortho_scale = escala
    dados.sensor_fit = ajuste
    ob = bpy.data.objects.new("Cam", dados)
    ob.location = local
    ob.rotation_euler = [math.radians(a) for a in rot_graus]
    bpy.context.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def render(caminho):
    sc = bpy.context.scene
    sc.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    print("  ->", os.path.relpath(caminho, SAIDA))


def saida_de(no, nome):
    for s in no.outputs:
        if s.name == nome and s.enabled:
            return s
    return no.outputs[nome]


def entrada_de(no, nome):
    for s in no.inputs:
        if s.name == nome and s.enabled:
            return s
    return no.inputs[nome]


class Nos:
    """Atalhos para montar materiais por nós."""

    def __init__(self, nome):
        self.mat = bpy.data.materials.new(nome)
        self.mat.use_nodes = True
        self.t = self.mat.node_tree
        self.t.nodes.clear()
        self.saida = self.t.nodes.new("ShaderNodeOutputMaterial")
        self.bsdf = self.t.nodes.new("ShaderNodeBsdfPrincipled")
        self.liga(self.bsdf.outputs["BSDF"], self.saida.inputs["Surface"])
        self.bsdf.inputs["Roughness"].default_value = 0.85

    def liga(self, a, b):
        self.t.links.new(a, b)

    def no(self, tipo, **props):
        n = self.t.nodes.new(tipo)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def coord_pixel(self, pixels=16):
        """Coordenada do objeto 'travada' numa grade de pixels (visual pixel art)."""
        tc = self.no("ShaderNodeTexCoord")
        snap = self.no("ShaderNodeVectorMath", operation="SNAP")
        self.liga(tc.outputs["Object"], snap.inputs[0])
        snap.inputs[1].default_value = (1 / pixels,) * 3
        return snap.outputs["Vector"]

    def ruido(self, vetor, escala=6.0, detalhe=2.0, semente_w=0.0):
        n = self.no("ShaderNodeTexNoise", noise_dimensions="4D")
        self.liga(vetor, n.inputs["Vector"])
        n.inputs["Scale"].default_value = escala
        n.inputs["Detail"].default_value = detalhe
        n.inputs["W"].default_value = semente_w
        return n.outputs["Fac"]

    def voronoi(self, vetor, escala=4.0, modo="F1", saida="Distance", semente_w=0.0):
        v = self.no("ShaderNodeTexVoronoi", voronoi_dimensions="4D", feature=modo)
        self.liga(vetor, v.inputs["Vector"])
        v.inputs["Scale"].default_value = escala
        v.inputs["W"].default_value = semente_w
        return saida_de(v, saida)

    def rampa(self, fator, cores, constante=True):
        r = self.no("ShaderNodeValToRGB")
        r.color_ramp.interpolation = "CONSTANT" if constante else "LINEAR"
        els = r.color_ramp.elements
        while len(els) > 1:
            els.remove(els[-1])
        for i, (pos, cor) in enumerate(cores):
            e = els[0] if i == 0 else els.new(pos)
            e.position = pos
            e.color = (*cor, 1) if len(cor) == 3 else cor
        self.liga(fator, r.inputs["Fac"])
        return r.outputs["Color"]

    def mistura(self, fator, a, b):
        m = self.no("ShaderNodeMix", data_type="RGBA")
        self.liga(fator, entrada_de(m, "Factor"))
        for sock, val in ((entrada_de(m, "A"), a), (entrada_de(m, "B"), b)):
            if isinstance(val, tuple):
                sock.default_value = (*val, 1)
            else:
                self.liga(val, sock)
        return saida_de(m, "Result")

    def mat_op(self, op, a, b=0.0):
        m = self.no("ShaderNodeMath", operation=op)
        for sock, val in ((m.inputs[0], a), (m.inputs[1], b)):
            if isinstance(val, (int, float)):
                sock.default_value = val
            else:
                self.liga(val, sock)
        return m.outputs["Value"]

    def eixo(self, vetor, eixo="Z"):
        s = self.no("ShaderNodeSeparateXYZ")
        self.liga(vetor, s.inputs["Vector"])
        return s.outputs[eixo]

    def cor_base(self, sock):
        self.liga(sock, self.bsdf.inputs["Base Color"])

    def relevo(self, altura, forca=0.35):
        b = self.no("ShaderNodeBump")
        b.inputs["Strength"].default_value = forca
        self.liga(altura, b.inputs["Height"])
        self.liga(b.outputs["Normal"], self.bsdf.inputs["Normal"])


def hexa(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def material_liso(nome, cor, rugosidade=0.7, emissao=0.0):
    m = Nos(nome)
    m.bsdf.inputs["Base Color"].default_value = (*hexa(cor), 1)
    m.bsdf.inputs["Roughness"].default_value = rugosidade
    if emissao:
        m.bsdf.inputs["Emission Color"].default_value = (*hexa(cor), 1)
        m.bsdf.inputs["Emission Strength"].default_value = emissao
    return m.mat


# ------------------------------------------------------------------- blocos
def mat_terra(m, w=0.0):
    p = m.coord_pixel()
    f = m.ruido(p, 5.0, 2.0, w)
    m.cor_base(m.rampa(f, [(0, hexa("#6b4423")), (0.42, hexa("#7f532c")),
                           (0.55, hexa("#946338")), (0.68, hexa("#5c3a1e"))]))
    m.relevo(f, 0.3)


def criar_materiais_blocos():
    mats = {}

    m = Nos("terra"); mat_terra(m); mats["terra"] = m.mat

    # grama: topo verde com borda irregular descendo sobre a terra
    m = Nos("grama")
    p = m.coord_pixel()
    f = m.ruido(p, 5.0, 2.0)
    terra = m.rampa(f, [(0, hexa("#6b4423")), (0.42, hexa("#7f532c")),
                        (0.55, hexa("#946338")), (0.68, hexa("#5c3a1e"))])
    verde = m.rampa(m.ruido(p, 7.0, 1.0, 3.0),
                    [(0, hexa("#3f9a3a")), (0.45, hexa("#4fb544")), (0.62, hexa("#63c94f"))])
    borda = m.mat_op("ADD", m.eixo(p, "Z"), m.mat_op("MULTIPLY", m.ruido(p, 9.0, 0.0, 7.0), 0.22))
    eh_verde = m.mat_op("GREATER_THAN", borda, 0.36)
    m.cor_base(m.mistura(eh_verde, terra, verde))
    m.relevo(m.mat_op("ADD", f, m.mat_op("MULTIPLY", eh_verde, 0.25)), 0.35)
    mats["grama"] = m.mat

    # pedra: cinza com rachaduras (bordas de voronoi)
    m = Nos("pedra")
    p = m.coord_pixel()
    rach = m.voronoi(p, 3.2, "DISTANCE_TO_EDGE", "Distance", 1.0)
    f = m.ruido(p, 6.0, 2.0, 2.0)
    cinza = m.rampa(f, [(0, hexa("#7a7d80")), (0.45, hexa("#8c9094")), (0.6, hexa("#a2a6a9"))])
    eh_rach = m.mat_op("LESS_THAN", rach, 0.06)
    m.cor_base(m.mistura(eh_rach, cinza, hexa("#55585b")))
    m.relevo(m.mat_op("SUBTRACT", f, m.mat_op("MULTIPLY", eh_rach, 0.6)), 0.4)
    mats["pedra"] = m.mat

    # minério: pedra com gemas douradas brilhantes
    m = Nos("minerio")
    p = m.coord_pixel()
    f = m.ruido(p, 6.0, 2.0, 4.0)
    cinza = m.rampa(f, [(0, hexa("#7a7d80")), (0.45, hexa("#8c9094")), (0.6, hexa("#a2a6a9"))])
    gema_d = m.voronoi(p, 3.0, "F1", "Distance", 5.0)
    eh_gema = m.mat_op("LESS_THAN", gema_d, 0.3)
    ouro = m.rampa(m.ruido(p, 12.0, 0.0, 9.0), [(0, hexa("#d99a1e")), (0.5, hexa("#ffd23f"))])
    m.cor_base(m.mistura(eh_gema, cinza, ouro))
    m.liga(m.mat_op("SUBTRACT", 0.85, m.mat_op("MULTIPLY", eh_gema, 0.6)), m.bsdf.inputs["Roughness"])
    m.liga(m.mat_op("MULTIPLY", eh_gema, 0.9), m.bsdf.inputs["Metallic"])
    m.relevo(m.mat_op("ADD", f, m.mat_op("MULTIPLY", eh_gema, 0.5)), 0.4)
    mats["minerio"] = m.mat

    # madeira: tronco com casca em faixas verticais
    m = Nos("madeira")
    p = m.coord_pixel()
    x = m.eixo(p, "X")
    faixa = m.mat_op("FRACT", m.mat_op("ADD", m.mat_op("MULTIPLY", x, 4.0),
                                       m.mat_op("MULTIPLY", m.ruido(p, 3.0, 0.0, 6.0), 0.8)))
    m.cor_base(m.rampa(faixa, [(0, hexa("#5a3b1f")), (0.25, hexa("#6e4a28")),
                               (0.6, hexa("#7d5631")), (0.85, hexa("#4a3018"))]))
    m.relevo(faixa, 0.45)
    mats["madeira"] = m.mat

    # folhas: verde escuro com buracos
    m = Nos("folhas")
    p = m.coord_pixel()
    f = m.ruido(p, 8.0, 1.0, 8.0)
    m.cor_base(m.rampa(f, [(0, hexa("#1f6b2a")), (0.4, hexa("#2c8a35")),
                           (0.55, hexa("#3aa241")), (0.7, hexa("#174f20"))]))
    m.relevo(f, 0.6)
    mats["folhas"] = m.mat

    # areia: bege com grãos
    m = Nos("areia")
    p = m.coord_pixel()
    f = m.ruido(p, 10.0, 1.0, 10.0)
    m.cor_base(m.rampa(f, [(0, hexa("#d9c27e")), (0.45, hexa("#e6d08f")), (0.62, hexa("#f0dda3"))]))
    m.relevo(f, 0.2)
    mats["areia"] = m.mat
    return mats


def cubo_chanfrado(tam=1.0, chanfro=0.045):
    me = bpy.data.meshes.new("cubo")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=tam)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Bloco", me)
    bpy.context.collection.objects.link(ob)
    bev = ob.modifiers.new("Chanfro", "BEVEL")
    bev.width = chanfro
    bev.segments = 3
    for p in me.polygons:
        p.use_smooth = True
    return ob


def gerar_blocos():
    print("Blocos e ícones")
    cena_nova(64, 64, amostras=64)
    mats = criar_materiais_blocos()
    cubo = cubo_chanfrado()
    luz = sol((50, -25, -35))
    cam = camera_orto((0, -5, 0), (90, 0, 0), 1.0)

    for nome, mat in mats.items():
        cubo.data.materials.clear()
        cubo.data.materials.append(mat)
        render(os.path.join(SAIDA, "blocos", f"{nome}.png"))

    # ícones isométricos para a barra de itens
    cena = bpy.context.scene
    cena.render.resolution_x = cena.render.resolution_y = 96
    cam.data.ortho_scale = 1.85
    cam.rotation_euler = (math.radians(54.736), 0, math.radians(45))
    cam.location = Vector((5, -5, 5 * math.sqrt(2) * math.tan(math.radians(35.264))))
    luz.rotation_euler = [math.radians(a) for a in (40, 0, 20)]
    for nome, mat in mats.items():
        cubo.data.materials.clear()
        cubo.data.materials.append(mat)
        render(os.path.join(SAIDA, "icones", f"{nome}.png"))

    cubo.data.materials.clear()
    cubo.data.materials.append(mats["grama"])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, "fonte", "blocos.blend"))


# --------------------------------------------------------------- personagem
def caixa(nome, tam, deslocamento, mat, pai=None, pivo=(0, 0, 0), chanfro=0.05):
    """Caixa arredondada com a origem no pivô (articulação)."""
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * tam[0] + deslocamento[0],
                       v.co.y * tam[1] + deslocamento[1],
                       v.co.z * tam[2] + deslocamento[2]))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(ob)
    ob.location = pivo
    if pai:
        ob.parent = pai
    ob.data.materials.append(mat)
    b = ob.modifiers.new("Chanfro", "BEVEL")
    b.width = chanfro
    b.segments = 4
    for p in me.polygons:
        p.use_smooth = True
    return ob


def esfera(nome, raio, local, mat, pai=None, escala=(1, 1, 1), meia=False):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=raio)
    if meia:  # só a metade de cima (domo)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(ob)
    ob.location = local
    ob.scale = escala
    if pai:
        ob.parent = pai
    ob.data.materials.append(mat)
    return ob


def cilindro(nome, raio, altura, local, rot, mat, pai=None):
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=raio, radius2=raio, depth=altura)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(ob)
    ob.location = local
    ob.rotation_euler = [math.radians(a) for a in rot]
    if pai:
        ob.parent = pai
    ob.data.materials.append(mat)
    return ob


def montar_personagem():
    """Mineirinho original: capacete amarelo com lanterna, macacão azul."""
    pele = material_liso("pele", "#f1b98c", 0.6)
    camisa = material_liso("camisa", "#e8742f", 0.8)
    camisa_t = material_liso("camisa_tras", "#b85a22", 0.8)
    macacao = material_liso("macacao", "#2f5fd0", 0.75)
    macacao_t = material_liso("macacao_tras", "#22469c", 0.75)
    bota = material_liso("bota", "#4a2f1c", 0.6)
    capacete = material_liso("capacete", "#ffc928", 0.35)
    preto = material_liso("olho", "#14161a", 0.3)
    luz_mat = material_liso("lanterna", "#fff4b0", 0.2, emissao=4.0)
    alca = material_liso("alca", "#ffd34d", 0.4)

    raiz = bpy.data.objects.new("Personagem", None)
    bpy.context.collection.objects.link(raiz)

    partes = {}
    # pernas (pivô no quadril)
    for lado, y, mat in (("tras", 0.09, macacao_t), ("frente", -0.09, macacao)):
        perna = caixa(f"perna_{lado}", (0.2, 0.17, 0.5), (0, 0, -0.25), mat, raiz, (0, y, 0.62))
        caixa(f"bota_{lado}", (0.27, 0.19, 0.14), (0.04, 0, -0.05), bota, perna, (0, 0, -0.5))
        partes[f"perna_{lado}"] = perna
    # braço de trás (atrás do corpo)
    braco_t = caixa("braco_tras", (0.16, 0.14, 0.46), (0, 0, -0.21), camisa_t, raiz, (0, 0.2, 1.12))
    esfera("mao_tras", 0.09, (0, 0, -0.45), pele, braco_t)
    partes["braco_tras"] = braco_t
    # tronco
    caixa("tronco", (0.4, 0.34, 0.58), (0, 0, 0.29), macacao, raiz, (0, 0, 0.6), chanfro=0.09)
    caixa("peito", (0.42, 0.3, 0.16), (0, 0, 0), camisa, raiz, (0, 0, 1.12), chanfro=0.07)
    caixa("bolso", (0.02, 0.16, 0.12), (0, 0, 0), alca, raiz, (0.205, -0.02, 0.97), chanfro=0.008)
    # cabeça
    cabeca = esfera("cabeca", 0.27, (0.02, 0, 1.43), pele)
    cabeca.parent = raiz
    esfera("olho", 0.042, (0.185, -0.2, 1.475), preto, raiz, escala=(0.8, 0.8, 1.4))
    esfera("nariz", 0.06, (0.285, -0.02, 1.4), pele, raiz)
    esfera("bochecha", 0.05, (0.15, -0.21, 1.36), material_liso("bochecha", "#f08a7a", 0.6), raiz,
           escala=(1, 0.4, 0.7))
    # capacete
    esfera("capacete", 0.3, (0.02, 0, 1.51), capacete, raiz, escala=(1.0, 1.0, 0.8), meia=True)
    cilindro("aba", 0.33, 0.05, (0.07, 0, 1.53), (0, 0, 0), capacete, raiz)
    cilindro("lanterna", 0.07, 0.08, (0.3, 0, 1.6), (0, 90, 0), luz_mat, raiz)
    cilindro("suporte", 0.085, 0.05, (0.26, 0, 1.6), (0, 90, 0), material_liso("metal", "#8a8f99", 0.3), raiz)
    # braço da frente
    braco_f = caixa("braco_frente", (0.16, 0.14, 0.46), (0, 0, -0.21), camisa, raiz, (0, -0.2, 1.12))
    esfera("mao_frente", 0.09, (0, 0, -0.45), pele, braco_f)
    partes["braco_frente"] = braco_f
    return raiz, partes


def pose(partes, perna_f, perna_t, braco_f, braco_t):
    partes["perna_frente"].rotation_euler.y = math.radians(perna_f)
    partes["perna_tras"].rotation_euler.y = math.radians(perna_t)
    partes["braco_frente"].rotation_euler.y = math.radians(braco_f)
    partes["braco_tras"].rotation_euler.y = math.radians(braco_t)


def gerar_personagem():
    print("Personagem")
    # hitbox do jogo: 24x38 -> renderiza em 4x (96x152)
    cena_nova(96, 152, amostras=64)
    raiz, partes = montar_personagem()
    sol((55, -20, -40), 3.0)
    camera_orto((0.03, -6, 0.95), (90, 0, 0), 1.9, ajuste="VERTICAL")

    # rotação em Y positiva gira o pé para trás (-X); o personagem olha para +X
    quadros = {
        "parado_0": (0, 0, 0, 0),
        "parado_1": (0, 0, 4, -4),
        "andar_0": (-28, 28, 30, -30),
        "andar_1": (0, 0, 0, 0),
        "andar_2": (28, -28, -30, 30),
        "andar_3": (0, 0, 0, 0),
        "pulo": (-35, 20, -150, -40),
        "quebrar_0": (-8, 8, -110, 10),
        "quebrar_1": (-8, 8, -40, 10),
    }
    for nome, angs in quadros.items():
        pose(partes, *angs)
        # leve balanço vertical ao andar
        raiz.location.z = 0.025 if nome in ("andar_1", "andar_3", "parado_1") else 0.0
        if nome == "parado_1":
            raiz.location.z = -0.01
        render(os.path.join(SAIDA, "personagem", f"{nome}.png"))
    pose(partes, 0, 0, 0, 0)
    raiz.location.z = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, "fonte", "personagem.blend"))
    return list(quadros)


# ------------------------------------------------------------------ cenário
def morros(nome, largura, base, ondas, cor_topo, cor_base, z=0.0, segs=256):
    """Faixa de morros periódica (emenda perfeita na horizontal)."""
    me = bpy.data.meshes.new(nome)
    bm = bmesh.new()
    topo, fundo = [], []
    for i in range(segs + 1):
        x = largura * i / segs
        h = base + sum(a * math.sin(2 * math.pi * k * x / largura + f) for a, k, f in ondas)
        topo.append(bm.verts.new((x, z, h)))
        fundo.append(bm.verts.new((x, z, 0)))
    for i in range(segs):
        bm.faces.new((fundo[i], fundo[i + 1], topo[i + 1], topo[i]))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nome, me)
    bpy.context.collection.objects.link(ob)

    m = Nos(nome)
    gen = m.no("ShaderNodeTexCoord")
    zz = m.eixo(gen.outputs["Object"], "Z")
    fator = m.mat_op("DIVIDE", zz, base + sum(a for a, _, _ in ondas))
    cor = m.mistura(fator, hexa(cor_base), hexa(cor_topo))
    # emissão pura: cor chapada e previsível para o fundo
    em = m.no("ShaderNodeEmission")
    m.liga(cor, em.inputs["Color"])
    m.liga(em.outputs["Emission"], m.saida.inputs["Surface"])
    ob.data.materials.append(m.mat)
    return ob


def nuvem(semente):
    rnd = random.Random(semente)
    branco = Nos(f"nuvem{semente}")
    branco.bsdf.inputs["Base Color"].default_value = (0.97, 0.98, 1.0, 1)
    branco.bsdf.inputs["Roughness"].default_value = 1.0
    grupo = []
    n = rnd.randint(5, 7)
    for i in range(n):
        x = (i - (n - 1) / 2) * 0.38 + rnd.uniform(-0.08, 0.08)
        r = 0.42 - abs(x) * 0.18 + rnd.uniform(-0.05, 0.07)
        grupo.append(esfera(f"bola{i}", r, (x, 0, r * 0.55 + rnd.uniform(-0.02, 0.06)),
                            branco.mat, escala=(1.15, 1, 0.92)))
    # base achatada
    grupo.append(esfera("base", 0.9, (0, 0, 0.12), branco.mat, escala=(1.55, 0.6, 0.22)))
    return grupo


def gerar_cenario():
    print("Cenário")
    largura = 16.0
    cena = cena_nova(1024, 256, amostras=16)
    cam = camera_orto((largura / 2, -10, 2.0), (90, 0, 0), largura)

    camadas = {
        "morros_longe": dict(base=2.0, ondas=[(0.7, 2, 0.3), (0.35, 5, 1.7), (0.12, 11, 0.4)],
                             cor_topo="#9fd0a8", cor_base="#7fb8a6"),
        "morros_perto": dict(base=1.5, ondas=[(0.55, 3, 2.1), (0.25, 7, 0.2), (0.08, 17, 1.1)],
                             cor_topo="#5fae55", cor_base="#3d8a4a"),
    }
    for nome, cfg in camadas.items():
        for ob in list(bpy.data.objects):
            if ob.type == "MESH":
                bpy.data.objects.remove(ob)
        morros(nome, largura, **cfg)
        render(os.path.join(SAIDA, "cenario", f"{nome}.png"))

    print("Nuvens")
    cena_nova(256, 128, amostras=48)
    sol((35, 0, -20), 2.5)
    camera_orto((0, -6, 0.35), (90, 0, 0), 3.2)
    for s in range(3):
        for ob in list(bpy.data.objects):
            if ob.type == "MESH":
                bpy.data.objects.remove(ob)
        nuvem(s + 11)
        render(os.path.join(SAIDA, "cenario", f"nuvem_{s}.png"))


if __name__ == "__main__":
    gerar_blocos()
    gerar_personagem()
    gerar_cenario()
    print("Pronto:", SAIDA)
