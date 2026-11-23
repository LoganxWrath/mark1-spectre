"""
MARK 1 SPECTRE v3 - cyberdeck cyberpunk parametrico (CadQuery)
Base: Rii Mini X1 (151 x 59 x 12.5 mm) | Tampa: Galaxy S10e (142.2 x 69.9 x 7.9 mm)
Pensado para FDM com bico 0.4 mm: paredes >= 0.8, ranhuras >= 0.8, letras >= 3.5 mm,
tudo impresso plano, sem suportes.

Correr:  python3 mark1_spectre_v3.py [pasta_saida]

Eixos: X comprimento (esq->dir), Y profundidade (frente y=0 -> dobradicas), Z altura (mesa z=0).
A tampa e modelada virada ao contrario (costas na mesa). Posicao fechada:
  (x, y, z)_fechada = (x, W - y, H_B + H_L - z)
"""
import math
import os
import sys

import cadquery as cq

# =========================== PARAMETROS ====================================
# Rii Mini X1: contorno IGUAL ao encaixe do modelo original (151.2 x 59.2, cantos R5.14 e R19)
KB_L, KB_W, KB_H = 151.2, 59.2, 12.5
PH_L, PH_W, PH_H = 142.2, 69.9, 7.9       # Galaxy S10e (sem capa)

KB_CLR = 0.5        # folga extra por lado para a impressao (0 = tamanho exato do original)
PH_CLR_L, PH_CLR_W = 0.15, 0.1        # impresso: 0.3/0.2 ficou largo
PH_PAD = 0.2                              # 4 pastilhas no fundo do encaixe (tira a folga em altura)
BTN_OUT = 0.5                             # face do botao Power: +0.5 = sai 1.0 mm para fora da cinta
CAP_CLR = 0.10

L, W = 164.0, 89.2
FC, BC = 9.0, 4.0                         # chanfro dos cantos: frente / tras
CH_BED_BASE, CH_BED_LID, CH_RIM = 1.0, 1.6, 0.8
BELT = 0.5                                # profundidade da cinta blindada
VG = 0.4                                  # meia-largura (=profundidade) das ranhuras em V

FLOOR = 2.2
H_B = FLOOR + KB_H + 0.5
KB_PL, KB_PW = KB_L + 2 * KB_CLR, KB_W + 2 * KB_CLR
# recorte do teclado = contorno exato do KeyboardTray (152.6 x 59.1, canto grande a frente-direita)
import json as _json
KB_TRAY = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb_tray_pocket.json")))
KB_PL, KB_PW = max(p[0] for p in KB_TRAY), max(p[1] for p in KB_TRAY)
KB_BUMP = (16.0, 30.9, 12.0, 3.0, 1.0)     # rasgo p/ ressalto nas costas do Rii (como no Tastatur_halter): comprimento desde a ponta, centro desde a frente do recorte, largura, raio, fundo
KB_X0, KB_Y0 = (L - KB_PL) / 2, 14.0
# raios dos cantos, iguais ao modelo original:
# frente-esq, frente-dir (curva grande junto ao D-pad), tras-dir, tras-esq
KB_RADII = (5.14, 19.0, 5.14, 5.14)
KB_SWITCH_FROM_BACK, KB_PORT_FROM_BACK = 18.0, 38.0
BASE_BELT_Z = (3.0, 12.6)

BACK, LIP_T = 2.2, 1.2
PH_PL, PH_PW = PH_L + 2 * PH_CLR_L, PH_W + 2 * PH_CLR_W
POCKET_D = PH_H + 0.3
H_L = BACK + POCKET_D + LIP_T
PH_X0, PH_Y0, PH_R = 15.0, 8.0, 7.0
HINGE_LIP, SNAP_LIP = 1.5, 1.0
SNAPS = ((62.0, 78.0), (120.0, 140.0))      # linguetas (x) - fora do botao Power
PWR_FROM_TOP = 26.9                       # centro do botao Power desde o topo do S10e (desenho oficial: 19.2-34.6)
VOL_FROM_TOP = (15.0, 75.0)
# camara S10e (modulo horizontal no topo, centrado). Em paisagem fica "em pe".
CAM_CENTER_FROM_TOP = 25.4                # centro do recorte desde o topo do S10e (desenho oficial: barra 19.2-31.7)
CAM_SIZE = (16.0, 37.0)                   # (ao longo do comprimento, ao longo da largura) - original 17 x 37
CAM_R = 5.0
LID_BELT_Z0 = 2.4

AX_OFF, R_K, HOLE_D = 4.6, 4.5, 3.4
K_GAP = 0.5
BASE_K = [(20.0, 40.0), (L - 40.0, L - 20.0)]
LID_K = [(40.5, 60.5), (L - 60.5, L - 40.5)]
OPEN_ANGLE = 115.0
STOP_X = (67.0, 97.0)
CBORE_D, CBORE_DEPTH = 6.4, 4.0           # cabeca M3 (5.5 x 3) + tampa laranja 0.9
NUT_AF, NUT_DEPTH = 5.8, 3.0              # porca M3 (5.5 AF)

TRAVEL = 4.0
TAB_OUT = 2.0                              # quanto a patilha da tranca sai da frente (mm)
HX = L / 2 - 5.5
ROOF = 1.8

# Letra: Orbitron Black (OFL) na pasta fonts/. Todas as letras >= 6 mm de altura e traco >= 1.2 mm
# para sairem limpas com bico 0.4. Gravacao 0.8 mm (4 camadas de 0.2).
_HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(_HERE, "fonts", "Orbitron-900.ttf")
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"
TXT_D = 0.8                               # profundidade das letras
AMS_LAYERS, LAYER_H = 2, 0.2              # AMS: laranja so nas 2 camadas a vista (poupa laranja)
FONT_JP = os.path.join(_HERE, "fonts", "DelaGothicOne-katakana.ttf")   # katakana (OFL)
NEON_D = 1.2                              # profundidade dos rasgos das barras neon (peca 10)
# barras neon (peca 10): (peca, face, inicio, fim, z do centro). Contornam os cantos da frente.
#   base: z 5.3 = altura da tranca e da 1.a linha de ventilacao; tampa: z 7.0 = altura do PWR
NEON = [("base", "front", 12.0, 58.0, 5.3), ("base", "front", 108.0, 152.0, 5.3),
        ("lid", "front", 92.0, 152.0, 7.0)]          # so na frente (sem barras laterais)
