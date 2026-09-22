# Runtime Process Contracts

## Shared Artifact

API, worker runner e frontend MUST executar a mesma imagem imutavel. Nao existe supervisor
compartilhado; cada container responde por seu proprio ciclo de vida.

## API

**Command**:

```text
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

**Lifecycle**: long-lived, com restart do container em encerramento inesperado.

**Network**: porta interna `8000`, publicada somente pelo proxy do Coolify.

**Startup configuration**: nenhuma; health deve responder mesmo sem configuracao.

**Readiness configuration**: `DATABASE_URL`.

**Contract**:

- Expoe somente `GET /health` e `GET /ready` conforme [runtime-api.yaml](./runtime-api.yaml).
- `/`, `/docs`, `/redoc`, `/openapi.json` e qualquer rota nao declarada retornam `404`.
- `/health/` e `/ready/` retornam `404`, sem redirect para os paths declarados.
- Metodos diferentes de `GET` nos dois paths retornam `405`.
- O processo inicia mesmo quando o PostgreSQL esta indisponivel; nesse estado health responde e
  readiness retorna `503`.

## Worker Runner

**Container command**:

```text
python -c "from threading import Event; Event().wait()"
```

**Container lifecycle**: long-lived e ocioso. O comando nao inicia sincronizacao.

**Task command**:

```text
python -m src.sync_service
```

**Task lifecycle**: one-shot, iniciado somente por tarefa Coolify explicita.

**Network**: nenhuma porta publicada.

**Runner startup configuration**: nenhuma; o container ocioso pode iniciar sem executar o job.

**Task configuration**: `DATABASE_URL`, `BOTNEXT_TOKEN`, `BOTNEXT_CHANNEL_IDS` e demais opcoes
existentes aplicaveis a sincronizacao. Ausencia faz somente a tarefa falhar com codigo nao zero.

**Contract**:

- O comando da tarefa, a ordem das etapas, as chamadas, a persistencia, os codigos de saida e os
  resultados de negocio existentes nao mudam.
- Mensagens de erro podem ser sanitizadas para remover response bodies, credenciais e dados
  sensiveis sem mudar o resultado da operacao.
- A API e o frontend podem estar parados durante toda a execucao.
- O deploy inicia somente o runner ocioso; nenhuma tarefa e criada ou executada automaticamente.
- O deploy produtivo desta feature MUST permanecer bloqueado ate a feature 002 comprovar exclusao
  mutua entre a tarefa e o fluxo manual do Streamlit.
- Agendamento, retry e lock de concorrencia estao fora do escopo desta feature.

## Frontend

**Command**:

```text
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

**Lifecycle**: long-lived, com restart do container em encerramento inesperado.

**Network**: porta interna `8501`, publicada somente pelo proxy do Coolify.

**Startup configuration**: nenhuma; configuracao ausente deve produzir estado indisponivel seguro.

**Functional configuration**: `DATABASE_URL` para o dashboard; `DATABASE_URL`, `BOTNEXT_TOKEN`,
`BOTNEXT_CHANNEL_IDS` e demais opcoes atuais para a sincronizacao manual temporaria.

**Contract**:

- Todos os fluxos Streamlit existentes permanecem disponiveis.
- O frontend nao e requisito de inicializacao ou execucao da API e do worker.
- Sua retirada depende de feature posterior com paridade React validada.

## Build And Configuration

- A imagem MUST ser construida com versao Python, base por digest e lock com hashes.
- `.env`, `.env.*`, `.git`, ambientes virtuais, caches e logs MUST ficar fora do contexto final.
- `.env.example` MUST usar somente hosts reservados e valores ficticios.
- Cada papel recebe somente as variaveis necessarias pelo ambiente do Coolify.
- Nenhuma credencial aparece no Compose, na imagem, em argumentos de comando ou em logs.
- O runner pode reiniciar como container ocioso; uma tarefa concluida nunca reinicia automaticamente.
