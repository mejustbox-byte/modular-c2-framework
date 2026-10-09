# Technical Stack

## Решение

После проверки основной документации выбран минимальный Python-стек для
изолированной mock-лаборатории. Сначала проверяем workflow без серверов и
внешних targets. Сетевой API, UI и прикладные зависимости вводятся отдельными
этапами после схемы сообщений, RBAC и containment tests.

| Слой | Выбор и версия | Обоснование |
| --- | --- | --- |
| Runtime | CPython **3.12.14**, Linux | Зрелая ветка, стандартные `unittest`, `tomllib`, `enum`, `dataclasses`; версия доступна и проверена в текущем workspace |
| Пакетный менеджер | **uv 0.12.24**, `.venv`, `uv.lock` | Единый lock/sync workflow, фиксированные версии; `uv sync --locked` отклоняет устаревший lock |
| Прикладные зависимости | Пока отсутствуют | Smoke не требует серверов, сети или credentials; минимум supply-chain surface |
| Тестовый стек | `unittest` из CPython 3.12.14 | Нет дополнительных пакетов для первичной проверки; unit/negative/integration tests добавляются с реализацией |
| Линтер и форматтер | **Ruff 0.16.10** | Один инструмент вместо отдельных linter/formatter, настройки в `pyproject.toml` |
| Контейнеризация | Docker Engine + Compose **v2**, Linux; пока план | Одна изолированная VM/namespace в первом MVP; multi-container transport требует отдельного review |
| CI | GitHub Actions, Ubuntu 24.04 | Read-only contents permissions, bounded timeout, SHA-pinned actions, никаких пользовательских secrets |
| Хранилище и аудит | Structured JSON events + stdlib SQLite; offline реализация | Bounded private journal, replay/lifecycle recovery; внешняя БД не нужна |
| UI и web framework | Отложены до API contract | Не нужны для первого smoke; не добавляем зависимости без требований и проверок |

Python 3.12.14 выбран как проверенный baseline, а не заявлен как самый новый
patch release. Runtime и инструменты обновляются отдельным PR после smoke,
lockfile, review release notes и проверки security advisories. Перед первым
сетевым runtime обязательна повторная проверка поддерживаемых security patches.
Версия Docker/Compose будет зафиксирована вместе с первым проверенным образцом
лаборатории; сейчас нет Dockerfile, образа или работающего контейнерного стенда.

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
- Для будущего стенда: non-root, read-only filesystem, dropped capabilities,
  no-new-privileges, resource limits, без host mounts/socket/network и egress deny.
  Эти меры пока требования, а не реализованная конфигурация.

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

## Реализованный этап: network-free core

Добавлен `mocklab` для in-process unit tests: фиксированные операции, строгий
JSON envelope, lab-scoped роли, replay guard и bounded in-memory аудит.
Действующий контракт и ограничения описаны в [CORE-CONTRACT.md](CORE-CONTRACT.md).
Предыдущие разделы про transport, authentication, durable audit и deployment
остаются проектными требованиями. Сетевые компоненты не реализованы.

Проверка: `uv run --locked --offline python -m unittest discover -s tests -v`.
Setup и CI запускают этот набор вместе с development smoke и Ruff.

Codex Cloud опубликована с единственным репозиторием, доступом «Только я», без
project/network secrets и с доменами pypi.org/files.pythonhosted.org. Setup на
commit PR #1 прошёл; новая реализация требует отдельной проверки в этой среде.
Enforcement сети не подтверждён; лабораторные запуски остаются запрещены.

## Offline workflow: текущая реализация

CLI, строгий TOML config, ephemeral identities с expiry/revocation, bounded
SQLite journal и restart recovery реализованы. Сетевых компонентов нет.
Действующие команды и ограничения: [OFFLINE-WORKFLOW.md](OFFLINE-WORKFLOW.md).
Документы выше про web/API, in-memory-only ограничения и ещё планируемую
identity/durable audit следует читать с учётом этого реализованного этапа.
Сетевой transport, membership management и containment всё ещё не готовы.
