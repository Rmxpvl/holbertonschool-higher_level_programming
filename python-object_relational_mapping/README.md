# Python – Object-Relational Mapping (ORM)

Ce projet fait le pont entre **Python** et une base de données **MySQL**. Il
part des requêtes SQL brutes (avec `MySQLdb`) pour arriver progressivement à
l'utilisation d'un **ORM** (`SQLAlchemy`), qui permet de manipuler des lignes
de base de données comme de simples objets Python.

---

## Sommaire

1. [Vocabulaire : qu'est-ce qu'un ORM ?](#1-vocabulaire--quest-ce-quun-orm-)
2. [Se connecter à MySQL avec `MySQLdb`](#2-se-connecter-à-mysql-avec-mysqldb)
3. [Le danger des injections SQL](#3-le-danger-des-injections-sql)
4. [Jointures (`JOIN`) entre tables](#4-jointures-join-entre-tables)
5. [Définir des modèles avec SQLAlchemy](#5-définir-des-modèles-avec-sqlalchemy)
6. [Engine et Session : la porte d'entrée de l'ORM](#6-engine-et-session--la-porte-dentrée-de-lorm)
7. [Lire des données : `query`, `filter`, `order_by`](#7-lire-des-données--query-filter-order_by)
8. [Créer, modifier, supprimer (CRUD)](#8-créer-modifier-supprimer-crud)
9. [Relations entre modèles](#9-relations-entre-modèles)
10. [SQL brut vs ORM : tableau récapitulatif](#10-sql-brut-vs-orm--tableau-récapitulatif)
11. [Pièges fréquents](#11-pièges-fréquents)
12. [Pour aller plus loin](#12-pour-aller-plus-loin)

---

## 1. Vocabulaire : qu'est-ce qu'un ORM ?

Un **ORM** (*Object-Relational Mapping*) est une bibliothèque qui fait
correspondre :

| Monde base de données | Monde Python (ORM) |
|------------------------|---------------------|
| Une **table** | Une **classe** |
| Une **ligne** (row) | Une **instance** de cette classe |
| Une **colonne** | Un **attribut** de l'instance |
| Une requête `SELECT ... WHERE ...` | Un appel `.query(...).filter(...)` |

L'objectif : écrire du Python plutôt que des chaînes SQL, tout en gardant le
contrôle sur les requêtes générées.

Ce projet utilise :

- **`MySQLdb`** (`mysqlclient`) : le driver "bas niveau" qui exécute du SQL
  brut.
- **SQLAlchemy** : l'ORM qui génère le SQL à partir d'objets Python.

---

## 2. Se connecter à MySQL avec `MySQLdb`

Avant l'ORM, on commence par le driver bas niveau :

```python
import MySQLdb

db = MySQLdb.connect(
    host="localhost",
    port=3306,
    user=argv[1],
    passwd=argv[2],
    db=argv[3]
)

cursor = db.cursor()
cursor.execute("SELECT * FROM states ORDER BY states.id ASC")

for row in cursor.fetchall():
    print(row)

cursor.close()
db.close()
```

Points clés :

- `db.cursor()` crée un **curseur**, l'objet utilisé pour exécuter des
  requêtes et lire les résultats.
- `cursor.execute(sql)` envoie la requête SQL au serveur.
- `cursor.fetchall()` récupère **toutes** les lignes du résultat sous forme
  de tuples Python (`(id, name)`).
- Toujours **fermer** le curseur et la connexion (`close()`) une fois
  terminé, pour libérer les ressources côté serveur.

---

## 3. Le danger des injections SQL

### Version dangereuse (concaténation / `.format()`)

```python
query = "SELECT * FROM states WHERE name = '{}' ORDER BY id ASC".format(
    argv[4]
)
cursor.execute(query)
```

Si `argv[4]` contient `Texas'; DROP TABLE states; --`, la requête finale
devient une **toute autre requête SQL** : c'est une **injection SQL**, l'une
des failles de sécurité les plus connues (OWASP Top 10).

### Version sûre (requête paramétrée)

```python
cursor.execute(
    "SELECT * FROM states WHERE name = %s ORDER BY id ASC",
    (argv[4],)
)
```

- `%s` est un **placeholder** géré par le driver, pas par Python.
- Le driver envoie la valeur **séparément** de la requête : elle ne peut
  jamais être interprétée comme du code SQL.
- **Règle d'or : ne jamais utiliser `.format()`, `%` ou des f-strings pour
  injecter une valeur utilisateur dans du SQL.** Toujours passer par les
  paramètres du driver (ou par l'ORM, qui le fait automatiquement).

---

## 4. Jointures (`JOIN`) entre tables

Pour combiner des informations venant de deux tables liées par une clé
étrangère (`state_id` dans `cities` qui référence `id` dans `states`) :

```sql
SELECT cities.id, cities.name, states.name
FROM cities
JOIN states ON cities.state_id = states.id
ORDER BY cities.id ASC
```

- `JOIN ... ON ...` indique **comment** relier les deux tables : ici, la
  colonne `state_id` d'une ville correspond à l'`id` d'un état.
- Chaque ligne du résultat combine des colonnes des **deux** tables.
- On peut filtrer le résultat d'une jointure avec un `WHERE` classique,
  toujours en paramétrant les valeurs (`%s`).

---

## 5. Définir des modèles avec SQLAlchemy

Un **modèle** est une classe Python qui représente une table.

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(128), nullable=False)
```

- `declarative_base()` crée une classe de base (`Base`) dont **tous les
  modèles doivent hériter**. Elle garde le registre de toutes les tables
  définies.
- `__tablename__` indique le nom exact de la table en base.
- `Column(...)` définit une colonne :
  - `Integer`, `String(128)`, etc. → le **type SQL**.
  - `primary_key=True` → clé primaire.
  - `nullable=False` → colonne obligatoire (`NOT NULL`).
  - `autoincrement=True` → valeur générée automatiquement (`AUTO_INCREMENT`).

### Une clé étrangère

```python
from sqlalchemy import Column, ForeignKey, Integer, String
from model_state import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(128), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
```

`ForeignKey("states.id")` indique que `state_id` référence la colonne `id`
de la table `states` — l'équivalent du `JOIN ON` vu plus haut, mais déclaré
une fois dans le modèle.

Important : **toutes les classes doivent partager le même `Base`** (ici,
`City` importe `Base` depuis `model_state.py`) pour que SQLAlchemy connaisse
toutes les tables et puisse résoudre les `ForeignKey`.

---

## 6. Engine et Session : la porte d'entrée de l'ORM

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'mysql+mysqldb://{}:{}@localhost/{}'.format(user, password, db_name),
    pool_pre_ping=True
)

Session = sessionmaker(bind=engine)
session = Session()
```

- **`create_engine(url)`** : décrit *comment* se connecter (driver, identifiants,
  base de données). `mysql+mysqldb://` signifie « base MySQL, via le driver
  `MySQLdb` ».
  - `pool_pre_ping=True` : SQLAlchemy vérifie que la connexion est toujours
    valide avant de l'utiliser (évite des erreurs si la connexion a expiré).
- **`sessionmaker(bind=engine)`** : fabrique une "classe Session" liée à cet
  `engine`.
- **`session = Session()`** : crée une session, l'objet à travers lequel on
  fait **toutes** les opérations (lecture, ajout, modification, suppression).
- Comme pour `MySQLdb`, on termine toujours par `session.close()`.

---

## 7. Lire des données : `query`, `filter`, `order_by`

```python
# Toutes les lignes, triées
states = session.query(State).order_by(State.id).all()

# La première ligne seulement
state = session.query(State).order_by(State.id).first()

# Filtrer (équivalent d'un WHERE)
states = session.query(State).filter(State.name.like('%a%')).order_by(State.id).all()

# Filtrer sur une égalité exacte
state = session.query(State).filter(State.name == sys.argv[4]).first()
```

| Méthode | Rôle | Équivalent SQL |
|---------|------|-----------------|
| `session.query(Model)` | Démarre une requête sur la table du modèle | `SELECT * FROM table` |
| `.filter(condition)` | Ajoute une condition | `WHERE ...` |
| `.order_by(Model.colonne)` | Trie le résultat | `ORDER BY ...` |
| `.all()` | Récupère **toutes** les lignes (liste d'objets) | – |
| `.first()` | Récupère la **première** ligne, ou `None` | `LIMIT 1` |
| `Model.colonne.like('%a%')` | Motif `LIKE` | `LIKE '%a%'` |

Le résultat de `.all()` est une **liste d'instances** de la classe (ici,
des objets `State`), pas des tuples : on accède aux colonnes via
`state.id`, `state.name`, comme des attributs Python normaux.

---

## 8. Créer, modifier, supprimer (CRUD)

### Create (ajouter une ligne)

```python
new_state = State(name="Louisiana")
session.add(new_state)
session.commit()

print(new_state.id)   # l'id est généré par la base, disponible après le commit
```

### Update (modifier une ligne existante)

```python
state = session.query(State).filter(State.id == 2).first()
state.name = "New Mexico"
session.commit()
```

On modifie simplement l'**attribut Python** de l'objet récupéré ; SQLAlchemy
détecte le changement et génère un `UPDATE` au moment du `commit()`.

### Delete (supprimer des lignes)

```python
for state in session.query(State).filter(State.name.like('%a%')):
    session.delete(state)
session.commit()
```

### Le cycle CRUD avec l'ORM

```
   add(obj)            modifier un attribut         delete(obj)
       │                       │                          │
       ▼                       ▼                          ▼
  ┌─────────────────────────────────────────────────────────┐
  │                  session (zone de travail)               │
  └─────────────────────────────────────────────────────────┘
                              │
                       session.commit()
                              │
                              ▼
                       Base de données MySQL
```

**`commit()` est l'étape qui écrit réellement en base.** Sans `commit()`,
les changements restent en mémoire côté session et peuvent être annulés
avec `session.rollback()`.

---

## 9. Relations entre modèles

Pour récupérer des `City` avec le nom de leur `State`, on peut joindre deux
modèles directement dans une requête ORM :

```python
results = session.query(City, State).join(
    State, City.state_id == State.id
).order_by(City.id).all()

for city, state in results:
    print("{}: ({}) {}".format(state.name, city.id, city.name))
```

- `session.query(City, State)` : on demande des **tuples** `(City, State)`.
- `.join(State, City.state_id == State.id)` : équivalent du `JOIN ... ON ...`
  vu en SQL brut, mais exprimé avec les attributs des modèles.
- Chaque élément de `results` est un tuple `(city, state)` où `city` est une
  instance de `City` et `state` une instance de `State`.

---

## 10. SQL brut vs ORM : tableau récapitulatif

| Opération | `MySQLdb` (SQL brut) | SQLAlchemy (ORM) |
|-----------|------------------------|-------------------|
| Connexion | `MySQLdb.connect(...)` | `create_engine(...)` + `sessionmaker` |
| Lire tout | `cursor.execute("SELECT * FROM states")` | `session.query(State).all()` |
| Filtrer | `WHERE name = %s` + tuple de params | `.filter(State.name == valeur)` |
| Trier | `ORDER BY id ASC` | `.order_by(State.id)` |
| Insérer | `INSERT INTO ... VALUES (%s)` | `session.add(obj)` + `commit()` |
| Modifier | `UPDATE ... SET ... WHERE ...` | modifier l'attribut + `commit()` |
| Supprimer | `DELETE FROM ... WHERE ...` | `session.delete(obj)` + `commit()` |
| Jointure | `JOIN ... ON ...` en SQL | `.query(A, B).join(B, A.fk == B.id)` |

---

## 11. Pièges fréquents

| Erreur | Conséquence | Solution |
|--------|-------------|----------|
| Construire une requête avec `.format()` ou f-string | Injection SQL | Utiliser `%s` (MySQLdb) ou les `filter()` de l'ORM |
| Oublier `session.commit()` | Les changements ne sont jamais écrits en base | Toujours `commit()` après `add`/modification/`delete` |
| Oublier `session.close()` / `db.close()` | Connexions qui s'accumulent, erreurs "too many connections" | Toujours fermer en fin de script |
| Définir deux `Base` différents (un par modèle) | SQLAlchemy ne voit pas les `ForeignKey` entre tables | Toujours importer le **même** `Base` depuis un seul module |
| Utiliser `.first()` sans vérifier `None` | `AttributeError` si aucune ligne trouvée | Toujours tester `if result is None:` avant d'accéder aux attributs |
| Confondre `==` Python et `==` SQLAlchemy | `State.id == 2` ne compare pas tout de suite : ça construit une *expression* utilisée par `filter()` | Cette syntaxe est normale **dans** `.filter(...)`, mais pas pour comparer deux valeurs Python classiques |

---

## 12. Pour aller plus loin

- **`relationship()` et `back_populates`** : au lieu de faire un `.join()`
  manuel, SQLAlchemy peut exposer directement `state.cities` (liste des
  villes d'un état) grâce à `relationship()`.
- **Alembic** : outil de migration de schéma pour faire évoluer les tables
  sans perdre les données.
- **Sessions et transactions** : `session.rollback()` permet d'annuler des
  changements non encore "commités" en cas d'erreur.
- **ORM vs SQL brut** : l'ORM est idéal pour la logique applicative, mais
  pour des requêtes très complexes ou des optimisations fines, écrire du SQL
  brut (via `session.execute(text(...))`) reste parfois pertinent.
