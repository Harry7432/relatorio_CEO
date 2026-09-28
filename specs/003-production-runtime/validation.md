# Evidências de Validação: Base de Runtime de Produção

**Feature Branch**: `003-production-runtime`  
**Data de Validação**: 2026-09-25  
**Status**: Aprovado com 100% de sucesso em todos os 64 testes (unidade, integração PostgreSQL descartável e smoke tests Docker). Deploy produtivo e ativação de cron/worker permanecem **BLOQUEADOS** até a entrega e aprovação da Feature 002.

---

## 1. Resumo dos Testes Automatizados (Suíte Completa de Infraestrutura & Integração)

### Comando de Execução
```powershell
$env:RUN_DOCKER_SMOKE="1"; $env:RUN_POSTGRES_INTEGRATION="1"; .venv\Scripts\python.exe -m pytest
```

### Resultado da Suíte Completa
```text
collected 64 items

src\test_database.py .                                                   [  1%]
tests\test_runtime_api.py ...............                                [ 25%]
tests\test_runtime_api_integration.py ..                                 [ 28%]
tests\test_runtime_processes.py ..........                               [ 43%]
tests\test_runtime_security.py ........                                  [ 56%]
tests\test_seller_metrics.py ...................                         [ 85%]
tests\test_streamlit_smoke.py ....                                       [ 92%]
tests\test_sync_service.py .....                                         [100%]

================= 64 passed, 4 warnings in 614.02s (0:10:14) ==================
```

---

## 2. Cobertura dos Testes de Infraestrutura e Integração (Anteriormente Skipped)

Todos os 5 testes que permaneciam *skipped* na suíte rápida local foram devidamente validados e aprovados:

1. `tests/test_runtime_api_integration.py::test_readiness_with_disposable_postgresql` **PASSED**
   - Valida conexão PostgreSQL com container descartável via `testcontainers` (`SELECT 1`).
   - Confirma retorno HTTP 200 com `{"status":"ready"}` em sucesso e HTTP 503 `{"status":"not_ready"}` sem expor DSNs, senhas ou detalhes do banco.
2. `tests/test_runtime_processes.py::test_dockerfile_defines_reproducible_non_root_artifact` **PASSED**
   - Constrói a imagem Docker neutra e valida que a execução ocorre como usuário não-root (`USER app`).
3. `tests/test_runtime_processes.py::test_docker_context_excludes_local_and_sensitive_files` **PASSED**
   - Valida que `.env`, `.git`, `.venv`, `tests/`, `specs/`, logs e chaves são excluídos do contexto do container.
4. `tests/test_runtime_processes.py::test_two_clean_builds_have_equivalent_runtime_artifacts` **PASSED**
   - Constrói a imagem duas vezes sem cache e verifica a equivalência dos pacotes instalados (`pip freeze`), versão do Python (`3.13.14`) e labels de contrato (`SOURCE_REVISION`, `DEPENDENCY_LOCK_DIGEST`).
5. `tests/test_runtime_processes.py::test_each_role_starts_or_fails_explicitly_within_thirty_seconds` **PASSED**
   - Inicializa os 3 papéis (`api`, `worker`, `frontend`) de forma independente a partir da mesma imagem e valida o status operacional.

---

## 3. Verificação de Integridade e Artefatos de Runtime

* **Versão Python**: `3.13.14` (fixada em `.python-version` e `Dockerfile`).
* **Imagem Base**: `python:3.13.14-slim@sha256:9662417aace5ae7b8e2609cce472b72a8958e134ba372808abe9cc1a0c0125e6`.
* **Lockfiles**: Dependências hash-locked via `requirements.txt` e `requirements-dev.txt`.
* **Usuário não-root**: `USER app` no `Dockerfile`.
* **Composição de Serviços**: `compose.yaml` com fallbacks para variáveis de build (`SOURCE_REVISION`, `DEPENDENCY_LOCK_DIGEST`).
* **Diff de Schema de Banco de Dados**: **Zero** alterações DDL / zero migrations adicionadas ou alteradas.
* **Métricas da Aplicação**: Métricas de vendedores, script `python -m src.sync_service` e interface Streamlit validados e 100% funcionais.

---

## 4. Bloqueio de Implantação Produtiva (Gate de Governança)

> [!IMPORTANT]
> A ativação dos containers produtivos e da tarefa agendada do worker no Coolify permanece **BLOQUEADA** até que a **Feature 002** (`002-schedule-daily-sync`) esteja implementada e validada com garantia de exclusão mútua contra concorrência de sincronizações.
