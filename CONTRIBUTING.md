# Contributing

## Область изменений

Принимаются документация, synthetic fixtures, mock lifecycle, loopback
transport, containment-проверки, RBAC, аудит и тесты учебной лаборатории.
Произвольное выполнение команд, скрытность, persistence и обход защит не входят
в scope. Предложение новой операции должно сохранять фиксированные входы и
детерминированный тестовый результат.

## Workflow

1. Работайте только в `mejustbox-byte/modular-c2-framework`. До изменений
   прочитайте применимые `AGENTS.md`, проверьте branch и `git status --short`.
2. Создайте отдельную ветку. Сохраняйте существующие файлы и чужие изменения;
   не используйте force-push и destructive cleanup.
3. Прочитайте соответствующую архитектуру и модель угроз. `CLAUDE.md` читайте
   только при конкретной необходимости.
4. Внесите узкое изменение. Используйте только синтетические данные и
   placeholder identities; секреты задаются через защищённые средства среды.
5. Обновите затронутые документы и `CHANGELOG.md` → `Unreleased`. В roadmap
   отмечайте завершение только после реализации и проверки. Сохраняйте MIT и
   attribution в `LICENSE`; у новых зависимостей проверьте лицензию.
6. Выполните проверки и review diff. Создайте PR с проблемой, результатом,
   командами проверки, фактическими итогами и ограничениями.

## Проверки сейчас

```bash
bash -n scripts/check-workspace.sh
bash scripts/check-workspace.sh
git diff --check
bash scripts/setup-cloud.sh
```

Workspace проверяет репозиторий и документы. Setup дополнительно запускает
unit/negative/CLI tests; сетевых сервисов пока нет. Development smoke и CI
описаны в TECH-STACK.md; запуск: `bash scripts/setup-cloud.sh` после bootstrap uv.
Не утверждайте, что RBAC, loopback или egress deny проверены этим скриптом.

## Тесты будущего MVP

- Unit: схема сообщения, операции enum, fixture IDs, lifecycle и RBAC matrix.
- Negative: неверные identities, чужая lab, неизвестная операция, oversize
  payload, replay и недоступный audit sink.
- Integration: разрешённый synthetic сценарий, полная корреляция audit events,
  отказ по роли и graceful stop.
- Containment: loopback bind, отсутствие публичных портов, host networking и
  privileged mounts; deny egress по IPv4, IPv6 и DNS.
- Resource limits: лимит агентов/событий, bounded queue и обработка заполнения
  audit storage.

Сетевые проверки выполняются в изолированной тестовой среде с контролируемыми
endpoints. Тесты не должны сканировать внешние адреса или production.

## Review

Reviewer проверяет соответствие scope, отсутствие секретов, default deny,
согласованность документации с кодом и реальные результаты тестов. Защиту от
потери аудита и сетевые ограничения проверяют отдельно от happy path.
Уязвимости сообщайте приватно согласно [SECURITY.md](SECURITY.md).

## Offline workflow: текущая реализация

CLI, строгий TOML config, ephemeral identities с expiry/revocation, bounded
SQLite journal и restart recovery реализованы. Сетевых компонентов нет.
Действующие команды и ограничения: [OFFLINE-WORKFLOW.md](OFFLINE-WORKFLOW.md).
Документы выше про web/API, in-memory-only ограничения и ещё планируемую
identity/durable audit следует читать с учётом этого реализованного этапа.
Сетевой transport, membership management и containment всё ещё не готовы.
