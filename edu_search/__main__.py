"""Search local educational text documents from the command line."""

from __future__ import annotations

import argparse

from .engine import SearchEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="Search a directory of educational .txt files.")
    parser.add_argument("directory", help="directory containing UTF-8 .txt resources")
    parser.add_argument("query", nargs="+", help="search terms")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    try:
        engine = SearchEngine.from_directory(args.directory)
        results = engine.search(" ".join(args.query), limit=args.limit)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if not results:
        print("No matching resources.")
        return 0
    for result in results:
        print(f"{result.title} [{result.document_id}] (score {result.score:.5f})")
        print(f"  {result.snippet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
