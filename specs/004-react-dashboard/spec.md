# Feature Specification: Dashboard Executivo em React + TypeScript

**Feature Branch**: `004-react-dashboard`  
**Created**: 2026-09-28  
**Updated**: 2026-09-28  
**Status**: Draft / Ready for Agent  

---

## 1. Problem Statement

Atualmente, o dashboard analítico comercial do `relatorio_CEO` é construído sobre o frontend legado em **Streamlit** (`app.py`). Embora funcional para prototipação inicial, o Streamlit apresenta limitações críticas para um ambiente executivo de produção:
1. **Performance e Experiência de Usuário**: O Streamlit executa o script Python completo a cada interação de filtro, gerando re-renders custosos e latência perceptível ao usuário.
2. **Design e Customização Limitados**: A interface do Streamlit não atende aos padrões visuais executivos modernos de SaaS/analytics, dificultando a inclusão de componentes interativos ricos, layouts responsivos sob medida e animações de estado.
3. **Acoplamento de Processo**: O frontend em Streamlit consulta diretamente o repositório de banco de dados (`buscar_dados_dashboard`), sem consumir uma API HTTP estruturada com contratos de resposta JSON.
4. **Falta de Preparação para Escalabilidade de UI**: Não há separação clara entre a camada de apresentação (client-side) e os serviços backend (FastAPI), o que impede o deploy eficiente e desacoplado no Coolify.

---

## 2. Solution

Substituir o frontend legado em Streamlit por um dashboard executivo moderno de alta performance desenvolvido em **React + TypeScript**, localizado no diretório `frontend/`, que consome a API **FastAPI** existente (expandida em `src/api.py`).

O novo dashboard React:
1. **Segue Rigorosamente o `DESIGN.md` (Linear Design System)**: Adota a estética visual executiva estilo Linear (tema escuro de alta densidade, tipografia tabular, cards de KPI modernos, ranking destacado e gráficos interativos). Futuras adaptações de marca da empresa (Falavinha) ocorrerão sobre os tokens desse design system.
2. **Consome FastAPI Exclusivamente (Somente Leitura)**: Todos os dados, estatísticas e rankings são servidos por endpoints JSON estruturados de leitura da FastAPI (`/api/v1/dashboard/*`), sem duplicar qualquer regra de negócio ou lógica de cálculo de métricas no frontend.
3. **Preserva Estritamente a Arquitetura de Sincronização (Features 002 e 003)**:
   - **Worker / Sincronização**: `python -m src.sync_service` executado via Coolify ou trigger manual de worker.
   - **FastAPI**: Serviço de dados e leitura para o frontend.
   - **React**: Apresentação e interação com dados.
   - **Sem Alterações no Worker**: Os módulos `src/sync_service.py` e `src/sync_lock.py` NÃO serão alterados nesta feature.
