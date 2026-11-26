# Variantes de carte (essai du 26.11.2026, non publié)

Cinq variantes générées à partir de `index.html` pour comparer la lisibilité :

- A : carte actuelle, avec le nom de chaque marché à côté de son épingle.
- B : A plus les surfaces bâties, les routes principales et les localités (swissTLMRegio, intégrés à la page).
- C : B plus le relief swisstopo en ombrage léger (tuiles).
- D : A plus les rues swisstopo (swissTLM3D Strassen) passées en gris, zoom jusqu'à 16 (tuiles).
- E : carte swisstopo grise (swissTLM3D) en fond, avec ses noms, zoom jusqu'à 16 (tuiles).

Regénérer (dossier de travail avec les GeoPackages swisstopo, voir `outils/fond-carte.py`) :

    python3 outils/variantes/extra.py swissTLMRegio_Product_LV95.gpkg swissBOUNDARIES3D_1_5_LV95_LN02.gpkg extra.json
    python3 outils/variantes/build.py index.html extra.json dossier-sortie
    node outils/variantes/shots.js dossier-sortie

Les données de B pèsent environ 600 Ko : à alléger avant toute mise en ligne.
