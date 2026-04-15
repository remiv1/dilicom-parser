# dilicom-parser

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

```python
from dilicom_parser import DistributorParser

parser = DistributorParser()
data = parser.parse_file("distributeur.txt")

for line in data.lines:
    print(line.bloc1.rs1, line.bloc1.ville)
