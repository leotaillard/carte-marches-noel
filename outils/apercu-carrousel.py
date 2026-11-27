"""Génère apercu-carrousel.html à partir de index.html : même carte, mais les marchés défilent en cartes
horizontales en bas de la carte (à la manière de Strava) au lieu de la liste verticale.
Aperçu pour décision, publié à part ; l'article utilise toujours index.html.

    python3 outils/apercu-carrousel.py index.html apercu-carrousel.html
"""
import sys
src, out = sys.argv[1:3]
s = open(src, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)
def cut(start, end, new):
    """remplace de start (inclus) à end (exclu)"""
    global s
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + new + s[j:]

rep("<title>Marchés de Noël 2026 – La Liberté</title>", "<title>Marchés de Noël 2026 – La Liberté (carrousel)</title>")

# ---------- CSS ----------
rep(".wrap{display:grid;grid-template-columns:minmax(0,1fr) 340px;height:100%;min-height:540px}",
    ".wrap{position:relative;height:100%;min-height:480px;overflow:hidden}")
rep("#map{position:relative;height:100%;min-height:420px;background:var(--ll-gray-300)}",
    "#map{position:absolute;inset:0;background:var(--ll-gray-300)}")
i = s.index("@media(max-width:700px){"); j = s.index("</style>", i)
s = s[:i] + """/* ===== Carrousel (à la manière de Strava) ===== */
.barre{position:absolute;top:10px;left:10px;right:56px;z-index:1001;display:flex;flex-wrap:wrap;align-items:center;gap:6px;pointer-events:none}
.barre>*{pointer-events:auto}
.barre .filters{gap:6px}
.barre .filters button{border-color:transparent;box-shadow:0 1px 4px rgba(0,0,0,.25)}
#count{margin:0;padding:7px 11px;background:rgba(255,255,255,.94);border-radius:999px;font-size:13px;line-height:1.2;color:var(--ll-gray-900);box-shadow:0 1px 4px rgba(0,0,0,.2)}
.carrousel{--lc:min(300px, calc(100vw - 64px));position:absolute;left:0;right:0;bottom:12px;z-index:1001;display:flex;gap:10px;margin:0;padding:6px calc((100vw - var(--lc)) / 2);list-style:none;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;scrollbar-width:none;overscroll-behavior-x:contain}
.carrousel::-webkit-scrollbar{display:none}
.carte{flex:0 0 var(--lc);scroll-snap-align:center;scroll-snap-stop:always;height:112px;padding:11px 14px;border:2px solid transparent;border-radius:8px;background:var(--ll-white);box-shadow:0 2px 10px rgba(0,0,0,.25);cursor:pointer;overflow:hidden}
.carte:hover{border-color:var(--ll-gray-300);background:var(--ll-white)}
.carte.actif:hover{border-color:var(--ll-black)}
.carte.actif{border-color:var(--ll-black)}
.carte:focus-visible{outline:2px solid var(--ll-red);outline-offset:2px}
.carte .t{display:flex;align-items:center;gap:6px;font:700 16px/1.2 var(--font-sans);white-space:nowrap}
.carte .t span:first-child{overflow:hidden;text-overflow:ellipsis}
.carte .t .badge{margin:0;flex:none}
.carte .n{margin-top:3px;font-size:15px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.carte .m{margin-top:4px;font-size:13px;line-height:1.3;color:var(--ll-gray-500);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.carrousel.saisi{scroll-snap-type:none;cursor:grabbing;user-select:none}
.carrousel.saisi .carte{cursor:grabbing}
@media (hover:hover) and (pointer:fine){.carte{cursor:grab}}
.carte.vide{cursor:default;color:var(--ll-gray-500);display:flex;align-items:center}
.fleche{position:absolute;bottom:56px;z-index:1002;width:36px;height:36px;border:0;border-radius:50%;background:var(--ll-white);color:var(--ll-black);box-shadow:0 1px 5px rgba(0,0,0,.3);font:700 18px/1 var(--font-sans);cursor:pointer;display:none}
.fleche.g{left:6px}.fleche.d{right:6px}
.fleche:focus-visible{outline:2px solid var(--ll-red);outline-offset:2px}
@media (hover:hover) and (pointer:fine){.fleche{display:block}}
.leaflet-marker-icon.actif .pin{transform:rotate(-45deg) scale(1.3)}
.leaflet-marker-icon.actif .cluster{transform:scale(1.15);box-shadow:0 0 0 3px var(--ll-black)}
.leaflet-top.leaflet-right{top:2px}
@media(max-width:700px){
  .wrap{height:560px;min-height:0}
  .barre{top:8px;left:8px}
  #count{font-size:12px;padding:6px 10px}
  .barre .filters button{font-size:13px;padding:5px 11px;min-height:32px}
}
""" + s[j:]

