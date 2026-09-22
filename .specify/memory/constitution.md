<!--
Sync Impact Report
- Version change: unversioned scaffold -> 1.0.0
- Modified principles:
  - Template Principle 1 -> I. Evolucao Incremental da Arquitetura
  - Template Principle 2 -> II. PostgreSQL como Fonte de Verdade
  - Template Principle 3 -> III. Processos Independentes e Contrato Estavel do Worker
  - Template Principle 4 -> IV. Sincronizacao Confiavel e Segura
  - Template Principle 5 -> V. Regras Criticas Verificadas
- Added sections:
  - Restricoes Arquiteturais
  - Fluxo de Entrega
- Removed sections: none
- Follow-up TODOs: none
-->
# Relatorio Comercial BotNext Constitution

## Core Principles

### I. Evolucao Incremental da Arquitetura
A arquitetura funcional existente MUST ser preservada e evoluida por mudancas pequenas,
compativeis e justificadas por uma necessidade observavel. Refatoracoes amplas, substituicoes de
tecnologia e novas abstracoes MUST demonstrar beneficio concreto e incluir uma estrategia de
transicao que mantenha o sistema operacional. Esta regra reduz risco e permite validar cada etapa
antes de ampliar seu alcance.

### II. PostgreSQL como Fonte de Verdade
O PostgreSQL MUST ser a fonte de verdade dos dados persistidos e consumidos pelo produto. Nenhum
cache, estado em memoria, arquivo local ou sistema externo pode substituir silenciosamente o estado
persistido no PostgreSQL. Alteracoes de schema MUST responder a uma necessidade comprovada, ser
entregues por migration versionada e documentar compatibilidade, aplicacao e reversao. Esta regra
assegura consistencia e torna a evolucao dos dados auditavel.

### III. Processos Independentes e Contrato Estavel do Worker
Worker, API e frontend MUST possuir ciclos de execucao independentes; a indisponibilidade ou o
reinicio de um deles nao pode exigir que os demais compartilhem o mesmo processo. A comunicacao
entre eles MUST ocorrer por contratos explicitos e persistencia controlada. O comando
`python -m src.sync_service` MUST permanecer como a interface publica e estavel para iniciar o
worker; qualquer mudanca incompativel exige migration operacional documentada e incremento MAJOR
desta constituicao. A separacao limita acoplamento e permite operacao, escala e diagnostico
independentes.

### IV. Sincronizacao Confiavel e Segura
Toda sincronizacao MUST ser idempotente, produzir sinais observaveis de inicio, termino, duracao,
resultado e falha, e impedir execucoes concorrentes que possam duplicar ou corromper dados. Retentativas
MUST preservar os mesmos invariantes da primeira execucao. Segredos, credenciais, tokens e dados
sensiveis MUST permanecer fora do repositorio e MUST ser removidos ou mascarados de logs, erros e
telemetria. Essas garantias tornam a operacao repetivel sem sacrificar integridade ou
confidencialidade.

### V. Regras Criticas Verificadas
Regras cuja falha altere metricas, integridade dos dados, idempotencia, concorrencia, autorizacao,
privacidade ou contratos entre processos MUST possuir testes automatizados. Uma alteracao nessas
regras MUST incluir ou atualizar testes que falhem sem a implementacao correspondente e cubram os
principais casos de erro. Testes de integracao MUST ser usados quando a garantia depender do banco,
de migrations ou da comunicacao entre processos. Esta regra transforma requisitos operacionais e
de negocio em verificacoes reproduziveis.

## Restricoes Arquiteturais

- O frontend Streamlit MUST permanecer disponivel como interface de referencia ate que a interface
  React demonstre paridade funcional validada para todos os fluxos em uso.
- A paridade do React MUST ser registrada por criterios verificaveis de comportamento, dados,
  filtros, estados de erro e fluxos operacionais antes da retirada do Streamlit.
- A API MUST expor contratos explicitos e nao pode transformar o frontend em fonte de verdade.
- O worker MUST operar sem depender do ciclo de vida da API ou do frontend.
- Configuracao sensivel MUST ser fornecida em tempo de execucao por mecanismo externo ao codigo
  versionado. Arquivos de exemplo podem conter apenas nomes e valores ficticios seguros.

## Fluxo de Entrega

Toda nova feature MUST seguir, nesta ordem, as etapas `specify`, `plan`, `tasks`, `implement` e
`converge`. Cada etapa MUST produzir criterios ou evidencias suficientes para revisar a etapa
seguinte; a implementacao nao pode substituir requisitos ou decisoes ausentes. O `converge` MUST
confirmar aderencia a especificacao, testes aplicaveis, migrations versionadas, observabilidade,
seguranca de dados e independencia dos processos antes de considerar a feature concluida.

Revisoes MUST verificar explicitamente os principios desta constituicao. Excecoes temporarias MUST
ser documentadas com justificativa, impacto, responsavel e prazo de remocao; conveniencia ou pressa
isoladamente nao constituem justificativa.

## Governance

Esta constituicao prevalece sobre praticas, planos e documentos conflitantes do projeto. Emendas
MUST ser propostas com motivacao, impacto de compatibilidade e plano de migracao quando afetarem
codigo, dados ou operacao. A aprovacao exige revisao explicita por um mantenedor responsavel pelo
projeto e atualizacao da versao e da data de emenda neste documento.

A versao segue Semantic Versioning: MAJOR para remocao ou redefinicao incompativel de principios;
MINOR para novo principio, nova secao normativa ou expansao material; PATCH para esclarecimentos sem
mudanca normativa. Cada revisao de feature e cada etapa `converge` MUST registrar conformidade ou
excecoes aprovadas. A conformidade desta constituicao MUST ser revista sempre que arquitetura,
schema, contratos de processo ou estrategia de frontend forem alterados.

**Version**: 1.0.0 | **Ratified**: 2026-09-21 | **Last Amended**: 2026-09-21