VENT_Z = (-2.6, 0.0, 2.6)                 # linhas de ventilacao nos paineis laterais (rel. ao centro)
# ==========================================================================

AX_Y = W + AX_OFF
ROOF_Z0 = H_B - ROOF
PH_Y1 = PH_Y0 + PH_PW
LIP_Z0 = H_L - LIP_T
PH_TOP = PH_X0 + PH_CLR_L
PH_CY = PH_Y0 + PH_PW / 2
PX = PH_TOP + PWR_FROM_TOP

FOOT_BASE = [(FC, 0), (L - FC, 0), (L, FC), (L, W - BC), (L - BC, W), (BC, W), (0, W - BC), (0, FC)]
FOOT_LID = [(x, W - y) for x, y in FOOT_BASE][::-1]


# ---------------------------------------------------------------- helpers --
def bx(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rbox(x0, x1, y0, y1, z0, z1, r):
    b = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
    if r > 0:
        b = b.edges("|Z").fillet(r)
    return b.translate((x0, y0, z0))


def poly_z(pts, z0, z1):
    return cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, 0, z0))


def prism_yz(pts, x0, x1):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0)


def cyl_x(yc, zc, r, x0, x1):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).moveTo(yc, zc).circle(r).extrude(x1 - x0)


def teardrop_x(yc, zc, d, x0, x1):
    r = d / 2
    k = r / math.sqrt(2)
    tri = [(yc - k, zc + k), (yc, zc + r * math.sqrt(2)), (yc + k, zc + k)]
    return cyl_x(yc, zc, r, x0, x1).union(prism_yz(tri, x0, x1))


def hex_x(yc, zc, af, x0, x1):
    d = af / math.cos(math.radians(30))
    return cq.Workplane("YZ", origin=(x0, 0, 0)).moveTo(yc, zc).polygon(6, d).extrude(x1 - x0)


ACC = {"base": [], "lid": []}             # gravacoes que tambem saem como pecas laranja (AMS)


def acc(key, solid):
    ACC[key].append(solid)
    return solid


def text_solid(txt, size, depth, mirror=None, font=None):
    t = cq.Workplane("XY").text(txt, size, depth, fontPath=font or FONT, halign="center", valign="center")
    if mirror:
        t = t.mirror(mirror)
    return t


def shell(pts, h, ch_bed, ch_top):
    s = cq.Workplane("XY").polyline(pts).close().extrude(h)
    s = s.faces("<Z").chamfer(ch_bed)
    s = s.faces(">Z").chamfer(ch_top)
    return s


def belt_ring(pts, z0, z1):
    outer = cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0)
    inner = cq.Workplane("XY").polyline(pts).close().offset2D(-BELT).extrude(z1 - z0)
    return outer.cut(inner).translate((0, 0, z0))


def vgroove(px, py, nx, ny, z0, z1, depth=VG):
    """Ranhura em V vertical numa parede (p = ponto na superficie, n = normal exterior)."""
    tx, ty = -ny, nx
    tri = [(px - tx * depth + nx * 0.05, py - ty * depth + ny * 0.05),
           (px + tx * depth + nx * 0.05, py + ty * depth + ny * 0.05),
           (px - nx * depth, py - ny * depth)]
    return poly_z(tri, z0, z1)


def louver(p0, p1, frac, w, depth, z0, z1, nout):
    """Ranhura de ventilacao decorativa numa faceta (p0->p1), normal exterior nout."""
    cx, cy = p0[0] + (p1[0] - p0[0]) * frac, p0[1] + (p1[1] - p0[1]) * frac
    dx, dy = (p1[0] - p0[0]), (p1[1] - p0[1])
    n = math.hypot(dx, dy)
    tx, ty = dx / n, dy / n
    nx, ny = nout
    a = (cx - tx * w / 2 + nx * 0.1, cy - ty * w / 2 + ny * 0.1)
    b = (cx + tx * w / 2 + nx * 0.1, cy + ty * w / 2 + ny * 0.1)
    c = (b[0] - nx * (depth + 0.1), b[1] - ny * (depth + 0.1))
    d = (a[0] - nx * (depth + 0.1), a[1] - ny * (depth + 0.1))
    return poly_z([a, b, c, d], z0, z1)


def groove_ring(pts, w=0.8, d=0.4):
    """Ranhura de painel (largura w, profundidade d) a seguir um contorno, na face da mesa."""
    o = cq.Workplane("XY").polyline(pts).close().extrude(d + 0.1)
    i = cq.Workplane("XY").polyline(pts).close().offset2D(-w).extrude(d + 0.1)
    return o.cut(i).translate((0, 0, -0.1))


