---
description: "Lista de tarefas para a sincronização automática diária via Coolify e controle de concorrência por Advisory Lock"
---

# Tasks: Sincronização Automática Diária

**Input**: Documentos de design em `/specs/002-schedule-daily-sync/`

**Prerequisites**: `spec.md`, `plan.md`

**Tests**: Testes automatizados cobrindo o PostgreSQL Advisory Lock de sessão, recusa determinística de concorrência, liberação natural em quedas, geração de `run_id` e sanitização de logs estruturados em stdout.

---

## Phase 1: Setup & Lock Infrastructure (Base de Concorrência)

**Purpose**: Implementar a trava distribuída via PostgreSQL Advisory Lock de sessão sem adicionar migrations nem modificar esquemas existentes.

- [X] T001 [P] Implementar módulo de trava distribuída via PostgreSQL Advisory Lock com aquisição não-bloqueante (`pg_try_advisory_lock`) e liberação no encerramento (`pg_advisory_unlock`) no arquivo `src/sync_lock.py`
- [X] T002 Adicionar testes unitários para a trava distribuída validando a manutenção do lock durante toda a sessão e a liberação natural na desconexão em `tests/test_sync_lock.py`
- [X] T003 [P] Garantir que o lock seja liberado obrigatoriamente no bloco `finally` em saídas normais ou exceções no arquivo `src/sync_lock.py`

---

## Phase 2: User Story 1 - Agendamento Diário via Scheduler/Cron do Coolify (Priority: P1) MVP

**Goal**: Garantir que a sincronização executada via `python -m src.sync_service` sob o fuso `America/Sao_Paulo` funcione como um job finito agendado no Coolify, desacoplado de FastAPI e Streamlit.

- [X] T004 [US1] Definir o contrato do job agendado no Coolify para disparar exatamente `python -m src.sync_service` sob o ambiente `TZ=America/Sao_Paulo` desacoplado dos containers de API e frontend
- [X] T005 [US1] Garantir no arquivo `src/sync_service.py` que falhas parciais ou totais em qualquer etapa de sincronização (`sync_usuarios`, `sync_contatos_sessoes`, `sync_mensagens`) lancem exceção e resultem em exit code != 0
- [X] T006 [US1] Adicionar testes em `tests/test_sync_service.py` comprovando que exit code != 0 é retornado em falhas e que cada invocação é isolada (uma falha anterior não impede a invocação do job seguinte)

---

## Phase 3: User Story 2 - Observabilidade com Run ID e Logs Estruturados em Stdout (Priority: P2)

**Goal**: Garantir que toda execução (manual ou agendada) possua um `run_id` único e escreva logs estruturados em `stdout` sanitizados por `runtime_security.py`.

- [X] T007 [US2] Adicionar geração de `run_id` único por invocação e emissão de logs estruturados em `stdout` (`[SYNC_RUN] run_id=... status=...`) no arquivo `src/sync_service.py`
- [X] T008 [US2] Integrar os logs de `stdout` em `src/sync_service.py` com o sanitizador `src/runtime_security.py` para mascarar DSNs, tokens, telefones e conteúdos de mensagens
- [X] T009 [P] [US2] Adicionar testes de caracterização em `tests/test_sync_service.py` verificando os logs estruturados no `stdout` e garantindo ausência de vazo de dados sensíveis

---

## Phase 4: User Story 3 - Exclusão Mútua Distribuída em Múltiplas Formas de Disparo (Priority: P3)

**Goal**: Garantir que TODAS as formas de execução (agendada via Coolify, manual via Streamlit ou CLI) passem pelo PostgreSQL Advisory Lock e que tentativas sobrepostas sejam recusadas de forma determinística.

- [X] T010 [US3] Envolver o ponto de entrada `executar_sincronizacao_completa` em `src/sync_service.py` com o Advisory Lock de `src/sync_lock.py`, mantendo a trava durante toda a execução
- [X] T011 [US3] Retornar recusa determinística (`status=skipped_concurrency` e exit code 0) quando o lock já estiver mantido por outro processo ativo em `src/sync_service.py`
- [X] T012 [P] [US3] Criar testes de concorrência distribuída em `tests/test_sync_concurrency.py` simulando invocação simultânea de múltiplos processos e verificando a recusa determinística da segunda execução
- [X] T013 [US3] Confirmar a idempotência de gravação no banco de dados durante reexecuções em `tests/test_sync_concurrency.py`

---

## Phase 5: Polish & Cross-Cutting Validation

**Purpose**: Garantir zero alteração de schema DDL ou de métricas de vendedores e documentar as evidências de validação.

- [X] T014 Adicionar asserções em `tests/test_seller_metrics.py` e `tests/test_runtime_processes.py` confirmando zero alterações de tabelas/schemas no PostgreSQL e nenhuma alteração em `seller_metrics.py`
- [X] T015 Executar a suíte completa de testes (`.venv\Scripts\python -m pytest`) e documentar evidências detalhadas no arquivo `specs/002-schedule-daily-sync/validation.md`
