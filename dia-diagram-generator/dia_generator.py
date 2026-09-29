#!/usr/bin/env python3
"""Generador de diagramas Entidad-Relación (.dia) a partir de JSON.

PROTOTIPO (Paso 1/2): reglas de tamaño y puntos de conexión verificadas contra
Dia 0.98. Aún sin validación exhaustiva ni CLI final (Paso 3).

Uso:  python3 dia_generator.py entrada.json salida.dia [--plain]
"""
import gzip
import json
import math
import sys
import xml.etree.ElementTree as ET

NS = "http://www.lysator.liu.se/~alla/dia/"
ET.register_namespace("dia", NS)

# --- Reglas medidas en archivos reales de Dia (fuente Courier 0.8) ---------
CHAR_W = 0.385            # ancho por carácter
ENTITY_PAD, ROUND_PAD = 1.4, 2.0
BOX_H = 1.8               # alto de entidad y atributo
REL_RATIO = 0.6           # alto/ancho del rombo
TRI_W, TRI_H = 2.225, 2.2  # triángulo "ES"
BORDER = 0.1

# Índices de puntos de conexión (0-7 fijos, 8 = centro con autogap)
RECT_CP = {"TL": 0, "N": 1, "TR": 2, "W": 3, "E": 4, "BL": 5, "S": 6, "BR": 7, "C": 8}
DIAMOND_CP = {"W": 0, "NW": 1, "N": 2, "NE": 3, "E": 4, "SW": 5, "S": 6, "SE": 7, "C": 8}
TRI_CENTER_CP = 12


def _fmt(v):
    return ("%.5f" % v).rstrip("0").rstrip(".")


class Shape:
    def __init__(self, kind, sid, name, cx, cy, w, h, **props):
        self.kind, self.id, self.name = kind, sid, name
        self.cx, self.cy, self.w, self.h = cx, cy, w, h
        self.props = props

    @property
    def x(self):
        return self.cx - self.w / 2

    @property
    def y(self):
        return self.cy - self.h / 2

    def cp_pos(self, side):
        """Posición (x, y) de un punto de conexión nombrado."""
        x, y, w, h = self.x, self.y, self.w, self.h
        if self.kind == "rel":
            pts = {"W": (x, y + h / 2), "N": (x + w / 2, y), "E": (x + w, y + h / 2),
                   "S": (x + w / 2, y + h), "NW": (x + w / 4, y + h / 4), "NE": (x + 3 * w / 4, y + h / 4),
                   "SW": (x + w / 4, y + 3 * h / 4), "SE": (x + 3 * w / 4, y + 3 * h / 4)}
        else:
            pts = {"TL": (x, y), "N": (x + w / 2, y), "TR": (x + w, y), "W": (x, y + h / 2),
                   "E": (x + w, y + h / 2), "BL": (x, y + h), "S": (x + w / 2, y + h), "BR": (x + w, y + h)}
        return pts.get(side, (self.cx, self.cy))

    def cp_index(self, side):
        return (DIAMOND_CP if self.kind == "rel" else RECT_CP)[side]

    def boundary(self, tx, ty):
        """Punto del borde de la forma en la dirección de (tx, ty)."""
        dx, dy = tx - self.cx, ty - self.cy
        if dx == 0 and dy == 0:
            return self.cx, self.cy
        a, b = self.w / 2, self.h / 2
        if self.kind in ("entity", "tri"):
            t = min(a / abs(dx) if dx else 1e9, b / abs(dy) if dy else 1e9)
        elif self.kind == "attr":
            t = 1 / math.hypot(dx / a, dy / b)
        else:  # rombo
            t = 1 / (abs(dx) / a + abs(dy) / b)
        return self.cx + dx * t, self.cy + dy * t


# --- Construcción XML --------------------------------------------------------
def _q(tag):
    return "{%s}%s" % (NS, tag)


def _attr(parent, name):
    return ET.SubElement(parent, _q("attribute"), name=name)


def _point(parent, x, y):
    ET.SubElement(parent, _q("point"), val="%s,%s" % (_fmt(x), _fmt(y)))


def _real(parent, name, v):
    ET.SubElement(_attr(parent, name), _q("real"), val=_fmt(v))


def _bool(parent, name, v):
    ET.SubElement(_attr(parent, name), _q("boolean"), val="true" if v else "false")


def _color(parent, name, v):
    ET.SubElement(_attr(parent, name), _q("color"), val=v)


def _string(parent, name, v):
    ET.SubElement(_attr(parent, name), _q("string")).text = "#%s#" % v


def _font(parent, name="font", family="monospace", style="0", fname="Courier"):
    ET.SubElement(_attr(parent, name), _q("font"), family=family, style=style, name=fname)