# ---------- Balisage ----------
i = s.index('<div class="wrap">'); j = s.index('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js">')
s = s[:i] + """<div class="wrap">
  <div id="map" role="region" aria-label="Carte des marchés de Noël"></div>
  <div class="barre">
    <div class="filters" role="group" aria-label="Filtrer">
      <button data-f="all" aria-pressed="true">Tous</button>
      <button data-f="now" aria-pressed="false">Aujourd’hui</button>
      <button data-f="we" aria-pressed="false">Ce week-end</button>
    </div>
    <p id="count" aria-live="polite"></p>
  </div>
  <button class="fleche g" type="button" aria-label="Marché précédent">‹</button>
  <ul class="carrousel" id="list" aria-label="Marchés"></ul>
  <button class="fleche d" type="button" aria-label="Marché suivant">›</button>
</div>

""" + s[j:]

# ---------- Carte : contrôles ----------
rep("const map = L.map('map', {", "const map = L.map('map', {zoomControl:false, ")
rep("map.attributionControl.setPrefix(false)", "L.control.zoom({position:'topright'}).addTo(map);\nmap.attributionControl.setPosition('topright');\nmap.attributionControl.setPrefix(false)")

# ---------- Rendu : carrousel au lieu de la liste ----------
cut("/* Sur mobile, la liste s'empile sous la carte", "/* Noms sur la carte, par priorité",
"""/* ===== Carrousel =====
   Faire défiler les cartes déplace la carte vers le marché affiché et le met en évidence.
   Toucher une épingle ouvre son infobulle et fait défiler le carrousel jusqu'à son marché.
   Toucher une carte zoome sur le marché et ouvre son infobulle. Glisser vers un autre marché referme l'infobulle. */
let rows = [], markers = [], actif = -1;
const hautCarrousel = () => list.getBoundingClientRect().height + 24;
const basBarre = () => document.querySelector('.barre').getBoundingClientRect().bottom + 10;

/* Centre la carte sur un point, en tenant compte de la place prise par le carrousel en bas. */
function centreSur(ll, z, anime){
  const p = map.project(ll, z).add([0, hautCarrousel() / 2 - 20]);
  map.setView(map.unproject(p, z), z, {animate: anime !== false});
}
function surligne(){
  document.querySelectorAll('.leaflet-marker-icon.actif').forEach(el => el.classList.remove('actif'));
  const mk = markers[actif]; if (!mk) return;
  const v = layer.getVisibleParent(mk); const el = v && v.getElement && v.getElement();
  if (el) el.classList.add('actif');
  markers.forEach((m, i) => m.setZIndexOffset(i === actif ? 1000 : 0));
}
function active(i, opts){
  opts = opts || {};
  if (i < 0 || i >= rows.length) return;
  actif = i;
  list.querySelectorAll('.carte[data-i]').forEach(c => c.classList.toggle('actif', +c.dataset.i === i));
  if (opts.defile) {   // pas de scrollIntoView : dans une iframe, il ferait aussi défiler l'article
    const c = list.querySelector('.carte[data-i="'+i+'"]');
    if (c) list.scrollTo({left: c.offsetLeft - (list.clientWidth - c.offsetWidth) / 2, behavior:'smooth'});
  }
  const mk = markers[i];
  if (opts.zoom) {
    map.closePopup();
    layer.zoomToShowLayer(mk, () => {
      map.once('moveend', () => { mk.openPopup(); surligne(); });
      centreSur(mk.getLatLng(), Math.max(map.getZoom(), 14));
    });
  } else if (opts.centre) {
    map.closePopup();
    const vis = layer.getVisibleParent(mk) || mk;
    const pt = map.latLngToContainerPoint(vis.getLatLng()), t = map.getSize();
    if (pt.x < 40 || pt.x > t.x - 40 || pt.y < 60 || pt.y > t.y - hautCarrousel()) centreSur(vis.getLatLng(), map.getZoom());
  }
  surligne(); majVilles();
}

function render(f){
  layer.clearLayers();
  rows = live.filter(m => f === 'now' ? m.on : f === 'we' ? weDays.some(x => openOn(m,x)) : true);
  markers = rows.map((m, i) => L.marker(m.c, {icon: icon(m.on), title: m.l, on: m.on})
    .bindPopup(popup(m), {autoPanPaddingTopLeft:[10, basBarre()], autoPanPaddingBottomRight:[10, hautCarrousel()]})
    .bindTooltip(esc(m.l), {permanent:true, direction:'right', offset:[12,-17], className:'etiq'})
    .on('click', () => active(i, {defile:true})));
  layer.addLayers(markers);
  count.textContent = rows.length + (rows.length > 1 ? ' marchés' : ' marché');
  actif = -1;
  drawList();
  if (markers.length) map.fitBounds(L.featureGroup(markers).getBounds(), {paddingTopLeft:[30,60], paddingBottomRight:[30, hautCarrousel()], maxZoom:12});
  list.scrollLeft = 0;
  if (rows.length) active(0);
  majVilles();
}

""")
cut("function drawList(){", "/* Intégration : la page envoie sa hauteur",
"""function drawList(){
  list.innerHTML = rows.length ? rows.map((m,i) =>
    '<li class="carte" tabindex="0" role="button" data-i="'+i+'" aria-label="'+esc(m.l+', '+m.n+', '+datesTxt(m))+'">'
    + '<div class="t"><span>'+esc(m.l)+'</span>'
    + (m.on ? '<span class="badge now">Aujourd’hui</span>' : m.nx <= addDays(today,7) ? '<span class="badge soon">Bientôt</span>' : '')
    + '</div><div class="n">'+esc(m.n)+'</div><div class="m">'+esc(datesTxt(m))+(m.h?' · '+esc(m.h):'')+(m.r?' · '+esc(m.r):'')+'</div></li>').join('')
    : '<li class="carte vide">Aucun marché pour cette sélection.</li>';
  list.querySelectorAll('.carte[data-i]').forEach(c => {
    const go = () => active(+c.dataset.i, {defile:true, zoom:true});
    c.addEventListener('click', go);
    c.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
  });
}
/* Fin du défilement : la carte la plus proche du centre devient le marché affiché. */
let attente;
list.addEventListener('scroll', () => {
  clearTimeout(attente);
  attente = setTimeout(() => {
    const mil = list.getBoundingClientRect().left + list.clientWidth / 2;
    let best = -1, d = Infinity;
    list.querySelectorAll('.carte[data-i]').forEach(c => { const r = c.getBoundingClientRect(), e = Math.abs(r.left + r.width / 2 - mil); if (e < d) { d = e; best = +c.dataset.i; } });
    if (best >= 0 && best !== actif) active(best, {centre:true});
  }, 140);
}, {passive:true});
const pas = dir => { const c = list.querySelector('.carte'); list.scrollBy({left: dir * (c ? c.getBoundingClientRect().width + 10 : 300), behavior:'smooth'}); };
document.querySelector('.fleche.g').addEventListener('click', () => pas(-1));
document.querySelector('.fleche.d').addEventListener('click', () => pas(1));
/* Souris : attraper le carrousel et le faire glisser. Au relâchement, il se cale sur la carte
   la plus proche du centre. Un glissement de plus de 5 px n'est pas compté comme un clic. */
let saisie = null;
list.addEventListener('pointerdown', e => {
  if (e.pointerType !== 'mouse' || e.button !== 0) return;
  saisie = {x: e.clientX, gauche: list.scrollLeft, bouge: false};
});
window.addEventListener('pointermove', e => {
  if (!saisie) return;
  const dx = e.clientX - saisie.x;
  if (!saisie.bouge && Math.abs(dx) > 5) { saisie.bouge = true; list.classList.add('saisi'); }
  if (saisie.bouge) { list.scrollLeft = saisie.gauche - dx; e.preventDefault(); }
});
window.addEventListener('pointerup', () => {
  if (!saisie) return;
  const bouge = saisie.bouge; saisie = null;
  if (!bouge) return;
  const mil = list.getBoundingClientRect().left + list.clientWidth / 2;
  let best = null, d = Infinity;
  list.querySelectorAll('.carte[data-i]').forEach(c => { const r = c.getBoundingClientRect(), e = Math.abs(r.left + r.width / 2 - mil); if (e < d) { d = e; best = c; } });
  const cible = best ? best.offsetLeft - (list.clientWidth - best.offsetWidth) / 2 : list.scrollLeft;
  list.scrollTo({left: cible, behavior:'smooth'});
  setTimeout(() => list.classList.remove('saisi'), 400);   // le calage reprend après l'animation
  const bloque = ev => { ev.stopPropagation(); ev.preventDefault(); };   // seulement le clic qui suit ce relâchement
  list.addEventListener('click', bloque, true);
  setTimeout(() => list.removeEventListener('click', bloque, true), 0);
});
list.addEventListener('dragstart', e => e.preventDefault());
layer.on('animationend', surligne);
map.on('zoomend', surligne);

""")
# Priorité des noms : le marché affiché d'abord
rep("  const vus = markers.filter(mk => layer.getVisibleParent(mk) === mk);",
    "  const vus = markers.filter(mk => layer.getVisibleParent(mk) === mk).sort((a, b) => (b === markers[actif]) - (a === markers[actif]));")
rep("let rows = [], markers = [], actif = -1;", "let rows = [], markers = [], actif = -1;")
open(out, 'w', encoding='utf-8').write(s)
print('ok', len(s))
