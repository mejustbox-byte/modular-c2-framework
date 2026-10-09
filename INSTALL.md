# Installation and Configuration

## Текущий статус

Платформа ещё не реализована. Сейчас можно подготовить checkout, проверить
документацию и выполнить offline smoke выбранного стека. Команд запуска teamserver, listener, mock-agent или UI пока нет.

Нужны Git и Bash; Python, Node, Docker и API-ключи для workspace check не нужны.

```bash
git clone https://github.com/mejustbox-byte/modular-c2-framework.git
cd modular-c2-framework
bash scripts/check-workspace.sh
```

Успешный результат — `Workspace check passed`. Скрипт проверяет origin,
наличие непустых документов и whitespace diff, показывает branch/status. Он не
проверяет секреты, RBAC, порты, маршруты и сетевую изоляцию.

## Codex Cloud

1. В ChatGPT выберите **Work in → Cloud → Select environment → Create environment**.
2. Выберите только `mejustbox-byte/modular-c2-framework`; подключите GitHub,
   если интерфейс запросит это. Не передавайте tokens через чат или Git.
3. После bootstrap uv из раздела ниже задайте setup command:
   `bash scripts/setup-cloud.sh`. Команда выполняется из корня клона. Пока изменения
   этого PR не объединены, для проверки нужна его ветка или предварительное
   объединение PR.
4. Проверьте setup. Для текущей задачи не нужны secrets, production credentials,
   внешние сервисы или прикладные пакеты. Для setup нужны uv и Ruff
   из официального package registry; затем smoke работает offline. Ограничьте доступ к среде своим
   аккаунтом. Для подготовки разрешите только GitHub и официальные источники
   Python/packages; это доступ setup, а не egress разрешение будущего стенда.
   Для offline smoke сетевой доступ не требуется.
5. Сохраните настройки, выберите **Publish** и дождитесь **Environment published**.
6. Начните задачу в среде; перед edits проверьте `AGENTS.md` и Git status.

Клон в текущем чате не означает, что среда опубликована. Официальная инструкция:
[Codex Cloud](https://learn.chatgpt.com/docs/cloud).

## Требования к будущей лаборатории

- Отдельная VM или изолированная контейнерная сеть без маршрута к production.
- Для первого transport — одна VM/network namespace и `127.0.0.1`.
- Никаких публичных портов, `0.0.0.0`, host networking, privileged mode,
  Docker socket или mounts с пользовательскими данными.
- Egress deny на уровне среды: IPv4, IPv6 и DNS; контролируемые endpoints для тестов.
- Одноразовые тестовые identities, synthetic fixtures, ограниченный audit storage.

Контейнерная internal network сама по себе не является доказательством
containment. Фактические routes, port publishing и runtime permissions должны
проверяться отдельно. Приложение не может обеспечить сетевую изоляцию вместо ОС.

## Проектная конфигурация

Ниже **предложение контракта**, а не поддерживаемый конфигурационный файл.
Runtime пока не читает эти параметры. Реализация должна определить строгую
схему и отвергать неизвестные поля.

| Поле | Предложение для MVP | Проверка |
| --- | --- | --- |
| `mode` | `mock` | Другие режимы запрещены |
| `lab_id` | `synthetic-lab` | Ограниченный формат, scope серверной identity |
| `bind_address` | `127.0.0.1` | Только это IPv4 loopback; IPv6 требует отдельного тестирования |
| `operations` | `ping`, `status`, `emit_test_event`, `stop` | Не допускает расширения произвольной строкой команды |
| `egress_policy` | `deny` | Требует внешней сетевой политики, не просто флага |
| `auth_required` | `true` | Отключение запрещено |
| `rbac_default` | `deny` | Роль и lab scope проверяются на сервере |
| `audit_required` | `true` | Недоступность sink блокирует начало операции |
| `max_agents` | 10 | Положительное число в пределах лабораторного hard limit |
| `max_payload_bytes` | 16384 | Проверяется до обработки сообщения |
| `max_events_per_run` | 1000 | Ограничение queue и генерации событий |

Значения лимитов предварительные и должны подтверждаться resource tests.
Порты, transport, credential references, retention и replay window будут
зафиксированы при реализации. Токены/ключи не встраиваются в конфигурацию Git;
используются защищённые средства среды с ограниченным сроком действия.

## План приемки и остановки

Перед первым запуском: config validation, loopback/port checks, отрицательные
RBAC tests, работоспособность audit sink и deny egress по всем transports.
Провал любого обязательного контроля блокирует сценарий.

После сценария: остановить mock lifecycle, закрыть listener, проверить отсутствие
оставшихся процессов и портов, отозвать test identities, сохранить обезличенный
аудит согласно retention и удалить только явно определённые disposable runtime
данные. Существующие файлы репозитория не удаляются.

Исполнимые команды containment/cleanup появятся вместе с выбранным runtime и
пройдут проверку в чистой лаборатории. Сейчас этот раздел описывает требования.

## Bootstrap и smoke выбранного стека

Для development workflow нужен CPython 3.12.14. Версии uv и Ruff зафиксированы
в [TECH-STACK.md](TECH-STACK.md), Ruff dependency — в `uv.lock`.
Установите uv в отдельное tool-окружение, не смешивая его с project `.venv`:

```bash
python3.12 -m venv .tools
.tools/bin/python -m pip install uv==0.12.24
export PATH="$PWD/.tools/bin:$PATH"
bash scripts/setup-cloud.sh
```

Bootstrap и `uv sync --locked` могут загружать пакеты. Следующие smoke/lint/format
шаги используют `--offline`, не запускают платформу и не требуют secrets.
Smoke состоит из четырёх development-проверок: runtime/metadata, документация и
ссылки, workspace, распространённые accidental secret signatures.
Он не читает значения environment variables. Нельзя считать этот ограниченный
scanner доказательством отсутствия любых секретов в среде.

Перед публикацией Codex Cloud отдельно проверьте в его настройках, что выбран
только этот репозиторий, project secrets и network secrets пусты, production
credentials и OIDC/VPN connections не настроены. Platform-managed authentication
не копируется в project files. Сохраните результат smoke, не выводя окружение.


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
