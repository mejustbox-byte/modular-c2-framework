"""Offline development smoke checks. No services or network operations."""

import re
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    "README.md",
    "ROADMAP.md",
    "INSTALL.md",
    "CHANGELOG.md",
    "LICENSE",
    "SECURITY.md",
    "ARCHITECTURE.md",
    "THREAT-MODEL.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "TECH-STACK.md",
)


class DevelopmentSmoke(unittest.TestCase):
    def test_runtime_and_project_metadata(self):
        pin = (ROOT / ".python-version").read_text().strip()
        self.assertEqual(".".join(map(str, sys.version_info[:3])), pin)
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())
        self.assertEqual(metadata["project"]["name"], "modular-c2-lab")
        self.assertEqual(metadata["project"]["dependencies"], [])
        self.assertEqual(metadata["dependency-groups"]["dev"], ["ruff==0.16.10"])

    def test_documents_and_local_links(self):
        for name in DOCUMENTS:
            with self.subTest(document=name):
                path = ROOT / name
                self.assertTrue(path.is_file(), name)
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.strip(), name)
                if path.suffix != ".md":
                    continue
                self.assertEqual(text.count("```") % 2, 0, f"Unclosed fence: {name}")
                for target in re.findall(r"\]\(([^)]+)\)", text):
                    if not target.startswith(("https://", "http://", "#")):
                        self.assertTrue((ROOT / target.split("#")[0]).is_file(), target)

    def test_workspace(self):
        result = subprocess.run(
            ["bash", "scripts/check-workspace.sh"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_common_accidental_secrets(self):
        # Inspect tracked and non-ignored project files; never inspect environment values.
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            timeout=15,
        )
        patterns = (
            re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
            re.compile(rb"gh[pousr]_" + rb"[A-Za-z0-9]{36,}"),
            re.compile(rb"github_pat_" + rb"[A-Za-z0-9_]{40,}"),
            re.compile(rb"AKIA" + rb"[A-Z0-9]{16}"),
        )
        for raw in set(result.stdout.split(b"\0")) - {b""}:
            name = raw.decode("utf-8")
            path = ROOT / name
            with self.subTest(file=name):
                self.assertFalse(path.is_symlink(), "Project symlinks need explicit review")
                self.assertFalse(path.name == ".env", "Environment file must not be committed")
                self.assertFalse(
                    path.name.startswith(".env.") and path.name != ".env.example",
                    "Environment file must not be committed",
                )
                self.assertNotIn(path.suffix, (".pem", ".key"), "Key file needs explicit review")
                content = path.read_bytes()
                for pattern in patterns:
                    self.assertIsNone(pattern.search(content), f"Possible secret in {name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
