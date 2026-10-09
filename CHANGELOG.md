# Changelog

Изменения ведутся по фактическому состоянию. Релизов пока нет.

## Unreleased

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

### Validation status

- Текущий workspace: 4 development smoke checks, Ruff lint/format и shell syntax
  прошли. Проверка signatures не нашла распространённых форматов secrets в
  project files; это не полный secrets audit.
- Публикация Codex Cloud и smoke в ней не проверены: вход в аккаунт отменён.
- GitHub CI workflow добавлен; результат будет отмечен после выполнения.
