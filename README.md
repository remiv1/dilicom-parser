# Package de gestion des fichiers Dilicom sur serveur SFTP

![PyPi version](https://img.shields.io/pypi/v/dilicom-parser)
![Licence](https://img.shields.io/badge/license-MIT-blue)
![Python version](https://img.shields.io/pypi/pyversions/dilicom-parser)
![Pandas version](https://img.shields.io/badge/pandas-%3E%3D3.0.2-green)
![Paramiko version](https://img.shields.io/badge/paramiko-%3E%3D4.0.0-green)
![python-dotenv version](https://img.shields.io/badge/python--dotenv-%3E%3D1.2.2-green)
![onixlib version](https://img.shields.io/badge/onixlib-%3E%3D0.1.1-green)

**dilicom-parser** est une bibliothèque Python souveraine dédiée à la lecture, au parsing, à la validation et à la transformation des fichiers Dilicom (distributeurs, commandes, etc.).
Elle fournit des modèles de données stricts, des parseurs robustes et des outils d’audit pour garantir une intégration fiable et reproductible.

## 🚀 Objectifs

- Offrir une **implémentation Python propre et moderne** des structures Dilicom.
- Fournir des **dataclasses typées** pour chaque bloc Dilicom.
- Faciliter l’intégration dans des pipelines d’audit, d’ETL ou de synchronisation.
- Proposer une base souveraine et open-source pour les acteurs du livre.

## ✨ Fonctionnalités

- 📦 Modèles de données Dilicom (Bloc 1, Bloc 2, Bloc 3…)
- 🧩 Parseur robuste basé sur l’ordre contractuel des champs
- 🔍 Validation des types et des valeurs
- 📊 Conversion DataFrame → objets Python
- 📚 Gestion des fichiers livres archivés (`.zip`, `.zip.rdy`, `.zip.rdy.csv`, etc.)
- 🚰 Basculement automatique en streaming au-delà de `512 MiB`
- 🧪 Tests unitaires inclus
- 🧠 Stubs de typage complets (`.pyi`) pour l'auto-complétion IDE et les outils de type-checking

## 📄 Exemple d’utilisation

Créer le fichier .env avec les variables d’environnement nécessaires :

```ini
#.env

# Variables pour les dossier d’entrée et de sortie des fichiers
DILICOM_IN_DIR=/path/to/dilicom/files
DILICOM_OUT_DIR=/path/to/output

# Optionnel, variables pour la connexion FTP si nécessaire
DILICOM_HOST=ftp.example.com
DILICOM_PORT=11234
DILICOM_USER=username
DILICOM_SECRET=password
```

## 🧪 Cas d'usage

### 1. Parser des fichiers locaux (distributor / eancom / gencod)

```python
from pathlib import Path
from dilicom_parser.classifier import FilesClassifier

files_directory = Path("/path/to/dilicom/files")
file_list = list(files_directory.glob("*"))

classifier = FilesClassifier(file_list=file_list, streaming_option=True)
classifier.classify()

counts = classifier.count_by_type()
print(counts)  # ex: {'distributor': 9, 'eancom': 5, 'gencod': 4}

parsed = classifier.parse()

distributor_results = parsed.get("distributor", [])
if distributor_results:
    first_file = distributor_results[0]
    first_line = first_file.lines[0]
    print(first_line.bloc1.rs1)
    print(first_line.bloc1.ville)
```

### 2. Récupérer les fichiers via SFTP puis parser

```python
from pathlib import Path
from dilicom_parser.transport import Connector
from dilicom_parser.classifier import FilesClassifier

local_dir = Path("/tmp/dilicom")
local_dir.mkdir(parents=True, exist_ok=True)

with Connector(env_path="/path/to/.env") as connector:
    downloaded_files = connector.download_all(local_dir=local_dir, archive=False)

classifier = FilesClassifier(file_list=downloaded_files, streaming_option=True)
results = classifier.classify().parse()
print(results.keys())
```

### 3. Dans un notebook Jupyter

```python
from dilicom_parser.classifier import FilesClassifier
from pathlib import Path
import ipynbname
path = ipynbname.path()

files_directory = Path(path).parent / "dilicom"
file_list = list(files_directory.glob(pattern="*"))
classifier = FilesClassifier(file_list=file_list, streaming_option=True)

classifier.classify()

print("Classification terminée. Résultats :")
from pprint import pprint
pprint(classifier.count_by_type())

parsed = classifier.parse()
pprint(parsed.keys())

```

Paramètre utile:

- `streaming_option=True` (défaut) pour un traitement orienté streaming.
- `streaming_option=False` pour un traitement non-streaming, sauf si un fichier dépasse `512 MiB` (forçage automatique du streaming).

Note sur le mode streaming:

- Si `streaming_option=False` mais qu'au moins un fichier dépasse `512 MiB`, le mode streaming est activé automatiquement.
- Ce basculement est journalisé (`WARNING`) et déclenche aussi un avertissement Python (`UserWarning`).

Note sur les archives:

- À l'initialisation, les fichiers `.zip` et `.zip.rdy` sont extraits automatiquement dans un dossier dédié.
- Les fichiers extraits sont ajoutés à la liste des fichiers à traiter.
- L'archive source est supprimée après extraction réussie.

## 🧾 Stubs de typage

La bibliothèque embarque des stubs `.pyi` complets sous `src/dilicom_parser/` pour tous les modules.

Objectif:

- Améliorer l'aide contextuelle des IDEs (signatures, retours, types).
- Faciliter l'analyse statique (mypy, pyright, pylance).

Régénération des stubs:

```bash
PYTHONPATH=src ./venv/bin/stubgen -p dilicom_parser -o /tmp/dilicom_stubs
cp -R /tmp/dilicom_stubs/dilicom_parser/* src/dilicom_parser/
touch src/dilicom_parser/py.typed
```

```console
Classification terminée. Résultats :
{'distributor': 9, 'eancom': 5, 'gencod': 4}
```
