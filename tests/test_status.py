from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from orchestrator.main import print_status


class StatusCommandTests(unittest.TestCase):
    def test_status_does_not_crash_when_memory_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENT_IDENTITY.md").write_text("# AGENT_IDENTITY\n", encoding="utf-8")
            (root / "PERSONALITY.md").write_text("# PERSONALITY\n", encoding="utf-8")
            (root / "BOUNDARIES.md").write_text("# BOUNDARIES\n", encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                print_status(repo_root=root, memory_file=root / "memory" / "missing.jsonl")

            self.assertIn("(no memory history found)", out.getvalue())

    def test_status_prints_recognizable_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENT_IDENTITY.md").write_text("# AGENT_IDENTITY\n", encoding="utf-8")
            (root / "PERSONALITY.md").write_text("# PERSONALITY\n", encoding="utf-8")
            (root / "BOUNDARIES.md").write_text("# BOUNDARIES\n", encoding="utf-8")
            memory = root / "memory" / "improvement_history.jsonl"
            memory.parent.mkdir(parents=True, exist_ok=True)
            memory.write_text('{"timestamp":"2026-01-01T00:00:00Z","intent":"test","summary":"ok"}\n', encoding="utf-8")

            out = io.StringIO()
            with redirect_stdout(out):
                print_status(repo_root=root, memory_file=memory)
            text = out.getvalue()

            self.assertIn("AGENT_IDENTITY", text)
            self.assertIn("BOUNDARIES", text)


if __name__ == "__main__":
    unittest.main()
