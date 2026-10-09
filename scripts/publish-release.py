"""Publish the tested source candidate from its authorized main merge workflow."""

import json
import os
import tomllib
import urllib.error
import urllib.request
from pathlib import Path


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    commit = os.environ["GITHUB_SHA"]
    if (
        repository != "mejustbox-byte/modular-c2-framework"
        or os.environ["GITHUB_REF"] != "refs/heads/main"
        or os.environ["GITHUB_EVENT_NAME"] != "push"
        or len(commit) != 40
        or any(c not in "0123456789abcdef" for c in commit)
    ):
        raise SystemExit("Release context refused")
    version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
    locked = tomllib.loads(Path("uv.lock").read_text())["package"]
    if version != "0.1.0rc1" or not any(
        p["name"] == "modular-c2-lab" and p["version"] == version for p in locked
    ):
        raise SystemExit("Release version refused")
    tag = "v0.1.0-rc.1"
    base = f"https://api.github.com/repos/{repository}/releases"
    headers = {
        "Authorization": "Bearer " + os.environ["GH_RELEASE_TOKEN"],
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        with urllib.request.urlopen(
            urllib.request.Request(f"{base}/tags/{tag}", headers=headers), timeout=30
        ) as response:
            existing = json.load(response)
        if existing["target_commitish"] != commit or not existing["prerelease"]:
            raise SystemExit("Existing release does not match tested commit")
        print("Matching release already published")
        return
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise SystemExit(f"Release lookup refused: HTTP {error.code}") from None
    body = Path("RELEASE.md").read_text()
    for document in ("INSTALL.md", "VALIDATION.md"):
        body = body.replace(
            f"]({document})", f"](https://github.com/{repository}/blob/{tag}/{document})"
        )
    body += f"\nTested source commit: `{commit}`.\n"
    body += (
        f"[Release CI](https://github.com/{repository}/actions/runs/"
        f"{os.environ['GITHUB_RUN_ID']})\n"
    )
    payload = json.dumps(
        {
            "tag_name": tag,
            "target_commitish": commit,
            "name": "v0.1.0-rc.1 — Isolated Mock Lab",
            "body": body,
            "draft": False,
            "prerelease": True,
        }
    ).encode()
    headers["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(
            urllib.request.Request(base, data=payload, headers=headers, method="POST"),
            timeout=30,
        ) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f"Release publication refused: HTTP {error.code}") from None
    if result["draft"] or not result["prerelease"] or result["target_commitish"] != commit:
        raise SystemExit("Unexpected release result")
    print("Release candidate published: " + result["html_url"])


if __name__ == "__main__":
    main()
