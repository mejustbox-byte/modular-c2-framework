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
unit/negative/CLI/API dispatch tests; сетевой listener не запускается. Development smoke и CI
описаны в TECH-STACK.md; запуск: `bash scripts/setup-cloud.sh` после bootstrap uv.
RBAC проверяется unit tests; loopback, mTLS и egress — отдельным Docker job.

## Реализованный тестовый набор

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

## Contained integration

`bash scripts/container-checks.sh` только на контролируемом Docker host.
Не запускайте listener в обычном workspace, не отключайте guard/mTLS и не
публикуйте порты. PR обязан иметь smoke, container/browser и image-audit CI evidence. Не помещайте
сгенерированную PKI, journals или runtime artifacts в Git. UI acceptance и
остаточные ограничения описаны в VALIDATION.md.

## Выпуск

При явном разрешении владельца завершите проверки, объедините зависимости PR
и release PR в main. Merge title `Release v<version>` включает gated release job;
он публикует stable source release после smoke, container/browser и image-audit success. Версии в pyproject.toml
и uv.lock должны совпадать. Stable promotion требует recorded browser/mTLS и runtime/CVE
приемки; порядок и ограничения см. [RELEASE.md](RELEASE.md).
