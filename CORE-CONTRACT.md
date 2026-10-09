# Network-free mock core

`mocklab.Lab` — single-threaded in-process компонент для unit tests, без сети,
процессов, файлового аудита или операций над ОС. Все данные synthetic.

## Поддерживаемый контракт

`Lab("lab-1", {"test-operator": "operator"})` создаёт единственный `mock-1`.
Membership задаёт доверенный адаптер при создании; роль не берётся из запроса.
Это не аутентификация: нельзя передавать клиентский actor напрямую из будущего API.
Membership/expiry/revocation transport identities ещё не реализованы.

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
Все identities ограничены одной lab. Management API и изменения ролей отсутствуют.

Запрос валиден 60 секунд; будущие timestamps запрещены. Успешно принятый ID
запоминается до уничтожения Lab, повтор отклоняется (результат не кешируется).
Отказы до допуска не занимают replay table. Между экземплярами replay не защищён.
Wall-clock не гарантирует монотонность: production transport потребует иной контроль.

## Лимиты и ошибки

До 100 memberships, один агент, по умолчанию 1000 audit records и 1000 request IDs;
лимиты допускаются от 2 до 10000. Нет автоматического удаления или eviction.
При переполнении требуется новая тестовая сессия. Rate limit пока отсутствует.
Перед операцией резервируется место под allowed/completed. Отказы записываются
как denied без raw payload. Invalid actor отклоняется до аудита, без его записи.

Ошибка любой записи возвращает фиксированный `audit_failed` и блокирует
последующие операции. Ошибка первой записи препятствует эффекту. Аудит in-memory, не durable,
не защищён от доверенного Python caller и не экспортируется в файл.

Ни этот компонент, ни флаг в конфигурации не доказывают containment. Запуск
лабораторных сервисов запрещён до внешней проверки IPv4/IPv6/DNS egress deny,
loopback bind, mounts/permissions и cleanup. Сетевого запуска в этом PR нет.
