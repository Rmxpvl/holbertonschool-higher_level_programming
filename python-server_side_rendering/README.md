# Python - Server-Side Rendering

## Objectif du projet

Le rendu côté serveur (**Server-Side Rendering**, SSR) est une technique où les pages web sont
générées entièrement sur le serveur, puis envoyées au navigateur sous forme de HTML déjà construit.
C'est l'opposé du rendu côté client (**Client-Side Rendering**, CSR), où c'est le navigateur qui
construit la page en JavaScript à partir de données dynamiques (ex: React, Vue qui font des appels
API puis injectent le DOM).

Ce projet a pour but d'apprendre à mettre en œuvre le SSR en Python avec **Flask**, en utilisant le
moteur de templates **Jinja2** pour générer du HTML dynamique.

### Objectifs pédagogiques

- Comprendre le concept de SSR et en quoi il diffère du CSR.
- Comprendre les avantages du SSR (SEO, temps de premier affichage, simplicité).
- Implémenter le SSR en Python avec Flask.
- Utiliser Jinja pour générer dynamiquement du HTML (boucles, conditions, includes).
- Lire et afficher des données provenant de sources différentes : JSON, CSV, SQLite.
- Gérer du contenu dynamique et des entrées utilisateur (query parameters) dans une application web.

## Cours : SSR, CSR et templating

### SSR vs CSR

