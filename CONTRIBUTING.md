# Guide de Contribution

Merci de votre intérêt pour **dilicom-parser** !
Ce projet vise à fournir une bibliothèque souveraine, fiable et ouverte pour le traitement des fichiers Dilicom.  
Les contributions sont les bienvenues : corrections, améliorations, documentation, tests, nouvelles fonctionnalités…

Ce document explique comment contribuer efficacement.

---

## 🧱 Principes Généraux

- Soyez respectueux et bienveillant (voir le Code de Conduite).
- Préférez des contributions **simples, lisibles et testées**.
- Privilégiez la cohérence : style, structure, typage, documentation.
- Une petite PR bien ciblée vaut mieux qu’une grosse PR difficile à relire.

---

## 🛠 Prérequis

Avant de contribuer, assurez-vous d’avoir :

- Python 3.10 ou plus
- `pip` ou `uv` ou `poetry`
- `git`

Clonez le dépôt :

```bash
git clone https://github.com/remiv1/dilicom-parser.git
cd dilicom-parser

Installez les dépendances :

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## 🧪 Lancer les tests

Les tests se trouvent dans le dossier `tests/`.

Pour les exécuter :

```bash
pytest
```

Merci de vérifier que tous les tests passent avant de soumettre une PR.

## 🧩 Style de Code

Nous utilisons :

- PEP8 pour le style général
- type hints obligatoires
- dataclasses pour les modèles Dilicom
- pytest pour les tests

Merci de respecter ces conventions.

## 🧬 Structure du Projet

```txt
dilicom_parser/
    models/         # Dataclasses Dilicom
    parser/         # Parseurs (distributeur, stock, etc.)
    utils/          # Alignement, validation, exceptions
    tests/          # Tests unitaires
```

## 📝 Proposer une Contribution

### 1. Ouvrir une issue

Avant de commencer une fonctionnalité importante, merci d’ouvrir une issue pour :

- décrire le problème
- proposer une solution
- éviter les doublons
- valider l’approche

### 2. Créer une branche

```bash
git checkout -b feature/ma-fonctionnalite
```

### 3. Faire des commits clairs

Format recommandé :

```txt
feat: ajout du parseur stock
fix: correction du décalage des colonnes
docs: amélioration du README
test: ajout de tests pour le bloc 2
```

### 4. Soumettre une Pull Request

Merci de :

- décrire clairement ce que fait la PR
- lier l’issue correspondante
- vérifier que les tests passent
- ajouter des tests si nécessaire

Les mainteneurs feront une revue dans les meilleurs délais.

## 🤝 Comment aider sans coder ?

Vous pouvez aussi contribuer en :

- signalant des bugs
- améliorant la documentation
- proposant des exemples d’usage
- testant la bibliothèque sur différents environnements
- partageant le projet

## 📬 Contact

Pour toute question, suggestion ou retour :

- <rverschuur@audit-io.fr>

Merci de contribuer à construire un outil souverain et utile pour l’écosystème Dilicom !
