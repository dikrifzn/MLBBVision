from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_VERSION = "1.0.0"
DEFAULT_IMAGE_WIDTH = 1600
DEFAULT_IMAGE_HEIGHT = 900


def _rect(x: int, y: int, w: int, h: int) -> dict[str, int]:
    return {"x": x, "y": y, "w": w, "h": h}


def _normalize_image_key(image_path: str) -> str:
    if not image_path:
        return ""

    return str(Path(image_path).resolve()).replace("\\", "/")


def _build_template_variables() -> dict[str, dict[str, int]]:
    variables: dict[str, dict[str, int]] = {}

    team_fields: tuple[tuple[str, tuple[int, int]], ...] = (
        ("hero", (118, 118)),
        ("name", (265, 35)),
        ("gold", (70, 24)),
        ("kda", (90, 24)),
        ("score", (70, 24)),
        ("level", (35, 25)),
        # ("damage", (210, 18)),
        # ("taken", (210, 18)),
        # ("tower", (210, 18)),
    )

    for team in ("blue", "red"):
        for field_name, (width, height) in team_fields:
            for player_index in range(1, 6):
                variable_name = f"{field_name}_{team}_{player_index}"
                variables[variable_name] = _rect(0, 0, width, height)

        for player_index in range(1, 6):
            for item_index in range(1, 7):
                variable_name = f"item{item_index}_{team}_{player_index}"
                variables[variable_name] = _rect(0, 0, 65, 65)

    variables["match_duration"] = _rect(0, 0, 80, 32)
    variables["blue_team_score"] = _rect(0, 0, 105, 75)
    variables["red_team_score"] = _rect(0, 0, 105, 75)
    variables["victory"] = _rect(0, 0, 464, 98)

    return variables


TEMPLATE_VARIABLES = _build_template_variables()


