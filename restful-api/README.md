# Python – API REST

Ce projet explore le protocole **HTTP** et la construction d'**API REST**
en Python, à la fois côté **client** (consommer une API existante) et côté
**serveur** (en créer une), avec une progression du module bas niveau
`http.server` jusqu'au framework **Flask**, en terminant par
l'**authentification** (Basic Auth et JWT).

---

## Sommaire

1. [Rappels sur HTTP](#1-rappels-sur-http)
2. [Consommer une API : le module `requests`](#2-consommer-une-api--le-module-requests)
3. [Créer un serveur HTTP "à la main"](#3-créer-un-serveur-http-à-la-main)
4. [Créer une API avec Flask](#4-créer-une-api-avec-flask)
5. [Principes REST](#5-principes-rest)
6. [Authentification : Basic Auth et JWT](#6-authentification--basic-auth-et-jwt)
7. [Sécurité](#7-sécurité)
8. [Pièges fréquents](#8-pièges-fréquents)
9. [Pour aller plus loin](#9-pour-aller-plus-loin)

---

## 1. Rappels sur HTTP

HTTP (*HyperText Transfer Protocol*) est un protocole **requête/réponse** :
un client envoie une **requête** à un serveur, qui répond avec une
**réponse**.

```
   Client                                Serveur
     │   ── GET /users/alice ──────────►   │
     │                                     │  (cherche "alice")
     │   ◄── 200 OK + JSON ───────────────  │
```

### Méthodes HTTP principales

| Méthode | Rôle | Exemple dans ce projet |
|---------|------|--------------------------|
| `GET` | Lire une ressource | `/data`, `/users/<username>` |
| `POST` | Créer une ressource | `/add_user`, `/login` |
| `PUT` / `PATCH` | Modifier une ressource | (non utilisé ici, mais courant en REST) |
| `DELETE` | Supprimer une ressource | (idem) |

### Codes de statut HTTP

| Code | Signification | Exemple |
|------|----------------|---------|
| `200 OK` | Succès | Donnée trouvée et renvoyée |
| `201 Created` | Ressource créée avec succès | Nouvel utilisateur ajouté |
| `400 Bad Request` | La requête du client est invalide | JSON manquant/invalide |
| `401 Unauthorized` | Authentification manquante ou invalide | Mauvais mot de passe, token absent |
| `403 Forbidden` | Authentifié mais pas autorisé | Route admin pour un utilisateur normal |
| `404 Not Found` | Ressource inexistante | Utilisateur ou endpoint introuvable |
| `409 Conflict` | La requête entre en conflit avec l'état actuel | Nom d'utilisateur déjà pris |

### En-têtes (headers)

Chaque requête/réponse contient des **en-têtes**, des métadonnées sous
forme `Clé: Valeur`. Le plus important ici est `Content-Type`, qui indique
le format du corps du message (`text/plain`, `application/json`...).

---

## 2. Consommer une API : le module `requests`

Le module `requests` permet d'envoyer des requêtes HTTP en Python.

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts")

print(response.status_code)   # ex: 200
data = response.json()        # convertit le corps JSON en liste/dict Python
```

- `requests.get(url)` envoie une requête `GET` et retourne un objet
  `Response`.
- `response.status_code` : le code de statut HTTP (`200`, `404`...).
- `response.json()` : parse automatiquement le corps de la réponse comme du
  JSON et le convertit en structures Python.
- **Toujours vérifier `status_code` avant d'utiliser les données** : si la
  requête a échoué, `response.json()` peut ne pas avoir le contenu attendu.

### Exemple : transformer une réponse API en CSV

```python
import csv

posts = response.json()

with open("posts.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["id", "title", "body"])
    writer.writeheader()
    writer.writerows(posts)
```

Ceci relie ce projet au projet **`python-serialization`** : une API renvoie
du JSON, qu'on peut convertir vers n'importe quel autre format (CSV, XML...).

`newline=""` est important sous Windows : sans ce paramètre, le module
`csv` peut ajouter des retours à la ligne en double.

---

## 3. Créer un serveur HTTP "à la main"

Le module standard `http.server` permet de créer un serveur HTTP **sans
framework**, pour comprendre ce qui se passe "sous le capot" de Flask.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class SimpleAPIHandler(BaseHTTPRequestHandler):

    def _send_response(self, code=200, content_type="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self._send_response(200)
            self.wfile.write(b"Hello, this is a simple API!")

        elif self.path == "/data":
            self._send_response(200, "application/json")
            data = {"name": "John", "age": 30, "city": "New York"}
            self.wfile.write(json.dumps(data).encode())

        else:
            self._send_response(404)
            self.wfile.write(b"Endpoint not found")


def run(server_class=HTTPServer, handler_class=SimpleAPIHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
```

Décomposition :

- **`BaseHTTPRequestHandler`** : classe de base fournie par Python ; on la
  hérite et on définit une méthode par méthode HTTP supportée
  (`do_GET`, `do_POST`...).
- **`self.path`** : le chemin demandé par le client (`/`, `/data`...). On le
  compare manuellement pour faire du **routage** — c'est exactement ce que
  Flask fait automatiquement avec `@app.route(...)`.
- **`send_response(code)`** : envoie la ligne de statut (`HTTP/1.1 200 OK`).
- **`send_header(...)` / `end_headers()`** : envoient les en-têtes puis
  signalent la fin des en-têtes (obligatoire avant d'écrire le corps).
- **`self.wfile.write(...)`** : écrit le **corps** de la réponse. Il attend
  des **octets** (`bytes`), donc on doit appeler `.encode()` sur une chaîne
  ou préfixer avec `b"..."`.
- **`json.dumps(data).encode()`** : sérialise un dict en JSON (texte), puis
  encode ce texte en octets pour `wfile.write`.
- **`httpd.serve_forever()`** : boucle infinie qui écoute les connexions.

Cet exercice montre que **Flask n'a rien de magique** : il automatise le
routage, la sérialisation JSON et la gestion des en-têtes que l'on fait ici
manuellement.

---

## 4. Créer une API avec Flask

[Flask](https://flask.palletsprojects.com/) est un micro-framework web qui
simplifie énormément la création d'API.

```python
from flask import Flask, jsonify, request

app = Flask(__name__)
users = {}


@app.route("/")
def home():
    return "Welcome to the Flask API!"


@app.route("/users/<username>")
def get_user(username):
    user = users.get(username)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/add_user", methods=["POST"])
def add_user():
    user = request.get_json(silent=True)

    if user is None:
        return jsonify({"error": "Invalid JSON"}), 400

    username = user.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    if username in users:
        return jsonify({"error": "Username already exists"}), 409

    users[username] = user
    return jsonify({"message": "User added", "user": user}), 201


if __name__ == "__main__":
    app.run()
```

### Les briques essentielles

| Élément | Rôle |
|---------|------|
| `Flask(__name__)` | Crée l'application Flask |
| `@app.route("/chemin")` | Associe une fonction à une URL (routage) |
| `methods=["POST"]` | Restreint la route à une méthode HTTP précise (par défaut : `GET`) |
| `<username>` dans l'URL | **Paramètre dynamique** : la valeur est passée comme argument à la fonction |
| `jsonify(obj)` | Convertit un dict/list Python en réponse JSON avec le bon `Content-Type` |
| `request.get_json(silent=True)` | Récupère le corps JSON de la requête ; `silent=True` retourne `None` au lieu de lever une exception si le JSON est invalide |
| `return data, 404` | Renvoyer un **tuple** `(corps, code_statut)` permet de fixer le code HTTP |

### Schéma de routage

```
Requête entrante
     │
     ▼
Flask compare path + méthode aux routes déclarées (@app.route)
     │
     ▼
Appelle la fonction correspondante
     │
     ▼
La fonction retourne une réponse (string, dict via jsonify, tuple avec code)
```

---

## 5. Principes REST

REST (*REpresentational State Transfer*) est un style d'architecture pour
les API web. Idées clés appliquées dans ce projet :

- **Ressources** identifiées par des URL : `/users/<username>` représente
  *l'utilisateur* `username`.
- **Verbes HTTP = actions** : `GET` pour lire, `POST` pour créer — pas de
  verbe dans l'URL (`/getUser` serait non-RESTful).
- **Sans état (stateless)** : chaque requête contient toute l'information
  nécessaire (ex : le token JWT), le serveur ne garde pas de "session" entre
  deux requêtes.
- **Réponses structurées** : toujours répondre avec un format cohérent
  (`{"error": "..."}` pour les erreurs, `{"message": "...", "user": {...}}`
  pour les succès) et le **bon code de statut**.

---

## 6. Authentification : Basic Auth et JWT

### Basic Authentication

Le client envoie `username:password` encodés en base64 dans l'en-tête
`Authorization`. Avec `flask_httpauth` :

```python
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = users.get(username)
    if user and check_password_hash(user["password"], password):
        return username
    return None


@app.route("/basic-protected")
@auth.login_required
def basic_protected():
    return "Basic Auth: Access Granted"
```

- `@auth.verify_password` définit **comment** vérifier des identifiants.
- `@auth.login_required` protège une route : sans identifiants valides,
  Flask répond automatiquement `401 Unauthorized`.
- Simple, mais le mot de passe est renvoyé à **chaque requête**.

### JWT (JSON Web Token)

Avec JWT, le client s'authentifie **une fois** (`/login`) et reçoit un
**jeton** signé qu'il réutilise ensuite dans l'en-tête
`Authorization: Bearer <token>`.

```python
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt_identity, jwt_required
)

app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)


@app.route("/login", methods=["POST"])
def login():
    credentials = request.get_json(silent=True)
    username = credentials.get("username")
    password = credentials.get("password")

    user = users.get(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=username, additional_claims={"role": user["role"]}
    )
    return jsonify(access_token=access_token)


@app.route("/jwt-protected")
@jwt_required()
def jwt_protected():
    return "JWT Auth: Access Granted"


@app.route("/admin-only")
@jwt_required()
def admin_only():
    username = get_jwt_identity()
    user = users.get(username)
    if not user or user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return "Admin Access: Granted"
```

- `create_access_token(identity=..., additional_claims=...)` génère un
  jeton signé contenant l'identité de l'utilisateur et des informations
  additionnelles (ici, son `role`).
- `@jwt_required()` exige un token valide dans la requête.
- `get_jwt_identity()` récupère l'identité encodée dans le token (sans
  re-demander le mot de passe).
- **Contrôle d'accès basé sur les rôles** : `admin_only` vérifie en plus
  que `user["role"] == "admin"` → distinction entre **authentification**
  (qui es-tu ?) et **autorisation** (as-tu le droit ?).

### Gestion des erreurs JWT

```python
@jwt.unauthorized_loader
def handle_unauthorized_error(err):
    return jsonify({"error": "Missing or invalid token"}), 401

@jwt.expired_token_loader
def handle_expired_token_error(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401
```

Ces *loaders* personnalisent la réponse renvoyée par `flask_jwt_extended`
dans chaque cas d'erreur (token absent, invalide, expiré, révoqué...), pour
garder un format de réponse JSON cohérent dans toute l'API.

### Basic Auth vs JWT

| | Basic Auth | JWT |
|---|------------|-----|
| Identifiants envoyés | À **chaque** requête | Une seule fois (`/login`) |
| Stocké côté client | login/mot de passe | Un jeton (token) |
| Révocation | Immédiate (changer le mot de passe) | Plus complexe (le jeton reste valide jusqu'à expiration) |
| Usage typique | Outils internes, scripts | API publiques, applications web/mobiles |

---

## 7. Sécurité

- **Ne jamais stocker un mot de passe en clair.**
  `generate_password_hash("password")` calcule un hash (avec sel) ;
  `check_password_hash(hash, password)` vérifie un mot de passe sans jamais
  le comparer en clair.
- **`JWT_SECRET_KEY`** sert à signer les tokens : si elle fuite, n'importe
  qui peut forger des tokens valides (y compris `role: admin`). En
  production, elle doit être longue, aléatoire, et stockée hors du code
  source (variable d'environnement).
- **Toujours valider les entrées utilisateur** (`request.get_json(silent=True)`
  puis vérifier `None`, vérifier la présence des champs requis) avant de
  les utiliser.
- **Codes de statut corrects** : un `401` (non authentifié) est différent
  d'un `403` (authentifié mais sans droit) — ne pas les confondre aide le
  client (et l'attaquant en sait moins).

---

## 8. Pièges fréquents

| Erreur | Conséquence | Solution |
|--------|-------------|----------|
| Oublier `.encode()` avec `http.server` | `TypeError: a bytes-like object is required` | `wfile.write` attend des `bytes`, pas des `str` |
| Oublier `end_headers()` | La réponse reste bloquée / corps non envoyé | Toujours appeler `end_headers()` avant `wfile.write` |
| Retourner un dict directement sans `jsonify` | Flask lève une erreur (un dict n'est pas une réponse valide) | Toujours utiliser `jsonify(...)` |
| Ne pas vérifier `request.get_json(silent=True) is None` | `AttributeError` sur `None.get(...)` | Toujours vérifier avant d'appeler `.get()` |
| Stocker des mots de passe en clair | Faille de sécurité critique | `generate_password_hash` / `check_password_hash` |
| Confondre `401` et `403` | Réponses incohérentes pour le client | `401` = pas authentifié, `403` = authentifié mais interdit |
| Ne pas vérifier `response.status_code` avec `requests` | Traiter une erreur comme une donnée valide | Toujours tester `if response.status_code == 200:` |

---

## 9. Pour aller plus loin

- **Flask Blueprints** : organiser une grosse API en plusieurs modules.
- **Flask-RESTful / Flask-Smorest** : frameworks au-dessus de Flask pour
  structurer des API REST plus complexes (validation, documentation
  automatique OpenAPI/Swagger).
- **CORS** (*Cross-Origin Resource Sharing*) : nécessaire si l'API est
  appelée depuis un site web sur un domaine différent.
- **Rate limiting** : limiter le nombre de requêtes par utilisateur pour
  éviter les abus.
- **HTTPS** : en production, toujours servir une API derrière TLS pour
  chiffrer les échanges (mots de passe, tokens...).