| | Server-Side Rendering (SSR) | Client-Side Rendering (CSR) |
|---|---|---|
| Qui construit le HTML ? | Le serveur (à chaque requête) | Le navigateur (via JS, après chargement d'un JS bundle) |
| Premier affichage | Rapide, HTML déjà prêt | Plus lent, il faut télécharger + exécuter le JS avant d'afficher quoi que ce soit |
| SEO | Bon par défaut (les robots voient le HTML final) | Nécessite des techniques supplémentaires (pré-rendu, hydratation) |
| Interactivité | Nécessite un rechargement de page ou du JS en plus | Très réactif une fois chargé (SPA) |
| Exemple | Flask + Jinja, Django, PHP | React/Vue/Angular sans SSR |

Il existe aussi le **pré-rendu** (génération statique au build, ex: sites statiques) qui est un
entre-deux : le HTML est généré à l'avance, pas à chaque requête.

### Le moteur de templates Jinja2

Flask utilise Jinja2 par défaut. Un template est un fichier HTML avec une syntaxe spéciale :

- `{{ variable }}` : insère la valeur d'une variable (interpolation).
- `{% if condition %} ... {% endif %}` : logique conditionnelle.
- `{% for item in liste %} ... {% endfor %}` : boucle.
- `{% include 'fichier.html' %}` : inclut un autre template (utile pour un header/footer partagés).
- `{% extends 'base.html' %}` / `{% block %}` : héritage de templates (non utilisé ici mais bon à
  connaître, voir la doc Jinja).

Côté Flask, `render_template('nom.html', variable=valeur)` cherche le fichier dans le dossier
`templates/` et l'affiche en injectant les variables passées en argument.

### Lire des données depuis différentes sources

- **JSON** : module `json` (`json.load(file)`), pratique car proche des structures Python
  (listes/dictionnaires).
- **CSV** : module `csv`, notamment `csv.DictReader` qui transforme chaque ligne en dictionnaire
  (les clés viennent de la première ligne d'en-tête).
- **SQLite** : module `sqlite3`, une base de données fichier (pas de serveur à lancer), idéale pour
  des petits projets ou des tests.

Dans ce projet, on montre qu'on peut avoir **une seule route Flask** qui sait servir la même donnée
depuis n'importe laquelle de ces trois sources, simplement en lisant un paramètre `?source=...` dans
l'URL (`request.args.get('source')`).

## Exercices

Chaque tâche est indépendante et correspond à un fichier `task_XX_*.py`. Un environnement virtuel
`venv/` (avec Flask installé) est fourni dans ce dossier — pense à l'activer ou à utiliser
`./venv/bin/python` pour lancer les scripts.

### 0. `task_00_intro.py` — Templating simple avec des chaînes de caractères

Avant même de toucher à Flask ou Jinja, cet exercice fait pratiquer le templating "à la main" avec
`str.replace()`. La fonction `generate_invitations(template, attendees)` :

- valide les types d'entrée (`template` doit être une chaîne, `attendees` une liste de dictionnaires) ;
- gère les cas vides (template vide, liste vide) avec des messages d'erreur loggés (module
  `logging`) plutôt que des exceptions qui plantent le programme ;
- remplace les placeholders (`{name}`, `{event_title}`, etc.) par les valeurs correspondantes, ou
  par `"N/A"` si une donnée est manquante (`dict.get(key)` renvoie `None` si absente) ;
- écrit un fichier `output_X.txt` par invité (`X` commence à 1).

C'est l'exercice qui pose les bases du "templating" avant d'introduire un vrai moteur (Jinja). Le
fichier `0-main.py` sert de script de test, et `template.txt` contient le template texte utilisé.

### 1. `task_01_jinja.py` — Premier Flask + Jinja, templates réutilisables

Une application Flask minimale avec trois routes (`/`, `/about`, `/contact`), chacune faisant un
`render_template()` vers un fichier HTML du dossier `templates/`.

Le point intéressant pédagogiquement : `header.html` et `footer.html` sont des templates séparés,
inclus dans chaque page via `{% include 'header.html' %}`. Ça évite de dupliquer le même code de
navigation sur chaque page — le principe DRY (*Don't Repeat Yourself*) appliqué au HTML.

### 2. `task_02_logic.py` — Boucles et conditions Jinja, route `/items`

Ajoute une route `/items` qui lit `items.json` (module `json`) et transmet la liste au template
`items.html`. Ce template illustre :

- `{% for item in items %} ... {% endfor %}` pour afficher chaque élément dans un `<li>` ;
- `{% if items %} ... {% else %} ... {% endif %}` pour afficher "No items found" si la liste est
  vide, sans dupliquer de logique côté Python — c'est Jinja qui décide quoi afficher.

### 3. `task_03_files.py` — Une route, plusieurs formats de données (JSON / CSV)

Route `/products?source=json|csv&id=X` (paramètres via `request.args`). Deux fonctions
`read_json()` / `read_csv()` renvoient toutes les deux la même structure (liste de dictionnaires
`{id, name, category, price}`), ce qui permet au template `product_display.html` de rester
identique quelle que soit la source.

Gestion des cas d'erreur : `source` invalide → message "Wrong source" ; `id` fourni mais absent des
données → "Product not found". Le template affiche soit le tableau de produits, soit le message
d'erreur, selon qu'une variable `error` a été passée ou non à `render_template()`.

### 4. `task_04_db.py` — Ajout de SQLite comme troisième source

Étend l'exercice précédent avec `source=sql`, qui lit dans une base **SQLite** (`products.db`) via
le module `sqlite3`. La fonction `read_sql(product_id=None)` fait une requête paramétrée
(`WHERE id = ?`) pour éviter les injections SQL quand un `id` est fourni.

Le script `create_db.py` (fourni séparément) crée la base et la table `Products`, puis insère deux
lignes d'exemple — à exécuter une fois avant de tester `source=sql`.

## Comment tester

```bash
cd python-server_side_rendering
./venv/bin/python create_db.py          # une seule fois, pour créer products.db
./venv/bin/python 0-main.py             # exercice 0, génère les output_X.txt

./venv/bin/python task_01_jinja.py      # puis ouvrir http://localhost:5000/
./venv/bin/python task_02_logic.py      # http://localhost:5000/items
./venv/bin/python task_03_files.py      # http://localhost:5000/products?source=json
./venv/bin/python task_04_db.py         # http://localhost:5000/products?source=sql
```

## Ressources

- [MDN - Server-Side Web Development](https://developer.mozilla.org/en-US/docs/Learn/Server-side)
- [Flask - documentation officielle](https://flask.palletsprojects.com/)
- [Jinja2 - documentation officielle](https://jinja.palletsprojects.com/)
- [Python - module `json`](https://docs.python.org/3/library/json.html)
- [Python - module `csv`](https://docs.python.org/3/library/csv.html)
- [Python - module `sqlite3`](https://docs.python.org/3/library/sqlite3.html)