def outline(x0, y0, l, w, radii, n=16):
    """Contorno retangular com raio diferente em cada canto (fe, fd, td, te)."""
    rfl, rfr, rbr, rbl = radii
    pts = []
    for (cx, cy, r, a0) in ((x0 + rfl, y0 + rfl, rfl, 180), (x0 + l - rfr, y0 + rfr, rfr, 270),
                           (x0 + l - rbr, y0 + w - rbr, rbr, 0), (x0 + rbl, y0 + w - rbl, rbl, 90)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def kb_pocket(x0, y0, z0, z1, clr=KB_CLR):
    from shapely.geometry import Polygon
    d = clr - KB_CLR                                   # >0 = contorno alargado (paredes do gabarito)
    poly = Polygon([(x0 + d + x, y0 + d + y) for x, y in KB_TRAY])
    if abs(d) > 1e-6:
        poly = poly.buffer(d, join_style=1, quad_segs=8).simplify(0.01)
    return poly_z(list(poly.exterior.coords)[:-1], z0, z1)


def kb_bump_cut(x0, y0, z0, z1):
    bl, bc, bw, br, _ = KB_BUMP
    xe = x0 + KB_PL + 0.01                             # vai ate a parede (o ressalto comeca no bordo)
    yc = y0 + bc
    return bx(xe - bl, xe, yc - bw / 2, yc + bw / 2, z0, z1).edges("|Z").fillet(br)


def cam_cut(cx, cy, w, l, r, z0, h, taper=None):
    sk = cq.Workplane("XY").center(cx, cy).sketch().rect(w, l).vertices().fillet(r).finalize()
    s = sk.extrude(h, taper=taper) if taper else sk.extrude(h)
    return s.translate((0, 0, z0))


def loft_y(cx, cz, y0, y1, wa, ha, wb, hb):
    """Transicao de seccao retangular (wa x ha em y0) para (wb x hb em y1), y1 > y0."""
    return cq.Workplane("XZ", origin=(cx, y1, cz)).rect(wb, hb).workplane(offset=y1 - y0).rect(wa, ha).loft()


def groove_line(pts, w=0.8, d=0.5):
    """Linha de painel ao longo de uma polilinha, na face da mesa."""
    from shapely.geometry import LineString
    poly = LineString(pts).buffer(w / 2, cap_style=2, join_style=2)
    return poly_z(list(poly.exterior.coords)[:-1], -0.1, d)


def glitch_text(txt, size, depth, shift=1.8, band=(-1.4, 1.2)):
    """Texto com efeito glitch: a faixa do meio desliza para o lado."""
    t = text_solid(txt, size, depth)
    big = 200
    lo = t.intersect(bx(-big, big, -big, band[0], -1, depth + 1))
    mid = t.intersect(bx(-big, big, band[0], band[1], -1, depth + 1)).translate((shift, 0, 0))
    hi = t.intersect(bx(-big, big, band[1], big, -1, depth + 1))
    return lo.union(mid).union(hi)


# pistas de circuito (vista fechada da tampa: x, y a partir da frente), largura 1.0 mm
CIRCUIT = [
    [(103.0, 64.0), (126.0, 64.0), (130.5, 68.5)],
    [(136.0, 64.0), (155.0, 64.0)],
    [(103.0, 26.0), (150.0, 26.0), (154.0, 30.0)],
    [(10.0, 75.5), (20.0, 75.5), (24.5, 80.0), (29.0, 80.0)],
    [(112.5, 73.5), (112.5, 78.5), (116.0, 82.0), (118.5, 82.0)],
]


def trace(pts, w=1.0, d=0.5, pad=1.2):
    """Pista de circuito gravada (face da mesa) com terminais redondos."""
    g = groove_line(pts, w, d)
    for x, y in (pts[0], pts[-1]):
        g = g.union(cq.Workplane("XY").circle(pad).extrude(d + 0.1).translate((x, y, -0.1)))
    return g


def neon_slot(face, a0, a1, zc, lid):
    """Rasgo de 2.0 mm de altura e NEON_D de fundo para uma barra neon."""
    if face == "front":
        return bx(a0, a1, W - BELT - NEON_D, W + 1, zc - 1, zc + 1) if lid else bx(a0, a1, -1, BELT + NEON_D, zc - 1, zc + 1)
    if face == "left":
        return bx(-1, BELT + NEON_D, a0, a1, zc - 1, zc + 1)
    return bx(L - BELT - NEON_D, L + 1, a0, a1, zc - 1, zc + 1)


def para(x0, y0, length, h, slant):
    """Paralelogramo (faixa inclinada)."""
    return [(x0, y0), (x0 + length, y0), (x0 + length + slant, y0 + h), (x0 + slant, y0 + h)]


S2 = 1 / math.sqrt(2)


# ------------------------------------------------------------------ BASE ---
def make_base():
    b = shell(FOOT_BASE, H_B, CH_BED_BASE, CH_RIM)
    z0, z1 = BASE_BELT_Z
    b = b.cut(belt_ring(FOOT_BASE, z0, z1))
    sx0, sx1 = BELT, L - BELT                    # superficie da cinta
    sy0 = BELT

    # encaixe do teclado (KeyboardTray) + rasgo + entalhe + compartimento recetor USB
    b = b.cut(kb_pocket(KB_X0, KB_Y0, FLOOR, H_B + 1))
    b = b.cut(kb_bump_cut(KB_X0, KB_Y0, FLOOR - KB_BUMP[4], FLOOR + 0.1))   # rasgo no fundo para o ressalto do Rii
    b = b.cut(rbox(KB_X0 + KB_PL - 1, KB_X0 + KB_PL + 3.4, 42, 62, 6.0, H_B + 1, 1.2))
    b = b.cut(rbox(70, 94, KB_Y0 + KB_PW + 2.2, W - 2.8, 4.2, H_B + 1, 1.5))

    # tranca: cavidade, entrada, passagem do dente, ranhura do gancho, janela frontal
    sl_x0 = HX - 4.5
    b = b.cut(bx(sl_x0 - 0.2, sl_x0 + 24 + TRAVEL + 0.2, 1.8, 12.1, FLOOR, ROOF_Z0))
    b = b.cut(bx(sl_x0 - 0.2, sl_x0 + 24 + TRAVEL + 0.2, 12.0, KB_Y0 + 0.1, FLOOR, 8.6))
    b = b.cut(bx(HX + 12.0, HX + 17.7, 12.0, KB_Y0 + 0.1, FLOOR, ROOF_Z0))
    b = b.cut(bx(HX - 0.6, HX + 11.6, 2.9, 6.9, ROOF_Z0 - 0.1, H_B + 1))
    b = b.cut(bx(HX - 0.9, HX + 15.9, -1, 1.9, 3.2, 7.4))
    # setas LOCK <  > OPEN na cinta frontal
    zc = 5.3
    for k in (0.0, 4.2):                                      # setas duplas << LOCK   OPEN >>
        b = b.cut(poly_z([(HX - 8.5 - k, zc), (HX - 3.5 - k, zc + 2.1), (HX - 3.5 - k, zc - 2.1)], 0, 1)
                  .rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 1.1, 0)))
        b = b.cut(poly_z([(HX + 24.4 + k, zc), (HX + 19.4 + k, zc + 2.1), (HX + 19.4 + k, zc - 2.1)], 0, 1)
                  .rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 1.1, 0)))

    # janelas laterais do teclado (esquerda) - juntas coincidem com as ranhuras da cinta
    kb_back = KB_Y0 + KB_PW - KB_CLR
    zc = FLOOR + KB_H / 2
    seams = []
    for d in (KB_SWITCH_FROM_BACK, KB_PORT_FROM_BACK):
        yc = kb_back - d
        b = b.cut(bx(sx0 - 1, sx0 + 3.0, yc - 7.5, yc + 7.5, z0, z1))
        b = b.cut(bx(sx0 + 2.9, KB_X0 + 0.5, yc - 7.0, yc + 7.0, zc - 4.0, zc + 4.0))
        seams += [yc - 7.5, yc + 7.5]
    for grp, face, a0, a1, zc_n in NEON:                     # rasgos das barras neon
        if grp == "base":
            b = b.cut(neon_slot(face, a0, a1, zc_n, lid=False))
    # riscas de aviso junto a dobradica (zona de entalar) nos dois lados
    for xs0, xs1 in ((-1, BELT + 0.6), (L - BELT - 0.6, L + 1)):
        for y0 in (65.0, 68.6, 72.2):
            b = b.cut(prism_yz([(y0, 4.2), (y0 + 1.6, 4.2), (y0 + 8.8, 11.4), (y0 + 7.2, 11.4)], xs0, xs1))
    zb = (z0 + z1) / 2
    for d in (KB_SWITCH_FROM_BACK, KB_PORT_FROM_BACK):
        yc = kb_back - d
        for dz in VENT_Z:
            b = b.cut(bx(sx1 - 0.6, L + 1, yc - 6.0, yc + 6.0, zb + dz - 0.5, zb + dz + 0.5))
    # ranhuras em V: juntas reais (esq) + juntas falsas iguais (dir) + divisoes extra
    for y in seams:
        b = b.cut(vgroove(sx0, y, -1, 0, z0 - 0.01, z1 + 0.01))
        b = b.cut(vgroove(sx1, y, 1, 0, z0 - 0.01, z1 + 0.01))
    for x in (22.0, 46.0, L - 46.0, L - 22.0):
        b = b.cut(vgroove(x, sy0, 0, -1, z0 - 0.01, z1 + 0.01))
    # grelhas nas facetas da frente
    for p0, p1, n in (((0.0, FC), (FC, 0.0), (-S2, -S2)), ((L - FC, 0.0), (L, FC), (S2, -S2))):
        q0 = (p0[0] - n[0] * BELT, p0[1] - n[1] * BELT)
        q1 = (p1[0] - n[0] * BELT, p1[1] - n[1] * BELT)
        for f in (0.3, 0.5, 0.7):
            b = b.cut(louver(q0, q1, f, 1.2, 0.8, z0 + 1.2, z1 - 1.2, n))

    # dobradicas: nos + furo em gota + escareado da cabeca
    k = R_K * S2
    for x0, x1 in BASE_K:
        web = [(AX_Y - 10, H_B), (AX_Y, H_B), (AX_Y + k, H_B - k), (AX_Y - (H_B - 2 * k), 0), (AX_Y - 10, 0)]
        b = b.union(prism_yz(web, x0, x1)).union(cyl_x(AX_Y, H_B, R_K, x0, x1))
        b = b.cut(teardrop_x(AX_Y, H_B, HOLE_D, x0 - 1, x1 + 1))
    b = b.cut(teardrop_x(AX_Y, H_B, CBORE_D, BASE_K[0][0] - 1, BASE_K[0][0] + CBORE_DEPTH))
    b = b.cut(teardrop_x(AX_Y, H_B, CBORE_D, BASE_K[1][1] - CBORE_DEPTH, BASE_K[1][1] + 1))
    # batente de abertura (espinha central)
    th = math.radians(OPEN_ANGLE)
    r0 = AX_OFF + BELT                    # face traseira da tampa (na cinta)
    p0 = (-r0 * math.cos(th), r0 * math.sin(th))
    p1 = (p0[0] + H_L * math.sin(th), p0[1] + H_L * math.cos(th))
    slope = (p1[1] - p0[1]) / (p1[0] - p0[0])
    zs = lambda yr: p0[1] + slope * (yr - p0[0])
    ya, yb = 5.5, 10.0
    spine = [(W - 2, 0), (AX_Y + yb, 0), (AX_Y + yb, H_B + zs(yb) - 0.05),
             (AX_Y + ya, H_B + zs(ya) - 0.05), (AX_Y + ya, H_B), (W - 2, H_B)]
    sp = prism_yz(spine, *STOP_X)
    sp = sp.edges("|Y").chamfer(1.0)
    b = b.union(sp)
    for x in (73.0, 78.0, 82.0, 86.0, 91.0):                      # alhetas na espinha
        b = b.cut(bx(x - 0.6, x + 0.6, AX_Y + yb - 0.8, AX_Y + yb + 1, 2.0, H_B - 2.0))

    # topo da faixa frontal: gravacoes + riscas de aviso junto ao gancho
    b = b.cut(acc("base", text_solid("SPECTRE", 9.5, TXT_D + 0.1).translate((35.5, 7.4, H_B - TXT_D))))
    b = b.cut(acc("base", text_solid("// MK-1", 9.5, TXT_D + 0.1).translate((131.5, 7.4, H_B - TXT_D))))
    for x0 in (HX - 11.6, HX - 8.2):
        b = b.cut(acc("base", poly_z(para(x0, 3.0, 1.4, 8.0, 8.0), H_B - 0.5, H_B + 1)))
    for x0 in (HX + 13.0, HX + 16.4):
        b = b.cut(acc("base", poly_z(para(x0, 3.0, 1.4, 8.0, 8.0), H_B - 0.5, H_B + 1)))

    # fundo: pes de borracha + placa de serie (espelhada para ler com a base virada)
    for x in (16, L - 16):
        for y in (12, W - 12):
            b = b.cut(cq.Workplane("XY").circle(5.0).extrude(0.8).translate((x, y, -0.01)))
    b = b.cut(acc("base", text_solid("LOGAN TECH", 16.0, TXT_D, mirror="YZ").translate((L / 2, 54, -0.01))))
    b = b.cut(acc("base", text_solid("SPECTRE // MK-1", 10.0, TXT_D, mirror="YZ").translate((L / 2, 33, -0.01))))
    b = b.cut(acc("base", text_solid("スペクター", 14.0, TXT_D, mirror="YZ", font=FONT_JP).translate((L / 2, 70, -0.01))))
    return b


