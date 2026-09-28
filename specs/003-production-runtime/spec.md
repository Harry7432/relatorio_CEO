# Feature Specification: Base de runtime de producao

**Feature Branch**: `main`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Criar a base de runtime de producao do relatorio_CEO no Coolify, com empacotamento Python reproduzivel, FastAPI expondo somente health e readiness, processos independentes para API e worker, preservacao do comando python -m src.sync_service, manutencao temporaria do Streamlit e nenhuma alteracao de schema ou da logica de sincronizacao."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publicar um runtime reproduzivel (Priority: P1)

Como operador, quero construir e iniciar o relatorio_CEO no ambiente de producao a partir de uma revisao conhecida para que implantacoes e recuperacoes usem o mesmo conjunto de dependencias e tenham comportamento previsivel.

**Why this priority**: Uma base reproduzivel e o requisito minimo para operar os demais processos com seguranca e repetir uma implantacao sem depender do estado de uma maquina anterior.

**Independent Test**: Pode ser testada construindo o runtime duas vezes, em ambientes limpos, a partir da mesma revisao e configuracao, e verificando que os mesmos processos iniciam com o mesmo conjunto de dependencias resolvidas.

**Acceptance Scenarios**:

1. **Given** uma revisao versionada e a configuracao obrigatoria disponivel, **When** o operador constroi o runtime duas vezes em ambientes limpos, **Then** ambas as construcoes resolvem as mesmas versoes de dependencias e iniciam com sucesso.
2. **Given** o runtime construido, **When** o operador seleciona o processo de API, worker ou frontend, **Then** somente o processo selecionado e iniciado com seu proprio comando e ciclo de vida.
3. **Given** uma configuracao necessaria ausente, **When** o papel correspondente e verificado ou usado, **Then** ele informa explicitamente que nao esta disponivel sem registrar segredos ou dados sensiveis.

---

### User Story 2 - Verificar saude e prontidao da API (Priority: P2)

Como operador, quero consultar separadamente a saude e a prontidao da API para que a plataforma de producao saiba quando o processo esta ativo e quando pode receber trafego.

**Why this priority**: Probes distintos permitem reiniciar processos inativos e evitar o envio de trafego antes que as dependencias obrigatorias estejam disponiveis.

**Independent Test**: Pode ser testada iniciando apenas a API, consultando os dois probes em estados pronto e nao pronto, e confirmando que nenhuma outra operacao publica esta disponivel.

**Acceptance Scenarios**:

1. **Given** que o processo da API esta ativo, **When** o probe de health e consultado, **Then** ele informa que o processo esta vivo sem depender do worker ou do frontend.
2. **Given** que a API possui toda configuracao e dependencias obrigatorias disponiveis, **When** o probe de readiness e consultado, **Then** ele informa que o processo esta pronto para receber trafego.
3. **Given** que uma dependencia obrigatoria esta indisponivel, **When** os probes sao consultados, **Then** health continua representando o estado do processo e readiness informa que ele nao esta pronto.
4. **Given** que qualquer operacao diferente de health e readiness e solicitada, **When** a API recebe a solicitacao, **Then** nenhuma funcionalidade ou dado de negocio e exposto.

---

### User Story 3 - Operar processos sem acoplamento (Priority: P3)

Como operador, quero iniciar, interromper e reiniciar API, worker e frontend separadamente para que manutencao ou falha em um processo nao interrompa os demais.

**Why this priority**: A independencia operacional reduz o impacto de falhas e preserva o worker e o Streamlit durante a evolucao incremental da arquitetura.

**Independent Test**: Pode ser testada reiniciando API e frontend isoladamente e, em homologacao sem outra sincronizacao ativa, executando o worker uma vez pelo comando publico atual; os demais processos continuam ativos.

**Acceptance Scenarios**:

1. **Given** que API, worker e Streamlit estao ativos, **When** a API e reiniciada, **Then** o worker e o Streamlit permanecem ativos.
2. **Given** o runtime de producao disponivel, **When** o operador executa `python -m src.sync_service`, **Then** o worker inicia pela interface publica existente sem depender da API ou do Streamlit.
3. **Given** que o Streamlit e interrompido, **When** o worker executa uma sincronizacao, **Then** sua execucao nao depende do ciclo de vida do frontend.
4. **Given** a nova base de runtime implantada, **When** o CEO acessa o frontend Streamlit existente, **Then** os fluxos atuais continuam disponiveis enquanto nao houver paridade validada com o React.

---

### Edge Cases

