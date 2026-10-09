# Technical Stack

## Решение

После проверки основной документации выбран минимальный Python-стек для
изолированной mock-лаборатории. Сначала проверяем workflow без серверов и
внешних targets. Сетевой API и UI реализованы поверх проверенного mock core; контейнерный
acceptance workflow проверяет mTLS, RBAC и containment.

| Слой | Выбор и версия | Обоснование |
| --- | --- | --- |
| Runtime | CPython **3.12.15**, Linux | Зрелая ветка, стандартные `unittest`, `tomllib`, `enum`, `dataclasses`; версия доступна и проверена в текущем workspace |
| Пакетный менеджер | **uv 0.12.24**, `.venv`, `uv.lock` | Единый lock/sync workflow, фиксированные версии; `uv sync --locked` отклоняет устаревший lock |
| Прикладные зависимости | Пока отсутствуют | Smoke не требует серверов, сети или credentials; минимум supply-chain surface |
| Тестовый стек | `unittest` из CPython 3.12.15 | Нет дополнительных пакетов для первичной проверки; unit/negative/integration tests добавляются с реализацией |
| Линтер и форматтер | **Ruff 0.16.10** | Один инструмент вместо отдельных linter/formatter, настройки в `pyproject.toml` |
| Контейнеризация | Docker Engine **28.0.4** в проверенном CI, Linux; Docker CLI; Compose не используется | Одна изолированная VM/namespace в первом MVP; multi-container transport требует отдельного review |
| CI | GitHub Actions, Ubuntu 24.04 | Read-only contents permissions, bounded timeout, SHA-pinned actions, никаких пользовательских secrets |
| Хранилище и аудит | Structured JSON events + stdlib SQLite; offline и contained API | Bounded private journal, replay/lifecycle recovery; внешняя БД не нужна |
| UI и web framework | stdlib http.server + ssl; fixed HTML/CSS/JS | Фиксированный UI и mTLS API без прикладных dependencies |

Python 3.12.15 выбран как проверенный baseline, а не заявлен как самый новый
patch release. Runtime и инструменты обновляются отдельным PR после smoke,
lockfile, review release notes и проверки security advisories. Перед стабильным или расширенным сетевым выпуском обязательна повторная
проверка поддерживаемых security patches; candidate сохраняет проверенный baseline.
Dockerfile и Docker CLI acceptance workflow реализованы; runtime image pinned
по digest, фактическая версия Docker Engine записывается в CI log.

## Альтернативы

Go удобен для компактных binaries, но пока нет задачи распространения реального
агента: mock-объекты, schema tests и аудит проще поддерживать в одном Python
проекте. TypeScript потребовал бы отдельного toolchain без текущей потребности
в web UI. Rust увеличил бы сложность первого mock-прототипа. Это выбор по
текущему scope, а не сравнение безопасности языков как гарантии containment.

## Воспроизводимость и безопасность

- Runtime pin хранится в `.python-version`, ограничения — в `pyproject.toml`.
- Единственная dev dependency — Ruff; разрешённые artifacts и hashes в `uv.lock`.
- Bootstrap uv из официального package registry с точной версией; не используем
  shell installers из произвольных URL.
- Setup может загружать packages; smoke выполняется offline и не открывает sockets.
- Никаких API keys, GitHub PAT, cloud credentials или private test certificates
  в репозитории и project configuration. Platform-managed authentication
  отделена от пользовательских secrets и не должна выводиться в diagnostics.
- Реализованный стенд: non-root, read-only filesystem, dropped capabilities,
  no-new-privileges, resource limits, без host mounts/socket/network и egress deny.
  Конфигурация проверяется через Docker inspect до запуска API.

## Проверка выбранного стека

После добавления setup файлов выполняются:

```bash
uv sync --locked
uv run --locked --offline python scripts/smoke.py
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
```

Smoke проверяет runtime, project metadata, документы/ссылки и распространённые
форматы accidental secrets в version-controlled/project files. Это ограниченная
проверка, не доказательство отсутствия любых секретов и не containment audit.
Codex Cloud считается проверенным только после запуска этой последовательности
в опубликованной среде, связанной с единственным разрешённым репозиторием.
Локальный результат и CI не подменяют проверку Codex Cloud.

## Первичные источники

- [Python 3.12 documentation](https://docs.python.org/3.12/).
- [uv project workflow](https://docs.astral.sh/uv/guides/projects/).
- [Ruff](https://docs.astral.sh/ruff/).
- [Codex Cloud](https://learn.chatgpt.com/docs/cloud).

## MVP runtime

Dockerfile: `python:3.12.15-alpine3.24` с digest
`sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4`,
полученным из фактической CI-сборки. Нет прикладных third-party dependencies.
TLS 1.3, mTLS и SQLite предоставляет stdlib; OpenSSL CLI используется только для
одноразовой PKI на CI host, не внутри application API. Compose не нужен: один
контейнер, Docker CLI configuration инспектируется перед запуском.
Docker Engine версию сообщает acceptance log; host runner image обновляется GitHub.
Это не полностью pinned host OS/Engine: base runtime image и Python tools pinned.

`http.server` выбран только для маленького single-threaded изолированного mock MVP;
он не предназначен для публичного production hosting. UI — packaged static assets
без CDN/build dependencies. Container integration отдельна от обычного unit setup.
См. [API.md](API.md), [VALIDATION.md](VALIDATION.md).

Release metadata: `0.1.0`; Git tag `v0.1.0`. Release job получает
`contents: write` только для публикации из main после smoke, container/browser и image-audit checks; обычные
smoke/container jobs сохраняют read-only permissions. См. [RELEASE.md](RELEASE.md).

Повторная приемка 2026-10-09 и advisory review: [ACCEPTANCE-2026-10-09.md](ACCEPTANCE-2026-10-09.md).
Python 3.12.15 принят как security baseline и локально проверен. Bookworm image
получил 53 HIGH и 2 CRITICAL findings; приложение переведено на официальный
Alpine 3.24 image для повторной полной CVE и containment/browser приемки.
Firefox 1.63.0 Playwright image используется только как CI test tooling,
отдельно от прикладного образа; native NSS CA и client certs, без TLS bypass.
Trivy 0.75.0 binary проверяется SHA256; все HIGH/CRITICAL блокируют выпуск.

Patched runtime zlib 1.3.2-r1; unused pip/ensurepip removed. Current acceptance:
[STABLE-ACCEPTANCE.md](STABLE-ACCEPTANCE.md). Historical Cloud snapshot is rc.1/3.12.14.
