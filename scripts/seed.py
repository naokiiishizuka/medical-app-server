#!/usr/bin/env python3
"""Database seeding entrypoint."""

from __future__ import annotations

import argparse
import asyncio
import logging
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.main.db.seeders import SeedFunc, load_seeders
from src.infrastructure.main.db.session import get_session_factory

LOGGER = logging.getLogger("seed")

SEEDERS: Dict[str, List[SeedFunc]] = load_seeders()
DEFAULT_TARGET = "default" if "default" in SEEDERS else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed database with initial data")
    if DEFAULT_TARGET:
        parser.add_argument(
            "target",
            choices=sorted(SEEDERS.keys()),
            nargs="?",
            default=DEFAULT_TARGET,
            help="Which seed set to run",
        )
    else:
        parser.add_argument(
            "target",
            choices=sorted(SEEDERS.keys()),
            help="Which seed set to run",
        )
    return parser.parse_args()


async def run_seed(target: str) -> None:
    factory = get_session_factory()
    seed_funcs = SEEDERS[target]
    async with factory() as session:
        for func in seed_funcs:
            async with session.begin():
                LOGGER.info("Seeding %s via %s", target, func.__module__)
                await func(session)
        LOGGER.info("Seeding %s data completed", target)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    asyncio.run(run_seed(args.target))


if __name__ == "__main__":
    main()
