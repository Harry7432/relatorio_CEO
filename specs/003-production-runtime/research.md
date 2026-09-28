# Research: Base de runtime de producao

## Python e imagem reproduzivel

**Decision**: Fixar Python 3.13.14 e a imagem oficial slim por digest. Gerar o lock no mesmo alvo
`linux/amd64` usado em producao e registrar atualizacoes de digest como mudancas revisaveis.

**Rationale**: O projeto ja foi validado com Python 3.13.14. Fixar versao e digest elimina variacao
do interpretador e da base entre builds, enquanto a atualizacao explicita preserva correcoes de
seguranca sob controle de versao.

**Alternatives considered**:

- Tag flutuante `python:3.13-slim`: rejeitada porque pode mudar sem alteracao no repositorio.
- Migrar para Python 3.12: rejeitada porque adicionaria uma mudanca de runtime sem necessidade.
- Imagem por processo: rejeitada porque aumenta divergencia e contradiz o artefato comum.

**Sources**:

- Docker build best practices: https://docs.docker.com/build/building/best-practices/
- Python official image: https://hub.docker.com/_/python

## Lock de dependencias

**Decision**: Manter o fluxo pip e introduzir `requirements.in` e `requirements-dev.in` como entradas
diretas. Gerar `requirements.txt` e `requirements-dev.txt` com todas as dependencias transitivas,
versoes exatas e hashes por `pip-compile --generate-hashes`. A imagem instala producao com
`pip install --require-hashes --only-binary=:all:`.

**Rationale**: E a menor evolucao para o manifesto existente, fixa transitivas e valida os artefatos
baixados sem introduzir um novo gerenciador no runtime. Um lock separado impede ferramentas de teste
de aumentarem a imagem de producao.

**Alternatives considered**:

- Manter apenas pins diretos: rejeitada porque transitivas ainda mudariam entre builds.
- Adotar Poetry, PDM ou uv: rejeitada por ampliar a migracao sem necessidade funcional atual.
- Usar `pylock.toml`: adiado porque o suporte correspondente no pip ainda e experimental.
- Permitir sdists: rejeitado no alvo inicial para evitar compilacoes dependentes do ambiente.

**Sources**:

- pip repeatable installs: https://pip.pypa.io/en/stable/topics/repeatable-installs/
- pip secure installs: https://pip.pypa.io/en/stable/topics/secure-installs/
- pip install options: https://pip.pypa.io/en/stable/cli/pip_install/
- pip-tools: https://pip-tools.readthedocs.io/en/stable/

## Topologia de processos no Coolify

**Decision**: Usar Docker Compose no Coolify com uma imagem comum e tres containers separados: API,
Streamlit e `worker-runner`. O runner permanece ativo por um comando Python ocioso e recebe tarefas
Coolify cujo comando e exatamente `python -m src.sync_service`. Esta feature entrega o alvo, mas nao
agenda nem ativa a sincronizacao em producao.

**Rationale**: Tarefas Coolify documentadas executam dentro de um container ativo e nao criam um
container efemero. Um runner dedicado isola recursos e segredos do processo web, nao sincroniza no
deploy e permite executar o comando publico sem wrapper. O processo da tarefa termina uma vez; o
runner continua disponivel para a proxima invocacao.

**Alternatives considered**:

- Tres processos no mesmo container: rejeitado por acoplar falhas, sinais e reinicios.
- `restart: unless-stopped` no worker: rejeitado porque o job e finito e seria repetido continuamente.
- Worker em profile Compose: rejeitado porque tarefas Coolify nao executam `docker compose run` nem
  podem selecionar um container que nao existe.
- Tres aplicacoes Coolify independentes: valido para deploys e rollbacks independentes, mas adiado
  porque triplica configuracao e nao e necessario para a base inicial.
- Agendador dentro da imagem: rejeitado por misturar responsabilidades e sobrepor a feature de
  sincronizacao diaria.

**Sources**:

- Coolify Docker Compose: https://coolify.io/docs/applications/builds/docker-compose
- Coolify deployment methods: https://coolify.io/docs/applications/choose-deployment-method
- Coolify scheduled tasks: https://coolify.io/docs/core/automation/scheduled-tasks/overview
- Compose services: https://docs.docker.com/reference/compose-file/services/
- Docker restart policies: https://docs.docker.com/engine/containers/start-containers-automatically/

## Dependencia de concorrencia

**Decision**: Bloquear o deploy produtivo e o `converge` completo da feature 003 ate a feature 002
implementar e validar exclusao mutua entre todos os acionamentos manuais e agendados. A feature 003
nao adiciona lock, nao presume que ele exista e nao admite excecao temporaria.

**Rationale**: O codigo atual permite que Streamlit e o comando do worker iniciem a mesma operacao
sem lock. Ativar um segundo caminho antes da feature 002 violaria a constituicao e criaria risco de
execucoes sobrepostas. Uma dependencia explicita preserva o escopo sem declarar uma garantia falsa.

**Alternatives considered**:

- Implementar lock nesta feature: rejeitado porque altera comportamento da sincronizacao e pertence
  ao escopo da feature 002.
- Confiar em operacao humana: rejeitado porque nao protege contra simultaneidade ou erro operacional.
- Remover o fluxo manual do Streamlit: rejeitado porque viola a manutencao temporaria do frontend.

## Contrato da API de runtime

**Decision**: Expor exatamente `GET /health` e `GET /ready`. Desabilitar redirect de barra final,
OpenAPI, Swagger UI e ReDoc. Retornar corpos JSON fixos e `Cache-Control: no-store`; toda outra rota
retorna `404` e metodos nao suportados retornam `405`.

