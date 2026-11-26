import json, sys, re
import geopandas as gpd
from shapely import force_2d
from shapely.geometry import box
from shapely.ops import unary_union, linemerge, transform
from pyproj import Transformer
L, B, OUT = sys.argv[1:4]
to_wgs = Transformer.from_crs(2056, 4326, always_xy=True).transform
BB = transform(Transformer.from_crs(4326, 2056, always_xy=True).transform, box(6.40, 46.27, 7.70, 47.23))
def lire(path, layer, **kw):
    d = gpd.read_file(path, layer=layer, bbox=BB.bounds, **kw); d['geometry'] = force_2d(d.geometry.values); return d
dist = lire(B, 'tlm_bezirksgebiet'); region = unary_union(dist[dist.bezirksnummer.isin([1001,1002,1003,1004,1005,1006,1007,2222])].geometry.buffer(0))
def ll(cs): return [[round(y,4), round(x,4)] for x,y in (to_wgs(x,y) for x,y in cs)]
def lignes(g, tol):
    g = g.simplify(tol); parts = [g] if g.geom_type=='LineString' else [p for p in getattr(g,'geoms',[]) if p.geom_type=='LineString']
    return [ll(p.coords) for p in parts if p.length > 100]
def polys(g, tol, amin):
    g = g.simplify(tol, preserve_topology=True); ps = [g] if g.geom_type=='Polygon' else [p for p in getattr(g,'geoms',[]) if p.geom_type=='Polygon']
    return [[ll(p.exterior.coords)] for p in ps if p.area > amin]
lc = lire(L, 'tlmregio_landcover_landcover', columns=['objval'])
bati = unary_union(lc[lc.objval.isin(['Siedl','Stadtzentr'])].geometry.buffer(0)).intersection(BB)
rd = lire(L, 'tlmregio_transportation_road', columns=['objval'])
cls = {'a': ['Autobahn','Autostr'], 'h': ['HauptStrAB4','HauptStrAB6'], 'v': ['VerbindStr4','VerbindStr6']}
routes = {k: lignes(linemerge(unary_union(rd[rd.objval.isin(v)].geometry).intersection(BB)), 40) for k,v in cls.items()}
nl = lire(L, 'tlmregio_names_namedlocation', columns=['objval','namn1'])
nl = nl[nl.objval.isin(['GOrtschaft','HOrtschaft1','MOrtschaft'])]
chefs = {'Fribourg','Bulle','Romont','Estavayer-le-Lac','Murten','Tafers','Châtel-St-Denis','Payerne'}
villes = []
for _, r in nl.iterrows():
    n = re.sub(r' (FR|NE|BE|VD)$', '', r.namn1)
    if n in chefs or not region.contains(r.geometry): continue
    lo, la = to_wgs(r.geometry.x, r.geometry.y)
    villes.append([n, round(la,4), round(lo,4), 1 if r.objval != 'MOrtschaft' else 2])
out = {'bati': polys(bati, 40, 40_000), 'routes': routes, 'villes': villes}
s = json.dumps(out, separators=(',',':'), ensure_ascii=False); open(OUT,'w').write(s)
print('taille', len(s), {k: (len(v) if not isinstance(v, dict) else {a: len(b) for a,b in v.items()}) for k,v in out.items()}, 'villes rang1', sum(1 for v in villes if v[3]==1), file=sys.stderr)
