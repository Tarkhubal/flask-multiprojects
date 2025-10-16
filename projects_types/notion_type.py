from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import abort, redirect, render_template, url_for
import markdown

from .base import ProjectType


class NotionProjectType(ProjectType):
    type_name = "notion"

    def __init__(self, app, raw_config: Dict[str, Any]) -> None:
        super().__init__(app, raw_config)
        markdown_config = raw_config.get("markdown", {})
        self.markdown_extensions = markdown_config.get(
            "extensions", ["fenced_code", "tables", "toc"]
        )
        self.markdown_extension_configs = markdown_config.get(
            "extension_configs", {}
        )

    def list_projects(self) -> List[Dict[str, Any]]:
        if not self.projects_root_exists():
            return []

        projects: List[Dict[str, Any]] = []
        for directory in sorted(self.projects_dir.iterdir()):
            if directory.is_dir():
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
            "/notion",
            endpoint="notion_list",
            view_func=self._notion_list_view,
        )

        app.add_url_rule(
            "/notion/<project_name>",
            endpoint="notion_project",
            view_func=self._notion_project_view,
            strict_slashes=False,
        )

        app.add_url_rule(
            "/notion/<project_name>/<path:page>",
            endpoint="notion_page",
            view_func=self._notion_page_view,
        )

    def _notion_list_view(self):
        projects = self.list_projects()
        return render_template("notion_list.html", projects=projects)

    def _notion_project_view(self, project_name: str):
        if not self._project_exists(project_name):
            abort(404)

        default_file = self._resolve_notion_page(project_name, "")
        if default_file:
            default_path = Path(default_file).with_suffix("")
            return redirect(
                url_for(
                    "notion_page", project_name=project_name, page=default_path.as_posix()
                )
            )

        files = self._gather_notion_files(project_name)
        return render_template(
            "notion_project.html",
            project_name=project_name,
            files=files,
        )

    def _notion_page_view(self, project_name: str, page: str):
        if not self._project_exists(project_name):
            abort(404)

        resolved = self._resolve_notion_page(project_name, page)
        if not resolved:
            abort(404)

        notion_file = self.projects_dir / project_name / resolved
        if not notion_file.exists() or not notion_file.is_file():
            abort(404)

        # Check if it's a CSV file (Notion database export)
        if notion_file.suffix.lower() == ".csv":
            csv_data = self._parse_csv_file(notion_file)
            file_tree = self._build_file_tree(project_name)
            project_config = self.load_project_config(project_name)

            return render_template(
                "notion_database.html",
                project_name=project_name,
                project_display_name=self.get_project_display_name(project_name),
                project_emoji=self.get_project_emoji(project_name),
                csv_data=csv_data,
                file_tree=file_tree,
                current_page=resolved,
                config=project_config,
            )
        
        # Otherwise, treat it as a Markdown file
        with notion_file.open("r", encoding="utf-8") as handle:
            content = handle.read()

        html_content = markdown.markdown(
            content,
            extensions=self.markdown_extensions,
            extension_configs=self.markdown_extension_configs,
        )

        file_tree = self._build_file_tree(project_name)
        project_config = self.load_project_config(project_name)

        return render_template(
            "notion_page.html",
            project_name=project_name,
            project_display_name=self.get_project_display_name(project_name),
            project_emoji=self.get_project_emoji(project_name),
            content=html_content,
            file_tree=file_tree,
            current_page=resolved,
            config=project_config,
        )

    def _parse_csv_file(self, csv_path: Path) -> Dict[str, Any]:
        """Parse a CSV file and return headers and rows."""
        headers = []
        rows = []
        
        try:
            with csv_path.open("r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, [])
                rows = list(reader)
        except Exception as e:
            print(f"Error parsing CSV file {csv_path}: {e}")
        
        return {
            "filename": csv_path.name,
            "headers": headers,
            "rows": rows,
        }

    def _project_exists(self, project_name: str) -> bool:
        project_directory = self.projects_dir / project_name
        return project_directory.is_dir()

    def _gather_notion_files(self, project_name: str) -> List[str]:
        project_directory = self.projects_dir / project_name
        if not project_directory.exists():
            return []

        project_config = self.load_project_config(project_name)
        hidden_files = set(
            project_config.get("notion", {}).get("hidden_files", [])
        )

        notion_files: List[str] = []
        for file_path in project_directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in [".md", ".csv"]:
                relative_path = file_path.relative_to(project_directory)
                relative_str = str(relative_path).replace("\\", "/")
                if relative_str not in hidden_files:
                    notion_files.append(relative_str)

        return sorted(notion_files)

    def _build_file_tree(self, project_name: str) -> Dict[str, Any]:
        project_directory = self.projects_dir / project_name
        if not project_directory.exists():
            return {}

        project_config = self.load_project_config(project_name)
        hidden_files = set(
            project_config.get("notion", {}).get("hidden_files", [])
        )
        hidden_folders = set(
            project_config.get("notion", {}).get("hidden_folders", [])
        )

        def build_tree(path: Path, base_path: Path, current_path: str = "") -> Dict[str, Any]:
            tree: Dict[str, Any] = {"files": [], "folders": {}}
            try:
                items = sorted(
                    path.iterdir(), key=lambda element: (not element.is_file(), element.name.lower())
                )
            except PermissionError:
                return tree

            for item in items:
                if item.is_file() and item.suffix.lower() in [".md", ".csv"]:
                    relative = item.relative_to(base_path)
                    relative_str = str(relative).replace("\\", "/")
                    if relative_str not in hidden_files:
                        slug = str(relative.with_suffix("")).replace("\\", "/")
                        file_type = "database" if item.suffix.lower() == ".csv" else "page"
                        tree["files"].append(
                            {
                                "name": item.name,
                                "path": relative_str,
                                "slug": slug,
                                "type": file_type,
                            }
                        )
                elif item.is_dir():
                    folder_name = item.name
                    folder_path = f"{current_path}/{folder_name}".lstrip("/")
                    if folder_name not in hidden_folders and folder_path not in hidden_folders:
                        tree["folders"][folder_name] = build_tree(item, base_path, folder_path)

            return tree

        return build_tree(project_directory, project_directory)

    def _resolve_notion_page(self, project_name: str, page: str) -> Optional[str]:
        project_directory = self.projects_dir / project_name
        normalized = page.strip("/")

        if not normalized:
            return self._default_notion_file(project_name, Path("."))

        candidate = project_directory / normalized
        if candidate.is_file() and candidate.suffix.lower() in [".md", ".csv"]:
            return str(candidate.relative_to(project_directory).as_posix())

        if candidate.suffix.lower() not in [".md", ".csv"]:
            parent = candidate.parent if candidate.parent != project_directory else project_directory
            stem = candidate.name
            if parent.exists():
                for file_path in parent.iterdir():
                    if (
                        file_path.is_file()
                        and file_path.suffix.lower() in [".md", ".csv"]
                        and file_path.stem == stem
                    ):
                        return str(file_path.relative_to(project_directory).as_posix())

        if candidate.exists() and candidate.is_dir():
            return self._default_notion_file(project_name, Path(normalized))

        return None

    def _default_notion_file(self, project_name: str, relative_dir: Path) -> Optional[str]:
        project_directory = self.projects_dir / project_name
        target = project_directory / relative_dir

        if not target.exists() or not target.is_dir():
            return None

        notion_files = [
            item for item in target.iterdir() 
            if item.is_file() and item.suffix.lower() in [".md", ".csv"]
        ]
        if not notion_files:
            return None

        for candidate in notion_files:
            if candidate.name.lower() == "readme.md":
                return str((relative_dir / candidate.name).as_posix()).lstrip("./")

        for candidate in notion_files:
            if candidate.name.lower() == "index.md":
                return str((relative_dir / candidate.name).as_posix()).lstrip("./")

        chosen = sorted(notion_files, key=lambda element: element.name.lower())[0]
        return str((relative_dir / chosen.name).as_posix()).lstrip("./")