**Rationale**: A superficie minima atende a operacao do orquestrador e evita criar prematuramente uma
API de negocio. Corpos estaveis e sem diagnosticos sao simples de testar e nao revelam arquitetura,
versoes ou configuracao.

**Alternatives considered**:

- Manter docs e OpenAPI padrao: rejeitado porque seriam rotas publicas adicionais.
- Responder `204`: rejeitado porque um JSON minimo e mais claro para validacao manual.
- Incluir versao, host ou dependencia no corpo: rejeitado por expandir contrato e exposicao.

**Sources**:

- FastAPI OpenAPI URL: https://fastapi.tiangolo.com/tutorial/metadata/#openapi-url
- FastAPI docs URLs: https://fastapi.tiangolo.com/tutorial/metadata/#docs-urls
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/

## Semantica de health e readiness

**Decision**: Health confirma apenas que o processo HTTP responde e nunca acessa configuracao ou
dependencias externas. Readiness valida `DATABASE_URL`, abre uma conexao curta com timeout total
limitado, executa `SELECT 1` e fecha a conexao. Sucesso retorna `200 {"status":"ready"}`; qualquer
falha esperada retorna `503 {"status":"not_ready"}` sem detalhes.

**Rationale**: Separar vida de prontidao permite diagnosticar um processo ativo durante falhas do
banco. Uma conexao autenticada testa as credenciais reais; `pg_isready` nao comprova usuario, senha
ou banco corretos. A consulta nao le nem altera dados de negocio.

**Alternatives considered**:

- Reutilizar `testar_conexao()`: rejeitado porque consulta metadados e tabelas desnecessariamente.
- Falhar o startup sem banco: rejeitado porque tornaria health indisponivel e acoplaria liveness.
- Pool de conexoes: adiado porque dois probes nao justificam estado e dependencia adicionais.
- Cachear readiness: adiado para preservar a atualidade do sinal no volume inicial.

**Sources**:

- Psycopg connections: https://www.psycopg.org/psycopg3/docs/api/connections.html
- PostgreSQL connection parameters: https://www.postgresql.org/docs/current/libpq-connect.html

## Segredos e contexto de build

**Decision**: Criar `.dockerignore` que exclua `.env*`, ambientes virtuais, caches, Git, logs e
artefatos locais. Trocar o host concreto de `.env.example` por um dominio reservado. Fornecer
variaveis no Coolify por papel. Respostas, stdout, stderr e erros de API, BotNext, worker e Streamlit
usam categorias sanitizadas, nunca valores, response bodies, IDs de sessao/contato/mensagem,
conteudo de mensagens ou excecoes brutas. A fronteira final no `sync_service` sanitiza toda saida de
subprocesso antes de agrega-la ou imprimi-la; cada etapa tambem deixa de emitir identificadores. Essa
mudanca limita-se a apresentacao e nao altera chamadas, persistencia, ordem ou codigos de saida.

**Rationale**: `.gitignore` nao protege o contexto Docker. Menor privilegio por processo reduz a
exposicao, e respostas constantes impedem que falhas vazem DSN, credenciais ou payloads. O Streamlit
recebe temporariamente as configuracoes BotNext porque seu fluxo manual existente deve permanecer;
essa excecao termina quando o fluxo for removido apos a paridade React.

**Alternatives considered**:

- Copiar todo o repositorio e confiar em `.gitignore`: rejeitado porque Docker nao o aplica.
- Compartilhar todas as variaveis entre os tres processos: rejeitado por ampliar acesso sem uso.
- Retornar a excecao de readiness: rejeitado porque erros podem conter host, usuario e banco.

**Sources**:

- Docker build context and cache: https://docs.docker.com/build/cache/optimize/
- Coolify environment variables: https://coolify.io/docs/applications/configuration/environment-variables
- Docker secrets: https://docs.docker.com/compose/how-tos/use-secrets/

## Estrategia de testes

**Decision**: Testar o contrato HTTP com dependencias substituidas, adicionar uma integracao curta
com PostgreSQL descartavel e validar imagem/processos com Docker Compose. Testes cobrem barras
finais, metodos, timeout, redacao com segredos semeados, comando de tarefa, runner ocioso e isolamento.
Testes de caracterizacao fixam ordem, subprocessos, codigos de saida e `main()` do worker. Casos de
falha parcial semeiam token, DSN, telefone, IDs e conteudo no stdout/stderr e comprovam que nenhum
valor atravessa a fronteira final. Um smoke test e roteiro funcional cobrem Streamlit. Dois builds
limpos comparam inventarios; comparacao de schema confirma ausencia de migrations.

**Rationale**: As regras criticas desta feature estao nos limites de processo, build e readiness. A
maioria pode ser coberta de forma deterministica sem infraestrutura; uma integracao real valida o
driver e a conexao efetiva.

**Alternatives considered**:

- Apenas verificacao manual no Coolify: rejeitada porque nao protege o contrato em mudancas futuras.
- Usar o banco de producao nos testes: rejeitado por risco de dados, disponibilidade e segredos.
- Testar novamente toda a sincronizacao pela API: rejeitado porque a API nao expoe essa operacao.

**Sources**:

- Starlette TestClient: https://www.starlette.io/testclient/
- FastAPI testing events: https://fastapi.tiangolo.com/advanced/testing-events/
- Docker Compose CLI: https://docs.docker.com/compose/reference/
