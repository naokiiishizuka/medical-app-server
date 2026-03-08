"""Seed orchestrators using per-target directories."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Awaitable, Callable, Dict, Iterable, List

from sqlalchemy.ext.asyncio import AsyncSession

SeedFunc = Callable[[AsyncSession], Awaitable[None]]

ROOT = Path(__file__).resolve().parent
MANIFEST_FILE = ROOT / "manifest.json"


def _load_manifest() -> Dict[str, str]:
    if not MANIFEST_FILE.exists():
        raise RuntimeError(f"Seed manifest not found: {MANIFEST_FILE}")
    with MANIFEST_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data


def _discover_modules(package: str) -> Iterable[str]:
    package_path = ROOT / package
    if not package_path.exists():
        return []
    modules = []
    for path in sorted(package_path.glob("*.py")):
        if path.name == "__init__.py":
            continue
        modules.append(path.stem)
    return modules


def load_seeders() -> Dict[str, List[SeedFunc]]:
    """Build mapping from target name to list of seed callables."""
    manifest = _load_manifest()
    result: Dict[str, List[SeedFunc]] = {}
    for target, package in manifest.items():
        module_names = _discover_modules(package)
        funcs: List[SeedFunc] = []
        for module_name in module_names:
            module = importlib.import_module(
                f"{__name__}.{package}.{module_name}"
            )
            func = getattr(module, "run", None)
            if func is None:
                raise RuntimeError(
                    f"Seed module {package}/{module_name}.py must define async run(session)"
                )
            funcs.append(func)
        result[target] = funcs
    return result


__all__ = ["load_seeders", "SeedFunc"]
