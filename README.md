# Multi-Projects Host

Flask web application for hosting multiple Flask, Markdown, and other configurable project types on a single server.

## Overview

Multi-Projects Host acts as an extensible hub. Each project type has its own logic, routes, and detection rules. Configuration is done via YAML files, which makes it easy to add or adjust new systems (Flask, Markdown, future types like Django, NodeJS, static HTML, etc.).

## Key Features

- simultaneous hosting of Flask, Markdown, Notion, static HTML/CSS/JS, and other custom project types
- dynamic routing driven by YAML configuration in `projects_types_configs`
- native support for Notion exports (Markdown pages and CSV databases)
- single-page application (SPA) navigation with smooth transitions
- collapsible hierarchical menu with dynamic icons
- advanced Markdown rendering (fenced code, tables, toc)
- interactive table display for Notion databases
- responsive interface with GPU-accelerated CSS animations
- custom error pages and client-side theme switching

## Configuration Architecture

YAML files in `projects_types_configs/` describe each project type. They accept the following fields:

- `type`: type identifier (e.g., `flask`, `markdown`, `static`)
- `identifier`: internal key used to reference the type in the application
- `projects_dir`: path (relative or absolute) to the projects folder
- `project_config_file`: name of the configuration file specific to each project (default `.mph-config`)
- `default_emoji`: emoji used if a project doesn't define one
- type-specific fields (e.g., `app_filename` for Flask, `markdown.extensions` for Markdown)
- `implementation` (optional): module:Class path if you provide your own `ProjectType` class

### Adding a New Type

1. Create a class inheriting from `projects_types.base.ProjectType` (e.g., `projects_types/my_type.py`).
2. In this class: implement `list_projects` and `register_routes`, then register the necessary Flask routes.
3. Add a file `projects_types_configs/my_type.yaml` with the corresponding `type` (or `implementation` to your custom class).
4. Restart the application to automatically load the new type.

## Repository Structure

```text
projects-flask-repo/
├── app.py
├── requirements.txt
├── projects/
│   ├── flask/
│   │   └── example/
│   │       └── app.py
│   ├── markdown/
│   │   └── example/
│   │       ├── index.md
│   │       └── ...
│   ├── notion/
│   │   └── my-export/
│   │       ├── index.md
│   │       ├── Database.csv
│   │       └── ...
│   └── static/
│       └── example/
│           ├── index.html
│           ├── style.css
│           └── script.js
├── projects_types/
│   ├── __init__.py
│   ├── base.py
│   ├── flask_type.py
│   ├── markdown_type.py
│   ├── notion_type.py
│   └── static_type.py
├── projects_types_configs/
│   ├── flask.yaml
│   ├── markdown.yaml
│   ├── notion.yaml
│   └── static.yaml
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
│   ├── notion_list.html
│   ├── notion_project.html
│   ├── notion_page.html
│   ├── notion_database.html
│   ├── static_list.html
│   ├── static_project.html
│   ├── debug_spa.html
│   ├── 404.html
│   └── 500.html
└── ...
```

## Installation

```bash
pip install -r requirements.txt
```

## Getting Started

```bash
python app.py
```

The application starts on <http://localhost:5000>.

## Main Routes

- `/` : homepage listing active projects
- `/flask` : list of Flask projects
- `/flask/<project_name>` : Flask project (sub-routes are delegated to the embedded application)
- `/md` : list of Markdown projects
- `/md/<project_name>` : Markdown project homepage
- `/md/<project_name>/<page>` : Markdown page rendering
- `/notion` : list of Notion projects
- `/notion/<project_name>` : Notion project homepage
- `/notion/<project_name>/<page>` : Notion page or database rendering
- `/static` : list of static HTML/CSS/JS projects
- `/static/<project_name>` : static project rendering
- `/static/<project_name>/<path>` : static file serving

## Adding a Flask Project

1. Create a folder in `projects/flask/project_name/`.
2. Create an `app.py` file containing a Flask application named according to `application_attribute` (default `app`).
3. Optional: add a `.mph-config` file to define `name`, `emoji`, etc.

Minimal example:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'welcome to my flask project'

if __name__ == '__main__':
    app.run(debug=True)
