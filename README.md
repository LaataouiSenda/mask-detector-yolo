# Mask Detector using YOLOv8

Ce projet implémente un détecteur de masques faciaux utilisant YOLOv8. Il peut détecter si une personne porte un masque, ne porte pas de masque, ou porte un masque de manière incorrecte.

## Structure du Projet

```
mask-detector-yolo/
├── data/                    # Dossier contenant les données
│   ├── raw/                # Données brutes
│   ├── train/              # Données d'entraînement
│   └── val/                # Données de validation
├── scripts/                 # Scripts Python
│   ├── prepare_dataset.py  # Préparation du dataset
│   ├── train.py           # Script d'entraînement
│   └── voc_to_yolo.py     # Conversion des annotations
└── models/                 # Modèles entraînés
```

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/mask-detector-yolo.git
cd mask-detector-yolo
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Préparez le dataset :
```bash
python scripts/prepare_dataset.py
```

2. Entraînez le modèle :
```bash
python scripts/train.py
```

## Résultats

Le modèle produit les résultats suivants :
- Détection des visages
- Classification en trois catégories :
  - Avec masque (cadre vert)
  - Sans masque (cadre rouge)
  - Masque porté incorrectement (cadre jaune)
- Compteur du nombre de personnes dans chaque catégorie

## Licence

Ce projet est sous licence MIT. 