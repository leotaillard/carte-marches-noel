"""Génère le fond de carte (constante FOND de index.html) depuis les données ouvertes swisstopo.

Sources (usage libre, y compris commercial, avec mention « © swisstopo ») :
- swissBOUNDARIES3D : limites de cantons et de districts
  https://data.geo.admin.ch/ch.swisstopo.swissboundaries3d/swissboundaries3d_2026-01/swissboundaries3d_2026-01_2056_5728.gpkg.zip
- swissTLMRegio : lacs
  https://data.geo.admin.ch/ch.swisstopo.swisstlmregio/swisstlmregio_2026/swisstlmregio_2026_2056.gpkg.zip

    pip install geopandas
    python3 outils/fond-carte.py swissBOUNDARIES3D_1_5_LV95_LN02.gpkg swissTLMRegio_Product_LV95.gpkg fond.json

Puis remplacer la valeur de « const FOND = … ; » dans index.html par le contenu de fond.json.
"""
import json, sys
import geopandas as gpd
from shapely import force_2d
from shapely.geometry import box
from shapely.ops import unary_union, linemerge, transform
from pyproj import Transformer

BOUNDARIES, TLMREGIO, OUT = sys.argv[1:4]
DISTRICTS = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 2222]  # 7 districts FR + Broye-Vully (VD)
TOL = 50            # simplification, en mètres
LAC_MIN = 400_000   # lacs de plus de 0,4 km²
to_wgs = Transformer.from_crs(2056, 4326, always_xy=True).transform
BB = transform(Transformer.from_crs(4326, 2056, always_xy=True).transform, box(6.40, 46.27, 7.70, 47.23))  # vue bornée de la carte, avec une marge

def lire(path, layer, **kw):
    d = gpd.read_file(path, layer=layer, bbox=BB.bounds, **kw)
    d['geometry'] = force_2d(d.geometry.values)
    return d

dist = lire(BOUNDARIES, 'tlm_bezirksgebiet')
dist = dist[dist.bezirksnummer.isin(DISTRICTS)]
assert sorted(dist.bezirksnummer) == DISTRICTS, sorted(dist.bezirksnummer)
cant = lire(BOUNDARIES, 'tlm_kantonsgebiet')
lacs = lire(TLMREGIO, 'tlmregio_hydrography_lake')
lacs = unary_union([g for g in lacs.geometry if g.area >= LAC_MIN]).intersection(BB)

region = unary_union(dist.geometry.buffer(0)).difference(lacs)
cant_lines = unary_union([g.boundary for g in cant.geometry])
lignes_cantons = linemerge(cant_lines.intersection(BB))
lignes_districts = unary_union([g.boundary for g in dist.geometry]).difference(cant_lines.buffer(20))
if lignes_districts.geom_type != 'LineString':
    lignes_districts = linemerge(lignes_districts)

def ll(coords):
    return [[round(y, 4), round(x, 4)] for x, y in (to_wgs(x, y) for x, y in coords)]
def lignes(g):
    g = g.simplify(TOL)
    parts = [g] if g.geom_type == 'LineString' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'LineString']
    return [ll(p.coords) for p in parts if p.length > 150]
def polygones(g):
    g = g.simplify(TOL, preserve_topology=True)
    polys = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
    return [[ll(r.coords) for r in [p.exterior, *p.interiors] if len(r.coords) > 3] for p in polys if p.area > 20_000]

out = {'region': polygones(region), 'lacs': polygones(lacs), 'cantons': lignes(lignes_cantons), 'districts': lignes(lignes_districts)}
s = json.dumps(out, separators=(',', ':'))
open(OUT, 'w').write(s)
print('taille', len(s), {k: len(v) for k, v in out.items()}, file=sys.stderr)