# ----------------------------------------------------------------- TAMPA ---
def make_lid():
    t = shell(FOOT_LID, H_L, CH_BED_LID, CH_RIM)
    t = t.cut(belt_ring(FOOT_LID, LID_BELT_Z0, H_L + 1))
    z0, z1 = LID_BELT_Z0, H_L + 0.01
    sx0, sx1, sy0, sy1 = BELT, L - BELT, BELT, W - BELT

    # encaixe do telemovel, labio fixo, linguetas
    t = t.cut(rbox(PH_X0, PH_X0 + PH_PL, PH_Y0, PH_Y1, BACK, H_L + 1, PH_R))
    for px in (PH_X0 + 10.0, PH_X0 + PH_PL - 12.0):          # pastilhas: apoiam as costas do S10e
        for py in (PH_Y0 + 8.0, PH_Y1 - 8.0):
            t = t.union(cq.Workplane("XY").circle(3.0).extrude(PH_PAD + 0.01).translate((px, py, BACK - 0.01)))
    lip = [(PH_Y0 - 0.01, LIP_Z0), (PH_Y0 + HINGE_LIP, LIP_Z0), (PH_Y0 + HINGE_LIP, H_L - 0.3),
           (PH_Y0 + HINGE_LIP - 0.3, H_L), (PH_Y0 - 0.01, H_L)]
    t = t.union(prism_yz(lip, PH_X0 + PH_R, PH_X0 + PH_PL - PH_R))
    for a, c in SNAPS:
        t = t.cut(bx(a, c, PH_Y1 + 1.2, PH_Y1 + 2.6, BACK, H_L + 1))
        t = t.cut(bx(a - 0.8, a, PH_Y1 - 0.01, PH_Y1 + 2.6, BACK, H_L + 1))
        t = t.cut(bx(c, c + 0.8, PH_Y1 - 0.01, PH_Y1 + 2.6, BACK, H_L + 1))
        snap = [(PH_Y1 + 0.01, LIP_Z0), (PH_Y1 - SNAP_LIP, LIP_Z0), (PH_Y1 - SNAP_LIP, LIP_Z0 + 0.2),
                (PH_Y1 + 0.01, H_L)]
        t = t.union(prism_yz(snap, a, c))
    t = t.cut(bx(PH_TOP + VOL_FROM_TOP[0], PH_TOP + VOL_FROM_TOP[1], PH_Y0 - 1.0, PH_Y0 + 0.1, 3.0, 9.0))
    # botao Power: camara do flange + batente a 45 graus + tunel ate fora
    zc = BACK + PH_H / 2
    t = t.cut(bx(PX - 10.0, PX + 10.0, PH_Y1 - 0.1, PH_Y1 + 2.4, zc - 3.9, zc + 3.9))
    t = t.cut(loft_y(PX, zc, PH_Y1 + 2.39, PH_Y1 + 4.4, 20.0, 7.8, 16.2, 7.2))
    t = t.cut(bx(PX - 8.1, PX + 8.1, PH_Y1 + 4.3, W + 1, zc - 3.6, zc + 3.6))   # folga 0.3

    # janelas laterais em U (abertas para o rebordo) com juntas nas ranhuras
    t = t.cut(bx(sx1 - 3.0, L + 1, PH_CY - 23.5, PH_CY + 23.5, z0, H_L + 1))           # dir: USB-C/jack
    t = t.cut(bx(PH_X0 + PH_PL - 1, sx1 - 2.9, PH_CY - 22.0, PH_CY + 22.0, z0, H_L + 1))
    t = t.cut(bx(-1, sx0 + 3.0, PH_CY - 11.0, PH_CY + 11.0, z0, H_L + 1))              # esq: mic/SIM
    t = t.cut(bx(sx0 + 2.9, PH_X0 + 1, PH_CY - 8.0, PH_CY + 8.0, 3.0, H_L + 1))
    seams = [PH_CY - 23.5, PH_CY + 23.5, PH_CY - 11.0, PH_CY + 11.0]
    for xs0, xs1 in ((-1, sx0 + 0.6), (sx1 - 0.6, L + 1)):   # riscas de aviso junto a dobradica
        for y0 in (5.5, 9.1):
            t = t.cut(prism_yz([(y0, 3.6), (y0 + 1.6, 3.6), (y0 + 8.4, 10.4), (y0 + 6.8, 10.4)], xs0, xs1))
    for y in seams:                                     # mesmo padrao dos dois lados
        t = t.cut(vgroove(sx0, y, -1, 0, z0 - 0.01, z1))
        t = t.cut(vgroove(sx1, y, 1, 0, z0 - 0.01, z1))
    for x in (PX - 10.5, PX + 10.5, 100.0, 128.0):
        t = t.cut(vgroove(x, sy1, 0, 1, z0 - 0.01, z1))
    for (p0, p1), n in zip((((0.0, W - FC), (FC, W)), ((L - FC, W), (L, W - FC))), ((-S2, S2), (S2, S2))):
        q0 = (p0[0] - n[0] * BELT, p0[1] - n[1] * BELT)
        q1 = (p1[0] - n[0] * BELT, p1[1] - n[1] * BELT)
        for f in (0.3, 0.5, 0.7):
            t = t.cut(louver(q0, q1, f, 1.2, 0.8, z0 + 1.0, H_L - 1.2, n))

    # ---- costas (face na mesa = topo do deck fechado) ----
    # baia optica da camara: rebaixo + recorte em capsula com chanfro
    cx = PH_TOP + CAM_CENTER_FROM_TOP
    cw, cl = CAM_SIZE
    hx, hy = cw / 2 + 4.5, cl / 2 + 4.5
    bay = [(cx - hx + 2, PH_CY - hy), (cx + hx - 4, PH_CY - hy), (cx + hx, PH_CY - hy + 4), (cx + hx, PH_CY + hy - 4),
           (cx + hx - 4, PH_CY + hy), (cx - hx + 2, PH_CY + hy), (cx - hx, PH_CY + hy - 2), (cx - hx, PH_CY - hy + 2)]
    t = t.cut(groove_ring(bay))
    t = t.cut(cam_cut(cx, PH_CY, cw, cl, CAM_R, -0.5, BACK + 1))
    t = t.cut(cam_cut(cx, PH_CY, cw + 2 * BACK, cl + 2 * BACK, CAM_R + BACK, -0.001, BACK, taper=45))
    # grelha hexagonal de ventilacao (atras do SoC)
    pts = []
    pitch, af = 4.8, 3.4
    gx0 = cx + hx + 3.0
    for i in range(8):
        for j in range(8):
            x = gx0 + 3.5 + i * pitch * math.cos(math.radians(30))
            y = PH_CY - 15.0 + j * pitch + (pitch / 2 if i % 2 else 0)
            if abs(y - PH_CY) <= 16.5:
                pts.append((x, y))
    d = af / math.cos(math.radians(30))
    t = t.cut(cq.Workplane("XY").pushPoints(pts).polygon(6, d).extrude(BACK + 1).translate((0, 0, -0.5)))
    # moldura da grelha
    gx1 = gx0 + 3.5 + 7 * pitch * math.cos(math.radians(30)) + 3.5
    t = t.cut(groove_ring([(gx0, PH_CY - 21), (gx1 - 3, PH_CY - 21), (gx1, PH_CY - 18), (gx1, PH_CY + 21),
                           (gx0 + 3, PH_CY + 21), (gx0, PH_CY + 18)]))
    # linhas de painel (ranhuras 0.8 x 0.4)
    frame_o = cq.Workplane("XY").polyline(FOOT_LID).close().offset2D(-4.6).extrude(0.5)
    frame_i = cq.Workplane("XY").polyline(FOOT_LID).close().offset2D(-5.4).extrude(0.5)
    t = t.cut(frame_o.cut(frame_i).translate((0, 0, -0.1)))
    yv = lambda y: W - y                                      # vista fechada -> impressao
    for ln in (((5.0, 23.0), (159.0, 23.0)), ((57.0, 69.5), (159.0, 69.5)), ((97.0, 23.0), (97.0, 69.5))):
        t = t.cut(groove_line([(x, yv(y)) for x, y in ln]))
    # chevrons >>> na faixa da frente
    for k in range(3):
        x0 = 143.0 + k * 4.2
        chev = [(x0, 10.0), (x0 + 1.6, 10.0), (x0 + 4.6, 14.3), (x0 + 1.6, 18.6), (x0, 18.6), (x0 + 3.0, 14.3)]
        t = t.cut(acc("lid", poly_z([(x, yv(y)) for x, y in chev], -0.1, 0.6)))
    # codigo de barras na faixa de tras
    xb = 121.0
    for wbar in (1.2, 2.4, 1.2, 1.2, 3.0, 1.2, 1.8, 1.2, 2.4, 1.2, 1.2, 2.4):
        t = t.cut(bx(xb, xb + wbar, yv(82.5), yv(72.5), -0.1, 0.5))
        xb += wbar + 1.2
    # rasgos para as pecas laranja (08)
    for s in inlay_shapes():
        t = t.cut(poly_z(s, -0.1, 1.0))
    # gravacoes (espelhadas para lerem bem com a tampa fechada)
    t = t.cut(acc("lid", glitch_text("SPECTRE", 15.0, TXT_D).mirror("XZ").translate((98.0, W - 14.6, -0.01))))
    t = t.cut(acc("lid", bx(48.0, 53.0, W - 14.6 - 0.9, W - 14.6 + 0.9, -0.1, TXT_D)))      # fragmento do glitch
    # katakana na vertical (スペクター), faixa da esquerda
    for i, ch in enumerate("スペクター"):
        g = text_solid(ch, 8.5, TXT_D, font=FONT_JP)
        if ch == "ー":
            g = g.rotate((0, 0, 0), (0, 0, 1), 90)
        t = t.cut(acc("lid", g.mirror("XZ").translate((16.5, W - (63.0 - i * 8.6), -0.01))))
    # pistas de circuito impresso
    for tr in CIRCUIT:
        t = t.cut(trace([(x, W - y) for x, y in tr]))
    # rasgo da barra neon na frente (ao lado de PWR)
    zl_n = (LID_BELT_Z0 + H_L) / 2
    for grp, face, a0, a1, zc_n in NEON:
        if grp == "lid":
            t = t.cut(neon_slot(face, a0, a1, zc_n, lid=True))
    t = t.cut(acc("lid", text_solid("MK-1", 20.0, TXT_D, mirror="XZ").translate((128.5, W - 51.0, -0.01))))
    t = t.cut(acc("lid", text_solid("LOGAN TECH", 10.0, TXT_D, mirror="XZ").translate((70.0, W - 77.0, -0.01))))
    # "PWR" grande ao lado do botao (cinta da frente), legivel com a tampa fechada
    pwr = (text_solid("PWR", 8.5, 0.7).rotate((0, 0, 0), (1, 0, 0), 90)
           .translate((PX + 24.5, BELT + 0.6, H_B + H_L - (LID_BELT_Z0 + H_L) / 2))
           .rotate((0, 0, 0), (1, 0, 0), 180).translate((0, W, H_B + H_L)))
    t = t.cut(pwr)
    # linhas de ventilacao nos paineis laterais (as da direita estao na tampa 05)
    zl = (LID_BELT_Z0 + H_L) / 2
    for dz in VENT_Z:
        for y0, y1 in ((PH_CY - 22.0, PH_CY - 11.0), (PH_CY + 11.0, PH_CY + 22.0)):
            t = t.cut(bx(-1, sx0 + 0.6, y0, y1, zl + dz - 0.5, zl + dz + 0.5))

    # ---- dobradicas (eixo y=-AX_OFF, z=H_L) com caixa de porca ----
    ay, az = -AX_OFF, H_L
    k = R_K * S2
    for x0, x1 in LID_K:
        web = [(ay + 10, az), (ay, az), (ay - k, az - k), (ay - k + (az - k), 0), (ay + 10, 0)]
        t = t.union(prism_yz(web, x0, x1)).union(cyl_x(ay, az, R_K, x0, x1))
        t = t.cut(teardrop_x(ay, az, HOLE_D, x0 - 1, x1 + 1))
    t = t.cut(hex_x(ay, az, NUT_AF, LID_K[0][1] - NUT_DEPTH, LID_K[0][1] + 1))
    t = t.cut(hex_x(ay, az, NUT_AF, LID_K[1][0] - 1, LID_K[1][0] + NUT_DEPTH))

    # gancho frontal em L
    ys0, ys1 = W - 6.4, W - 3.4
    foot_z0 = H_B - 8.6
    t = t.union(bx(HX, HX + 8.0, ys0, ys1, H_L - 0.5, H_L + foot_z0))
    t = t.union(bx(HX, HX + 11.0, ys0, ys1, H_L + foot_z0 - 2.4, H_L + foot_z0))
    return t


