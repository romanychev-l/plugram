import tomllib
from pathlib import Path

import tomli_w


DEFAULT_CONFIG = {
    "modules": {
        "translate": {"enabled": True},
        "ask": {"enabled": True},
        "tldr": {"enabled": True},
        "fact": {"enabled": True},
        "twin": {"enabled": False},
        "manage": {"enabled": True},
    },
    "llm": {
        "default_model": "deepseek/deepseek-v3.2",
    },
}


class Config:
    def __init__(self, path: Path):
        self.path = path
        self._data: dict = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            with self.path.open("rb") as f:
                self._data = tomllib.load(f)
        else:
            self._data = {}
        self._apply_defaults()

    def _apply_defaults(self) -> None:
        modules = self._data.setdefault("modules", {})
        for name, defaults in DEFAULT_CONFIG["modules"].items():
            modules.setdefault(name, dict(defaults))
        llm = self._data.setdefault("llm", {})
        for k, v in DEFAULT_CONFIG["llm"].items():
            llm.setdefault(k, v)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("wb") as f:
            tomli_w.dump(self._data, f)

    def is_enabled(self, module_name: str) -> bool:
        return bool(
            self._data.get("modules", {}).get(module_name, {}).get("enabled", False)
        )

    def set_enabled(self, module_name: str, enabled: bool) -> None:
        self._data.setdefault("modules", {}).setdefault(module_name, {})[
            "enabled"
        ] = enabled
        self.save()

    @property
    def model(self) -> str:
        return self._data.get("llm", {}).get(
            "default_model", DEFAULT_CONFIG["llm"]["default_model"]
        )
