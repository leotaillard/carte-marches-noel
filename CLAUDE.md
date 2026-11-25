# Carte des marchés de Noël – La Liberté

Carte interactive des marchés de Noël du canton de Fribourg et de la Broye vaudoise, intégrée en iframe dans l'article de laliberte.ch :
https://www.laliberte.ch/articles/regions/canton/voici-ou-et-quand-ont-lieu-les-marches-de-noel-pres-de-chez-vous-1487401

Projet de Léo (Labo Digital, St-Paul Médias). Langue du projet, des commits et de l'interface : français.

## Principe

- Une seule page statique : `index.html` (HTML + CSS + JS dans le même fichier, sans build ni framework).
- Les données viennent d'une Google Sheet, lue à chaque ouverture de la page (CSV).
- La page n'affiche que les marchés en cours ou à venir, d'après la date du lecteur. Les marchés passés disparaissent seuls.
- Filtres : Tous / Aujourd'hui / Ce week-end. Liste cliquable à côté de la carte. Sur mobile, elle passe dessous et n'affiche que les 3 prochains marchés (`LIMITE_MOBILE`), le reste derrière un bouton.
- Fond de carte épuré, sans tuiles ni noms de lieux : région FR + Broye-Vully en blanc, reste en gris, lacs en gris-bleu, limites cantonales (gris foncé) et de districts (gris clair). Seuls repères nommés : les chefs-lieux de district, Fribourg en gras. Attribution : « © swisstopo ».
- Géométries intégrées dans `index.html` (constante `FOND`), générées par `outils/fond-carte.py` depuis les données ouvertes swisstopo : swissBOUNDARIES3D (cantons, districts) et swissTLMRegio (lacs). Usage commercial autorisé avec mention de la source. Ne pas utiliser les limites de l'OFS (ThemaKart) : leur usage commercial demande une autorisation. Vue bornée à la région, zoom 9 à 13.
- Épingles proches regroupées en pastilles numérotées (noires, rouges si un marché du groupe est ouvert aujourd'hui). Clic sur une pastille : zoom ; au zoom maximal, les épingles superposées s'écartent. Un clic dans la liste ouvre le marché même s'il est dans une pastille.
- Hébergement : GitHub Pages, puis intégration en iframe dans l'article.

## Structure

```
index.html                              la carte (seul fichier publié qui compte)
outils/fond-carte.py                    génère la constante FOND depuis swissBOUNDARIES3D et swissTLMRegio (swisstopo)
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
- Pas de titre dans la carte : l'article porte déjà le sien. GT Ultra Median (titres du site) n'est donc pas utilisé.
- Forme Grotesque Pro 400/700 pour tout le texte de la carte, y compris les noms de lieux dans la liste et les infobulles.
- Texte courant : FK Roman Standard 400 (19/28 px). Pas utilisé dans la carte.
- Convention de titre : surtitre en rouge suivi du titre en noir. Toujours une ponctuation à la fin du surtitre (point ou deux-points).

Polices : sous licence commerciale. Ne jamais copier les fichiers .woff2 dans ce dépôt. Le CSS les référence sur `https://www.laliberte.ch/fonts/…` ; elles ne se chargent que si la page est servie depuis laliberte.ch ou si le site autorise le CORS sur `/fonts/`. Sinon, Inter s'applique en repli.

## Contraintes

- Garder un seul fichier `index.html`, sans dépendance à installer. Leaflet 1.9.4 et Leaflet.markercluster 1.5.3 via cdnjs (la 2.x vise Leaflet 2).
- Tout texte venant de la feuille passe par `esc()` avant d'entrer dans le HTML.
- Pas de suivi ni de cookies ajoutés.
- Accessibilité : boutons au clavier, focus visible, `aria-pressed` sur les filtres.

## Tester

- Ouvrir `index.html` directement dans Chrome : le fond est intégré, il s'affiche aussi en `file://`.
- Simuler une autre date : `index.html?date=2026-12-12`.
- Serveur local si besoin : `python3 -m http.server 8000`.

## Publier

Voir README.md. En bref : dépôt GitHub public, Pages sur la branche `main`, dossier racine.

## Pistes ouvertes

- Ajouter la colonne `Jours` dans la feuille : Gruyères `ven-dim`, Golf de Payerne `mar-dim`.
- Vérifier les coordonnées : vallée du Gottéron, Arsen'alt, Golf de Payerne, château de Montet.
