# Roadmap

Чекбокс означает проверенный результат, а не обещание. Runtime пока отсутствует.

## 0. Подготовка разработки

- [x] Описаны scope, архитектура, модель угроз и правила участия.
- [x] Добавлены инструкции Codex и read-only workspace check.
- [x] Документирован setup среды Codex Cloud для единственного репозитория.
- [x] Стек зафиксирован в TECH-STACK.md с runtime/tool pins и lockfile.
- [x] Offline development smoke, lint и форматирование прошли в текущем workspace.
- [x] CI workflow выполнен на GitHub: push и pull_request checks прошли.
- [ ] Среда Codex Cloud опубликована и задача в ней успешно проверена.

## 1. Контракт событий и конфигурации

- [ ] Реализовать строгую схему envelope, версии и фиксированные операции.
- [ ] Описать lifecycle, окно replay и идемпотентность request ID.
- [ ] Реализовать fail-closed validation и безопасные diagnostics.

Готово, когда malformed input, неизвестные операции, URL/пути и избыточные
payload отклоняются; schema tests проходят, секреты не попадают в сообщения.

## 2. Mock-agent и loopback

- [ ] In-memory mock-agent с synthetic fixtures и `ping/status/emit_test_event/stop`.
- [ ] Listener и API только на loopback в одной изолированной VM/namespace.
- [ ] Ограничения количества агентов, событий, размера сообщений и очереди.

Готово, когда lifecycle tests проходят, wildcard/non-loopback configuration
отклоняется, неизвестная операция не исполняется и нет доступа к ОС хоста.

## 3. RBAC, transport identity и аудит

- [ ] Server-side viewer/operator/lab-admin с default deny и lab scope.
- [ ] Тестовые identities с expiry/revocation; mTLS после выбора transport.
- [ ] Структурированный audit sink, корреляция и bounded retention.
- [ ] Fail closed при недоступности обязательного аудита.

Готово, когда отрицательные тесты ролей, identities, replay и отказа audit sink
проходят; отказ и результат связываются request ID без записи секретов.

## 4. Containment и воспроизводимая лаборатория

- [ ] Изолированная VM/контейнерный runtime без host networking и privileged mode.
- [ ] Egress deny, включая IPv4/IPv6/DNS; только разрешённые внутренние связи.
- [ ] Проверки портов, mounts, маршрутов и cleanup.
- [ ] Зафиксированные зависимости и автоматизация лабораторных проверок.

Готово, когда контролируемый внешний endpoint недоступен, loopback проверен,
нет production routes и сценарий не запускается при провале containment.

## 5. Тестовый UI и интеграционные сценарии

- [ ] UI для статуса, фиксированных mock-операций и обезличенного аудита.
- [ ] Happy path и негативные сценарии в CI без внешних targets.
- [ ] Проверенные команды установки, конфигурации и остановки лаборатории.

Готово, когда сценарий воспроизводим в чистой среде и документация совпадает с
реальными командами и поведением. Публичный deployment не является целью MVP.

Скрытность, persistence, обход защиты и неограниченное выполнение команд
исключены на всех этапах.
