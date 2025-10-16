# Guide d'installation

## prérequis

- python 3.8 ou supérieur
- pip package manager
- environnement virtuel (recommandé)

## étapes d'installation

### 1. cloner le projet

```bash
git clone https://github.com/user/projet.git
cd projet
```

### 2. créer environnement virtuel

```bash
python -m venv venv
```

### 3. activer environnement

**windows :**
```bash
venv\Scripts\activate
```

**linux/mac :**
```bash
source venv/bin/activate
```

### 4. installer dépendances

```bash
pip install -r requirements.txt
```

### 5. lancer l'app

```bash
python app.py
```

## configuration

créer un fichier `.env` :

```env
SECRET_KEY=votre-clé-secrète
DEBUG=True
PORT=5000
```

## dépannage

### erreur : module non trouvé

vérifier que l'environnement virtuel est activé

### erreur : port déjà utilisé

changer le port dans la config

```python
app.run(port=5001)
```

[← retour à l'accueil](index.md) | [documentation api →](api.md)
