# Quickstart: Validacao do runtime de producao

Este guia valida a feature em ambiente local ou de homologacao. Nunca use credenciais ou dados de
producao nos cenarios de falha.

## Prerequisites

- Docker Engine com Docker Compose v2
- Acesso a um PostgreSQL descartavel de homologacao
- Python 3.13.14 para validacoes fora do container
- Variaveis de teste fornecidas pelo ambiente, sem arquivos versionados de segredo

## 1. Validate Specification Artifacts

```bash
docker compose config
```

Confirmar na saida:

- API, worker runner e frontend usam a mesma imagem.
- O runner usa comando ocioso, nao publica portas e nao inicia sincronizacao.
- A tarefa Coolify planejada resolve exatamente para `python -m src.sync_service`.
- API, runner e frontend possuem containers e ciclos de vida independentes.
- Nenhum valor de segredo esta embutido no Compose.

## 2. Validate Dependency Locks

Em um ambiente limpo com a versao de Python fixada:

```bash
python -m pip install --require-hashes -r requirements-dev.txt
python -m pip check
python -m pytest tests/test_runtime_api.py tests/test_runtime_processes.py tests/test_runtime_security.py tests/test_sync_service.py tests/test_streamlit_smoke.py
```

Regenerar os locks duas vezes no mesmo alvo e confirmar que nao ha diff. Uma dependencia com hash
incorreto deve fazer a instalacao falhar antes de executar qualquer processo.

## 3. Build The Shared Image

```bash
docker build --no-cache --tag relatorio-ceo:validation-a .
docker build --no-cache --tag relatorio-ceo:validation-b .
docker run --rm relatorio-ceo:validation-a python -m pip freeze --all > inventory-a.txt
docker run --rm relatorio-ceo:validation-b python -m pip freeze --all > inventory-b.txt
diff inventory-a.txt inventory-b.txt
```

O diff dos inventarios deve estar vazio. Confirmar a versao Python, executar smoke startup dos tres
papeis nas duas imagens e registrar seus digests. Os digests OCI podem diferir por metadados de build;
o criterio obrigatorio e a mesma base, lock, versoes instaladas e comportamento de startup. Inspecionar
contexto e imagens para garantir que `.env*`, `.git`, `.venv`, caches, logs e credenciais nao entraram.

## 4. Validate API Without PostgreSQL

Iniciar a API sem `DATABASE_URL`:

```bash
docker run --rm --name relatorio-ceo-api-unready -p 8000:8000 relatorio-ceo:validation-a python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Em outro terminal:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
curl -i http://localhost:8000/
curl -i http://localhost:8000/docs
curl -i http://localhost:8000/redoc
curl -i http://localhost:8000/openapi.json
curl -i http://localhost:8000/health/
curl -i http://localhost:8000/ready/
curl -i -X POST http://localhost:8000/health
curl -i -X POST http://localhost:8000/ready
```

Expected outcomes:

- `/health`: `200`, `{"status":"ok"}` e `Cache-Control: no-store`.
- `/ready`: `503`, `{"status":"not_ready"}` e nenhum diagnostico interno.
- Todas as outras rotas, inclusive paths com barra final: `404`, sem redirect.
- Metodos nao suportados nos dois probes: `405`.
- Logs nao contem DSN, host, usuario, senha ou valores de ambiente.

## 5. Validate API With PostgreSQL

Iniciar a API com `DATABASE_URL` apontando para o banco descartavel:

```bash
docker run --rm --name relatorio-ceo-api-ready -p 8000:8000 -e DATABASE_URL relatorio-ceo:validation-a python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
```

Expected outcome: ambos retornam `200`; readiness contem somente `{"status":"ready"}`. Repetir com
senha invalida e host indisponivel; health permanece `200`, readiness retorna `503` em ate 5 segundos
e nenhuma resposta ou log revela o erro bruto.

## 6. Validate Independent Processes

Iniciar os processos long-lived:

```bash
docker compose up --build -d api worker-runner frontend
docker compose ps
```

Parar e iniciar cada container separadamente. Em cada operacao, confirmar que os outros continuam
ativos. Inspecionar o runner e confirmar que esta ocioso e que nenhuma sincronizacao foi iniciada.

Em homologacao, com credenciais controladas, validar o job one-shot:

```bash
docker compose exec worker-runner python -m src.sync_service
```

Expected outcomes:

- O comando executado e `python -m src.sync_service`.
- API e frontend podem permanecer desligados durante a execucao.
- O processo da tarefa encerra ao concluir e o runner permanece ocioso.
- Uma nova sincronizacao exige um novo acionamento explicito.
- O teste so ocorre em homologacao, sem fluxo manual concorrente. Em producao, a tarefa permanece
  bloqueada ate a feature 002 comprovar exclusao mutua.

## 7. Validate Streamlit Regression

Acessar o dominio de homologacao do frontend e validar `Visao geral`, `Vendedores` e `Conversas`,
todos os filtros, metricas, estados vazios, exportacoes e a presenca do fluxo manual existente.
Executar a sincronizacao manual somente em homologacao isolada. O smoke test automatizado deve
iniciar o Streamlit com dependencias controladas e comprovar que as tres abas carregam sem excecao.

## 8. Validate Schema And Synchronization Boundaries

Capturar o schema-only do PostgreSQL descartavel antes e depois dos testes e comparar os arquivos.
O diff deve estar vazio. Executar os testes de caracterizacao da sincronizacao e confirmar ordem,
interpretador, modulos, argumentos, codigos de saida e resultados de negocio. Repetir sucesso e
falha parcial com token, DSN, telefone, IDs de sessao/contato/mensagem e conteudo semeados. Confirmar
que respostas, excecoes, stdout/stderr de cada etapa, saida agregada e UI nao exibem nenhum valor.

```bash
python -m pytest
```

Se a suite ampla coletar scripts diagnosticos legados que exigem servicos externos, registrar essa
limitacao e executar somente a suite automatizada isolada; nunca apontar esses scripts para producao.

## 9. Validate Coolify

No ambiente de homologacao do Coolify:

1. Confirmar que a feature 002 foi implementada e validada antes de implantar esta feature em producao.
2. Implantar o Compose e confirmar que o worker runner permanece ocioso.
3. Confirmar os domains apenas para API e frontend.
4. Confirmar que as imagens dos containers possuem o mesmo digest.
5. Consultar health e readiness pela rota externa da API.
6. Reiniciar cada container separadamente e verificar os demais.
7. Confirmar que configuracao ausente produz readiness `503`, sem aparecer em logs.
8. Apos o gate de concorrencia, criar a tarefa Coolify no runner com o comando exato e executa-la uma
   vez; confirmar que o processo termina e nao e repetido automaticamente.

## Completion Evidence

- Locks regenerados sem diff e instalacao por hash aprovada
- Digest comum registrado para API, worker runner e frontend
- Contrato HTTP aprovado, inclusive rotas ausentes e redacao
- Processos reiniciados isoladamente sem efeito cruzado
- Worker caracterizado e executado em homologacao pelo comando estavel, sem repeticao
- Gate da feature 002 aprovado antes de qualquer ativacao produtiva
- Todas as abas e fluxos Streamlit inventariados e validados sem regressao
- Comparacao de schema sem alteracoes
- Logs inspecionados sem segredos ou dados sensiveis
