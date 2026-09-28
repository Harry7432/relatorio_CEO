---

description: "Task list for the production runtime foundation"
---

# Tasks: Base de runtime de producao

**Input**: Design documents from `/specs/003-production-runtime/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Automated tests are required by the specification, test strategy, and project constitution for runtime contracts, synchronization behavior, process isolation, and sensitive-data redaction.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes different files and has no dependency on incomplete tasks
- **[Story]**: Maps the task to a user story from `spec.md`
- Every task names the exact file or files it changes

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the pinned Python and dependency inputs used by all runtime roles.

- [X] T001 Pin the local runtime to exactly Python `3.13.14` in `.python-version`
- [X] T002 [P] Declare only direct production dependencies for FastAPI, Uvicorn, psycopg 3, Streamlit, pandas, Plotly, requests, python-dotenv, and openpyxl in `requirements.in`
- [X] T003 [P] Declare pip-tools and the direct test dependencies for pytest, FastAPI/Starlette TestClient, PostgreSQL integration, and container smoke validation in `requirements-dev.in`
- [X] T004 Generate the complete production lock for Python 3.13.14 on `linux/amd64` with exact versions and hashes via `pip-compile --generate-hashes` in `requirements.txt`
- [X] T005 Generate the complete validation lock from `requirements-dev.in` with exact versions and hashes via `pip-compile --generate-hashes` in `requirements-dev.txt`
- [X] T006 [P] Exclude `.env*`, `.git`, virtual environments, caches, logs, local artifacts, and credentials in `.dockerignore`, and replace the concrete database host with reserved, fictitious values in `.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide the shared redaction boundary required before exposing errors from any runtime role.

**CRITICAL**: No user story work begins until this phase is complete.

- [X] T007 Add failing tests that seed a token, DSN, password, phone number, session/contact/message IDs, message content, response body, stdout, and stderr and assert that none cross response, exception, log, aggregate-output, or UI boundaries in `tests/test_runtime_security.py`
- [X] T008 Implement reusable allow-listed operational error categories and recursive sensitive-value redaction without returning raw exceptions or payloads in `src/runtime_security.py`
- [X] T009 [P] Make configuration failures cite only missing variable names, never values, while preserving current defaults and validation behavior in `src/config.py`
- [X] T010 [P] Replace BotNext HTTP failure details, response bodies, request URLs containing parameters, and chained raw exceptions with sanitized categories without changing requests or returned business data in `src/botnext_client.py`
- [X] T011 [P] Remove contact, session, message, phone, and content identifiers from per-stage progress and retry output without changing calls, persistence, ordering, or result counts in `src/sync_usuarios.py`, `src/sync_contatos_sessoes.py`, and `src/sync_mensagens.py`
- [X] T012 Sanitize every subprocess stdout/stderr value before aggregation, printing, or raising while preserving interpreter, module order, arguments, timeout, exit-code semantics, and `python -m src.sync_service` in `src/sync_service.py`

**Checkpoint**: Shared runtime failures are safe to expose through API, worker, and frontend surfaces.

---

## Phase 3: User Story 1 - Publicar um runtime reproduzivel (Priority: P1) MVP

**Goal**: Build one immutable Python image twice from the same revision and run each role from the same dependency set without embedding secrets.

**Independent Test**: Build twice without cache on clean builders, compare Python version, base digest, lock digest, and complete installed-package inventories, then start API, worker runner, and frontend commands separately from each image.

### Tests for User Story 1

- [X] T013 [US1] Add failing tests for Python `3.13.14`, a SHA-256-pinned base, hash-verified binary-only installation, non-root execution, excluded secrets, role startup commands, and the verbatim Build Artifact constraints `source_revision`: "Commit ou revisao unica, obrigatoria e nao secreta.", `python_version`: "Exatamente `3.13.14` nesta feature.", `base_image_digest`: "Digest SHA-256 obrigatorio da imagem base.", `dependency_lock_digest`: "Hash do lock de producao versionado.", and `image_digest`: "Digest imutavel produzido pelo build." in `tests/test_runtime_processes.py`

### Implementation for User Story 1

- [X] T014 [US1] Build a neutral production image from the official Python 3.13.14 slim image pinned by SHA-256 digest, install `requirements.txt` with `--require-hashes --only-binary=:all:`, copy only runtime files, run as a non-root user, and define no role-specific default behavior in `Dockerfile`
- [X] T015 [US1] Define a single shared image/build anchor and selectable processes with the verbatim Runtime Process constraints `role`: "`api`, `worker_runner` ou `frontend`.", `container_command`: "Comando long-lived do papel.", `lifecycle`: "`long_lived` para os tres containers.", `restart_policy`: "Reinicia somente o container do papel que encerrou.", `exposed_port`: "API e frontend usam porta interna; worker runner usa `null`.", `required_configuration`: "Apenas nomes das variaveis necessarias ao papel.", and `state`: "Estado operacional atual, nao persistido pela aplicacao." plus runtime-only environment injection and no embedded credentials in `compose.yaml`
- [X] T016 [US1] Extend clean-build smoke coverage to build the image twice, compare dependency inventories, reject a modified package hash, inspect both images for `.env*`, `.git`, `.venv`, caches, logs, and credentials, and verify each role starts or fails explicitly within 30 seconds in `tests/test_runtime_processes.py`