4. **Oferece Estados de UI Completos**: Implementa **Loading Skeletons (Shimmer)** durante requisições, **Empty States** informativos para pesquisas sem resultados e **Error Banners** com capacidade de retry para falhas de rede/banco.
5. **Pronto para Deploy no Coolify**: Inclui configuração multi-stage Docker / Nginx / Vite para build estático e integração com a arquitetura de runtime neutra declarada no [ADR-0001](file:///c:/Users/harry.silva/Desktop/relatorio_CEO/docs/adr/0001-production-runtime-architecture.md).

---

## 3. User Stories

1. **As a CEO**, I want an executive commercial dashboard built in React + TypeScript with instant visual response and Linear design system aesthetic, so that I can monitor company-wide communications, seller performance, and conversion metrics effortlessly.
2. **As a CEO**, I want to view top KPI cards (Total Messages, Total Conversations, Total Contacts, % Identified Contacts, Total Seller Messages) at a glance, so that I can understand overall commercial volume instantly.
3. **As a Commercial Director**, I want a highlighted seller leaderboard/ranking showing messages sent, percentage share, and ranked positions (1st, 2nd, 3rd badges), so that I can motivate top sellers and track team engagement.
4. **As a Commercial Director**, I want modern interactive charts (daily volume trend, message type distribution, conversation status donut, channel distribution, contacts by seller/origin), so that I can identify peak operational days and bottleneck channels.
5. **As a Sales Manager**, I want a comprehensive filter bar (date range, sellers, channels, session status, message types, directions, seller origins), so that I can drill down into specific seller teams or WhatsApp channels.
6. **As a Sales Rep**, I want a searchable conversations table with real-time text/phone search, column sorting, and pagination, so that I can inspect specific customer messages quickly.
7. **As an Analyst**, I want to export filtered message reports to CSV and Excel directly from the React UI, so that I can conduct offline auditing or custom spreadsheet analysis.
8. **As an Operator**, I want feedback states for loading (skeletons), empty results, and API errors with retry buttons, so that the application never freezes or shows blank screens unexpectedly.
9. **As a DevOps Engineer**, I want the React application bundled in an optimized Docker image ready for deployment on Coolify, so that it runs decoupled from the FastAPI backend and Python background workers.

---

## 4. Requirements

### 4.1 Functional Requirements (FR)

- **FR-001**: O frontend MUST ser desenvolvido em React com TypeScript no diretório `frontend/`, utilizando Vite como build tool.
- **FR-002**: O frontend MUST consumir a API FastAPI (`src/api.py`) via rotas HTTP REST de leitura (`/api/v1/dashboard/*`), sem se conectar diretamente ao banco de dados ou acionar rotas de escrita/sincronização.
- **FR-003**: A FastAPI MUST expor exatamente os seguintes 5 endpoints de serviço de dados:
  - `GET /api/v1/dashboard/metrics`: Retorna métricas agregadas dos vendedores (via `src/seller_metrics.py`) e KPIs globais.
  - `GET /api/v1/dashboard/overview`: Retorna dados para gráficos de linha, barra, donut e barras horizontais.
  - `GET /api/v1/dashboard/conversations`: Retorna mensagens/conversas paginadas, filtradas e ordenadas.
  - `GET /api/v1/dashboard/filters`: Retorna opções de filtros disponíveis (vendedores, canais, status, tipos, direções, origens, limites de datas).
  - `GET /api/v1/dashboard/export`: Gera e faz download de relatórios em formato CSV e XLSX.
- **FR-004**: O frontend MUST incorporar a estrutura de layout definida em [DESIGN.md](file:///c:/Users/harry.silva/Desktop/relatorio_CEO/DESIGN.md) (Linear Design System):
  - Sidebar compacta recolhível (64px / 220px).
  - Header executivo com timestamp de atualização dos dados.
  - Grid de KPI Cards na área superior.
  - Card em destaque para o Ranking de Vendedores (Leaderboard com posições, medalhas de 1º/2º/3º e barras de participação %).
  - Grid de Gráficos Modernos em 2 colunas.
  - Barra de Filtros organizada com botão de reset.
  - Tabela de Conversas/Mensagens interativa com busca em tempo real e paginação.
- **FR-005**: O frontend MUST implementar estados visuais claros para todas as visões:
  - **Loading State**: Skeletons animados com efeito shimmer durante o carregamento de dados.
  - **Empty State**: Componentes informativos com ilustrações e botão para limpar filtros quando nenhum dado for encontrado.
  - **Error State**: Banners com borda vermelha e botão de "Tentar Novamente" em caso de falha de conexão com a FastAPI.
- **FR-006**: O frontend MUST ser totalmente responsivo (adaptando-se a telas mobile, tablet e desktop executivo).
- **FR-007**: A aplicação MUST ser empacotada em container Docker otimizado (multi-stage build com Nginx para servir assets estáticos em produção), pronta para deploy no Coolify.

### 4.2 Non-Functional Requirements (NFR)

- **NFR-001 (Preservação de Métricas)**: O frontend NUNCA deve recalcular regras de métricas comerciais ou posições de vendedores; o cálculo MUST residir estritamente no backend Python (`src/seller_metrics.py`).
- **NFR-002 (Imutabilidade de Schema e Worker)**: A feature NUNCA deve alterar, adicionar ou remover tabelas/colunas do PostgreSQL, nem modificar `src/sync_service.py` ou `src/sync_lock.py`.
- **NFR-003 (Separação de Papéis de Runtime)**: O frontend React NUNCA deve iniciar sincronização através da FastAPI; a sincronização é executada pelo worker desacoplado (`python -m src.sync_service`).
- **NFR-004 (Performance)**: As páginas do dashboard React devem carregar os dados via API em menos de 1 segundo em conexões padrão de produção.
- **NFR-005 (Segurança)**: Nenhuma chave API, DSN de banco de dados ou dado de mensagem sensível deve ser exposto em stderr, logs do console ou arquivos de build estático.
- **NFR-006 (Fidelidade Visual e Branding)**: O frontend MUST seguir estritamente o guia de estilos em [DESIGN.md](file:///c:/Users/harry.silva/Desktop/relatorio_CEO/DESIGN.md) (Linear). Adaptações da marca Falavinha serão feitas exclusivamente alterando tokens no design system.

---

## 5. Implementation Decisions

- **Frontend Stack**:
  - **Framework**: React 18+ com TypeScript (`tsx`).
  - **Build System**: Vite.
  - **Styling**: Tailwind CSS + Lucide React icons.
  - **Visual System**: Conforme declarado no [DESIGN.md](file:///c:/Users/harry.silva/Desktop/relatorio_CEO/DESIGN.md) (Linear Design System).
  - **Gráficos**: Recharts (linhas smooth, barras arredondadas, donuts com hole 60%).
  - **Gerenciamento de Estado de API**: TanStack Query (React Query) para caching, auto-refetch, debounce de busca e estados de loading/error transparentes.
  - **Exportação**: Utilitários client-side ou blobs gerados pelo endpoint `GET /api/v1/dashboard/export`.

- **Backend API Expansion (`src/api.py`)**:
  - Manter as rotas `/health` e `/ready` intactas.
  - Adicionar o prefixo `/api/v1/dashboard` com os 5 endpoints RESTful de leitura construídos sobre `src/dashboard_repository.py` e `src/seller_metrics.py`.
  - Habilitar Middleware CORS configurável.

- **Deploy & Runtime**:
  - Criar `Dockerfile.frontend` (multi-stage build com Nginx Alpine) para servir os arquivos estáticos compilados do React.
  - Atualizar `compose.yaml` adicionando o serviço `frontend-react`.

---

## 6. Testing Decisions

- **Costuras de Teste (Seams)**:
  1. **Backend Integration Tests** (`tests/test_api_dashboard.py`): Testar os 5 endpoints de leitura da FastAPI para validar schemas JSON, filtros de data, cálculo de ranking e tratamento de exceções com pytest e `TestClient`.
  2. **Frontend Unit & Component Tests** (`frontend/src/**/*.test.tsx`): Testar componentes de KPI, Leaderboard, Filtros e Tabelas com Vitest + React Testing Library.
  3. **Verification of Zero Schema/Sync Regressions**: Garantir zero alteração no banco e em `src/sync_service.py` / `src/sync_lock.py`.

---

## 7. Out of Scope

- Acionamento ou gatilhos de sincronização via frontend ou FastAPI (`POST /api/v1/dashboard/sync` foi removido desta feature).
- Alteração nos arquivos de sincronização `src/sync_service.py` e `src/sync_lock.py`.
- Alteração em schemas do PostgreSQL ou criação de tabelas intermediárias.
- Modificação nas regras de negócio ou na função `calcular_metricas_vendedores`.

---

## 8. Success Criteria

- **SC-001**: 100% dos 5 endpoints `/api/v1/dashboard/*` retornam respostas validadas com código HTTP 200 e tempos de resposta inferiores a 500ms.
- **SC-002**: O ranking de vendedores exibido na interface React coincide 100% com os valores gerados por `src/seller_metrics.py`.
- **SC-003**: Os estados de Loading Skeleton, Empty State e Error Banner funcionam comprovadamente em cenários simulados de carregamento, sem dados e falha de servidor.
- **SC-004**: O frontend React compila sem avisos ou erros de TypeScript (`tsc --noEmit`) e passa em 100% dos testes unitários e de integração.
- **SC-005**: O build Docker do frontend é executado com sucesso e roda de forma desacoplada no ambiente Coolify/Compose.