- Se a API estiver viva, mas uma dependencia obrigatoria estiver indisponivel, health deve permanecer distinto de readiness.
- Se API, worker ou frontend encerrar inesperadamente, os demais processos nao devem ser encerrados ou reiniciados por esse evento.
- A ativacao produtiva do worker MUST permanecer bloqueada ate que a protecao de concorrencia da feature 002 esteja implementada e validada; esta feature nao cria nem substitui essa protecao.
- Se uma variavel obrigatoria estiver ausente ou invalida, a falha deve indicar o nome da configuracao sem revelar seu valor.
- Se uma rota desconhecida, documentacao automatica ou descricao de contrato for solicitada na API de producao, nenhuma operacao alem de health e readiness deve ser exposta.
- Se duas construcoes partirem da mesma revisao, mas de maquinas limpas diferentes, a resolucao de dependencias deve permanecer equivalente.
- Se o novo runtime for adotado enquanto o Streamlit estiver em uso, o frontend atual deve continuar acessivel sem migracao de interface.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O projeto MUST fornecer uma base de runtime de producao implantavel no Coolify.
- **FR-002**: O empacotamento Python MUST declarar e fixar todas as dependencias necessarias para que uma mesma revisao produza ambientes equivalentes em construcoes limpas.
- **FR-003**: O runtime MUST permitir iniciar API, worker e frontend como processos separados, cada um com comando, configuracao e ciclo de vida proprios.
- **FR-004**: A API MUST usar FastAPI e disponibilizar publicamente somente as operacoes de health e readiness.
- **FR-005**: A operacao de health MUST representar apenas se o processo da API esta ativo e capaz de responder.
- **FR-006**: A operacao de readiness MUST representar se a API possui configuracao valida e acesso as dependencias obrigatorias para operar.
- **FR-007**: Health e readiness MUST retornar estados inequivocos para uso pelos mecanismos de verificacao da plataforma de producao.
- **FR-008**: Rotas de negocio, documentacao interativa, descricao publica de contrato e qualquer outra operacao da API MUST permanecer indisponiveis nesta feature.
- **FR-009**: O worker MUST continuar iniciando pelo comando publico `python -m src.sync_service`.
- **FR-010**: O inicio e a execucao do worker MUST NOT depender de a API ou o frontend estarem ativos.
- **FR-011**: O inicio e a execucao da API MUST NOT depender de o worker ou o frontend estarem ativos.
- **FR-012**: O frontend Streamlit existente MUST permanecer executavel e disponivel durante a transicao para React.
- **FR-013**: A retirada ou substituicao do Streamlit MUST permanecer fora do escopo ate existir validacao de paridade funcional do React.
- **FR-014**: A feature MUST NOT criar, remover ou alterar tabelas, colunas, indices, constraints ou migrations de banco de dados.
- **FR-015**: A feature MUST NOT alterar regras, ordem de etapas, persistencia, idempotencia, concorrencia ou resultados da sincronizacao existente.
- **FR-016**: A configuracao de cada processo MUST ser fornecida em tempo de execucao sem versionar credenciais, tokens, connection strings ou outros segredos.
- **FR-017**: Falhas de configuracao e logs de inicializacao MUST identificar o processo e o problema sem expor valores sensiveis ou dados de negocio.
- **FR-018**: A mesma base empacotada MUST permitir selecionar qual dos tres processos executar sem exigir alteracao no artefato da aplicacao.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Duas construcoes limpas da mesma revisao e configuracao resolvem 100% das dependencias nas mesmas versoes e iniciam os tres processos previstos.
- **SC-002**: Em 100% dos testes operacionais, o operador identifica em menos de 30 segundos se a API esta viva e se esta pronta para receber trafego.
- **SC-003**: Em uma verificacao de todas as operacoes publicas, exatamente duas categorias de diagnostico estao disponiveis e nenhuma informacao de negocio e retornada.
- **SC-004**: Em testes de interrupcao e reinicio de API e frontend e em uma execucao controlada do worker, os demais processos permanecem ativos em 100% das tentativas.
- **SC-005**: Em 100% dos testes de regressao, o comando publico existente do worker continua iniciando a sincronizacao com os mesmos resultados de negocio, ordem de etapas e codigos de saida; mensagens inseguras podem ser substituidas por diagnosticos sanitizados.
- **SC-006**: A comparacao estrutural do banco antes e depois da entrega apresenta zero alteracoes de schema.
- **SC-007**: Todos os fluxos do frontend atual cobertos pela validacao existente permanecem acessiveis apos a adocao do novo runtime.
- **SC-008**: Um operador com as configuracoes necessarias consegue iniciar ou reiniciar individualmente API, worker runner ou frontend em ate 15 minutos, sem editar o artefato da aplicacao.
- **SC-009**: Em testes com configuracao ausente e falhas de inicializacao, zero segredos ou dados sensiveis aparecem nas respostas e nos registros operacionais.

## Assumptions

- O Coolify ja esta disponivel e possui acesso ao repositorio e ao ambiente de producao; provisionamento da plataforma fica fora do escopo.
- O PostgreSQL existente continua sendo a fonte de verdade e suas credenciais sao fornecidas externamente em tempo de execucao.
- Health e readiness sao probes operacionais sem autenticacao e, por isso, retornam apenas estado minimo, sem detalhes internos ou dados de negocio.
- A verificacao de readiness considera somente configuracoes e dependencias realmente obrigatorias para a API; o worker e o frontend nao sao dependencias de prontidao da API.
- O agendamento, a frequencia e as protecoes de concorrencia da sincronizacao pertencem ao comportamento existente ou a features separadas.
- A implementacao atual ainda nao possui protecao de concorrencia; concluir ou implantar esta feature em producao depende da implementacao e validacao da feature 002, inclusive para o fluxo manual do Streamlit.
- Esta feature entrega a base para implantacao, mas nao adiciona endpoints de negocio, React, migrations, mudancas de dashboard ou mudancas na sincronizacao.
- Os mecanismos atuais de validacao funcional do Streamlit e da sincronizacao serao reutilizados para detectar regressao.
