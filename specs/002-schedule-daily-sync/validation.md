# Validation Plan & Results: Sincronização Automática Diária

**Feature Branch**: `002-schedule-daily-sync` | **Date**: 2026-09-28 | **Spec**: [spec.md](./spec.md)

## Summary

Este documento consolida o plano e os **resultados reais de execução** da validação da feature `002-schedule-daily-sync`, cobrindo o controle de concorrência por PostgreSQL Advisory Lock de sessão, a recusa determinística, o desacoplamento de worker, a geração de `run_id`, a sanitização de `stdout` e o comportamento de exit code.

---

## Validated Scenarios & Test Results

### 1. Concorrência Distribuída e PostgreSQL Advisory Lock
- **Cenário**: Invocação simultânea do ponto de entrada por múltiplos processos/threads.
- **Evidência Real**: Teste `tests/test_sync_concurrency.py::test_concurrency_lock_held_skips_execution_cleanly` executado com sucesso.
- **Resultado**: O segundo processo detecta o Advisory Lock mantido pela primeira sessão, emite `[SYNC_RUN] run_id=... status=skipped_concurrency message="Lock de sincronizacao ja adquirido por outra execucao."` no `stdout` e encerra deterministicamente sem executar módulos adicionais nem gerar erro.

### 2. Manutenção do Lock e Liberação Natural
- **Cenário**: O processo de sincronização obtém o lock e é finalizado (normalmente ou com erro).
- **Evidência Real**: Testes em `tests/test_sync_lock.py` (`test_obter_lock_sincronizacao_context_manager_releases_lock_on_exit` e `test_obter_lock_sincronizacao_releases_lock_even_on_exception`) executados com sucesso.
- **Resultado**: O lock `pg_try_advisory_lock` permanece ativo durante toda a execução e é obrigatoriamente liberado via `pg_advisory_unlock` no bloco `finally` ou no fechamento da conexão PostgreSQL.

### 3. Falhas Parciais/Totais e Exit Code Semantics
- **Cenário**: Falha em qualquer etapa de sincronização durante a execução via `main()`.
- **Evidência Real**: Teste `tests/test_sync_concurrency.py::test_main_exits_with_nonzero_on_stage_failure` executado com sucesso.
- **Resultado**: A falha é capturada, logada de forma sanitizada (`status=failed error=...`), e `main()` encerra com `SystemExit(code=1)` (exit code != 0).

### 4. Run ID e Observabilidade em Stdout
- **Cenário**: Invocação da sincronização completa.
- **Evidência Real**: Teste `tests/test_sync_concurrency.py::test_logs_are_sanitized` e `test_concurrency_lock_acquired_runs_sync` executados com sucesso.
- **Resultado**: Cada execução gera um `run_id` único no formato `sync_<hash12>` e imprime eventos estruturados no `stdout`. Todos os valores passam por `redact_sensitive()`, garantindo 100% de sanitização para DSNs, telefones e conteúdos.

### 5. Imutabilidade de Schema e Regressão de Métricas
- **Cenário**: Verificação de schema e regressão das métricas de vendedores.
- **Evidência Real**: Teste `tests/test_seller_metrics.py::test_schedule_daily_sync_preserves_schema_and_metrics_contract` executado com sucesso.
- **Resultado**: Zero alterações DDL, nenhuma migration criada e integridade total das métricas mantida.

---

## Command Execution Logs

```powershell
.venv\Scripts\python -m pytest
```

**Output Real do Teste**:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\harry.silva\Desktop\relatorio_CEO
plugins: anyio-4.15.1
collected 75 items

tests\test_runtime_api.py ...............                                [ 20%]
tests\test_runtime_api_integration.py ss                                 [ 22%]
tests\test_runtime_processes.py .......sss                               [ 36%]
tests\test_runtime_security.py ........                                  [ 46%]
tests\test_seller_metrics.py ....................                        [ 73%]
tests\test_streamlit_smoke.py ....                                       [ 78%]
tests\test_sync_concurrency.py .....                                     [ 85%]
tests\test_sync_lock.py ......                                           [ 93%]
tests\test_sync_service.py .....                                         [100%]

================== 70 passed, 5 skipped, 2 warnings in 6.47s ==================
```
