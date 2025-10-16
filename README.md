# Multi-Projects Host

Application web Flask pour héberger plusieurs projets Flask, Markdown et autres types configurables sur un seul serveur.

## Présentation

Multi-Projects Host agit comme un hub extensible. Chaque type de projet possède sa propre logique, ses routes et ses règles de détection. La configuration se fait via des fichiers YAML, ce qui facilite l'ajout ou l'ajustement de nouveaux systèmes (Flask, Markdown, futurs types comme Django, NodeJS, HTML statique, etc.).

## Fonctionnalités clés

- hébergement simultané de projets Flask, Markdown et d'autres types personnalisés
- routage dynamique piloté par la configuration YAML dans `projects_types_configs`
- navigation single-page (SPA) avec transitions fluides
- menu Markdown hiérarchique pliable avec icônes dynamiques
- rendu Markdown avancé (fenced code, tables, toc)
- interface responsive avec animations CSS accélérées GPU
- pages d'erreur personnalisées et theme switch côté client

## Architecture de configuration

Les fichiers YAML contenus dans `projects_types_configs/` décrivent chaque type de projet. Ils acceptent les champs suivants :

- `type` : identifiant du type (ex. `flask`, `markdown`)
- `identifier` : clé interne utilisée pour référencer le type dans l'application
- `projects_dir` : chemin (relatif ou absolu) vers le dossier des projets
- `project_config_file` : nom du fichier de configuration propre à chaque projet (par défaut `.mph-config`)
- `default_emoji` : emoji utilisé si un projet n'en définit pas
- champs spécifiques (ex. `app_filename` pour Flask, `markdown.extensions` pour Markdown)
- `implementation` (optionnel) : chemin module:Classe si vous fournissez votre propre classe `ProjectType`

### Ajouter un nouveau type

1. Créer une classe héritant de `projects_types.base.ProjectType` (ex. `projects_types/my_type.py`).
2. Dans cette classe : implémenter `list_projects` et `register_routes`, puis enregistrer les routes Flask nécessaires.
3. Ajouter un fichier `projects_types_configs/mon_type.yaml` avec `type` correspondant (ou `implementation` vers votre classe personnalisée).
4. Redémarrer l'application pour charger automatiquement le nouveau type.

## Structure du dépôt

```text
projects-flask-repo/
├── app.py
├── requirements.txt
├── projects/
│   ├── flask/
│   │   └── exemple/
│   │       └── app.py
│   └── markdown/
│       └── exemple/
│           ├── index.md
│           └── ...
├── projects_types/
│   ├── __init__.py
│   ├── base.py
│   ├── flask_type.py
│   └── markdown_type.py
├── projects_types_configs/
│   ├── flask.yaml
│   └── markdown.yaml
├── static/
│   ├── css/style.css
│   └── js/
│       ├── spa.js
│       └── theme.js
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── flask_list.html
│   ├── md_list.html
│   ├── md_project.html
│   ├── md_page.html
│   ├── debug_spa.html
│   ├── 404.html
│   └── 500.html
└── ...
```

## Installation

```powershell
pip install -r requirements.txt
```

## Démarrage

```powershell
python app.py
```

L'application démarre sur <http://localhost:5000>.

## Routes principales

