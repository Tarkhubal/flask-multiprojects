from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from flask import abort, render_template, send_from_directory

from .base import ProjectType


class StaticProjectType(ProjectType):
    type_name = "static"

    def list_projects(self) -> List[Dict[str, Any]]:
        if not self.projects_root_exists():
            return []

        projects: List[Dict[str, Any]] = []
        for directory in sorted(self.projects_dir.iterdir()):
            if directory.is_dir():
                # Check if the directory contains an index.html file
                index_file = directory / "index.html"
                if index_file.is_file():
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
            "/static-projects",
            endpoint="static_list",
            view_func=self._static_list_view,
        )

        app.add_url_rule(
            "/static-projects/<project_name>/",
            endpoint="static_project",
            view_func=self._static_project_view,
        )

        app.add_url_rule(
            "/static-projects/<project_name>/<path:filepath>",
            endpoint="static_file",
            view_func=self._static_file_view,
        )

    def _static_list_view(self):
        projects = self.list_projects()
        return render_template("static_list.html", projects=projects)

    def _static_project_view(self, project_name: str):
        if not self._project_exists(project_name):
            abort(404)

        # Serve the index.html file
        project_directory = self.projects_dir / project_name
        index_file = project_directory / "index.html"
        
        if not index_file.is_file():
            abort(404)

        return send_from_directory(project_directory, "index.html")

    def _static_file_view(self, project_name: str, filepath: str):
        if not self._project_exists(project_name):
            abort(404)

        project_directory = self.projects_dir / project_name
        file_path = project_directory / filepath

        # Security check: ensure the file is within the project directory
        try:
            file_path.resolve().relative_to(project_directory.resolve())
        except ValueError:
            abort(404)

        if not file_path.is_file():
            abort(404)

        return send_from_directory(project_directory, filepath)

    def _project_exists(self, project_name: str) -> bool:
        project_directory = self.projects_dir / project_name
        index_file = project_directory / "index.html"
        return project_directory.is_dir() and index_file.is_file()
