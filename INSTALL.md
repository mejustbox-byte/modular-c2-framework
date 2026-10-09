# Installation

## Development

Runtime: CPython 3.12.14, Linux. Bootstrap выполняется до отключения сети:

```bash
python3.12 -m venv .tools
.tools/bin/python -m pip install uv==0.12.24
export PATH="$PWD/.tools/bin:$PATH"
bash scripts/setup-cloud.sh
```

Setup проверяет origin/documents, locked dependencies, smoke, unit/CLI tests,
lint и форматирование. Не запускает listener. Runtime/mock fixtures не требуют
project secrets. Не выводите environment variables или platform credentials.

## Offline exercise

```bash
uv run --locked --offline python -m mocklab --config examples/offline.toml
uv run --locked --offline python -m mocklab --interactive
```

Сохранение private audit и конфигурация: [OFFLINE-WORKFLOW.md](OFFLINE-WORKFLOW.md).

## Полная контейнерная приемка

Нужны Linux Docker Engine, Bash, OpenSSL и sudo для provisioning ownership
одноразовой synthetic PKI. Этот workflow выполняется в GitHub Actions Ubuntu 24.04.

```bash
bash scripts/container-checks.sh
```

Скрипт собирает digest-pinned образ; создаёт контейнер с network none, без ports,
bind mounts/privileged mode, UID/GID 10001, read-only root, cap-drop ALL,
no-new-privileges, 256 MiB memory, 1 CPU, 64 PIDs и 32 MiB private tmpfs `/run/lab`.
Перед listener проверяет `docker inspect`, затем runtime guard проверяет
interfaces/routes, UID, capabilities, no-new-privileges и read-only root.

Одноразовая PKI создаётся вне Git и образа, действует один день. Enrollment
содержит только synthetic viewer/operator/admin и fingerprint сертификата.
TLS 1.3 и client certificate обязательны; session expiry — 10 минут.
Скрипт проверяет API/UI, mTLS/RBAC/replay/membership, аудит, restart, IPv4/IPv6/DNS
отказ по documentation-only адресам и cleanup listener. В конце удаляет только
свой контейнер и свой временный каталог PKI. Production endpoints не используются.

Это acceptance, а не команда публикации портов или установки публичного сервера.
CLI/API команды и модель доступа: [API.md](API.md).

## Локальный UI в лаборатории

Для браузера требуется та же отдельная изолированная VM/namespace, где работает
loopback listener, плюс доверенный lab CA и pre-enrolled client certificate.
Обычный host browser не видит network-none контейнер; port publishing не допускается.
HTTPS URL внутри лаборатории: `https://127.0.0.1:8443/`. Не отключайте certificate
validation, не обходите warnings и не расширяйте сеть. CA private key доступен
только владельцу disposable лаборатории, никогда не хранится в Git и не
передаётся в application container.

## Cleanup и удержание данных

`stop` останавливает mock lifecycle, не ОС. Acceptance завершает server process,
проверяет закрытие listener и удаляет disposable runtime data. Private offline
journal сохраняется только при явном `--audit-directory`; записи не ротируются
автоматически. При capacity — отказ, новый run требует нового journal.
После неполной операции replay/recovery блокируется до ручного разбора, без reset.

## Codex Cloud

Опубликована отдельная private среда для единственного репозитория, без project
и network secrets, с allowlist PyPI/file storage. Setup commit PR #1 проверен.
Текущий MVP проверяется локально и в GitHub CI; первоначальный Cloud install/start
script привязан к старому commit и требует обновления после review новой ветки.
Её собственный runtime containment не подтверждён: listener там запускать нельзя.
