# Changelog

## Unreleased

- Повторная release/main приемка, проверка Git tag и обновление Cloud setup через
  verified local bundle без расширения allowlist; отчет ACCEPTANCE-2026-10-09.md.
- Runtime review выявил security release Python 3.12.15; stable promotion требует
  patch adoption/revalidation и полноценной browser/mTLS приемки.

- Полная browser/mTLS приемка и runtime security-patch revalidation перед стабильным релизом.

## v0.1.0-rc.1 — 2026-10-09

Первый release candidate учебного mock MVP. Публикация выполняется только после
успешной приемки merge commit; статус и commit указаны в GitHub Releases.

### Isolated mock MVP

- Loopback TLS 1.3 API с mandatory mTLS/fingerprint pinning, expiry, Host/Origin checks.
- Pre-enrolled membership management/revocation с audit/replay/recovery.
- Packaged local web UI: fixed operations, membership и audit, без credential storage/CDN.
- Runtime guard и digest-pinned network-none Docker acceptance workflow.
- Synthetic one-day PKI вне checkout/image; cleanup собственных disposable данных.
- Добавлены API unit tests и contained mTLS/egress/lifecycle/restart/cleanup integration.
- Переписана основная документация под реальный MVP и operational acceptance scope.

### Offline workflow и исправления

- CLI demo и fixed-operation terminal UI, просмотр аудита, строгий TOML config.
- Ephemeral token hashes, monotonic expiry, revocation, lab scope и session budget.
- Private SQLite audit journal, capacity checks, replay/lifecycle recovery.
- Fail closed после interrupted operation; private-file/symlink checks.
- Исправлен приём UTF-16 при обязательном UTF-8 envelope.
- Добавлены identity, storage, restart, config и CLI integration tests.
- Contained network workflow реализован и проверен отдельным Docker CI job.

### Mock core MVP

- Добавлены network-free `mocklab`, строгий JSON envelope и фиксированные synthetic операции.
- Добавлены роли и lab scope, 60-second validity, replay guard и bounded in-memory аудит.
- Добавлены 12 unit/negative tests, включая audit failure, capacity и отсутствие OS operations.
- CI/setup дополнены unit tests; CORE-CONTRACT описывает реализованный контракт и ограничения.
- Приватная Codex Cloud проверена на setup commit PR #1; новая версия требует отдельной Cloud приемки.

### Added

- `ARCHITECTURE.md`: компоненты mock-лаборатории, ограниченные операции, RBAC,
  audit contract, lifecycle и fail-closed поведение.
- `THREAT-MODEL.md`: активы, границы доверия, containment threats, отрицательные
  проверки и остаточные риски.
- `CONTRIBUTING.md`: workflow, публичный OPSEC, review и план тестирования.
- `AGENTS.md`: работа только в этом репозитории, проверка состояния перед edits,
  сохранение файлов и обязательной документации.
- `scripts/check-workspace.sh`: read-only проверка origin, документов и Git diff.

- `TECH-STACK.md`: CPython 3.12.14, uv 0.12.24, unittest, Ruff 0.16.10,
  rationale, контейнерные требования и SHA-pinned GitHub Actions.
- Runtime pin, `pyproject.toml`, `uv.lock`, offline smoke, setup script и CI workflow.

### Changed

- README описывает учебный изолированный scope и отличает требования от
  реализованных возможностей.
- INSTALL содержит действующую workspace check, подготовку Codex Cloud,
  проектную конфигурацию, containment acceptance и cleanup requirements.
- ROADMAP разбит на этапы с проверяемыми критериями завершения.
- SECURITY дополнен правилами публичного OPSEC и обработки утечки credentials.

### Initial scaffold

- Зафиксирован учебный и изолированный scope.
- Добавлены базовые документы проекта, MIT license и security policy.

### Acceptance

- 33 tests (30 core/CLI/API + 3 mocked release tests), 4 smoke checks,
  Ruff lint/format и shell/whitespace проверки прошли.
- CI run 37888774720: smoke и 5 contained integration tests прошли.
- Выпуск из main дополнительно требует обе успешные CI jobs для release commit.
- Browser visual/mTLS и новый commit в Cloud пока не проверены.
