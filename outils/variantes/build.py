import sys, json
src, extra_path, outdir = sys.argv[1:4]
base = open(src, encoding='utf-8').read()
extra = open(extra_path, encoding='utf-8').read()

ETIQ_CSS = """
.leaflet-tooltip.etiq{background:transparent;border:0;box-shadow:none;padding:0 0 0 2px;font:700 12px/1.1 var(--font-sans);color:var(--ll-black);text-shadow:0 0 2px #fff,0 0 2px #fff,0 0 4px #fff,0 0 4px #fff}
.leaflet-tooltip.etiq::before{display:none}
.ville.petite{font-size:11px;color:var(--ll-gray-500)}
.ville.petite i{width:4px;height:4px;background:var(--ll-gray-500)}
"""
MARKER_OLD = "markers = rows.map(m => L.marker(m.c, {icon: icon(m.on), title: m.l, on: m.on}).bindPopup(popup(m)));"
MARKER_NEW = "markers = rows.map(m => L.marker(m.c, {icon: icon(m.on), title: m.l, on: m.on}).bindPopup(popup(m))\n    .bindTooltip(esc(m.l), {permanent:true, direction:'right', offset:[12,-17], className:'etiq'}));"
LACS = "L.polygon(FOND.lacs, {...vec, stroke:false, fillColor:'#C9D7E0', fillOpacity:1}).addTo(map);"
REGION = "L.polygon(FOND.region, {...vec, stroke:false, fillColor:'#fff', fillOpacity:1}).addTo(map);"
DISTRICTS = "L.polyline(FOND.districts, {...vec, color:'#C4C4C4', weight:1}).addTo(map);"

REPERES = """
/* VARIANTE : surfaces bâties, routes principales et localités (swissTLMRegio). */
L.polygon(EXTRA.bati, {...vec, stroke:false, fillColor:'#E4E4E4', fillOpacity:1}).addTo(map);
const routesV = L.polyline(EXTRA.routes.v, {...vec, color:'#D2D2D2', weight:1});
L.polyline(EXTRA.routes.h, {...vec, color:'#B8B8B8', weight:1.6}).addTo(map);
L.polyline(EXTRA.routes.a, {...vec, color:'#8C8C8C', weight:2.4}).addTo(map);
map.createPane('villes2').style.zIndex = 440;
const villeIc = (n, r) => L.divIcon({className:'', iconSize:[0,0], html:'<div class="ville petite"><i></i>'+n+'</div>'});
const villes1 = L.layerGroup(EXTRA.villes.filter(v => v[3]===1).map(([n,la,lo]) => L.marker([la,lo], {pane:'villes2', interactive:false, keyboard:false, icon:villeIc(n)})));
const villes2 = L.layerGroup(EXTRA.villes.filter(v => v[3]===2).map(([n,la,lo]) => L.marker([la,lo], {pane:'villes2', interactive:false, keyboard:false, icon:villeIc(n)})));
const echelle = () => { const z = map.getZoom();
  z >= 11 ? routesV.addTo(map) : routesV.remove();
  z >= 10.5 ? villes1.addTo(map) : villes1.remove();
  z >= 12 ? villes2.addTo(map) : villes2.remove(); };
map.on('zoomend', echelle); echelle();
"""
RELIEF = """
/* VARIANTE : relief swisstopo en ombrage léger, mélangé au fond. */
map.createPane('relief').style.zIndex = 402;
map.getPane('relief').style.mixBlendMode = 'multiply';
L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.leichte-basiskarte_reliefschattierung/default/current/3857/{z}/{x}/{y}.png', {pane:'relief', opacity:0.35}).addTo(map);
"""
RUES_GRIS = """
/* VARIANTE : rues swisstopo en gris, au-dessus du fond épuré. */
map.createPane('routes').style.zIndex = 405;
map.getPane('routes').style.filter = 'grayscale(1) contrast(1.15)';
L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swisstlm3d-strassen/default/current/3857/{z}/{x}/{y}.png', {pane:'routes', opacity:0.75}).addTo(map);
"""
CARTE_GRISE = """
/* VARIANTE : carte swisstopo grise (swissTLM3D) en fond, avec ses noms. */
L.tileLayer('https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swisstlm3d-karte-grau/default/current/3857/{z}/{x}/{y}.png', {maxZoom:16}).addTo(map);
"""

def make(name, inject, maxzoom=13, carte_grise=False):
    s = base
    def rep(a, b):
        nonlocal s
        assert s.count(a) == 1, (name, a[:60]); s = s.replace(a, b)
    rep(".leaflet-container{font-family:var(--font-sans);", ETIQ_CSS + ".leaflet-container{font-family:var(--font-sans);")
    rep(MARKER_OLD, MARKER_NEW)
    rep("minZoom:9, maxZoom:13,", f"minZoom:9, maxZoom:{maxzoom},")
    if carte_grise:
        rep(REGION, "")
        rep(DISTRICTS, "")
        rep(LACS, "")
        # fond hors région voilé, pour garder la région lisible
        rep("L.polyline(FOND.cantons,", "L.polygon([[[-85,-180],[-85,180],[85,180],[85,-180]], ...FOND.region.map(p => p[0])], {...vec, stroke:false, fillColor:'#fff', fillOpacity:0.55}).addTo(map);\nL.polyline(FOND.cantons,")
        rep("map.createPane('villes').style.zIndex = 450;", inject + "\nmap.createPane('villes').style.zIndex = 450;")
    else:
        rep(LACS, LACS + inject)
    rep("const FOND = ", "const EXTRA = " + extra + ";\nconst FOND = ")
    s = s.replace("map.attributionControl.setPrefix(false)", "window.__map = map;\nmap.attributionControl.setPrefix(false)", 1)
    open(f"{outdir}/{name}.html", 'w', encoding='utf-8').write(s)

make('a-actuelle', "")
make('b-reperes', REPERES)
make('c-reperes-relief', REPERES + RELIEF)
make('d-rues-gris', RUES_GRIS, maxzoom=16)
make('e-carte-grise', CARTE_GRISE, maxzoom=16, carte_grise=True)
print('ok')
