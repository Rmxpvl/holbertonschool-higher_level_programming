# Python – Sérialisation de données

Ce projet explore plusieurs façons de **transformer des objets Python en
données stockables/transmissibles** (sérialisation) et de **les
reconstruire** ensuite (désérialisation), avec quatre formats : **JSON**,
**Pickle**, **CSV** et **XML**.

---

## Sommaire

1. [Qu'est-ce que la sérialisation ?](#1-quest-ce-que-la-sérialisation-)
2. [JSON : le format universel](#2-json--le-format-universel)
3. [Pickle : sérialiser des objets Python](#3-pickle--sérialiser-des-objets-python)
4. [CSV : données tabulaires](#4-csv--données-tabulaires)
5. [XML : données structurées et hiérarchiques](#5-xml--données-structurées-et-hiérarchiques)
6. [Comparatif des formats](#6-comparatif-des-formats)
7. [Gestion des erreurs et des fichiers](#7-gestion-des-erreurs-et-des-fichiers)
8. [Pièges fréquents](#8-pièges-fréquents)
9. [Pour aller plus loin](#9-pour-aller-plus-loin)

---

## 1. Qu'est-ce que la sérialisation ?

La **sérialisation** consiste à convertir une structure de données ou un
objet présent en mémoire (dictionnaire, liste, instance de classe...) en une
**suite d'octets ou de texte** qui peut être :

- écrite dans un fichier,
- envoyée sur le réseau,
- stockée en base de données.

La **désérialisation** (ou *deserialization*) est l'opération inverse : on
reconstruit l'objet Python d'origine à partir de ces données.

```
   Objet Python                Fichier / réseau               Objet Python
   {"name": "Alice"}  --sérialiser-->  '{"name": "Alice"}'  --désérialiser-->  {"name": "Alice"}
```

Chaque format de ce projet répond à un besoin différent :

| Format | Cas d'usage typique |
|--------|----------------------|
| **JSON** | Échanger des données structurées (API web, fichiers de config) |
| **Pickle** | Sauvegarder/restaurer des objets **Python** complets (y compris des instances de classes) |
| **CSV** | Données tabulaires (export Excel, logs, jeux de données) |
| **XML** | Données hiérarchiques avec métadonnées (configurations, échanges inter-systèmes) |

---

## 2. JSON : le format universel

JSON (*JavaScript Object Notation*) est un format texte, lisible par un
humain, compris par quasiment tous les langages.

### Sérialiser (`json.dump`)

```python
import json

def serialize_and_save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file)
```

- `json.dump(obj, file)` écrit la représentation JSON de `obj` directement
  dans le fichier ouvert.
- `json.dumps(obj)` (avec un "s") fait la même chose mais **retourne une
  chaîne** au lieu d'écrire dans un fichier.

### Désérialiser (`json.load`)

```python
def load_and_deserialize(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)
```

- `json.load(file)` lit le contenu JSON d'un fichier et le convertit en
  structures Python (`dict`, `list`, `str`, `int`, `float`, `bool`, `None`).
- `json.loads(s)` fait la même chose à partir d'une chaîne.

### Correspondance des types

| Python | JSON |
|--------|------|
| `dict` | `object` (`{...}`) |
| `list`, `tuple` | `array` (`[...]`) |
| `str` | `string` |
| `int`, `float` | `number` |
| `True` / `False` | `true` / `false` |
| `None` | `null` |

JSON ne sait représenter que des **types de données simples** : il est
impossible de sérialiser directement une instance de classe personnalisée
avec `json` (sans conversion manuelle en dictionnaire au préalable).

---

## 3. Pickle : sérialiser des objets Python

`pickle` est le format **natif** de Python : il peut sérialiser presque
n'importe quel objet, y compris des **instances de classes personnalisées**,
ce que JSON ne sait pas faire.

```python
import pickle

class CustomObject:
    def __init__(self, name, age, is_student):
        self.name = name
        self.age = age
        self.is_student = is_student

    def serialize(self, filename):
        with open(filename, "wb") as file:      # "wb" = écriture binaire
            pickle.dump(self, file)

    @classmethod
    def deserialize(cls, filename):
        try:
            with open(filename, "rb") as file:  # "rb" = lecture binaire
                return pickle.load(file)
        except (FileNotFoundError, pickle.PickleError,
                EOFError, AttributeError, TypeError):
            return None
```

Points clés :

- Pickle produit des **données binaires** : on ouvre les fichiers en mode
  `"wb"` (write binary) et `"rb"` (read binary), pas en mode texte.
- `pickle.dump(obj, file)` sérialise l'objet **avec toute sa classe et ses
  attributs**.
- `pickle.load(file)` reconstruit un objet du **même type**, avec les mêmes
  attributs.
- `@classmethod` : `deserialize` est appelée sur la **classe**
  (`CustomObject.deserialize(...)`) et non sur une instance ; `cls`
  représente la classe elle-même. C'est logique ici : pour désérialiser, on
  n'a pas encore d'instance !

### ⚠️ Pickle et sécurité

> **Ne jamais utiliser `pickle.load()` sur des données provenant d'une
> source non fiable** (fichier téléchargé, requête réseau, utilisateur
> externe). `pickle` peut exécuter du code arbitraire pendant la
> désérialisation. Réservez `pickle` aux données que **vous** avez générées
> et stockées localement.

---

## 4. CSV : données tabulaires

CSV (*Comma-Separated Values*) représente des données sous forme de
**tableau** : une ligne d'en-têtes, puis une ligne par enregistrement.

```python
import csv
import json

def convert_csv_to_json(CSV_filename):
    try:
        data = []
        with open(CSV_filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)

        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return True
    except (FileNotFoundError, OSError):
        return False
```

- `csv.DictReader(file)` lit le CSV et transforme **chaque ligne en
  dictionnaire**, en utilisant la première ligne du fichier comme clés
  (en-têtes de colonnes).

  ```
  CSV :                          ->  dict produit :
  name,age                           {"name": "Alice", "age": "30"}
  Alice,30
  ```

- `json.dump(data, file, indent=4)` : l'argument `indent=4` formate le JSON
  avec une indentation de 4 espaces, pour un fichier **lisible** par un
  humain (sinon tout est sur une seule ligne).

- Cet exercice illustre une idée centrale : **on peut combiner plusieurs
  formats** — ici, lire du CSV puis écrire le résultat en JSON.

---

## 5. XML : données structurées et hiérarchiques

XML (*eXtensible Markup Language*) représente les données sous forme
d'**arbre de balises imbriquées**.

```python
import xml.etree.ElementTree as ET


def serialize_to_xml(dictionary, filename):
    root = ET.Element("data")

    for key, value in dictionary.items():
        child = ET.SubElement(root, key)
        child.text = str(value)

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=False)


def deserialize_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    return {child.tag: child.text for child in root}
```

Pour `dictionary = {"name": "Alice", "age": "30"}`, le XML produit
ressemble à :

```xml
<data>
    <name>Alice</name>
    <age>30</age>
</data>
```

Concepts du module `xml.etree.ElementTree` :

| Élément | Rôle |
|---------|------|
| `ET.Element("data")` | Crée un nœud racine `<data>` |
| `ET.SubElement(root, key)` | Ajoute un **enfant** `<key>` sous `root` |
| `child.text = str(value)` | Définit le contenu texte de la balise |
| `ET.ElementTree(root)` | Encapsule l'arbre pour pouvoir l'écrire |
| `tree.write(filename, ...)` | Sérialise l'arbre dans un fichier |
| `ET.parse(filename)` | Lit et parse un fichier XML en arbre |
| `tree.getroot()` | Récupère le nœud racine |
| `{child.tag: child.text for child in root}` | Reconstruit un dictionnaire à partir des enfants directs de la racine |

Remarque : `child.text` est toujours une **chaîne de caractères** — XML ne
distingue pas nativement les types (entier, booléen...), contrairement à
JSON. Si on veut récupérer un `int`, il faut convertir explicitement
(`int(child.text)`).

---

## 6. Comparatif des formats

| Critère | JSON | Pickle | CSV | XML |
|---------|------|--------|-----|-----|
| Lisible par un humain | ✅ | ❌ (binaire) | ✅ | ✅ |
| Interopérable (autres langages) | ✅ | ❌ (Python uniquement) | ✅ | ✅ |
| Supporte les objets Python personnalisés | ❌ | ✅ | ❌ | ❌ |
| Adapté aux données tabulaires | Moyen | Mauvais | ✅ | Moyen |
| Mode d'ouverture de fichier | texte (`"w"`/`"r"`) | binaire (`"wb"`/`"rb"`) | texte | texte |
| Risque de sécurité à la désérialisation | Faible | **Élevé** (code arbitraire) | Faible | Faible (sauf XML "bombs") |

---

## 7. Gestion des erreurs et des fichiers

Tous ces exercices suivent le même schéma :

```python
with open(filename, mode, encoding="utf-8") as file:
    ...
```

- Le bloc `with` garantit que le fichier est **fermé automatiquement**, même
  en cas d'erreur.
- `encoding="utf-8"` est important pour les fichiers texte (JSON, CSV) afin
  d'éviter les problèmes d'accents/caractères spéciaux selon la plateforme.
- Pour Pickle, **pas d'`encoding`** : les modes sont `"wb"`/`"rb"` (binaire).

Pour signaler un échec sans faire crasher le programme, on encapsule les
opérations risquées dans un `try/except` qui capture les exceptions
pertinentes (`FileNotFoundError`, `OSError`, `pickle.PickleError`,
`EOFError`...) et retourne une valeur (`None`, `False`) plutôt que de
laisser l'exception se propager.

---

## 8. Pièges fréquents

| Erreur | Conséquence | Solution |
|--------|-------------|----------|
| Ouvrir un fichier Pickle en mode texte (`"w"`/`"r"`) | `TypeError` (Pickle produit des octets, pas du texte) | Utiliser `"wb"`/`"rb"` |
| `json.dump` sur un objet personnalisé non converti | `TypeError: Object of type X is not JSON serializable` | Convertir l'objet en `dict` avant de sérialiser |
| Oublier `encoding="utf-8"` | Caractères accentués mal lus/écrits selon l'OS | Toujours préciser l'encodage pour les fichiers texte |
| Désérialiser un Pickle non fiable | Exécution de code arbitraire (faille de sécurité) | Ne charger que des fichiers Pickle créés par votre propre code |
| Oublier que `csv.DictReader` retourne des **chaînes** | `"30" + 1` lève une erreur | Convertir explicitement (`int(row["age"])`) si besoin |
| Confondre `dump`/`load` (fichier) et `dumps`/`loads` (chaîne) | `TypeError` (mauvais type d'argument) | `dump`/`load` ↔ fichier ; `dumps`/`loads` ↔ chaîne |

---

## 9. Pour aller plus loin

- **`json.dumps(obj, default=...)`** : permet de fournir une fonction de
  conversion personnalisée pour sérialiser des objets non standards en JSON.
- **`csv.DictWriter`** : l'inverse de `DictReader`, pour écrire des
  dictionnaires Python vers un fichier CSV.
- **`yaml`** (bibliothèque tierce) : format proche de JSON mais plus lisible,
  très utilisé pour les fichiers de configuration.
- **`marshmallow` / `pydantic`** : bibliothèques de (dé)sérialisation et
  validation de données, très utilisées avec les API web (voir le projet
  `restful-api`).