**Checkpoint**: User Story 1 provides a reproducible shared artifact and is independently demonstrable as the MVP.

---

## Phase 4: User Story 2 - Verificar saude e prontidao da API (Priority: P2)

**Goal**: Expose only liveness and PostgreSQL-backed readiness with stable, non-sensitive responses.

**Independent Test**: Start only the API, verify health with no configuration, readiness with missing/valid/invalid PostgreSQL access, and prove that every undeclared route and automatic documentation surface is unavailable.

### Tests for User Story 2

- [X] T017 [P] [US2] Add failing TestClient contract tests for exact `GET /health` and `GET /ready`, no configuration or I/O in health, disabled slash redirects/docs/OpenAPI/ReDoc, `404` undeclared routes, `405` unsupported probe methods, no leaked diagnostics, and the verbatim Probe Result constraints `probe`: "`health` ou `readiness`; derivado da rota, nao retornado no corpo.", `status`: "`ok`, `ready` ou `not_ready`.", `http_status`: "`200` para `ok`/`ready`; `503` para `not_ready`.", and `cache_control`: "Sempre `no-store`." in `tests/test_runtime_api.py`
- [X] T018 [P] [US2] Add a failing disposable-PostgreSQL integration test proving readiness executes only `SELECT 1`, closes its short-lived connection, returns `200 {"status":"ready"}` on success, returns `503 {"status":"not_ready"}` within 5 seconds for absent/invalid/unreachable `DATABASE_URL`, and never returns DSN, host, user, database, schema, exception, or duration in `tests/test_runtime_api_integration.py`

### Implementation for User Story 2

- [X] T019 [US2] Implement FastAPI with `openapi_url=None`, `docs_url=None`, `redoc_url=None`, `redirect_slashes=False`, exact health/readiness responses, `Cache-Control: no-store`, and a bounded psycopg connection that executes only `SELECT 1` in `src/api.py`
- [X] T020 [US2] Configure the API command `python -m uvicorn src.api:app --host 0.0.0.0 --port 8000`, internal port `8000`, role-specific `DATABASE_URL`, and independent liveness/readiness checks without worker or frontend dependencies in `compose.yaml`

**Checkpoint**: User Story 2 can be tested with the API alone and exposes exactly the two contracted operations.

---

## Phase 5: User Story 3 - Operar processos sem acoplamento (Priority: P3)

**Goal**: Operate API, one-shot worker invocations, and the existing Streamlit frontend with independent lifecycles.

**Independent Test**: Restart API and frontend separately, execute `python -m src.sync_service` once in an idle runner in isolated staging, and verify the other containers remain active and all existing Streamlit flows load.

### Tests for User Story 3

- [X] T021 [P] [US3] Add failing characterization tests for stage order, `sys.executable`, module arguments, callback progress, subprocess success/failure output, timeout, `main()`, business results, and the verbatim Worker Invocation constraints `command`: "Exatamente `python -m src.sync_service`.", `trigger`: "`manual` nesta feature; `scheduled` somente apos a feature 002.", `state`: "`requested`, `running`, `succeeded`, `failed` ou `blocked`.", and `exit_code`: "Preserva a semantica atual do comando." in `tests/test_sync_service.py`
- [X] T022 [P] [US3] Add a failing Streamlit smoke test with controlled repositories and synchronization dependencies that loads `Visao geral`, `Vendedores`, and `Conversas`, filters, empty states, exports, and the existing manual synchronization flow without exceptions in `tests/test_streamlit_smoke.py`
- [X] T023 [US3] Add failing Compose tests proving each role is long-lived and independently restartable, the runner exposes no port and starts no sync, a completed invocation is not restarted, API/frontend may remain stopped during a worker invocation, and no container failure restarts another role in `tests/test_runtime_processes.py`

### Implementation for User Story 3

- [X] T024 [US3] Configure `worker-runner` with exactly `python -c "from threading import Event; Event().wait()"`, no published port, no startup configuration, no automatic task/retry/schedule, and configure `frontend` with exactly `python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501`; apply per-container restart policies only in `compose.yaml`
- [X] T025 [US3] Keep the current Streamlit flows and manual sync available while presenting missing dashboard/manual-sync configuration and runtime failures as sanitized unavailable states without raw exception logging in `app.py`

**Checkpoint**: All three roles use the same artifact but can be started, stopped, failed, and restarted independently.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate invariants spanning every story and capture deploy evidence without changing schema or synchronization behavior.

