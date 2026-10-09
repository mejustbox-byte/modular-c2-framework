"""Real Firefox UI and native NSS mTLS in the laboratory's network namespace."""

import json
import subprocess
from pathlib import Path

from playwright.sync_api import Error, expect, sync_playwright

ROOT = Path("/run/lab")
ORIGIN = "https://127.0.0.1:8443"


def profile(name, actor=None, trusted=True):
    directory = ROOT / name
    directory.mkdir(mode=0o700)

    def run(*args):
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    run("certutil", "-N", "-d", f"sql:{directory}", "--empty-password")
    if trusted:
        run(
            "certutil",
            "-A",
            "-d",
            f"sql:{directory}",
            "-n",
            "synthetic-ca",
            "-t",
            "C,,",
            "-i",
            str(ROOT / "ca.crt"),
        )
    if actor:
        bundle = directory / "client.p12"
        run(
            "openssl",
            "pkcs12",
            "-export",
            "-in",
            str(ROOT / f"{actor}.crt"),
            "-inkey",
            str(ROOT / f"{actor}.key"),
            "-out",
            str(bundle),
            "-passout",
            "pass:",
        )
        run("pk12util", "-i", str(bundle), "-d", f"sql:{directory}", "-W", "")
        bundle.unlink()
    return directory


with sync_playwright() as playwright:

    def launch(name, actor=None, trusted=True):
        return playwright.firefox.launch_persistent_context(
            str(profile(name, actor, trusted)),
            headless=True,
            ignore_https_errors=False,
            firefox_user_prefs={"security.default_personal_cert": "Select Automatically"},
        )

    for name, actor, trusted in [("no-client", None, True), ("untrusted-server", "viewer", False)]:
        context = launch(name, actor, trusted)
        try:
            try:
                context.pages[0].goto(ORIGIN, timeout=10000)
            except Error:
                pass
            else:
                raise AssertionError(f"{name}: TLS unexpectedly accepted")
        finally:
            context.close()

    for actor in ["viewer", "operator", "admin"]:
        context = launch(actor, actor)
        try:
            page = context.pages[0]
            errors = []
            page.on("pageerror", lambda error, captured=errors: captured.append(str(error)))
            response = page.goto(ORIGIN, timeout=15000)
            assert response.status == 200
            expect(page.locator("#identity")).to_contain_text(actor)
            expect(page.get_by_role("heading", name="Mock Lab", exact=True)).to_be_visible()
            if actor == "viewer":
                expect(page.get_by_role("button", name="Ping", exact=True)).to_be_disabled()
                expect(page.locator("#membership")).to_be_hidden()
            else:
                expect(page.get_by_role("button", name="Ping", exact=True)).to_be_enabled()
            page.get_by_role("button", name="Статус", exact=True).click()
            expect(page.locator("#result")).to_contain_text("stopped")
            page.get_by_role("button", name="Обновить журнал", exact=True).click()
            expect(page.locator("#result")).to_contain_text("audit_records")
            assert len(json.loads(page.locator("#events").inner_text())) > 0
            if actor == "admin":
                expect(page.locator("#membership")).to_be_visible()
                page.locator("#target").select_option("viewer")
                page.locator("#role").select_option("operator")
                page.get_by_role("button", name="Применить", exact=True).click()
                expect(page.locator("#result")).to_contain_text("viewer")
                page.locator("#role").select_option("viewer")
                page.get_by_role("button", name="Применить", exact=True).click()
                expect(page.locator("#result")).to_contain_text("viewer")
            page.screenshot(path=str(ROOT / f"{actor}.png"), full_page=True)
            assert not errors, errors
            print(f"Firefox native mTLS UI: {actor} passed", flush=True)
        finally:
            context.close()
    print("Real browser acceptance passed; absent client and untrusted CA refused.", flush=True)