def inlay_shapes():
    """Faixas laranja nas costas da tampa (coordenadas de impressao da tampa)."""
    yv = lambda y: W - y                       # vista fechada -> impressao
    shapes = []
    bar = para(102.0, 30.0, 50.0, 4.5, 4.5)                 # barra por baixo de MK-1
    shapes.append([(x, yv(y)) for x, y in bar])
    for x0 in (18.0, 26.5, 35.0):                          # riscas de aviso, frente-esquerda
        d = para(x0, 9.5, 5.0, 9.5, 5.0)
        shapes.append([(x, yv(y)) for x, y in d])
    return shapes


# ------------------------------------------------------ PECAS ----------
def make_slide():
    x0 = HX - 4.5
    s = bx(x0, x0 + 24, 2.1, 13.7, FLOOR, 8.2)
    blk = bx(HX + 8.3, HX + 13.4, 2.6, 11.6, 8.2, ROOF_Z0 - 0.2)
    blk = blk.cut(bx(HX + 8.3 - 0.1, HX + 11.4, 2.5, 7.4, 8.1, 11.3))
    s = s.union(blk)
    s = s.union(bx(HX - 0.5, HX + 11.5, -TAB_OUT, 2.2, 3.6, 7.0))     # patilha sai TAB_OUT para fora (empurra com o dedo)
    for g in (HX + 2.0, HX + 4.5, HX + 7.0, HX + 9.5):                  # estrias de aderencia
        s = s.cut(bx(g - 0.4, g + 0.4, -TAB_OUT - 0.1, -TAB_OUT + 0.5, 3.5, 7.1))
    return s


