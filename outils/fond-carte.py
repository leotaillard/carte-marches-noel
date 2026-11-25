"""Génère le fond de carte (constante FOND de index.html).

Source : limites généralisées OFS 2026, paquet npm swiss-maps (TopoJSON en WGS84).
Les districts de la région sont reconnus par recoupement avec data/fribourg-broye-districts.geojson.

    npm pack swiss-maps && tar xzf swiss-maps-*.tgz
    pip install shapely
    python3 outils/fond-carte.py package/2026/ch-combined.json data/fribourg-broye-districts.geojson fond.json

Puis remplacer la valeur de « const FOND = … ; » dans index.html par le contenu de fond.json.
"""
import json, sys
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, MultiLineString, box, mapping
from shapely.ops import unary_union, linemerge
topo_path, old_path, out_path = sys.argv[1:4]
t = json.load(open(topo_path)); sx, sy = t['transform']['scale']; tx, ty = t['transform']['translate']
arcs = []
for a in t['arcs']:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x*sx+tx, y*sy+ty))
    arcs.append(pts)
def arc(i): return arcs[i] if i >= 0 else arcs[~i][::-1]
def ring(idx):
    pts = []
    for i in idx:
        a = arc(i); pts.extend(a if not pts else a[1:])
    return pts
def geom(g):
    if g['type'] == 'Polygon': return Polygon(ring(g['arcs'][0]), [ring(r) for r in g['arcs'][1:]])
    if g['type'] == 'MultiPolygon': return MultiPolygon([Polygon(ring(p[0]), [ring(r) for r in p[1:]]) for p in g['arcs']])
    raise ValueError(g['type'])
O = t['objects']
BB = box(6.30, 46.22, 7.82, 47.28)
TOL = 0.0003
def rnd(o):
    if isinstance(o, (list, tuple)):
        if o and isinstance(o[0], float): return [round(o[0], 4), round(o[1], 4)]
        return [rnd(x) for x in o]
    return o
# Districts de la région : reconnus par recoupement avec l'ancien GeoJSON
old = [(f['properties']['name'], shape(f['geometry'])) for f in json.load(open(old_path))['features']]
dists = []
for g in O['districts']['geometries']:
    gm = geom(g).buffer(0)
    if not gm.intersects(BB): continue
    p = gm.representative_point()
    for name, og in old:
        if og.buffer(0.002).contains(p) and gm.intersection(og).area > 0.5 * gm.area:
            dists.append((name, gm)); break
print('districts:', sorted(n for n, _ in dists), file=sys.stderr)
lakes = unary_union([geom(g).buffer(0) for g in O['lakes']['geometries']]).intersection(BB)
region = unary_union([g for _, g in dists]).difference(lakes)
# Limites cantonales et frontière nationale, en lignes
cant = [geom(g).buffer(0) for g in O['cantons']['geometries']]
lines = linemerge(unary_union([c.boundary for c in cant if c.intersects(BB)]).intersection(BB))
# Limites de districts internes à la région (hors limites cantonales)
dlines = unary_union([g.boundary for _, g in dists]).difference(unary_union([c.boundary for c in cant]).buffer(0.0002)).intersection(BB)
dlines = linemerge(dlines) if dlines.geom_type != 'LineString' else dlines
def lc(g):
    g = g.simplify(TOL)
    parts = [g] if g.geom_type == 'LineString' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'LineString']
    return [rnd([(y, x) for x, y in p.coords]) for p in parts if p.length > 0.002]
def pc(g):
    g = g.simplify(TOL, preserve_topology=True)
    polys = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
    return [[rnd([(y, x) for x, y in r.coords]) for r in [p.exterior, *p.interiors]] for p in polys if p.area > 2e-6]
out = {'region': pc(region), 'lacs': pc(lakes), 'cantons': lc(lines), 'districts': lc(dlines)}
s = json.dumps(out, separators=(',', ':'))
open(out_path, 'w').write(s)
print('taille', len(s), {k: len(v) for k, v in out.items()}, file=sys.stderr)
