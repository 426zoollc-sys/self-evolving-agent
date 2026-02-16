from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MEMORY_FILE = REPO_ROOT / "memory" / "improvement_history.jsonl"
SUMMARY_FILES = ["AGENT_IDENTITY.md", "PERSONALITY.md", "BOUNDARIES.md"]


def get_git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return "unavailable"
    branch = result.stdout.strip()
    return branch or "unavailable"


def first_lines(path: Path, count: int = 5) -> list[str]:
    if not path.exists():
        return ["(missing)"]
    lines = []
    with path.open("r", encoding="utf-8") as handle:
        for _ in range(count):
            line = handle.readline()
            if not line:
                break
            lines.append(line.rstrip("\n"))
    return lines or ["(empty)"]


def read_last_memory_entries(path: Path, count: int = 5) -> list[dict]:
    if not path.exists():
        return []
    entries: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                entries.append(value)
    return entries[-count:]


def print_status(repo_root: Path = REPO_ROOT, memory_file: Path = MEMORY_FILE) -> None:
    print("SELF VIEW")
    print(f"Branch: {get_git_branch()}")
    print()

    print("RECENT IMPROVEMENTS")
    items = read_last_memory_entries(memory_file, count=5)
    if not items:
        print("- (no memory history found)")
    else:
        for item in items:
            timestamp = item.get("timestamp", "unknown-time")
            intent = item.get("intent", "unknown-intent")
            summary = item.get("summary", "")
            print(f"- {timestamp} | {intent} | {summary}")
    print()

    for filename in SUMMARY_FILES:
        print(f"{filename} (first 5 lines)")
        for line in first_lines(repo_root / filename, count=5):
            print(line)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Orchestrator entrypoint")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("status", help="Print self view")
    args = parser.parse_args()

    if args.command == "status":
        print_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
