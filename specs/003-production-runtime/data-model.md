# Data Model: Base de runtime de producao

Esta feature nao cria entidades persistidas, tabelas, colunas, indices ou migrations. Os modelos
abaixo representam somente contratos operacionais de build e execucao.

## Build Artifact

Representa a imagem imutavel compartilhada pelos tres processos.

| Field | Type | Rules |
|-------|------|-------|
| `source_revision` | string | Commit ou revisao unica, obrigatoria e nao secreta. |
| `python_version` | string | Exatamente `3.13.14` nesta feature. |
| `base_image_digest` | string | Digest SHA-256 obrigatorio da imagem base. |
| `dependency_lock_digest` | string | Hash do lock de producao versionado. |
| `image_digest` | string | Digest imutavel produzido pelo build. |

**Relationships**: Um Build Artifact inicia zero ou mais Runtime Processes. Todos os processos de uma
mesma entrega devem referenciar o mesmo `image_digest`.

**Validation rules**:

- A revisao e os locks devem estar versionados antes do build.
- O build deve falhar quando um pacote ou hash nao corresponder ao lock.
- Segredos e arquivos `.env*` nao fazem parte do artefato.

## Runtime Process

Representa uma execucao isolada de um papel da aplicacao.

| Field | Type | Rules |
|-------|------|-------|
| `role` | enum | `api`, `worker_runner` ou `frontend`. |
| `container_command` | string list | Comando long-lived do papel. |
| `lifecycle` | enum | `long_lived` para os tres containers. |
| `restart_policy` | enum | Reinicia somente o container do papel que encerrou. |
| `exposed_port` | integer/null | API e frontend usam porta interna; worker runner usa `null`. |
| `required_configuration` | string set | Apenas nomes das variaveis necessarias ao papel. |
| `state` | enum | Estado operacional atual, nao persistido pela aplicacao. |

**Relationships**: Cada Runtime Process usa um Build Artifact. API e frontend podem consultar o
PostgreSQL; o worker runner hospeda Worker Invocations que tambem acessam BotNext. Nenhum container
depende do ciclo de vida de outro.

**Validation rules**:

- Worker runner usa somente um comando ocioso, nao publica porta e nao sincroniza durante deploy.
- API publica somente as duas operacoes descritas no contrato HTTP.
- Frontend preserva o entrypoint Streamlit existente.

**State transitions**:

```text
API/frontend/worker_runner: created -> starting -> running -> stopping -> stopped
                                               |-> failed
```

Um processo `failed` pode ser recriado independentemente sem reiniciar os outros containers.

## Worker Invocation

Representa uma sincronizacao one-shot iniciada como tarefa no worker runner.

| Field | Type | Rules |
|-------|------|-------|
| `command` | string list | Exatamente `python -m src.sync_service`. |
| `trigger` | enum | `manual` nesta feature; `scheduled` somente apos a feature 002. |
| `state` | enum | `requested`, `running`, `succeeded`, `failed` ou `blocked`. |
| `exit_code` | integer/null | Preserva a semantica atual do comando. |

**Relationships**: Cada Worker Invocation executa dentro de um worker runner e usa o mesmo Build
Artifact dos demais processos.

**Validation rules**:

- O deploy do runner nao cria Worker Invocation.
- Producao bloqueia `manual` e `scheduled` ate a protecao de concorrencia da feature 002 passar.
- Uma invocacao concluida nao reinicia automaticamente.
- API e frontend podem estar parados durante toda a invocacao.

**State transitions**:

```text
requested -> blocked
requested -> running -> succeeded
                     |-> failed
```

## Probe Result

Representa a resposta publica minima da API.

| Field | Type | Rules |
|-------|------|-------|
| `probe` | enum | `health` ou `readiness`; derivado da rota, nao retornado no corpo. |
| `status` | enum | `ok`, `ready` ou `not_ready`. |
| `http_status` | integer | `200` para `ok`/`ready`; `503` para `not_ready`. |
| `cache_control` | string | Sempre `no-store`. |

**Validation rules**:

- O corpo contem somente `status`.
- Health nao consulta Runtime Configuration nem PostgreSQL.
- Readiness nunca retorna DSN, host, usuario, banco, schema, excecao ou duracao.

**State transitions**:

```text
health: ok enquanto o processo HTTP responde
readiness: not_ready <-> ready conforme configuracao e PostgreSQL
```

## Runtime Configuration

Representa configuracao injetada no inicio do processo e nunca persistida pela feature.

| Role | Startup required | Operation required | Optional names |
|------|------------------|--------------------|----------------|
| API | none | Readiness: `DATABASE_URL` | `PORT`, `LOG_LEVEL` |
| Worker runner | none | Task: `DATABASE_URL`, `BOTNEXT_TOKEN`, `BOTNEXT_CHANNEL_IDS` | `DB_SCHEMA`, URLs BotNext, limites e timezone existentes |
| Frontend | none | Dashboard: `DATABASE_URL`; manual sync: `DATABASE_URL`, `BOTNEXT_TOKEN`, `BOTNEXT_CHANNEL_IDS` | `DB_SCHEMA`, `PORT`, URLs BotNext, limites e timezone existentes |

**Validation rules**:

- Valores sensiveis existem somente no ambiente de runtime do papel que os utiliza.
- Mensagens de erro podem citar o nome ausente, nunca seu valor.
- Arquivos versionados contem apenas nomes e exemplos ficticios.
- Coolify MUST receber todas as configuracoes de operacao antes do deploy produtivo, mas os processos
  ainda definem comportamento seguro para ausencia ou invalidade em testes e falhas operacionais.
- API sem configuracao continua viva e informa `not_ready`; uma invocacao do worker sem configuracao
  falha com codigo nao zero; o frontend permanece acessivel e apresenta indisponibilidade sanitizada.
