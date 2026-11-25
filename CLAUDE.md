# Carte des marchés de Noël – La Liberté

Carte interactive des marchés de Noël du canton de Fribourg et de la Broye vaudoise, intégrée en iframe dans l'article de laliberte.ch :
https://www.laliberte.ch/articles/regions/canton/voici-ou-et-quand-ont-lieu-les-marches-de-noel-pres-de-chez-vous-1487401

Projet de Léo (Labo Digital, St-Paul Médias). Langue du projet, des commits et de l'interface : français.

## Principe

- Une seule page statique : `index.html` (HTML + CSS + JS dans le même fichier, sans build ni framework).
- Les données viennent d'une Google Sheet, lue à chaque ouverture de la page (CSV).
- La page n'affiche que les marchés en cours ou à venir, d'après la date du lecteur. Les marchés passés disparaissent seuls.
- Filtres : Tous / Aujourd'hui / Ce week-end. Liste cliquable à côté de la carte (en dessous sur mobile).
- Fond de carte : swisstopo, carte nationale en gris (WMTS gratuit, attribution obligatoire), éclairci (opacité 0.6). Hors des districts, un voile blanc ; limites de districts en gris. Vue bornée à la région.
- Hébergement : GitHub Pages, puis intégration en iframe dans l'article.

## Structure

```
index.html                              la carte (seul fichier publié qui compte)
data/fribourg-broye-districts.geojson   districts FR + Broye-Vully (VD) : limites grises et voile blanc hors zone
README.md                               mise en ligne et intégration
.nojekyll                               GitHub Pages sert les fichiers tels quels
```

## Source des données

- Google Sheet : https://docs.google.com/spreadsheets/d/1EfNcVvLC9w1iIyrNCNuGf_QXUBpfxSI1FY-ZHU2UMDg/edit
- Onglet lu : `Saisie` (via `CSV_URL` en haut du script). La feuille est partagée en lecture par lien.
- En production, remplacer `CSV_URL` par l'URL « Publier sur le web » (onglet Saisie, format CSV) : Google la met en cache, plus robuste pour un article à fort trafic.

Colonnes lues par nom d'en-tête (insensible à la casse) :

| Colonne | Format | Rôle |
|---|---|---|
| Nom | texte | nom du marché |
| Lieu | texte | titre dans la liste et l'infobulle |
| Région | texte | district (Sarine, Gruyère, Broye, Glâne, Lac, Veveyse, Singine) |
| Latitude, Longitude | nombre, virgule ou point accepté | position |
| Début, Fin | date `JJ.MM.AAAA` ou `AAAA-MM-JJ` | période d'ouverture, bornes incluses |
| Dates | texte | affiché tel quel ; si vide, généré depuis Début/Fin |
| Infos | texte | horaires, lieu précis |
| Jours | facultatif, ex. `ven-dim`, `mar-dim`, `sam,dim` | jours d'ouverture ; vide = tous les jours |

Les colonnes `Statut` et `Ligne active` de la feuille servent à Datawrapper ; la page les ignore.

## Identité graphique laliberte.ch

Relevée sur le site le 25.11.2026. Tokens dans `:root` de `index.html`.

- Rouge : `#E21B22` (surtitres, accents, « ouvert aujourd'hui »), rouge clair `#F4353C`.
- Noir `#000` pour le texte ; gris `#7D7D7D` (secondaire), `#DBDBDB` et `#E8E8E8` (filets), `#F2F2F2` (fonds).
- GT Ultra Median 700 : uniquement pour le grand titre (h1), letter-spacing ≈ -0.03em (H1 article : 42/46 px).
- Forme Grotesque Pro 400/700 pour tout le reste, y compris les noms de lieux dans la liste et les infobulles (chapeau : 23/32 px).
- Texte courant : FK Roman Standard 400 (19/28 px). Pas utilisé dans la carte.
- Convention de titre : surtitre en rouge suivi du titre en noir. Toujours une ponctuation à la fin du surtitre (point ou deux-points).

Polices : sous licence commerciale. Ne jamais copier les fichiers .woff2 dans ce dépôt. Le CSS les référence sur `https://www.laliberte.ch/fonts/…` ; elles ne se chargent que si la page est servie depuis laliberte.ch ou si le site autorise le CORS sur `/fonts/`. Sinon, les replis s'appliquent (Georgia pour les titres, Inter pour le reste).

## Contraintes

- Garder un seul fichier `index.html`, sans dépendance à installer. Leaflet 1.9.4 via cdnjs.
- Tout texte venant de la feuille passe par `esc()` avant d'entrer dans le HTML.
- Pas de suivi ni de cookies ajoutés.
- Accessibilité : boutons au clavier, focus visible, `aria-pressed` sur les filtres.

## Tester

- Ouvrir `index.html` directement dans Chrome (l'aperçu des outils Claude bloque les tuiles de carte). En `file://`, les districts ne se chargent pas : la carte s'affiche sans voile ni limites. Passer par le serveur local pour les voir.
- Simuler une autre date : `index.html?date=2026-12-12`.
- Serveur local si besoin : `python3 -m http.server 8000`.

## Publier

Voir README.md. En bref : dépôt GitHub public, Pages sur la branche `main`, dossier racine.

## Pistes ouvertes

- Ajouter la colonne `Jours` dans la feuille : Gruyères `ven-dim`, Golf de Payerne `mar-dim`.
- Vérifier les coordonnées : vallée du Gottéron, Arsen'alt, Golf de Payerne, château de Montet.
