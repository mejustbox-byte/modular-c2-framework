"""Publication checks with a mocked API; no credentials or network are used."""

import importlib.util
import io
import json
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("publish_release", Path("scripts/publish-release.py"))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

ENV = {
    "GITHUB_REPOSITORY": "mejustbox-byte/modular-c2-framework",
    "GITHUB_SHA": "a" * 40,
    "GITHUB_REF": "refs/heads/main",
    "GITHUB_EVENT_NAME": "push",
    "GITHUB_RUN_ID": "123",
    "GH_RELEASE_TOKEN": "synthetic-placeholder",
}


class ReleaseTests(unittest.TestCase):
    def test_rejects_non_main_without_network(self):
        with (
            patch.dict(release.os.environ, {**ENV, "GITHUB_REF": "refs/heads/other"}, clear=True),
            patch.object(release.urllib.request, "urlopen") as api,
            self.assertRaises(SystemExit),
        ):
            release.main()
        api.assert_not_called()

    def test_publishes_prerelease_at_exact_tested_commit(self):
        response = {
            "draft": False,
            "prerelease": True,
            "target_commitish": ENV["GITHUB_SHA"],
            "html_url": "https://github.com/mejustbox-byte/modular-c2-framework/releases/tag/v0.1.0-rc.1",
        }
        with (
            patch.dict(release.os.environ, ENV, clear=True),
            patch.object(
                release.urllib.request,
                "urlopen",
                side_effect=[
                    urllib.error.HTTPError("synthetic", 404, "missing", {}, None),
                    io.BytesIO(json.dumps(response).encode()),
                ],
            ) as api,
            patch("builtins.print"),
        ):
            release.main()
        payload = json.loads(api.call_args_list[1].args[0].data)
        self.assertTrue(payload["prerelease"])
        self.assertFalse(payload["draft"])
        self.assertEqual(payload["target_commitish"], ENV["GITHUB_SHA"])
        self.assertIn("/blob/v0.1.0-rc.1/INSTALL.md", payload["body"])

    def test_existing_other_commit_cannot_be_overwritten(self):
        response = {"target_commitish": "b" * 40, "prerelease": True}
        with (
            patch.dict(release.os.environ, ENV, clear=True),
            patch.object(
                release.urllib.request,
                "urlopen",
                return_value=io.BytesIO(json.dumps(response).encode()),
            ) as api,
            self.assertRaises(SystemExit),
        ):
            release.main()
        self.assertEqual(api.call_count, 1)
