from pathlib import Path
from typing import Dict, List

from flask import Flask, render_template

from projects_types import load_project_types


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

BASE_PATH = Path(__file__).parent
app.config['PROJECTS_DIR'] = BASE_PATH / 'projects'
app.config['PROJECTS_BASE_DIR'] = app.config['PROJECTS_DIR']
app.config['PROJECT_TYPE_CONFIGS_DIR'] = BASE_PATH / 'projects_types_configs'

project_types = load_project_types(app, app.config['PROJECT_TYPE_CONFIGS_DIR'])


def _projects_for(identifier: str) -> List[Dict[str, str]]:
    project_type = project_types.get(identifier)
    if not project_type:
        return []
    return project_type.list_projects()


@app.route('/')
def index():
    """homepage with all projects"""
    flask_projects = _projects_for('flask')
    md_projects = _projects_for('markdown')
    return render_template('index.html',
                           flask_projects=flask_projects,
                           md_projects=md_projects)


@app.errorhandler(404)
def not_found(e):
    """custom 404 page"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """custom 500 page"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    for project_type in project_types.values():
        project_type.ensure_environment()
    app.run(debug=True, host='0.0.0.0', port=5000)
