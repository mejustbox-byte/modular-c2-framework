# Offline workflow

## Запуск

```bash
uv sync --locked
uv run --locked --offline python -m mocklab --config examples/offline.toml
uv run --locked --offline python -m mocklab --interactive
```

Первый режим выполняет status → ping → synthetic event → stop → status,
показывает результаты и отзывает ephemeral identity. Второй предлагает только
фиксированные операции, просмотр аудита и выход. Не принимает shell commands,
URLs, file paths для mock-агента или исполняемый код. Сетевого listener нет.
CLI — доверенный локальный учебный интерфейс с synthetic operator, без входа
пользователей и без выдачи токенов в терминал. Его нельзя выставлять через web.

По умолчанию SQLite journal находится в private temporary directory и удаляется
при выходе: это одноразовая demo, не retention. Чтобы сохранять аудит:

```bash
umask 077
mkdir -p .runtime/exercise-001
uv run --locked --offline python -m mocklab --audit-directory .runtime/exercise-001
```

Каталог должен уже существовать с mode 0700 и принадлежать текущему пользователю.
Symlinks, shared permissions и hardlinks для audit.sqlite3 отклоняются.
`.runtime/` игнорируется Git. Не помещайте туда реальные данные или secrets.
Тот же журнал сохраняет stopped state и replay IDs; повторная demo завершается
отказом `agent_stopped`, а не сбрасывает состояние. Для нового упражнения создайте
новый приватный каталог. Старый журнал автоматически не удаляется.

## Конфигурация

Поддерживаемые TOML поля: lab_id, max_events, max_requests, burst.
lab_id — ограниченный synthetic ID; events/requests от 2 до 10000; burst от 1 до 1000.
Неизвестные поля, bool вместо числа, дубликаты и файл больше 4096 bytes запрещены.
Конфигурация не содержит identities, passwords, tokens или network toggles.

## Проверка и ограничения

```bash
uv run --locked --offline python -m unittest discover -s tests -v
uv run --locked --offline python scripts/smoke.py
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
```

Контракт: [CORE-CONTRACT.md](CORE-CONTRACT.md). Journal рассчитан на один Lab,
один процесс и доверенное локальное хранилище. Он не является tamper-proof audit.
Crash после allowed до completed блокирует восстановленную сессию: нужен разбор
журнала, автоматического unsafe retry/reset нет. Replay хранится до конца журнала.
SQLite гарантии durability зависят также от файловой системы и оборудования.

Offline scenario завершён как отдельный этап. Полный сетевой MVP ещё не готов:
нет listener/API, web UI, transport identity/mTLS, membership management или
проверенного контейнерного стенда. В текущем workspace Docker отсутствует;
network namespace isolation ранее была запрещена. Полный containment и
IPv4/IPv6/DNS egress deny здесь проверить нельзя. Эти условия блокируют запуск
лабораторных сетевых сервисов, а не заменяются флагом в конфиге.