def power_icon(depth):
    """Simbolo de power (anel aberto + barra), traco 0.8 mm, em XY (u, v=cima)."""
    ring = cq.Workplane("XY").circle(2.75).circle(1.75).extrude(depth)
    ring = ring.cut(bx(-1.3, 1.3, 0.3, 3.2, -0.1, depth + 0.1))
    bar = bx(-0.5, 0.5, 0.2, 3.25, 0, depth)
    return ring.union(bar)


def make_button():
    """Botao Power cativo (coords da tampa, posicao de repouso encostado ao batente).
    Nub central carrega so na tecla do S10e; face exterior com simbolo de power."""
    zc = BACK + PH_H / 2
    y_out = W + BTN_OUT
    b = bx(PX - 5.0, PX + 5.0, PH_Y1 + 0.45, PH_Y1 + 1.25, zc - 1.2, zc + 1.2)         # nub (quase encostado a tecla)
    b = b.union(bx(PX - 9.8, PX + 9.8, PH_Y1 + 1.2, PH_Y1 + 2.45, zc - 3.75, zc + 3.75))  # flange
    b = b.union(loft_y(PX, zc, PH_Y1 + 2.4, PH_Y1 + 4.45, 19.6, 7.5, 15.6, 6.6))         # chanfro 45
    b = b.union(bx(PX - 7.9, PX + 7.9, PH_Y1 + 4.4, y_out, zc - 3.4, zc + 3.4))         # haste (folga 0.2 no tunel)
    icon = (power_icon(0.6).rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 1, 0), 180)
            .translate((PX, y_out + 0.1, zc)))
    b = b.cut(icon)
    return b


