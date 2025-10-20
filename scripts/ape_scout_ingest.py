"""Command-line entry point for Ape Scout ingestion."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime

from refiners.ape_scout.config import get_settings
from refiners.ape_scout.services import run_ingestion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect ApeWisdom data and store it in the local database.")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Ingestion date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO if not args.verbose else logging.DEBUG)

    target_date = None
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()

    settings = get_settings()
    if not settings.polygon_api_key:
        raise SystemExit("POLYGON_API_KEY 未设置，无法继续。")

    run_ingestion(target_date=target_date, settings=settings)


if __name__ == "__main__":
    main()