```

## Adding a Markdown Project

1. Create a folder in `projects/markdown/project_name/`.
2. Add `.md` files (an `index.md` or `README.md` serves as the automatic homepage).
3. Configure `.mph-config` to hide certain files (`markdown.hidden_files`) or folders (`markdown.hidden_folders`).

## Adding a Notion Project

1. Export your Notion workspace or page (Format: Markdown & CSV).
2. Place the exported folder in `projects/notion/project_name/`.
3. Optional: add a `.mph-config` file to customize the name and emoji.

The application will automatically detect:
- Notion pages (`.md` files) and display them with Markdown rendering
- Notion databases (`.csv` files) and display them as tables
- The hierarchical folder structure

Example `.mph-config` file for a Notion project:

```yaml
name: Project Documentation
emoji: "📓"
description: Export of our Notion workspace
notion:
    hidden_files:
        - drafts/todo.md
    hidden_folders:
        - archives
```

## Adding a Static HTML/CSS/JS Project

1. Create a folder in `projects/static/project_name/`.
2. Add your HTML, CSS, and JavaScript files.
3. Create an `index.html` file as the entry point.
4. Optional: add a `.mph-config` file to customize the name and emoji.

Minimal example:

Create `projects/static/my-site/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Static Site</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Welcome to my static site</h1>
    <script src="script.js"></script>
</body>
</html>
```

Create `projects/static/my-site/.mph-config`:

```yaml
name: My Portfolio
emoji: "🌐"
description: Personal website
```

### Configuration Examples

Example for a Flask project (`projects/flask/blog/.mph-config`):

```yaml
name: Internal Blog
emoji: "🧪"
description: Test Flask application
environment:
    FLASK_ENV: development
    FEATURE_FLAG: search
routes:
    - path: /
      label: Home
    - path: /admin
      label: Administration
```

Example for a Markdown project (`projects/markdown/docs/.mph-config`):

```yaml
name: Product Documentation
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

## Creating a Custom Type (e.g., NodeJS)

1. Create the file `projects_types/node_type.py` with a dedicated class.
2. Define the type in `projects_types_configs/node.yaml` specifying `implementation`.
3. Restart the application to load the new type.

Minimal code snippet for the custom class:

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

Corresponding YAML configuration (`projects_types_configs/node.yaml`):

```yaml
type: node
identifier: node
implementation: projects_types.node_type:NodeProjectType
projects_dir: projects/node
project_config_file: .mph-config
default_emoji: "🟢"
```

## SPA and Hierarchical Navigation

### SPA (Single Page Application)

The `static/js/spa.js` script intercepts clicks on links marked with `data-spa`. The following pages benefit from smooth navigation:

- `/flask`
- `/md`
- all individual Markdown pages

Advantages: near-instant loading, smooth transitions, better user experience, and reduced traffic.

```javascript
fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then((response) => response.text())
    .then((html) => {
        container.innerHTML = html;
        history.pushState({}, '', url);
    });
```

### Hierarchical Markdown Menu

Markdown projects automatically display the folder structure:

```text
📂 folder/
    📝 test.md
    📂 subfolder/
        📝 nested.md
📝 index.md
📝 api.md
```

Interactions: click to collapse/expand, dynamic icon (📁 ↔ 📂), fast `slideDown` animations, and open state preserved for folders belonging to the active page.

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

## AJAX API

All SPA requests send the `X-Requested-With: XMLHttpRequest` header.

```http
X-Requested-With: XMLHttpRequest
```

Example JSON responses:

```json
{
    "projects": ["example", "docs"]
}
```

```json
{
    "content": "<html>...",
    "current_page": "folder/test.md",
    "project_name": "example"
}
```

## Animations and Performance

- `cubic-bezier(0.4, 0, 0.2, 1)` curves for all transitions
- `fadeIn` and `slideUp` (0.6s), `slideDown` (0.3s), `slideLeft` (0.6s)
- GPU rendering when possible
- targeted DOM updates to limit reflows
- typical loading times: first paint < 100ms, content loaded < 200ms, ready < 300ms

## Compatibility

- Chrome / Edge 90+
- Firefox 88+
- Safari 14+
- Modern browsers supporting Fetch API, History API, CSS animations, and `<details>/<summary>` elements
