from __future__ import annotations

import importlib.util
from typing import Any, Dict, List

from flask import abort, render_template
from werkzeug.exceptions import NotFound

from .base import ProjectType


class FlaskProjectType(ProjectType):
    type_name = "flask"

    def __init__(self, app, raw_config: Dict[str, Any]) -> None:
        super().__init__(app, raw_config)
        self.app_filename = raw_config.get("app_filename", "app.py")
        self.application_attribute = raw_config.get("application_attribute", "app")
        self.module_prefix = raw_config.get(
            "module_prefix", f"{self.identifier}_projects"
        )

    def list_projects(self) -> List[Dict[str, Any]]:
        if not self.projects_root_exists():
            return []

        projects: List[Dict[str, Any]] = []
        for directory in sorted(self.projects_dir.iterdir()):
            if directory.is_dir() and (directory / self.app_filename).exists():
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

        app.add_url_rule(
            "/flask",
            endpoint="flask_list",
            view_func=self._flask_list_view,
        )

        app.add_url_rule(
            "/flask/<project_name>",
            defaults={"subpath": ""},
            endpoint="flask_project",
            view_func=self._flask_project_view,
            strict_slashes=False,
        )

        app.add_url_rule(
            "/flask/<project_name>/<path:subpath>",
            view_func=self._flask_project_view,
        )

    def _flask_list_view(self):
        projects = self.list_projects()
        return render_template("flask_list.html", projects=projects)

    def _flask_project_view(self, project_name: str, subpath: str = ""):
        if not self._project_exists(project_name):
            abort(404)

        project_app = self._load_flask_app(project_name)
        if project_app is None:
            abort(500)

        request_path = f"/{subpath}" if subpath else "/"
        with project_app.test_request_context(request_path):
            try:
                return project_app.full_dispatch_request()
            except NotFound:
                abort(404)

    def _project_exists(self, project_name: str) -> bool:
        project_directory = self.projects_dir / project_name
        return project_directory.is_dir() and (project_directory / self.app_filename).exists()

    def _load_flask_app(self, project_name: str):
        module_path = self.projects_dir / project_name / self.app_filename
        if not module_path.exists():
            return None

        spec = importlib.util.spec_from_file_location(
            f"{self.module_prefix}.{project_name}", module_path
        )
        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # pragma: no cover - defensive logging only
            print(f"Error loading Flask project {project_name}: {exc}")
            return None

        flask_app = getattr(module, self.application_attribute, None)
        return flask_app
