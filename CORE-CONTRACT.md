# Network-free mock core

`mocklab.Lab` — single-threaded in-process компонент для unit tests, без сети
и операций над ОС mock-агента. CLI читает только указанный конфиг и свой audit journal. Все данные synthetic.

## Поддерживаемый контракт

`Lab("lab-1", {"test-operator": "operator"})` создаёт единственный `mock-1`.
Membership задаёт доверенный адаптер при создании; роль не берётся из запроса.
Это не аутентификация: нельзя передавать клиентский actor напрямую из будущего API.
Identities выдаёт доверенный in-process setup, хранятся только hashes случайных
токенов; TTL 1–3600 секунд с monotonic clock, expiry/revocation и lab scope.
Это не transport authentication: сетевого входа нет.

`execute(actor, payload)` принимает bytes UTF-8 JSON до 4096 bytes. Обязательны:
`schema_version` (int 1), `request_id`, `lab_id`, `agent_id`, `operation`,
`issued_at` (finite Unix seconds). ID: `[a-zA-Z0-9_-]{1,64}`. Неизвестные и
повторяющиеся поля запрещены, bool не считается числом. Fixture разрешён только
для `emit_test_event` и только `synthetic-login`.

| Операция | Ответ | Роли |
| --- | --- | --- |
| ping | pong | operator, lab-admin |
| status | ready/stopped | все три роли |
| emit_test_event | mock_login synthetic fixture | operator, lab-admin |
| stop | stopped | operator, lab-admin |

После stop разрешён только status. Viewer читает копию аудита через `audit(actor)`.
Все identities ограничены одной lab. API поддерживает изменения ролей/revocation pre-enrolled identities;
контракт — [API.md](API.md).

Запрос валиден 60 секунд; будущие timestamps запрещены. Успешно принятый ID
запоминается до уничтожения Lab, повтор отклоняется (результат не кешируется).
Отказы до допуска не занимают replay table. С SQLite journal replay IDs и stopped state восстанавливаются между экземплярами.
При незавершённом allowed событии восстановление блокирует новые операции.
Wall-clock не гарантирует монотонность: production transport потребует иной контроль.

## Лимиты и ошибки

До 100 memberships, один агент, по умолчанию 1000 audit records и 1000 request IDs;
лимиты допускаются от 2 до 10000. Нет автоматического удаления или eviction.
При переполнении требуется новая тестовая сессия. Session ограничивает число запросов одного actor (по умолчанию 100) до конца
сессии, включая отклонённые авторизованные запросы; временного rate limit нет.
Перед операцией резервируется место под allowed/completed. Отказы записываются
как denied без raw payload. Invalid actor отклоняется до аудита, без его записи.

Ошибка любой записи возвращает фиксированный `audit_failed` и блокирует
последующие операции. Ошибка первой записи препятствует эффекту. Опциональный SQLite journal использует synchronous FULL и ограничение capacity.
Нужен приватный owner-only directory (0700), файл 0600, без symlinks/hardlinks.
Журнал не защищён от администратора ОС или доверенного Python caller.
Токены не записываются. Нет автоматического удаления или rotation: сохраняйте
результаты вне Git согласно своей retention policy. SQLite — stdlib dependency.

Ни этот компонент, ни флаг в конфигурации не доказывают containment. Запуск
лабораторных сервисов запрещён до внешней проверки IPv4/IPv6/DNS egress deny,
loopback bind, mounts/permissions и cleanup. Сетевой listener реализован отдельно и допускается только после runtime guard
и внешней проверки контейнера; обычный unit workflow не запускает его.
