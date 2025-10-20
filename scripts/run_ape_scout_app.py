"""Start the Ape Scout FastAPI dashboard."""

from __future__ import annotations

import argparse
import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Ape Scout dashboard server.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    uvicorn.run("refiners.ape_scout.app:create_app", factory=True, host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
