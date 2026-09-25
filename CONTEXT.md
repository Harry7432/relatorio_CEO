# Domain Context: Relatório CEO (`relatorio_CEO`)

## Executive Summary

`relatorio_CEO` é uma plataforma de inteligência e acompanhamento executivo comercial que consolida dados de atendimentos, sessões de chat, mensagens e métricas de vendedores a partir da plataforma BotNext (Hub de Comunicação). 

O sistema expõe:
1. **Frontend (Streamlit)**: Painel executivo interativo com visões por vendedor, canal e conversas.
2. **API (FastAPI)**: Rotas mínimas de liveness (`GET /health`) e readiness com PostgreSQL (`GET /ready`).
3. **Worker (Python)**: Processo desacoplado responsável por executar a sincronização incremental dos dados (`python -m src.sync_service`).

---

## Boundaries & Non-Goals

- **Isolamento de Estado**: O banco de dados PostgreSQL é a fonte da verdade para leituras analíticas do dashboard.
- **Redação de Dados Sensíveis**: Senhas, DSNs, telefones e conteúdos de mensagens são estritamente higienizados antes de qualquer exposição em logs, erros de API ou stdout/stderr.
- **Imutabilidade de Schema**: Nenhuma alteração DDL ou adição de migration é permitida fora de especificações formais de banco de dados.
- **Exclusão Mútua**: A ativação de tarefas agendadas de sincronização em ambiente produtivo requer controle de concorrência com o disparo manual.

---

## Glossary & Ubiquitous Language

| Termo | Definição no Domínio | Termos a Evitar |
| :--- | :--- | :--- |
| **Sessão** | Período contínuo de atendimento entre um cliente/contato e a equipe comercial via canal de atendimento. | *Ticket de suporte*, *atendimento avulso* |
| **Contato** | Entidade cliente final associada a um número de telefone e nome de cadastro/WhatsApp. | *Lead genérico*, *usuário final* |
| **Mensagem** | Unidade individual de comunicação trafegada na sessão (direção `TO_HUB` ou `FROM_HUB`). | *Payload*, *chat item* |
| **Vendedor** | Usuário comercial responsável pela condução de uma sessão e interação com o contato. | *Agente genérico*, *atendente* |
| **Sincronização** | Processo incremental de ingestão de usuários, contatos, sessões e mensagens via BotNext API. | *ETL genérico*, *dump* |
| **Hub** | Plataforma BotNext de onde derivam os dados operacionais de comunicação comercial. | *Backend principal*, *servidor externo* |
| **Canal** | Meio de comunicação (ex.: WhatsApp) vinculado ao identificador do canal de atendimento. | *Plataforma*, *rede social* |

---

## Architectural Decision Records (ADRs)

Todas as decisões de arquitetura duráveis deste contexto são registradas sequencialmente em `docs/adr/`.
Consulte `docs/adr/` antes de propor alterações estruturais no sistema.
