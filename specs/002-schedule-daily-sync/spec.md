# Feature Specification: Sincronização Automática Diária

**Feature Branch**: `002-schedule-daily-sync`
**Status**: Draft / Ready for Agent

## Problem Statement

O CEO e a equipe comercial precisam de um dashboard com dados analíticos atualizados diariamente sobre **vendedores**, **sessões**, **contatos** e **mensagens**. Atualmente, a **sincronização** dos dados depende da execução manual ou do acionamento via frontend (Streamlit), o que introduz dependência operacional humana, risco de desatualização dos dados operacionais do **Hub** (BotNext) e possibilidade de execuções concorrentes indesejadas se múltiplos operadores dispararem a sincronização simultaneamente.

## Solution

Implementar a automação da **sincronização** diária no ambiente de produção através do agendador/cron nativo da infraestrutura (Coolify), programado para executar exatamente `python -m src.sync_service` às 00:00 no fuso horário `America/Sao_Paulo` (configurado via ambiente do container/job `TZ=America/Sao_Paulo`). O processo Worker é um job finito e opera de forma totalmente independente do frontend Streamlit e da API FastAPI. TODAS as formas de execução (agendada via Coolify, manual via Streamlit ou CLI) são obrigatoriamente protegidas por **PostgreSQL Advisory Lock**, garantindo exclusão mútua distribuída durante toda a execução. Cada invocação gera um `run_id` único e registra logs estruturados no `stdout` sanitizados por `runtime_security`, sem expor dados sensíveis ou alterar o schema do banco.

## User Stories

1. As a CEO, I want the complete daily synchronization to execute automatically at 00:00 (America/Sao_Paulo) via the Coolify infrastructure scheduler, so that executive metrics and seller reports are always fresh without requiring manual intervention or continuous Python loops.
2. As a CEO, I want synchronization to run independently of the Streamlit frontend and FastAPI probes, so that system restarts or closed browser sessions do not interrupt scheduled data ingestion.
3. As an operator, I want manual synchronization triggers (Streamlit or CLI) to respect background scheduled executions, so that duplicate or overlapping sync jobs do not overload the BotNext API or produce race conditions.
4. As an operator, I want automated scheduled sync jobs to respect active manual sync jobs, so that an ongoing manual sync is not disrupted by a scheduled midnight run.
5. As an operator, I want clear execution logs containing `run_id`, start time, end time, duration, and status (success, failure, skipped due to concurrency) in `stdout`, so that I can audit sync health in under 2 minutes.
6. As a security officer, I want all sync failure and operational logs to be sanitized of tokens, passphrases, and message content, so that security standards and sensitive data isolation rules are preserved.
7. As a data engineer, I want process terminations or crashes to release the PostgreSQL advisory lock naturally via session disconnection, so that subsequent daily runs or manual retries are never permanently blocked.
8. As a data engineer, I want incremental sync operations for users, contacts, sessions, and messages to remain strictly idempotent, so that re-running or retrying synchronization never creates duplicate DB records.

## Implementation Decisions

- **Infrastructure Scheduler Integration**: O agendamento de produção é de responsabilidade do scheduler/cron do Coolify, que invoca `python -m src.sync_service` às 00:00 com a variável de ambiente `TZ=America/Sao_Paulo`. Não é criado nenhum loop Python permanente em `src/scheduler.py`.
- **Worker Execution Architecture**: O worker permanece um job finito acionado por `python -m src.sync_service`, desacoplado da API FastAPI (`src/api.py`) e do Streamlit (`app.py`).
- **Distributed Advisory Lock**: Utilização de PostgreSQL Advisory Lock de sessão (`pg_try_advisory_lock`), mantido durante toda a execução do processo `sync_service`. O lock protege TODAS as formas de disparo (agendado ou manual). Tentativas concorrentes são recusadas deterministicamente (`status=skipped_concurrency`) e encerram com exit code 0. Quedas de processo liberam a trava naturalmente pelo encerramento da conexão PostgreSQL.
- **Run ID & Structured Logging**: Cada invocação gera um `run_id` único e escreve logs em `stdout` no formato `[SYNC_RUN] run_id=... status=...`, sanitizados via `runtime_security.py`.
- **Exit Code Semantics**: Falha total ou parcial nas etapas de sincronização resulta em exceção lançada e exit code != 0. Falhas em um dia não afetam a invocação do job do dia seguinte.
- **Zero Schema Change**: Nenhuma alteração DDL, migration ou mudança em métricas de vendedor.

## Testing Decisions

- **Testing Philosophy**: Testar o comportamento externo nos limites mais altos da aplicação sem expor dados sensíveis ou acoplar a detalhes de implementação interna.
- **Primary Testing Seam**: 
  - `src.sync_service.executar_sincronizacao_completa` e `src.sync_lock` como as costuras principais para validação de concorrência, retivas de lock, exit codes e idempotência.
  - `tests/test_sync_concurrency.py` e `tests/test_sync_lock.py` para simulação de processos concorrentes e comportamento de liberação em quedas.
- **Prior Art**: 
  - `tests/test_sync_service.py` (validação de fluxo de etapas, logs estruturados e exceções de sincronização).
  - `tests/test_runtime_security.py` (validação de sanitização).

## Out of Scope

- Loop Python residente em memória/daemon para agendamento (o agendamento é delegado ao Coolify).
- Modificações de schema DDL ou tabelas adicionais.
- Alertas externos via E-mail/Slack/PagerDuty.

## Further Notes

- Alinhado com o dicionário ubíquo em `CONTEXT.md` e com a arquitetura de runtime de produção do ADR `docs/adr/0001-production-runtime-architecture.md`.