class JsonManager:

    def __init__(self, filename: str = "coordinates.json") -> None:
        self.path = Path(filename)

    def load_state(self) -> dict[str, Any]:
        if not self.path.exists():
            state = self._empty_state()
            self._write_state(state)
            return state

        try:
            with self.path.open("r", encoding="utf-8") as file_handle:
                raw_data: Any = json.load(file_handle)
        except (OSError, json.JSONDecodeError):
            state = self._empty_state()
            self._write_state(state)
            return state

        if not isinstance(raw_data, dict):
            state = self._empty_state()
            self._write_state(state)
            return state

        if "variables" in raw_data and isinstance(raw_data.get("variables"), dict):
            state = self._normalize_state(raw_data)
        else:
            state = self._migrate_legacy_state(raw_data)

        registry = self._normalize_registry(raw_data.get("images", {}))
        state["images"] = registry

        active_key = _normalize_image_key(state["image"].get("path", ""))
        if active_key and active_key in registry:
            state = self._merge_snapshot(state, registry[active_key], registry)

        self._write_state(state)
        return state

    def load(self) -> dict[str, list[int]]:
        state = self.load_state()
        variables = state.get("variables", {})
        if not isinstance(variables, dict):
            return {}

        return {
            name: [
                int(value["x"]),
                int(value["y"]),
                int(value["w"]),
                int(value["h"]),
            ]
            for name, value in variables.items()
            if isinstance(name, str) and isinstance(value, dict)
        }

    def save_state(self, image_width: int, image_height: int, variables: dict[str, list[int]]) -> None:
        self.save_state_with_image_path(image_width, image_height, "", variables)

    def save_state_with_image_path(
        self,
        image_width: int,
        image_height: int,
        image_path: str,
        variables: dict[str, list[int]],
    ) -> None:
        normalized_variables = self._normalize_variables(variables)
        snapshot = {
            "version": DEFAULT_VERSION,
            "image": {
                "width": int(image_width),
                "height": int(image_height),
                "path": str(image_path),
            },
            "variables": self._apply_template(normalized_variables),
        }

        current_state = self.load_state()
        registry = self._normalize_registry(current_state.get("images", {}))
        image_key = _normalize_image_key(image_path)
        if image_key:
            registry[image_key] = dict(snapshot)

        snapshot["images"] = registry
        self._write_state(snapshot)

    def load_state_for_image(self, image_path: str) -> dict[str, Any] | None:
        state = self.load_state()
        registry = self._normalize_registry(state.get("images", {}))
        image_key = _normalize_image_key(image_path)
        if not image_key:
            return None

        snapshot = registry.get(image_key)
        if snapshot is None:
            return None

        return self._merge_snapshot(state, snapshot, registry)

    def save(self, data: dict[str, list[int]]) -> None:
        self.save_state(0, 0, data)

    def _empty_state(self) -> dict[str, Any]:
        return {
            "version": DEFAULT_VERSION,
            "image": {
                "width": DEFAULT_IMAGE_WIDTH,
                "height": DEFAULT_IMAGE_HEIGHT,
                "path": "",
            },
            "variables": self._apply_template({}),
            "images": {},
        }

    def _normalize_state(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        image_data = raw_data.get("image", {})
        variables_data = raw_data.get("variables", {})

        image_width = self._to_int(image_data.get("width") if isinstance(image_data, dict) else 0)
        image_height = self._to_int(image_data.get("height") if isinstance(image_data, dict) else 0)

        return {
            "version": str(raw_data.get("version", DEFAULT_VERSION)),
            "image": {
                "width": image_width if image_width > 0 else DEFAULT_IMAGE_WIDTH,
                "height": image_height if image_height > 0 else DEFAULT_IMAGE_HEIGHT,
                "path": str(image_data.get("path", "")) if isinstance(image_data, dict) else "",
            },
            "variables": self._apply_template(
                self._normalize_variables(variables_data if isinstance(variables_data, dict) else {})
            ),
            "images": {},
        }

    def _migrate_legacy_state(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        variables: dict[str, list[int]] = {}

        for name, value in raw_data.items():
            if isinstance(name, str) and isinstance(value, list) and len(value) == 4:
                try:
                    variables[name] = [
                        int(value[0]),
                        int(value[1]),
                        int(value[2]),
                        int(value[3]),
                    ]
                except (TypeError, ValueError):
                    continue

        return {
            "version": DEFAULT_VERSION,
            "image": {
                "width": DEFAULT_IMAGE_WIDTH,
                "height": DEFAULT_IMAGE_HEIGHT,
                "path": "",
            },
            "variables": self._apply_template(self._normalize_variables(variables)),
            "images": {},
        }

    def _normalize_registry(self, raw_registry: Any) -> dict[str, dict[str, Any]]:
        if not isinstance(raw_registry, dict):
            return {}

        normalized_registry: dict[str, dict[str, Any]] = {}
        for image_key, snapshot in raw_registry.items():
            if not isinstance(image_key, str) or not isinstance(snapshot, dict):
                continue

            normalized_snapshot = self._normalize_snapshot(snapshot)
            if normalized_snapshot is not None:
                normalized_registry[image_key] = normalized_snapshot

        return normalized_registry

    def _normalize_snapshot(self, raw_snapshot: dict[str, Any]) -> dict[str, Any] | None:
        image_data = raw_snapshot.get("image", {})
        variables_data = raw_snapshot.get("variables", {})

        if not isinstance(image_data, dict):
            return None

        image_width = self._to_int(image_data.get("width"))
        image_height = self._to_int(image_data.get("height"))
        image_path = str(image_data.get("path", ""))

        return {
            "version": str(raw_snapshot.get("version", DEFAULT_VERSION)),
            "image": {
                "width": image_width if image_width > 0 else DEFAULT_IMAGE_WIDTH,
                "height": image_height if image_height > 0 else DEFAULT_IMAGE_HEIGHT,
                "path": image_path,
            },
            "variables": self._apply_template(
                self._normalize_variables(variables_data if isinstance(variables_data, dict) else {})
            ),
        }

    def _merge_snapshot(
        self,
        base_state: dict[str, Any],
        snapshot: dict[str, Any],
        registry: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        merged_state = {
            "version": str(snapshot.get("version", base_state.get("version", DEFAULT_VERSION))),
            "image": snapshot.get("image", base_state.get("image", {})),
            "variables": snapshot.get("variables", base_state.get("variables", {})),
            "images": registry,
        }
        return merged_state

    def _normalize_variables(self, raw_variables: dict[str, Any]) -> dict[str, dict[str, int]]:
        normalized_variables: dict[str, dict[str, int]] = {}

        for name, value in raw_variables.items():
            if not isinstance(name, str):
                continue

            coordinates = self._extract_coordinates(value)
            if coordinates is None:
                continue

            normalized_variables[name] = coordinates

        return normalized_variables

    def _apply_template(self, input_variables: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
        templated_variables: dict[str, dict[str, int]] = {}

        for name, default_rect in TEMPLATE_VARIABLES.items():
            value = input_variables.get(name)
            if value is None:
                templated_variables[name] = dict(default_rect)
                continue

            width = int(value["w"])
            height = int(value["h"])

            if name.startswith("item"):
                width = int(default_rect["w"])
                height = int(default_rect["h"])

            templated_variables[name] = {
                "x": int(value["x"]),
                "y": int(value["y"]),
                "w": width,
                "h": height,
            }

        return templated_variables

    def _extract_coordinates(self, value: Any) -> dict[str, int] | None:
        if isinstance(value, list) and len(value) == 4:
            try:
                return {
                    "x": int(value[0]),
                    "y": int(value[1]),
                    "w": int(value[2]),
                    "h": int(value[3]),
                }
            except (TypeError, ValueError):
                return None

        if isinstance(value, dict):
            try:
                return {
                    "x": int(value["x"]),
                    "y": int(value["y"]),
                    "w": int(value["w"]),
                    "h": int(value["h"]),
                }
            except (KeyError, TypeError, ValueError):
                return None

        return None

    def _to_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _write_state(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8", newline="\n") as file_handle:
            json.dump(data, file_handle, indent=2)
