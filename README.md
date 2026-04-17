# Package de gestion des fichiers Dilicom sur serveur SFTP

![PyPi version](https://img.shields.io/pypi/v/dilicom-parser)
![Licence](https://img.shields.io/badge/license-MIT-blue)
![Python version](https://img.shields.io/pypi/pyversions/dilicom-parser)
![Pandas version](https://img.shields.io/badge/pandas-%3E%3D3.0.2-green)
![Paramiko version](https://img.shields.io/badge/paramiko-%3E%3D4.0.0-green)
![python-dotenv version](https://img.shields.io/badge/python--dotenv-%3E%3D1.2.2-green)

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
- 🧪 Tests unitaires inclus

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

Ensuite, utiliser le parser dans votre code Python :

```python
from dotenv import load_dotenv
from dilicom_parser import DistributorParser

load_dotenv('path/to/.env')

parser = DistributorParser()
data = parser.parse_file("distributeur.txt")

for line in data.lines:
    print(line.bloc1.rs1)   # Raison sociale principale du distributeur
    print(line.bloc1.ville)  # Ville du distributeur
```
