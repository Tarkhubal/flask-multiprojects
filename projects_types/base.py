from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask
import yaml


class ProjectType(ABC):
    """Base helper that encapsulates how a project type integrates with the host app."""

    type_name: str = ""

    def __init__(self, app: Flask, raw_config: Dict[str, Any]) -> None:
        if not raw_config:
            raise ValueError("Project type configuration must not be empty")

        self.app = app
        self.raw_config = raw_config

        identifier = raw_config.get("identifier") or raw_config.get("type")
        if not identifier:
            raise ValueError("Project type configuration requires an 'identifier' or 'type' field")
        self.identifier = identifier

        self.label = raw_config.get("label", identifier.title())
        self.description = raw_config.get("description", "")
        self.url_prefix = raw_config.get("url_prefix")

        base_projects_dir = Path(
            app.config.get(
                "PROJECTS_BASE_DIR",
                app.config.get("PROJECTS_DIR", Path(app.root_path) / "projects"),
            )
        )
        root_dir = Path(app.root_path)
        projects_dir_value = raw_config.get("projects_dir")
        if projects_dir_value:
            candidate = Path(projects_dir_value)
            if not candidate.is_absolute():
                candidate = root_dir / candidate
        else:
            candidate = base_projects_dir / identifier
        self.projects_dir = candidate

        self.project_config_filename = raw_config.get("project_config_file", ".mph-config")
        self.default_emoji = raw_config.get("default_emoji", "📦")

    def ensure_environment(self) -> None:
        """Make sure the directory that stores projects for this type exists."""
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def projects_root_exists(self) -> bool:
        return self.projects_dir.exists() and self.projects_dir.is_dir()

    def _project_config_path(self, project_name: str) -> Path:
        return self.projects_dir / project_name / self.project_config_filename

    def load_project_config(self, project_name: str) -> Dict[str, Any]:
        """Load the YAML configuration associated with a single project."""
        config_path = self._project_config_path(project_name)
        if not config_path.exists():
            return {}

        try:
            with config_path.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}
        except Exception as exc:  # pragma: no cover - defensive logging only
            print(f"Error loading config for {self.identifier}:{project_name}: {exc}")
            return {}

    def get_project_display_name(self, project_name: str) -> str:
        project_config = self.load_project_config(project_name)
        return project_config.get("name", project_name)

    def get_project_emoji(self, project_name: str) -> str:
        project_config = self.load_project_config(project_name)
        return project_config.get("emoji", self.default_emoji)

    @abstractmethod
    def list_projects(self) -> List[Dict[str, Any]]:
        """Return the projects handled by this type."""

    @abstractmethod
    def register_routes(self) -> None:
        """Register all HTTP routes that relate to this project type."""