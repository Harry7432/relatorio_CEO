# Implementation Plan: Sincronização Automática Diária

**Branch**: `002-schedule-daily-sync` | **Date**: 2026-09-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification de `/specs/002-schedule-daily-sync/spec.md`

## Summary

Esta funcionalidade implementa a automação e proteção da sincronização diária de dados (usuários, contatos, sessões e mensagens do BotNext). O agendamento de produção é de responsabilidade nativa do scheduler/cron da infraestrutura (Coolify), que dispara a tarefa diária às 00:00 com a variável de ambiente `TZ=America/Sao_Paulo`. O job invoca exatamente `python -m src.sync_service` e roda em um container Worker finito, totalmente desacoplado da API FastAPI e do Streamlit. TODAS as execuções (agendadas ou manuais) são protegidas por **PostgreSQL Advisory Lock** (`pg_try_advisory_lock`), mantido durante toda a execução. Caso uma invocação encontre a trava ocupada, a tentativa é recusada deterministicamente (`status=skipped_concurrency`) e encerra com exit code 0. Crashes ou quedas de conexão liberam a trava naturalmente via desconexão da sessão no PostgreSQL. Cada execução gera um `run_id` único e escreve logs estruturados em `stdout` sanitizados por `runtime_security`. Qualquer falha parcial ou total encerra o processo com exit code != 0, sem comprometer a invocação do job no dia seguinte. Nenhuma migration, tabela extra ou alteração de schema DDL é criada.

## Technical Context

**Language/Version**: Python 3.13.14 (fixado no ambiente do projeto)

**Primary Dependencies**: `psycopg` / `psycopg2` para conexão ao PostgreSQL e Advisory Lock nativo; `runtime_security` para redação e sanitização de logs.

**Storage**: PostgreSQL existente como fonte de verdade e mecanismo distribuído de trava (`pg_try_advisory_lock` / `pg_advisory_unlock`). Zero alterações de schema ou migrations DDL.

**Testing**: `pytest` com testes unitários de trava (`test_sync_lock.py`), testes de concorrência com múltiplos processos simultâneos (`test_sync_concurrency.py`) e caracterização de exit codes/logs estruturados (`test_sync_service.py`).

**Target Platform**: Containers Linux (`linux/amd64`) no Coolify executando o job `worker` desacoplado dos demais containers (`api` e `frontend`).

**Performance Goals**: Obtenção de lock em < 50ms; verificação de concorrência instantânea sem degradação da base de dados; liberação imediata ao término do processo ou em caso de desconexão da sessão TCP.

**Constraints**:
- O agendamento de produção é delegado ao scheduler/cron do Coolify às 00:00 no fuso `America/Sao_Paulo` (configurado via ambiente `TZ=America/Sao_Paulo`).
- Sem loop Python permanente em `src/scheduler.py`.
- Invocação exata: `python -m src.sync_service`.
- Worker totalmente desacoplado do Streamlit (`app.py`) e da API FastAPI (`src/api.py`).
- PostgreSQL Advisory Lock mantido durante toda a execução e cobrindo TODAS as formas de disparo (agendado, manual via Streamlit ou CLI).
- Recusa determinística de invocações concorrentes (`status=skipped_concurrency`, exit code 0).
- Desconexão/crash do processo libera o lock naturalmente no PostgreSQL.
- Identificador `run_id` único por execução.
- Output estruturado no `stdout` sanitizado via `runtime_security.py`.
- Exit code != 0 em falha total ou parcial.
- Idempotência preservada nas operações de gravação no banco.
- Zero alterações de schema DDL ou de métricas de vendedores (`seller_metrics.py`).

## Hard Prerequisite

A trava de concorrência via PostgreSQL Advisory Lock deve estar implementada e validada por testes unitários e integrados de concorrência antes da ativação do agendamento cron no Coolify.

## Constitution Check

| Gate | Result | Evidence |
|------|--------|----------|
| Evolução incremental | PASS | A trava distribuída e os logs estruturados são integrados ao `src/sync_service.py` sem alterar o domínio nem o fluxo interno das etapas. |
| PostgreSQL como fonte de verdade | PASS | O controle de exclusão mútua utiliza o mecanismo de Advisory Lock de sessão nativo do PostgreSQL, sem tabelas intermediárias. |
| Processos independentes | PASS | O job de sincronização roda de forma finita e desacoplada da API e do Streamlit. |
| Contrato estável do worker | PASS | O comando executado no cron permanece exatamente `python -m src.sync_service`. |
| Sincronização confiável | PASS | O lock é mantido durante toda a execução e liberado em `finally` ou no fechamento da conexão PostgreSQL. |
| Segurança e observabilidade | PASS | Logs estruturados em `stdout` passam por `runtime_security` para sanitizar dados sensíveis. |

## Lock & Infrastructure Scheduler Strategy Decisions

### 1. Estratégia de Lock Distribuído: PostgreSQL Advisory Lock de Sessão
- **Mecanismo**: Chamadas nativas `SELECT pg_try_advisory_lock(:lock_id)` na inicialização e `SELECT pg_advisory_unlock(:lock_id)` na finalização.
- **Chave de Lock**: Hash numérico de 64 bits constante identificando exclusivamente o lock do `relatorio_CEO`.
- **Manutenção & Liberação Natural**: A trava permanece adquirida durante toda a duração da sincronização. Se o processo sofrer um crash, SIGKILL ou perda de conexão, o PostgreSQL detecta o encerramento da sessão TCP e desfaz o lock naturalmente.

### 2. Estratégia de Agendamento: Scheduler / Cron Nativo do Coolify
- **Mecanismo**: O Coolify agenda a execução diária às 00:00 disparando o container worker com a variável de ambiente `TZ=America/Sao_Paulo`.
- **Comando do Job**: `python -m src.sync_service`.
- **Independência de Falhas**: Como cada agendamento diário é uma nova invocação isolada do processo pelo Coolify, qualquer falha no dia anterior (que encerra com exit code != 0) não afeta nem impede a invocação programada para o dia seguinte.

## Project Structure

```text
specs/002-schedule-daily-sync/
├── spec.md
├── plan.md
├── tasks.md
└── validation.md

src/
├── sync_lock.py          # Gerenciamento de PostgreSQL Advisory Lock de sessão (try_lock, unlock, context manager)
├── sync_service.py        # Ponto de entrada principal com run_id, logs em stdout e proteção por lock
└── runtime_security.py   # Sanitização existente aplicada aos novos logs estruturados

tests/
├── test_sync_lock.py        # Testes de unidade e liberação natural do Advisory Lock
├── test_sync_concurrency.py  # Testes de concorrência com processos simultâneos tentando obter o lock
└── test_sync_service.py      # Caracterização expandida com run_id, exit codes e recusa determinística
```
