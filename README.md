# Carte des marchés de Noël 2026

Carte interactive des marchés de Noël du canton de Fribourg et de la Broye vaudoise, pour l'article de La Liberté. Elle lit une Google Sheet et n'affiche que les marchés en cours ou à venir.

## Mettre à jour les marchés

Tout se fait dans la [Google Sheet](https://docs.google.com/spreadsheets/d/1EfNcVvLC9w1iIyrNCNuGf_QXUBpfxSI1FY-ZHU2UMDg/edit), onglet **Saisie**. Une ligne par marché. La carte lit l'onglet publié sur le web au format CSV : une modification apparaît après quelques minutes, sans republier le site. L'onglet doit rester publié (Fichier > Partager > Publier sur le web).

## Publier sur GitHub Pages

Avec le CLI GitHub (`gh`) :

```bash
git init && git add . && git commit -m "Carte des marchés de Noël"
gh repo create carte-marches-noel --public --source . --push
gh api -X POST repos/{owner}/carte-marches-noel/pages -f "source[branch]=main" -f "source[path]=/"
```

Ou dans l'interface : Settings > Pages > Deploy from a branch > `main` / `(root)`.

La carte est ensuite en ligne à l'adresse `https://<compte>.github.io/carte-marches-noel/`, après une à deux minutes.

## Intégrer dans l'article

Bloc HTML du CMS :

```html
<iframe src="https://<compte>.github.io/carte-marches-noel/"
        title="Carte des marchés de Noël"
        style="width:100%;height:640px;border:0"
        loading="lazy"></iframe>
```

Sur mobile, la carte et la liste s'empilent. La liste n'affiche que les trois prochains marchés, avec un bouton pour voir les autres : prévoir environ 830 px de hauteur. Le nombre se règle avec `LIMITE_MOBILE` dans le script.

## À savoir

- **Polices** : la police du site (Forme Grotesque Pro) est sous licence et n'est pas incluse. Sur github.io, elle peut ne pas se charger : Inter la remplace. Pour l'identité complète, héberger la page sur le domaine laliberte.ch, ou demander à l'équipe web d'autoriser le CORS sur `/fonts/` pour l'adresse de la carte.
- **Fond de carte** : © swisstopo (swissBOUNDARIES3D et swissTLMRegio, données ouvertes, usage commercial autorisé avec mention de la source). Les contours sont intégrés dans la page. Pour les régénérer (nouvelle année, autre zone), voir `outils/fond-carte.py`.
- **Tester une date** : ajouter `?date=2026-12-12` à l'adresse.