def _bbox(parent, x0, y0, x1, y1, pad=0.05):
    ET.SubElement(_attr(parent, "obj_bb"), _q("rectangle"),
                  val="%s,%s;%s,%s" % (_fmt(x0 - pad), _fmt(y0 - pad), _fmt(x1 + pad), _fmt(y1 + pad)))


def _obj(layer, otype, oid, version="0"):
    return ET.SubElement(layer, _q("object"), type=otype, version=version, id=oid)


def _element_common(o, s):
    ET.SubElement(_attr(o, "obj_pos"), _q("point"), val="%s,%s" % (_fmt(s.x), _fmt(s.y)))
    # Un rombo con etiquetas de cardinalidad reserva ~1.15 cm extra (como guarda Dia)
    ex = 1.15 if s.kind == "rel" else 0.0
    _bbox(o, s.x, s.y - ex, s.x + s.w, s.y + s.h + ex)
    ET.SubElement(_attr(o, "elem_corner"), _q("point"), val="%s,%s" % (_fmt(s.x), _fmt(s.y)))
    _real(o, "elem_width", s.w)
    _real(o, "elem_height", s.h)


def _style(o):
    _real(o, "border_width", BORDER)
    _color(o, "border_color", "#000000")
    _color(o, "inner_color", "#ffffff")


def _write_shape(layer, s):
    if s.kind == "entity":
        o = _obj(layer, "ER - Entity", s.id)
        _element_common(o, s); _style(o)
        _string(o, "name", s.name)
        _bool(o, "weak", s.props.get("weak", False))
        _bool(o, "associative", s.props.get("associative", False))
    elif s.kind == "attr":
        o = _obj(layer, "ER - Attribute", s.id)
        _element_common(o, s); _style(o)
        _string(o, "name", s.name)
        _bool(o, "key", s.props.get("key", False))
        _bool(o, "weak_key", s.props.get("weak_key", False))
        _bool(o, "derived", s.props.get("derived", False))
        _bool(o, "multivalued", s.props.get("multivalued", False))
    elif s.kind == "rel":
        o = _obj(layer, "ER - Relationship", s.id)
        _element_common(o, s); _style(o)
        _string(o, "name", s.name)
        _string(o, "left_card", s.props.get("left_card", ""))
        _string(o, "right_card", s.props.get("right_card", ""))
        _bool(o, "identifying", s.props.get("identifying", False))
        _bool(o, "rotated", s.props.get("rotated", False))
    elif s.kind == "tri":
        o = _obj(layer, "Flowchart - Merge", s.id, version="1")
        ET.SubElement(_attr(o, "obj_pos"), _q("point"), val="%s,%s" % (_fmt(s.x), _fmt(s.y)))
        _bbox(o, s.x, s.y, s.x + s.w, s.y + s.h, pad=0.1)
        ET.SubElement(_attr(o, "meta"), _q("composite"), type="dict")
        ET.SubElement(_attr(o, "elem_corner"), _q("point"), val="%s,%s" % (_fmt(s.x), _fmt(s.y)))
        _real(o, "elem_width", s.w)
        _real(o, "elem_height", s.h)
        _real(o, "line_width", BORDER)
        _color(o, "line_colour", "#000000")
        _color(o, "fill_colour", "#ffffff")
        _bool(o, "show_background", True)
        ls = _attr(o, "line_style")
        ET.SubElement(ls, _q("enum"), val="0")
        ET.SubElement(ls, _q("real"), val="1")
        _real(o, "padding", 0.1)
        txt = ET.SubElement(_attr(o, "text"), _q("composite"), type="text")
        _string(txt, "string", "ES")
        _font(txt, "font", "sans", "0", "Helvetica")
        _real(txt, "height", 0.8)
        ty = s.y + (s.h - 0.75 if s.props.get("flip") else 0.75)
        ET.SubElement(_attr(txt, "pos"), _q("point"), val="%s,%s" % (_fmt(s.cx), _fmt(ty)))
        _color(txt, "color", "#000000")
        ET.SubElement(_attr(txt, "alignment"), _q("enum"), val="1")
        _bool(o, "flip_horizontal", False)
        _bool(o, "flip_vertical", s.props.get("flip", False))
        _real(o, "subscale", 1)
        return
    else:
        raise ValueError(s.kind)
    _font(o)
    _real(o, "font_height", 0.8)


def _connections(o, pairs):
    c = ET.SubElement(o, _q("connections"))
    for handle, (target, cp) in enumerate(pairs):
        ET.SubElement(c, _q("connection"), handle=str(handle), to=target, connection=str(cp))


