# Technical Stack

## Runtime and tooling

| Area | Choice | Purpose |
| --- | --- | --- |
| Runtime | CPython 3.12.15 | Standard-library service and mock laboratory |
| Dependency management | uv 0.12.24 with `uv.lock` | Locked, repeatable development installation |
| Lint and format | Ruff 0.16.10 | Consistent static checks and formatting |
| State and audit | SQLite and structured JSON | Bounded local state and offline audit journal |
| API and UI | Python standard library, TLS 1.3, packaged HTML/CSS/JavaScript | Small authenticated laboratory interface |
| Container runtime | Docker Engine on Linux | Disposable, network-isolated integration testing |
| CI | GitHub Actions on Ubuntu 24.04 | Automated checks with read-only permissions by default |

The service is a controlled mock laboratory. It does not provide a public
production command-and-control service. Network-facing tests require the
containerized acceptance workflow described in [INSTALL.md](INSTALL.md).

## Reproducible checks

Run the project setup and offline checks from a clean checkout:

```sh
bash scripts/setup-cloud.sh
```

The check validates locked dependencies, project metadata, unit and CLI tests,
lint, formatting, and documentation. Container acceptance is separate because
it requires Linux Docker and disposable synthetic credentials. No customer
credentials or production endpoints are needed.

## Runtime boundaries

The API is intended for a contained laboratory. Container checks use a
non-root identity, read-only root filesystem, dropped capabilities,
no-new-privileges, resource limits, and no network or host mounts. These
controls reduce exposure for the test runtime; they do not certify a public
deployment or protect a compromised host.
