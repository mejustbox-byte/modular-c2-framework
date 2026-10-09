# Security Policy

This is a controlled-lab research project. Use it only for authorized
exercises, with strict network isolation, containment, logging, and cleanup.
Never deploy agents or listeners against third-party systems.

Report vulnerabilities privately through GitHub Security Advisories. Do not
include operational secrets, live infrastructure details, or weaponized
payloads in public issues.

## Public development OPSEC

Use synthetic data, placeholder infrastructure and disposable test identities
in public documentation and examples. Do not publish tokens, private keys,
customer logs, internal hostnames, live target addresses or infrastructure
inventories. Supply credentials only through the platform's secure credential
or secret-management controls, never through chat, commits or PR descriptions.

The repository includes a network-free in-memory mock core and development checks.
No listener or server is implemented. Loopback binding,
command restrictions and egress isolation are future design requirements;
`check-workspace.sh` does not enforce containment or scan for secrets.

Review diffs before publishing. If a credential is exposed, revoke or rotate it
first and notify the maintainer privately; deleting a later file does not remove
it from Git history. Use the repository's private vulnerability-reporting flow
when available. If it is unavailable, ask the maintainer for a private reporting
channel without disclosing vulnerability details in a public issue.

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
