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

Bloc HTML du CMS (recommandé) :

```html
<style>
  .ll-carte-noel{width:100%;height:640px;border:0;display:block}
  @media (max-width:700px){.ll-carte-noel{height:850px}}
</style>
<iframe class="ll-carte-noel"
        src="https://leotaillard.github.io/carte-marches-noel/"
        title="Carte des marchés de Noël du canton de Fribourg et de la Broye"
        loading="lazy"></iframe>
<script>
window.addEventListener('message', function (e) {
  if (e.origin !== 'https://leotaillard.github.io' || !e.data || e.data.type !== 'll-carte-noel-hauteur') return;
  document.querySelectorAll('iframe.ll-carte-noel').forEach(function (f) {
    if (f.contentWindow === e.source) f.style.height = e.data.hauteur + 'px';
  });
});
</script>
```

La carte envoie sa hauteur à l'article, et le script ajuste l'iframe : plus de défilement à l'intérieur de l'iframe sur mobile, même quand la liste est dépliée. Sur ordinateur, la hauteur reste 640 px.

Si le CMS refuse les balises `<style>` ou `<script>`, utiliser une hauteur fixe. Sur mobile, déplier la liste fera alors défiler l'intérieur de l'iframe.

```html
<iframe src="https://leotaillard.github.io/carte-marches-noel/"
        title="Carte des marchés de Noël du canton de Fribourg et de la Broye"
        style="width:100%;height:850px;border:0;display:block"
        loading="lazy"></iframe>
```

Sur mobile, la carte et la liste s'empilent. La liste n'affiche que les trois prochains marchés, avec un bouton pour voir les autres. Le nombre se règle avec `LIMITE_MOBILE` dans le script.

Sur écran tactile, un doigt fait défiler l'article et deux doigts déplacent ou zooment la carte. Un message l'indique si le lecteur glisse à un doigt sur la carte.

## À savoir

- **Polices** : la police du site (Forme Grotesque Pro) est sous licence et n'est pas incluse. Sur github.io, elle peut ne pas se charger : Inter la remplace. Pour l'identité complète, héberger la page sur le domaine laliberte.ch, ou demander à l'équipe web d'autoriser le CORS sur `/fonts/` pour l'adresse de la carte.
- **Fond de carte** : © swisstopo, données ouvertes, usage commercial autorisé avec mention de la source. Contours, zones bâties, routes et localités (swissBOUNDARIES3D, swissTLMRegio) sont intégrés dans la page ; pour les régénérer (nouvelle année, autre zone), voir `outils/fond-carte.py`. Le relief et les rues sont des tuiles swisstopo chargées à l'affichage.
- **Tester une date** : ajouter `?date=2026-12-12` à l'adresse.
