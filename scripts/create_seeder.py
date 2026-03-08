#!/usr/bin/env python3
"""Create a new seeder template (seed_<name>.py)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SEEDERS_ROOT = Path("src/infrastructure/main/db/seeders")
MANIFEST_FILE = SEEDERS_ROOT / "manifest.json"
TEMPLATE = '''"""Seed data for the {target} target."""

from sqlalchemy.ext.asyncio import AsyncSession


async def run(session: AsyncSession) -> None:
    """Populate data for the '{target}' seed target."""
    # TODO: implement seed logic
    return None
'''

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a seed file under a target directory")
    parser.add_argument("target", help="Seed target (e.g., default, test)")
    parser.add_argument("name", help="Seeder file name (without .py)")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing seeder if it already exists",
    )
    return parser.parse_args()


def validate_name(name: str) -> str:
    if not NAME_PATTERN.match(name):
        raise SystemExit(f"Seed name must match '[a-z][a-z0-9_]*'. Got: {name}")
    return name


def create_seeder(target: str, name: str, overwrite: bool) -> Path:
    target_dir = SEEDERS_ROOT / target
    if not target_dir.exists():
        raise SystemExit(f"Seed target '{target}' does not exist under {SEEDERS_ROOT}.")
    filename = f"{name}.py"
    path = target_dir / filename
    if path.exists() and not overwrite:
        raise SystemExit(f"{path} already exists. Use --overwrite to replace it.")
    target_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(target=target), encoding="utf-8")
    return path


def main() -> None:
    args = parse_args()
    target = validate_name(args.target)
    name = validate_name(args.name)
    path = create_seeder(target, name, args.overwrite)
    print(f"Created seeder: {path}")


if __name__ == "__main__":
    main()
