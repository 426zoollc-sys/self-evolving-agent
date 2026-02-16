#!/usr/bin/env python3
"""Usage: python chat_self.py [optional user message]

If no message is passed as an argument, an interactive prompt is shown.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PERSONALITY_PATH = ROOT / "PERSONALITY.md"
BOUNDARIES_PATH = ROOT / "BOUNDARIES.md"
CHAT_HISTORY_PATH = ROOT / "chat_history.jsonl"
SEPARATOR = "\n\n---\n\n"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _get_user_message(argv: list[str]) -> str:
    if len(argv) > 1:
        return " ".join(argv[1:]).strip()
    return input("Message: ").strip()


def _build_system_prompt(personality: str, boundaries: str, user_message: str) -> str:
    return f"{personality}{SEPARATOR}{boundaries}{SEPARATOR}{user_message}"


def _run_openclaw(system_prompt: str) -> str:
    result = subprocess.run(
        ["openclaw", "agent", "--agent", "self", "--message", system_prompt],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(stderr or f"openclaw failed with code {result.returncode}")
    return result.stdout


def _append_history(user_message: str, system_prompt: str, reply: str) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user_message,
        "system": system_prompt,
        "reply": reply,
    }
    with CHAT_HISTORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        personality = _read_text(PERSONALITY_PATH)
        boundaries = _read_text(BOUNDARIES_PATH)
        user_message = _get_user_message(sys.argv)
        if not user_message:
            print("Error: user message is empty.", file=sys.stderr)
            return 1

        system_prompt = _build_system_prompt(personality, boundaries, user_message)
        reply = _run_openclaw(system_prompt)
        print(reply, end="" if reply.endswith("\n") else "\n")
        _append_history(user_message, system_prompt, reply)
        return 0
    except FileNotFoundError as exc:
        print(f"Missing file: {exc.filename}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"OpenClaw error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