- `/` : accueil listant les projets actifs
- `/flask` : liste des projets Flask
- `/flask/<project_name>` : projet Flask (les sous-routes sont déléguées à l'application embarquée)
- `/md` : liste des projets Markdown
- `/md/<project_name>` : page d'accueil du projet Markdown
- `/md/<project_name>/<page>` : rendu d'une page Markdown

## Ajouter un projet Flask

1. Placer un dossier dans `projects/flask/nom_du_projet/`.
2. Créer un fichier `app.py` contenant une application Flask nommée selon `application_attribute` (par défaut `app`).
3. Optionnel : ajouter un fichier `.mph-config` pour définir `name`, `emoji`, etc.

Exemple minimal :

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'bienvenue sur mon projet flask'

if __name__ == '__main__':
    app.run(debug=True)
```

## Ajouter un projet Markdown

1. Placer un dossier dans `projects/markdown/nom_du_projet/`.
2. Ajouter des fichiers `.md` (un `index.md` ou `README.md` sert de page d'accueil automatique).
3. Configurer `.mph-config` pour masquer certains fichiers (`markdown.hidden_files`) ou dossiers (`markdown.hidden_folders`).

### Exemples de fichiers `.mph-config`

Exemple pour un projet Flask (`projects/flask/blog/.mph-config`) :

```yaml
name: Blog interne
emoji: "🧪"
description: Application Flask de test
environment:
    FLASK_ENV: development
    FEATURE_FLAG: search
routes:
    - path: /
      label: Accueil
    - path: /admin
      label: Administration
```

Exemple pour un projet Markdown (`projects/markdown/docs/.mph-config`) :

```yaml
name: Documentation Produit
emoji: "📘"
markdown:
    hidden_files:
        - drafts/todo.md
    hidden_folders:
        - old_versions
    extensions:
        - fenced_code
        - toc
        - tables
breadcrumbs:
    enabled: true
```

## Créer un type tiers (ex. NodeJS)

1. Créer le fichier `projects_types/node_type.py` avec une classe dédiée.
2. Définir le type dans `projects_types_configs/node.yaml` en précisant `implementation`.
3. Redémarrer l'application pour charger le nouveau type.

Extrait minimal pour la classe personnalisée :

```python
from pathlib import Path
from typing import Any, Dict, List

from flask import abort, render_template

from projects_types.base import ProjectType


class NodeProjectType(ProjectType):
    type_name = "node"

    def list_projects(self) -> List[Dict[str, Any]]:
        if not self.projects_root_exists():
            return []
        projects: List[Dict[str, Any]] = []
        for directory in sorted(self.projects_dir.iterdir()):
            package_file = directory / "package.json"
            if package_file.is_file():
                project_id = directory.name
                projects.append(
                    {
                        "id": project_id,
                        "name": self.get_project_display_name(project_id),
                        "emoji": self.get_project_emoji(project_id),
                    }
                )
        return projects

    def register_routes(self) -> None:
        app = self.app

        @app.route(f"/node/<project_name>")
        def node_project(project_name: str):
            package_file = self.projects_dir / project_name / "package.json"
            if not package_file.is_file():
                abort(404)
            return render_template(
                "node_project.html",
                project_name=project_name,
                project_display_name=self.get_project_display_name(project_name),
                project_emoji=self.get_project_emoji(project_name),
            )
```

Configuration YAML correspondante (`projects_types_configs/node.yaml`) :

```yaml
type: node
identifier: node
implementation: projects_types.node_type:NodeProjectType
projects_dir: projects/node
project_config_file: .mph-config
default_emoji: "🟢"
```

## SPA et navigation hiérarchique

### SPA (Single Page Application)

Le script `static/js/spa.js` intercepte les clics sur les liens marqués `data-spa`. Les pages suivantes bénéficient de la navigation fluide :

- `/flask`
- `/md`
- toutes les pages Markdown individuelles

Avantages : chargement quasi instantané, transitions lissées, meilleure expérience utilisateur et trafic réduit.

```javascript
fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then((response) => response.text())
    .then((html) => {
        container.innerHTML = html;
        history.pushState({}, '', url);
    });
```

### Menu Markdown hiérarchique

Les projets Markdown affichent automatiquement la structure des dossiers :

```text
📂 folder/
    📝 test.md
    📂 subfolder/
        📝 nested.md
📝 index.md
📝 api.md
```

Interactions : clic pour plier/déplier, icône dynamique (📁 ↔ 📂), animations `slideDown` rapides et état ouvert conservé pour les dossiers appartenant à la page active.

```css
.folder-summary {
    cursor: pointer;
    transition: all 0.3s ease;
}

.folder-content {
    animation: slideDown 0.3s ease-out;
    border-left: 2px solid var(--border);
}
```

## API AJAX

Toutes les requêtes SPA envoient l'entête `X-Requested-With: XMLHttpRequest`.

```http
X-Requested-With: XMLHttpRequest
```

Exemple de réponses JSON :

```json
{
    "projects": ["exemple", "docs"]
}
```

```json
{
    "content": "<html>...",
    "current_page": "folder/test.md",
    "project_name": "exemple"
}
```

## Animations et performances

- courbes `cubic-bezier(0.4, 0, 0.2, 1)` pour toutes les transitions
- `fadeIn` et `slideUp` (0.6 s), `slideDown` (0.3 s), `slideLeft` (0.6 s)
- rendu GPU lorsque possible
- mises à jour DOM ciblées pour limiter les reflows
- chargements typiques : first paint < 100 ms, content loaded < 200 ms, ready < 300 ms

## Compatibilité

- Chrome / Edge 90+
- Firefox 88+
- Safari 14+
- Navigateurs modernes supportant Fetch API, History API, animations CSS et éléments `<details>/<summary>`
