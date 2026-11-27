# Carte des marchés de Noël – La Liberté

Carte interactive des marchés de Noël du canton de Fribourg et de la Broye vaudoise, intégrée en iframe dans l'article de laliberte.ch :
https://www.laliberte.ch/articles/regions/canton/voici-ou-et-quand-ont-lieu-les-marches-de-noel-pres-de-chez-vous-1487401

Projet de Léo (Labo Digital, St-Paul Médias). Langue du projet, des commits et de l'interface : français.

## Principe

- Une seule page statique : `index.html` (HTML + CSS + JS dans le même fichier, sans build ni framework).
- Les données viennent d'une Google Sheet, lue à chaque ouverture de la page (CSV).
- La page n'affiche que les marchés en cours ou à venir, d'après la date du lecteur. Les marchés passés disparaissent seuls.
- Filtres : Tous / Aujourd'hui / Ce week-end. Liste cliquable à côté de la carte. Sur mobile, elle passe dessous et n'affiche que les 3 prochains marchés (`LIMITE_MOBILE`), le reste derrière un bouton.
- Fond de carte épuré, en trois niveaux selon le zoom (variantes A, C et D retenues le 26.11.2026) :
  - toujours : région FR + Broye-Vully en blanc, reste en gris, lacs en gris-bleu, limites cantonales (gris foncé) ; nom de chaque marché à côté de son épingle ;
  - vue régionale : zones bâties en gris clair, autoroutes et routes principales, limites de districts, relief swisstopo en ombrage léger, chefs-lieux nommés (Fribourg en gras), grandes localités dès le zoom 10,5, autres dès 12 ;
  - zoom rapproché : rues swisstopo (swissTLM3D Strassen, sans noms) passées en gris dès le zoom 12 ; routes vectorielles masquées dès 13, limites de districts dès 14. Zoom 9 à 16 ; un clic dans la liste zoome au moins à 14.
- Noms sur la carte, par priorité : marchés visibles (ordre de la liste), chefs-lieux, autres localités. Un nom qui en chevauche un autre est masqué, de même qu'une localité quand un marché visible à moins de 3 km porte un lieu qui commence par son nom.
- Géométries intégrées dans `index.html` (constante `FOND`, environ 200 Ko), générées par `outils/fond-carte.py` depuis les données ouvertes swisstopo : swissBOUNDARIES3D (cantons, districts) et swissTLMRegio (lacs, zones bâties, routes, localités). Relief et rues : tuiles WMTS swisstopo (wmts.geo.admin.ch). Usage commercial autorisé avec mention « © swisstopo ». Ne pas utiliser les limites de l'OFS (ThemaKart) : leur usage commercial demande une autorisation. Vue bornée à la région.
- Épingles proches regroupées en pastilles numérotées (noires, rouges si un marché du groupe est ouvert aujourd'hui). Clic sur une pastille : zoom ; au zoom maximal, les épingles superposées s'écartent. Un clic dans la liste ouvre le marché même s'il est dans une pastille.
- Hébergement : GitHub Pages, puis intégration en iframe dans l'article.
- Écrans tactiles (`pointer: coarse`) : glisser à un doigt désactivé sur la carte pour laisser défiler l'article ; deux doigts déplacent et zooment, avec un message d'aide.
- Dans une iframe, la page envoie sa hauteur à l'article (`postMessage`, type `ll-carte-noel-hauteur`). Le script d'intégration du README ajuste l'iframe, sans défilement interne.

## Structure

```
index.html                              la carte (seul fichier publié qui compte)
outils/fond-carte.py                    génère la constante FOND depuis swissBOUNDARIES3D et swissTLMRegio (swisstopo)
README.md                               mise en ligne et intégration
.nojekyll                               GitHub Pages sert les fichiers tels quels
```

## Source des données

- Google Sheet : https://docs.google.com/spreadsheets/d/1EfNcVvLC9w1iIyrNCNuGf_QXUBpfxSI1FY-ZHU2UMDg/edit
- Onglet lu : `Saisie`, via son adresse « Publier sur le web » au format CSV (`CSV_URL` en haut du script). Google la met en cache environ 5 minutes : elle tient la charge, et une modification de la feuille apparaît sur la carte après quelques minutes.
- Si l'onglet change de nom ou si la publication est retirée, la carte affiche « Impossible de charger la liste des marchés ». Republier l'onglet Saisie et mettre à jour `CSV_URL` si l'adresse change.

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

La feuille (« Marchés de Noël 2026 – carte La Liberté ») n'a plus que deux onglets : `Saisie`, colonnes A à J dans l'ordre du tableau ci-dessus (`Jours` en J : Gruyères `ven-dim`, Golf de Payerne `mar-dim`), et `Mode d'emploi`, qui explique comment remplir la feuille et rappelle de ne pas retirer la publication.

Datawrapper n'est plus utilisé : son onglet `Carte` et les colonnes `Statut` et `Ligne active` ont été supprimés le 26.11.2026. La page lit les colonnes par leur nom, donc ajouter ou déplacer une colonne ne la casse pas. Seul l'onglet `Saisie` doit rester publié.

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

- Ouvrir `index.html` directement dans Chrome : le fond est intégré, il s'affiche aussi en `file://` (relief et rues demandent une connexion).
- Simuler une autre date : `index.html?date=2026-12-12`.
- Serveur local si besoin : `python3 -m http.server 8000`.

## Publier

Voir README.md. En bref : dépôt GitHub public, Pages sur la branche `main`, dossier racine.

## Pistes ouvertes

- Vérifier les coordonnées : vallée du Gottéron, Arsen'alt, Golf de Payerne, château de Montet.
- Branches `variante-rues` et `variantes-carte` : essais antérieurs, dépassés par la version en ligne (A + C + D).
- Aperçu « carrousel » (`apercu-carrousel.html`, généré par `outils/apercu-carrousel.py` depuis `index.html`) : carte pleine largeur, filtres flottants en haut, marchés en cartes horizontales en bas, à la manière de Strava. Publié à part pour décision ; l'article utilise toujours `index.html`. Si retenu, il remplace `index.html` ; sinon, supprimer les deux fichiers.