def make_cap(w, h, depth, vent=None, vz0=0.0):
    """Tampa disfarcada: face exterior em z=0 (na mesa), juntas laterais em V.
    vent = (u0, u1) extensao das linhas de ventilacao; vz0 = desvio vertical do centro das linhas."""
    cw, chh = w - 2 * CAP_CLR, h - 2 * CAP_CLR
    c = cq.Workplane("XY").box(cw, chh, depth, centered=(True, True, False))
    c = c.faces("<Z").edges("|Y").chamfer(VG)
    c = c.faces(">Z").edges().chamfer(0.3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = c.union(cq.Workplane("XY").circle(0.35).extrude(depth - 1.2).translate(
                (sx * (cw / 2 - 0.2), sy * chh / 4, 1.0)))
    c = c.cut(bx(-2.5, 2.5, -chh / 2 - 1, -chh / 2 + 0.6, -1, 0.5))        # entalhe da unha
    if vent:
        for dz in VENT_Z:
            c = c.cut(bx(max(vent[0], -cw / 2 - 1), min(vent[1], cw / 2 + 1), vz0 + dz - 0.5, vz0 + dz + 0.5, -1, 0.6))
    return c


def make_inlays():
    parts = None
    for s in inlay_shapes():
        p = cq.Workplane("XY").polyline(s).close().offset2D(-CAP_CLR).extrude(1.0)
        parts = p if parts is None else parts.union(p)
    return parts


def make_neon():
    """Barras laranja tipo neon (frente da base x2 + frente da tampa), face visivel na mesa."""
    out, y = None, 0.0
    for grp, face, a0, a1, zc_n in NEON:
        bar = bx(0, (a1 - a0) - 2 * CAP_CLR, y, y + 2.0 - 2 * CAP_CLR, 0, NEON_D - 0.05)
        out = bar if out is None else out.union(bar)
        y += 4.0
    return out


def make_letters(key, body, shell_solid):
    """Letras laranja para AMS: enchem exatamente as gravacoes (ficam a face)."""
    u = None
    for s_ in ACC[key]:
        u = s_ if u is None else u.union(s_)
    return shell_solid.intersect(u).cut(body)


def make_hinge_covers():
    c = cq.Workplane("XY").circle(CBORE_D / 2 - 0.08).extrude(0.9)
    c = c.cut(cq.Workplane("XY").polygon(6, 3.2).extrude(0.5).translate((0, 0, -0.01)))
    return c.union(c.translate((10, 0, 0)))


def make_test_phone():
    """Gabarito rapido: confirma encaixe do S10e, camara e botao Power (~10 g)."""
    wall, h = 1.6, 4.0
    g = rbox(PH_X0 - wall, PH_X0 + PH_PL + wall, PH_Y0 - wall, PH_Y1 + wall, 0, 1.2 + h, PH_R + wall)
    g = g.cut(rbox(PH_X0, PH_X0 + PH_PL, PH_Y0, PH_Y1, 1.2, 10, PH_R))
    cx = PH_TOP + CAM_CENTER_FROM_TOP
    g = g.cut(cam_cut(cx, PH_CY, CAM_SIZE[0], CAM_SIZE[1], CAM_R, -1, 5))
    g = g.cut(bx(PX - 8.5, PX + 8.5, PH_Y1 - 1, PH_Y1 + 5, 1.2, 10))
    g = g.cut(bx(PH_TOP + VOL_FROM_TOP[0], PH_TOP + VOL_FROM_TOP[1], PH_Y0 - 5, PH_Y0 + 1, 1.2 + 2.0, 10))
    g = g.cut(rbox(PH_X0 + 25, PH_X0 + PH_PL - 25, PH_Y0 + 12, PH_Y1 - 12, -1, 5, 6))
    return g.translate((-PH_X0 + 5, -PH_Y0 + 5, 0))


def make_test_keyboard():
    """Gabarito rapido: confirma encaixe do Rii X1 e as janelas do lado esquerdo."""
    wall, h = 1.6, 9.0
    g = kb_pocket(-wall, -wall, 0, 1.2 + h, clr=KB_CLR + wall)
    g = g.cut(kb_pocket(0, 0, 1.2, 20))
    g = g.cut(rbox(15, KB_PL - 15, 12, KB_PW - 12, -1, 5, 6))
    g = g.cut(kb_bump_cut(0, 0, -1, 1.3))
    kb_back = KB_PW - KB_CLR
    for d in (KB_SWITCH_FROM_BACK, KB_PORT_FROM_BACK):
        yc = kb_back - d
        g = g.cut(bx(-5, 1, yc - 7.0, yc + 7.0, 1.2 + KB_H / 2 - 4.0, 20))
    return g.translate((5, 5, 0))


# ---------------------------------------------------------------- EXPORT ---
def main(out):
    os.makedirs(out, exist_ok=True)
    slide, button = make_slide(), make_button()
    base, lid = make_base(), make_lid()
    parts = {
        "01_mark1_spectre_base_PRETO": base,
        "02_mark1_spectre_lid_PRETO": lid,
        "03_mark1_tranca_slide_LARANJA": slide.translate((0, 0, -FLOOR)),
        "04_mark1_botao_power_LARANJA": button.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, W + BTN_OUT)),
        "05_mark1_tampa_usbc_DIR_PRETO": make_cap(47.0, H_L - LID_BELT_Z0 + CAP_CLR, 3.0, vent=(-22.0, 22.0), vz0=-CAP_CLR / 2),
        "06_mark1_tampa_mic_ESQ_PRETO": make_cap(22.0, H_L - LID_BELT_Z0 + CAP_CLR, 3.0, vent=(-99, 99), vz0=-CAP_CLR / 2),
        "07_mark1_tampas_base_x2_PRETO": make_cap(15.0, BASE_BELT_Z[1] - BASE_BELT_Z[0], 3.0, vent=(-6.0, 6.0)),
        "08_mark1_faixas_tampa_LARANJA": make_inlays(),
        "09_mark1_tampas_parafuso_x2_LARANJA": make_hinge_covers(),
        "10_mark1_barras_neon_x3_LARANJA": make_neon(),
        "00a_TESTE_encaixe_S10e": make_test_phone(),
        "00b_TESTE_encaixe_RiiX1": make_test_keyboard(),
    }
    # ---- versao AMS: laranja so numa pele de AMS_LAYERS camadas, o resto da gravacao fica preto
    skin = AMS_LAYERS * LAYER_H
    lb = make_letters("base", base, shell(FOOT_BASE, H_B, CH_BED_BASE, CH_RIM))
    ll = make_letters("lid", lid, shell(FOOT_LID, H_L, CH_BED_LID, CH_RIM))
    slab_b = bx(-10, L + 10, -10, W + 30, -1, skin).union(bx(-10, L + 10, -10, W + 30, H_B - skin, H_B + 10))
    slab_l = bx(-10, L + 10, -20, W + 10, -1, skin)
    lb_skin, ll_skin = lb.intersect(slab_b), ll.intersect(slab_l)
    parts["01_mark1_spectre_base_PRETO_AMS"] = base.union(lb.cut(lb_skin))
    parts["02_mark1_spectre_lid_PRETO_AMS"] = lid.union(ll.cut(ll_skin))
    parts["11_AMS_letras_base_LARANJA"] = lb_skin
    parts["12_AMS_letras_tampa_LARANJA"] = ll_skin
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(out, name + ".stl"), tolerance=0.02, angularTolerance=0.15)
        if not name.startswith("00"):
            cq.exporters.export(p, os.path.join(out, name + ".step"))
    asm = os.path.join(out, "_assembly")
    os.makedirs(asm, exist_ok=True)
    cq.exporters.export(slide, os.path.join(asm, "slide_locked.stl"), tolerance=0.02)
    cq.exporters.export(button, os.path.join(asm, "button_lidcoords.stl"), tolerance=0.02)
    print("OK ->", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl"))