def _write_line(layer, oid, a, b):
    """Línea atributo↔forma: extremos en el borde, conectada por el centro (autogap)."""
    p0, p1 = a.boundary(b.cx, b.cy), b.boundary(a.cx, a.cy)
    o = _obj(layer, "Standard - Line", oid)
    ET.SubElement(_attr(o, "obj_pos"), _q("point"), val="%s,%s" % (_fmt(p0[0]), _fmt(p0[1])))
    _bbox(o, min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]))
    ep = _attr(o, "conn_endpoints")
    _point(ep, *p0); _point(ep, *p1)
    ET.SubElement(_attr(o, "numcp"), _q("int"), val="1")
    _connections(o, [(a.id, 8), (b.id, TRI_CENTER_CP if b.kind == "tri" else 8)]
                 if a.kind != "tri" else [(a.id, TRI_CENTER_CP), (b.id, 8)])


def _write_participation(layer, oid, rel, rside, ent, eside, total):
    p0, p1 = rel.cp_pos(rside), ent.cp_pos(eside)
    horizontal_first = rside in ("W", "E", "NW", "NE", "SW", "SE")
    if horizontal_first:
        pts = [p0, ((p0[0] + p1[0]) / 2, p0[1]), ((p0[0] + p1[0]) / 2, p1[1]), p1]
        orient = [0, 1, 0]
    else:
        pts = [p0, (p0[0], (p0[1] + p1[1]) / 2), (p1[0], (p0[1] + p1[1]) / 2), p1]
        orient = [1, 0, 1]
    o = _obj(layer, "ER - Participation", oid, version="1")
    ET.SubElement(_attr(o, "obj_pos"), _q("point"), val="%s,%s" % (_fmt(p0[0]), _fmt(p0[1])))
    _bbox(o, min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
    op = _attr(o, "orth_points")
    for p in pts:
        _point(op, *p)
    oo = _attr(o, "orth_orient")
    for v in orient:
        ET.SubElement(oo, _q("enum"), val=str(v))
    _bool(o, "autorouting", True)   # Dia recalcula la ruta al cargar
    _bool(o, "total", total)
    _connections(o, [(rel.id, rel.cp_index(rside)), (ent.id, ent.cp_index(eside))])


def _auto_sides(ent, rel):
    """Lados de conexión (rombo, entidad) según posición relativa."""
    dx, dy = ent.cx - rel.cx, ent.cy - rel.cy
    if abs(dy) <= 0.6:
        return ("E", "W") if dx > 0 else ("W", "E")
    if abs(dx) <= 0.6:
        return ("S", "N") if dy > 0 else ("N", "S")
    if abs(dx) > abs(dy):
        return ("E" if dx > 0 else "W", "N" if dy > 0 else "S")
    return ("S" if dy > 0 else "N", "W" if dx > 0 else "E")


# --- API principal ------------------------------------------------------------
def build(spec):
    shapes, order, by_id = [], [], {}
    counter = [0]

    def new_id():
        i = "O%d" % counter[0]
        counter[0] += 1
        return i

    def add(kind, ref, name, cx, cy, w, h, **p):
        s = Shape(kind, new_id(), name, cx, cy, w, h, **p)
        shapes.append(s)
        if ref:
            by_id[ref] = s
        return s

    for e in spec.get("entidades", []):
        n = e["nombre"]
        add("entity", e["id"], n, e["x"], e["y"], round(CHAR_W * len(n) + ENTITY_PAD, 4), BOX_H,
            weak=e.get("debil", False), associative=e.get("asociativa", False))

    rel_defs = []
    for r in spec.get("relaciones", []):
        n = r["nombre"]
        w = round(CHAR_W * len(n) + ROUND_PAD, 4)
        s = add("rel", r["id"], n, r["x"], r["y"], w, round(REL_RATIO * w, 4),
                identifying=r.get("identificadora", False))
        rel_defs.append((s, r))

    for a in spec.get("atributos", []):
        n = a["nombre"]
        t = a.get("tipo", "simple")
        add("attr", None, n, a["x"], a["y"], round(CHAR_W * len(n) + ROUND_PAD, 4), BOX_H,
            key=t == "clave", weak_key=t == "clave_parcial", derived=t == "derivado",
            multivalued=t == "multivalorado", owner=a["de"])

    for es in spec.get("especializaciones", []):
        add("tri", es["id"], "ES", es["x"], es["y"], TRI_W, TRI_H, flip=es.get("voltear", False))

    # Etiquetas de cardinalidad, lados y orientación de cada relación
    part_plan = []
    for s, r in rel_defs:
        parts = r["participantes"]
        plan = []
        for idx, p in enumerate(parts):
            ent = by_id[p["entidad"]]
            rs, es_ = _auto_sides(ent, s)
            if len(parts) == 2 and parts[0]["entidad"] == parts[1]["entidad"]:
                rs = "W" if idx == 0 else "E"
            rs = p.get("lado_relacion", rs)
            es_ = p.get("lado_entidad", es_)
            plan.append((ent, rs, es_, p))
        rotated = all(x[1] in ("N", "S") for x in plan)
        s.props["rotated"] = rotated
        left_slot, right_slot = ("N", "S") if rotated else ("W", "E")
        extra = []
        for ent, rs, es_, p in plan:
            card = p.get("cardinalidad", "")
            if rs == left_slot and "left_card" not in s.props:
                s.props["left_card"] = card
            elif rs == right_slot and "right_card" not in s.props:
                s.props["right_card"] = card
            else:
                extra.append((rs, card))
        for rs, card in extra:   # rombo sólo tiene 2 etiquetas: la 3.ª va como texto
            s.props.setdefault("extra_labels", []).append((rs, card))
        part_plan.append((s, plan))

    root = ET.Element(_q("diagram"))
    _write_header(root, spec)
    layer = ET.SubElement(root, _q("layer"), name="Fondo", visible="true", active="true")
    for s in shapes:
        _write_shape(layer, s)
        for rs, card in s.props.get("extra_labels", []):
            _write_text(layer, new_id(), s, rs, card)

    for a in [x for x in shapes if x.kind == "attr"]:
        _write_line(layer, new_id(), a, by_id[a.props["owner"]] if a.props["owner"] in by_id else _find_rel(rel_defs, a.props["owner"]))
    for es in spec.get("especializaciones", []):
        tri = by_id[es["id"]]
        _write_line(layer, new_id(), by_id[es["padre"]], tri)
        for h in es["hijos"]:
            _write_line(layer, new_id(), tri, by_id[h])
    for s, plan in part_plan:
        for ent, rs, es_, p in plan:
            _write_participation(layer, new_id(), s, rs, ent, es_, p.get("total", False))
    return root


def _find_rel(rel_defs, rid):
    for s, r in rel_defs:
        if r["id"] == rid:
            return s
    raise KeyError(rid)


def _write_text(layer, oid, rel, side, text):
    """Etiqueta suelta (Standard - Text) cerca del vértice de la relación."""
    px, py = rel.cp_pos(side)
    off = {"N": (0.4, -0.5), "S": (0.4, 0.9), "W": (-0.9, -0.3), "E": (0.4, -0.3)}[side]
    x, y = px + off[0], py + off[1]
    o = _obj(layer, "Standard - Text", oid)
    ET.SubElement(_attr(o, "obj_pos"), _q("point"), val="%s,%s" % (_fmt(x), _fmt(y)))
    _bbox(o, x, y - 0.6, x + 0.5 * len(text), y + 0.2)
    txt = ET.SubElement(_attr(o, "text"), _q("composite"), type="text")
    _string(txt, "string", text)
    _font(txt, "font", "monospace", "0", "Courier")
    _real(txt, "height", 0.8)
    ET.SubElement(_attr(txt, "pos"), _q("point"), val="%s,%s" % (_fmt(x), _fmt(y)))
    _color(txt, "color", "#000099")
    ET.SubElement(_attr(txt, "alignment"), _q("enum"), val="0")
    ET.SubElement(_attr(o, "valign"), _q("enum"), val="3")


def _write_header(root, spec):
    dd = ET.SubElement(root, _q("diagramdata"))
    _color(dd, "background", "#ffffff")
    _color(dd, "pagebreak", "#000099")
    paper = ET.SubElement(_attr(dd, "paper"), _q("composite"), type="paper")
    _string(paper, "name", spec.get("papel", "A4"))
    for m in ("tmargin", "bmargin", "lmargin", "rmargin"):
        _real(paper, m, 2.54)
    _bool(paper, "is_portrait", False)
    _real(paper, "scaling", 1)
    _bool(paper, "fitto", False)
    grid = ET.SubElement(_attr(dd, "grid"), _q("composite"), type="grid")
    _real(grid, "width_x", 1)
    _real(grid, "width_y", 1)
    ET.SubElement(_attr(grid, "visible_x"), _q("int"), val="1")
    ET.SubElement(_attr(grid, "visible_y"), _q("int"), val="1")
    ET.SubElement(grid, _q("composite"), type="color")
    _color(dd, "color", "#d8e5e5")
    g = ET.SubElement(_attr(dd, "guides"), _q("composite"), type="guides")
    _attr(g, "hguides")
    _attr(g, "vguides")


def write(root, path, plain=False):
    ET.indent(root, space="  ")
    data = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="utf-8")
    if plain:
        open(path, "wb").write(data)
    else:
        with gzip.open(path, "wb") as f:
            f.write(data)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    spec = json.load(open(args[0], encoding="utf-8"))
    write(build(spec), args[1], plain="--plain" in sys.argv)
    print("OK ->", args[1])
