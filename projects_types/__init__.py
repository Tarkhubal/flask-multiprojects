from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Type, Union

from flask import Flask
import yaml

from .base import ProjectType
from .flask_type import FlaskProjectType
from .markdown_type import MarkdownProjectType


TYPE_REGISTRY: Dict[str, Type[ProjectType]] = {
    "flask": FlaskProjectType,
    "markdown": MarkdownProjectType,
}


def _iter_config_files(config_dir: Path) -> Iterable[Path]:
    patterns: List[str] = ["*.yml", "*.yaml"]
    for pattern in patterns:
        for path in sorted(config_dir.glob(pattern)):
            if path.is_file():
                yield path


def load_project_types(app: Flask, configs_dir: Union[str, Path]) -> Dict[str, ProjectType]:
    """Load every configured project type and eagerly register its routes."""
    config_path = Path(configs_dir)
    config_path.mkdir(parents=True, exist_ok=True)

    registered: Dict[str, ProjectType] = {}
    for file_path in _iter_config_files(config_path):
        with file_path.open("r", encoding="utf-8") as handle:
            config_data = yaml.safe_load(handle) or {}

        type_name = config_data.get("type")
        if not type_name:
            print(f"Ignoring {file_path.name}: missing 'type' field")
            continue

        implementation_path = config_data.get("implementation")
        project_type_class: Optional[Type[ProjectType]] = None

        if implementation_path:
            try:
                if ":" in implementation_path:
                    module_name, class_name = implementation_path.split(":", 1)
                else:
                    module_name, class_name = implementation_path.rsplit(".", 1)
                module = import_module(module_name)
                project_type_class = getattr(module, class_name)
            except (ValueError, ImportError, AttributeError) as exc:
                print(
                    f"Ignoring {file_path.name}: unable to import implementation '{implementation_path}' ({exc})"
                )
                continue
        else:
            project_type_class = TYPE_REGISTRY.get(type_name)

        if not project_type_class:
            print(f"Ignoring {file_path.name}: unknown project type '{type_name}'")
            continue

        try:
            project_type = project_type_class(app, config_data)
        except Exception as exc:  # pragma: no cover - defensive logging only
            print(f"Unable to load {file_path.name}: {exc}")
            continue

        if project_type.identifier in registered:
            print(
                f"Skipping {file_path.name}: identifier '{project_type.identifier}' already registered",
            )
            continue

        project_type.ensure_environment()
        project_type.register_routes()
        registered[project_type.identifier] = project_type

    app.extensions["project_types"] = registered
    return registered


def get_project_type(app: Flask, identifier: str) -> Optional[ProjectType]:
    project_types = app.extensions.get("project_types", {})
    return project_types.get(identifier)
