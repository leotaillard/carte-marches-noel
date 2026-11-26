"""Génère le fond de carte (constante FOND de index.html) depuis les données ouvertes swisstopo.

Sources (usage libre, y compris commercial, avec mention « © swisstopo ») :
- swissBOUNDARIES3D : limites de cantons et de districts
  https://data.geo.admin.ch/ch.swisstopo.swissboundaries3d/swissboundaries3d_2026-01/swissboundaries3d_2026-01_2056_5728.gpkg.zip
- swissTLMRegio : lacs, zones bâties, routes principales, localités
  https://data.geo.admin.ch/ch.swisstopo.swisstlmregio/swisstlmregio_2026/swisstlmregio_2026_2056.gpkg.zip

    pip install geopandas
    python3 outils/fond-carte.py swissBOUNDARIES3D_1_5_LV95_LN02.gpkg swissTLMRegio_Product_LV95.gpkg fond.json

Puis remplacer la valeur de « const FOND = … ; » dans index.html par le contenu de fond.json.
"""
import json, re, sys
import geopandas as gpd
from shapely import force_2d
from shapely.geometry import box
from shapely.ops import unary_union, linemerge, transform
from pyproj import Transformer

BOUNDARIES, TLMREGIO, OUT = sys.argv[1:4]
DISTRICTS = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 2222]  # 7 districts FR + Broye-Vully (VD)
TOL = 50             # simplification des limites, en mètres
TOL_LACS = 15        # lacs de la région, plus fins pour les zooms rapprochés
LAC_MIN = 400_000    # lacs de plus de 0,4 km²
TOL_BATI = 80
BATI_MIN = 150_000   # zones bâties de plus de 0,15 km², dans la région seulement
ROUTES = {'a': ['Autobahn', 'Autostr'], 'h': ['HauptStrAB4', 'HauptStrAB6']}  # autoroutes, routes principales
CHEFS_LIEUX = {'Fribourg', 'Bulle', 'Romont', 'Estavayer-le-Lac', 'Murten', 'Tafers', 'Châtel-St-Denis', 'Payerne'}  # déjà dans index.html
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
zone = unary_union(dist.geometry.buffer(0))
lacs = lire(TLMREGIO, 'tlmregio_hydrography_lake')
lacs = [g.buffer(0) for g in lacs.geometry if g.area >= LAC_MIN]
lacs_fins = unary_union([g for g in lacs if g.intersects(zone)]).intersection(BB)
lacs_autres = unary_union([g for g in lacs if not g.intersects(zone)]).intersection(BB)

region = zone.difference(lacs_fins)
cant_lines = unary_union([g.boundary for g in cant.geometry])
lignes_cantons = linemerge(cant_lines.intersection(BB))
lignes_districts = unary_union([g.boundary for g in dist.geometry]).difference(cant_lines.buffer(20))
if lignes_districts.geom_type != 'LineString':
    lignes_districts = linemerge(lignes_districts)

lc = lire(TLMREGIO, 'tlmregio_landcover_landcover', columns=['objval'])
bati = unary_union(lc[lc.objval.isin(['Siedl', 'Stadtzentr'])].geometry.buffer(0)).intersection(zone)
rd = lire(TLMREGIO, 'tlmregio_transportation_road', columns=['objval'])
routes = {k: linemerge(unary_union(rd[rd.objval.isin(v)].geometry).intersection(BB)) for k, v in ROUTES.items()}
nl = lire(TLMREGIO, 'tlmregio_names_namedlocation', columns=['objval', 'namn1'])
nl = nl[nl.objval.isin(['HOrtschaft1', 'GOrtschaft', 'MOrtschaft'])]

def ll(coords):
    return [[round(y, 4), round(x, 4)] for x, y in (to_wgs(x, y) for x, y in coords)]
def lignes(g, tol=TOL, lmin=150):
    g = g.simplify(tol)
    parts = [g] if g.geom_type == 'LineString' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'LineString']
    return [ll(p.coords) for p in parts if p.length > lmin]
def polygones(g, tol=TOL, amin=20_000, trous=True):
    g = g.simplify(tol, preserve_topology=True)
    polys = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
    return [[ll(r.coords) for r in ([p.exterior, *p.interiors] if trous else [p.exterior]) if len(r.coords) > 3] for p in polys if p.area > amin]

villes = []  # [nom, lat, lon, rang] : 1 = grande localité, 2 = autre localité ; seulement dans la région
for _, r in nl.iterrows():
    n = re.sub(r' (FR|NE|BE|VD)$', '', r.namn1)
    if n in CHEFS_LIEUX or not zone.contains(r.geometry):
        continue
    lo, la = to_wgs(r.geometry.x, r.geometry.y)
    villes.append([n, round(la, 4), round(lo, 4), 2 if r.objval == 'MOrtschaft' else 1])

out = {
    'region': polygones(region),
    'lacs': polygones(lacs_fins, TOL_LACS) + polygones(lacs_autres),
    'cantons': lignes(lignes_cantons),
    'districts': lignes(lignes_districts),
    'bati': polygones(bati, TOL_BATI, BATI_MIN, trous=False),
    'routes': {k: lignes(g, 60) for k, g in routes.items()},
    'villes': sorted(villes),
}
s = json.dumps(out, separators=(',', ':'), ensure_ascii=False)
open(OUT, 'w').write(s)
print('taille', len(s), {k: len(json.dumps(v, separators=(',', ':'), ensure_ascii=False)) for k, v in out.items()}, file=sys.stderr)