- [X] T026 [P] Add regression assertions that this feature introduces no migration/DDL artifacts and that existing seller metrics remain unchanged in `tests/test_seller_metrics.py` and `tests/test_runtime_processes.py`
- [X] T027 Run the hash-locked full pytest suite plus Docker/Compose smoke tests and record commands, results, dependency inventories, image digests, startup durations, and any isolated legacy-script limitation in `specs/003-production-runtime/validation.md`
- [X] T028 Compare schema-only dumps from the disposable PostgreSQL database before and after validation and record the zero-diff evidence without adding migrations in `specs/003-production-runtime/validation.md`
- [X] T029 Execute every local/staging scenario in `specs/003-production-runtime/quickstart.md`, record probe, isolation, redaction, worker, and Streamlit evidence in `specs/003-production-runtime/validation.md`, and explicitly leave production deploy, Coolify worker task activation, and full converge blocked until feature 002 proves mutual exclusion for manual and scheduled triggers

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately; T004 depends on T002 and T005 depends on T003 plus the production input.
- **Foundational (Phase 2)**: Depends on Setup and blocks all stories; T008 follows the failing T007 tests, T009-T011 can then proceed in parallel, and T012 follows stage redaction.
- **User Story 1 (Phase 3)**: Depends only on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Depends only on Foundational for source-level testing; its Compose integration T020 also requires the base `compose.yaml` from US1.
- **User Story 3 (Phase 5)**: Characterization and Streamlit tests depend only on Foundational; container isolation T023-T024 requires the shared artifact and base Compose from US1.
- **Polish (Phase 6)**: Depends on all stories selected for delivery; production evidence remains blocked by feature 002.

### User Story Dependency Graph

```text
Setup -> Foundational -> US1 (MVP) --------------------+
                      -> US2 source/API tests ---------+-> Polish
                      -> US3 source/UI tests ----------+
US1 shared image/Compose -> US2 Compose validation ----+
US1 shared image/Compose -> US3 container isolation ---+
Feature 002 mutual exclusion ---------------------------> Production deploy and converge only
```

### Within Each User Story

- Write the listed tests first and confirm they fail for the intended missing behavior.
- Implement the smallest production change that satisfies the contracts.
- Keep shared-artifact and source-level checks separate from environment-dependent smoke validation.
- Complete the independent test before starting the next priority when delivering sequentially.

### Parallel Opportunities

- T002 and T003 can run in parallel; T006 can run alongside dependency declaration work.
- After T008, T009, T010, and T011 touch independent source files and can run in parallel.
- US1, source-level US2, and source-level US3 work can begin in parallel after Foundational.
- T017 and T018 can run in parallel because they use separate API test files.
- T021 and T022 can run in parallel because worker characterization and Streamlit smoke coverage use separate files.
- T026 can run while validation prerequisites and staging access for T027-T029 are prepared.

---

## Parallel Example: User Story 1

```text
Task: "Implement the pinned, neutral image in Dockerfile"
Task: "Prepare clean-builder environments for the two-build checks in tests/test_runtime_processes.py"
```

## Parallel Example: User Story 2

```text
Task: "Write HTTP contract tests in tests/test_runtime_api.py"
Task: "Write disposable PostgreSQL readiness tests in tests/test_runtime_api_integration.py"
```

## Parallel Example: User Story 3

```text
Task: "Characterize worker behavior in tests/test_sync_service.py"
Task: "Add controlled Streamlit smoke coverage in tests/test_streamlit_smoke.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and generate both hash-locked dependency files.
2. Complete the shared security foundation.
3. Complete User Story 1 and validate two clean builds independently.
4. Stop and review the shared artifact before adding runtime endpoints or operational activation.
5. Use only isolated local/staging environments; production remains blocked by feature 002.

### Incremental Delivery

1. Deliver Setup + Foundational as the safe packaging base.
2. Deliver US1 as the reproducible shared-image MVP.
3. Deliver US2 and validate the API independently from worker/frontend state.
4. Deliver US3 and validate worker/Streamlit behavior independently from API state.
5. Run cross-cutting schema, redaction, build, and staging validation.
6. Activate production worker tasks only after feature 002's mutual-exclusion evidence is approved.

### Parallel Team Strategy

1. Complete Setup and Foundational together.
2. Assign one developer to the shared image/clean-build path, one to API probes, and one to worker/Streamlit characterization.
3. Merge US1's base Compose before US2 and US3 add role-specific operational checks.
4. Combine all completed story evidence in `specs/003-production-runtime/validation.md` before any production decision.

---

## Notes

- `[P]` means different files and no dependency on an incomplete task.
- Story labels provide requirement traceability; Setup, Foundational, and Polish tasks intentionally have no story label.
- This feature creates no persistent entity, schema object, index, constraint, or migration.
- The worker task command remains exactly `python -m src.sync_service`.
- The runner must never synchronize during deploy, and a completed invocation must never restart automatically.
- Do not run failure scenarios against production credentials or production data.
