# Modular C2 Framework — Mock Lab

Стабильный source-релиз: [v0.1.0](https://github.com/mejustbox-byte/modular-c2-framework/releases/tag/v0.1.0), опубликован 2026-10-09.
Python metadata: `0.1.0`; проверенные tag/release указывают на точный main commit.

Учебная лаборатория управления **только mock-агентом**. Данные синтетические,
операции фиксированные: `ping`, `status`, `emit_test_event`, `stop`.
Нет shell, исполнения пользовательского кода, чтения файлов агентом, скрытности,
persistence, обхода защиты или работы с реальными targets.

## Реализованный MVP

- Строгий versioned JSON envelope, ограниченные ID/payload и replay protection.
- Один deterministic mock-agent и проверяемый lifecycle.
- Viewer/operator/lab-admin, lab scope, изменения ролей и отзыв доступа.
- TLS 1.3 loopback API с обязательным mTLS и fingerprint pinning client certificates.
- Локальный web UI: статус, операции, управление ролями и просмотр аудита.
- Private bounded SQLite audit; восстановление состояния и fail closed после crash.
- Offline CLI/menu и строгая TOML конфигурация.
- Настоящая Firefox/NSS mTLS UI-приемка и полный Trivy CVE audit/SBOM.
- Docker containment acceptance в CI: network none, non-root, read-only root,
  dropped capabilities, no-new-privileges, tmpfs и resource limits.

Это ограниченный учебный MVP, не production C2 и не публичный сервис.
Исходники релиза объединяются в `main` после успешной приемки. Статус публикации
и точный commit: [GitHub Releases](https://github.com/mejustbox-byte/modular-c2-framework/releases).
Фактическая приемка описана в [VALIDATION.md](VALIDATION.md).

## Быстрый offline запуск

```bash
uv sync --locked
uv run --locked --offline python -m mocklab
uv run --locked --offline python -m mocklab --interactive
```

Для setup нужны CPython 3.12.15 и uv 0.12.24; Ruff 0.16.10 зафиксирован lockfile.
[INSTALL.md](INSTALL.md) содержит bootstrap, контейнерные проверки и cleanup.

## Сетевая лаборатория

Сервер привязывается только к `127.0.0.1` и отказывается запускаться без runtime
containment guard. Клиенты работают в том же изолированном network namespace;
**порты на host не публикуются**. Обычный браузер хоста не может подключиться к
network-none контейнеру. Web UI используется в отдельной проверенной изолированной
VM/namespace с браузером, доверенным lab CA и клиентским сертификатом.
Нельзя обходить guard или отключать проверку TLS ради подключения UI.

## Документы

- [TECH-STACK.md](TECH-STACK.md), [ARCHITECTURE.md](ARCHITECTURE.md).
- [CORE-CONTRACT.md](CORE-CONTRACT.md), [API.md](API.md), [OFFLINE-WORKFLOW.md](OFFLINE-WORKFLOW.md).
- [THREAT-MODEL.md](THREAT-MODEL.md), [SECURITY.md](SECURITY.md).
- [ROADMAP.md](ROADMAP.md), [CHANGELOG.md](CHANGELOG.md), [CONTRIBUTING.md](CONTRIBUTING.md).

Работа только в `mejustbox-byte/modular-c2-framework`. Лицензия — [MIT](LICENSE).

## Релиз и ограничения

[RELEASE.md](RELEASE.md) описывает состав source-релиза, проверки и установку.
Runtime обновлен до Python 3.12.15; браузерный mTLS и image audit входят в CI gates.
Текущая приемка: [STABLE-ACCEPTANCE.md](STABLE-ACCEPTANCE.md).
Историческая приемка rc.1 и обновления Cloud:
[ACCEPTANCE-2026-10-09.md](ACCEPTANCE-2026-10-09.md).
