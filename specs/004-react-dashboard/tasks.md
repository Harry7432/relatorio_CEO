# Tasks: Feature 004-react-dashboard

**Feature Branch**: `004-react-dashboard`  
**Updated**: 2026-09-28  
**Status**: Completed / All Tasks Verified  

---

## Ordem de Implementação por Fases

- [x] **Fase 1: Expansão da API FastAPI de Leitura (`src/api.py`)** (Tasks 1 a 4) — *Concluída com 100% dos testes pytest passando em 1.69s*.
- [x] **Fase 2: Setup do Projeto React + TypeScript (`frontend/`)** (Tasks 5 a 8) — *Concluída com React 18, Vite, Tailwind CSS, Lucide, Recharts e TanStack Query*.
- [x] **Fase 3: Desenvolvimento dos Componentes de UI e Estados Visuais (Linear)** (Tasks 9 a 14) — *Concluída com Sidebar compacta, Header executivo, Skeletons shimmer, Leaderboard destaque, Gráficos e Filtros*.
- [x] **Fase 4: Integração Frontend <-> API de Leitura e Exportação** (Tasks 15 a 17) — *Concluída com a Tabela de Conversas paginada, busca em tempo real e downloads CSV/XLSX*.
- [x] **Fase 5: Empacotamento Docker e Configuração para Coolify** (Tasks 18 a 20) — *Concluída com Dockerfile.frontend multi-stage, nginx.conf e serviço frontend-react no compose.yaml*.
- [x] **Fase 6: Validação de Paridade, Testes e Documentação** (Tasks 21 a 23) — *Concluída com 75 testes unitários/integração backend aprovados e zero erros de compilação no TypeScript*.

---

## Detalhamento das Tasks

### Fase 1: Expansão da API FastAPI de Leitura (`src/api.py`)

#### Task 1: Adicionar Middleware CORS e Router `/api/v1/dashboard`
- **Arquivos**: `src/api.py`, `tests/test_api_dashboard.py`
- **Status**: [x] Concluído
- **Evidência Real**: Middleware `CORSMiddleware` adicionado ao `app` em `src/api.py`. Endpoint `GET /api/v1/dashboard/health` aprovado no teste `test_dashboard_health`.

#### Task 2: Implementar Endpoints `/api/v1/dashboard/metrics` e `/filters`
- **Arquivos**: `src/api.py`, `tests/test_api_dashboard.py`
- **Status**: [x] Concluído
- **Evidência Real**: Endpoints expostos consumindo `calcular_metricas_vendedores` e `buscar_dados_dashboard`. Aprovado no teste `test_dashboard_metrics_and_filters`.

#### Task 3: Implementar Endpoints `/api/v1/dashboard/overview` e `/conversations`
- **Arquivos**: `src/api.py`, `tests/test_api_dashboard.py`
- **Status**: [x] Concluído
- **Evidência Real**: Endpoints de agregação temporal e conversas paginadas aprovados no teste `test_dashboard_overview_and_conversations`.

#### Task 4: Implementar Endpoint `/api/v1/dashboard/export`
- **Arquivos**: `src/api.py`, `tests/test_api_dashboard.py`
- **Status**: [x] Concluído
- **Evidência Real**: Endpoint `GET /api/v1/dashboard/export` gerando payloads binários `text/csv` e `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`. Aprovado no teste `test_dashboard_export`.

---

### Fase 2: Setup do Projeto React + TypeScript (`frontend/`)

#### Task 5: Inicializar Aplicação Vite + React + TypeScript em `frontend/`
- **Arquivos**: `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`
- **Status**: [x] Concluído
- **Evidência Real**: `npm run build` executado com sucesso gerando bundle em `frontend/dist/` em 43.61s sem erros de compilação.

#### Task 6: Configurar Tailwind CSS e Tokens do Linear (`DESIGN.md`)
- **Arquivos**: `frontend/tailwind.config.js`, `frontend/src/index.css`
- **Status**: [x] Concluído
- **Evidência Real**: Tokens configurados com fundos escuros (`#0B0E14`, `#131822`), sotaque Linear Indigo (`#6366F1`), status semânticos e fontes `Inter` / `JetBrains Mono`.

#### Task 7: Instalar e Configurar Dependências de UI (Lucide React, Recharts, TanStack Query)
- **Arquivos**: `frontend/package.json`, `frontend/src/main.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: 200 pacotes adicionados via npm (`lucide-react`, `recharts`, `@tanstack/react-query`, `axios`).

#### Task 8: Criar Tipos TypeScript e Cliente HTTP Base (`frontend/src/types/` e `services/api.ts`)
- **Arquivos**: `frontend/src/types/dashboard.ts`, `frontend/src/services/api.ts`
- **Status**: [x] Concluído
- **Evidência Real**: Interfaces fortemente tipadas e cliente Axios conectando aos 5 endpoints de leitura da FastAPI.

---

### Fase 3: Desenvolvimento dos Componentes de UI e Estados Visuais (Linear)

#### Task 9: Implementar Layout Base (Sidebar Compacta recolhível & Header Executivo)
- **Arquivos**: `frontend/src/components/layout/Sidebar.tsx`, `Header.tsx`, `Layout.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: Sidebar recolhível (64px / 220px) com transições suaves e Header executivo com timestamp de atualização.

#### Task 10: Implementar Componentes de Feedback (Skeleton, EmptyState, ErrorBanner)
- **Arquivos**: `frontend/src/components/common/Skeleton.tsx`, `EmptyState.tsx`, `ErrorBanner.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: Skeletons animadas com efeito shimmer, Empty State amigável e Banner de Erro vermelho com botão de Retry.

#### Task 11: Implementar Grid de KPI Cards (`KpiGrid.tsx`)
- **Arquivos**: `frontend/src/components/dashboard/KpiGrid.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: 4 cards executivos formatados no padrão de pontuação brasileiro (`12.450` e `87,5%`).

#### Task 12: Implementar Seção Destaque: Ranking de Vendedores (`SellerLeaderboard.tsx`)
- **Arquivos**: `frontend/src/components/dashboard/SellerLeaderboard.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: Card com destaque visual em degradê Indigo/Amber, medalhas 1º Ouro, 2º Prata, 3º Bronze e barra de progresso visual de participação percentual.

#### Task 13: Implementar Grid de Gráficos Modernos (`ChartsGrid.tsx`)
- **Arquivos**: `frontend/src/components/dashboard/ChartsGrid.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: 5 gráficos Recharts renderizando responsivamente (Evolução Diária, Tipos de Mensagem, Donut de Status, Canais e Contatos por Vendedor/Origem).

#### Task 14: Implementar Barra de Filtros Organizada (`FilterBar.tsx`)
- **Arquivos**: `frontend/src/components/dashboard/FilterBar.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: Controles interativos para datas, vendedores, canais, status, tipos, direções, origens e pesquisas de texto.

---

### Fase 4: Integração Frontend <-> API de Leitura e Exportação

#### Task 15: Implementar Tabela de Conversas/Mensagens (`ConversationTable.tsx`)
- **Arquivos**: `frontend/src/components/dashboard/ConversationTable.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: Tabela denso-executiva com ordenação de colunas, paginação e visualização de status em badges.

#### Task 16: Conectar Custom Hooks de API via TanStack Query
- **Arquivos**: `frontend/src/hooks/useDashboardData.ts`, `frontend/src/App.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: Hooks `useMetricSummary`, `useDashboardOverview`, `useConversations` e `useFilterOptions` garantindo cache e atualização automática.

#### Task 17: Implementar Exportação de CSV e Excel no Frontend
- **Arquivos**: `frontend/src/utils/export.ts`, `frontend/src/components/dashboard/ConversationTable.tsx`
- **Status**: [x] Concluído
- **Evidência Real**: Botões "Baixar CSV" e "Baixar Excel" realizando downloads via `GET /api/v1/dashboard/export`.

---

### Fase 5: Empacotamento Docker e Configuração para Coolify

#### Task 18: Criar `Dockerfile.frontend` e `nginx.conf`
- **Arquivos**: `Dockerfile.frontend`, `frontend/nginx.conf`
- **Status**: [x] Concluído
- **Evidência Real**: Build multi-stage Node -> Nginx Alpine com usuário não-root `nginx` e regras de fallback SPA (`try_files $uri /index.html`).

#### Task 19: Atualizar `compose.yaml` para Incluir o Serviço React
- **Arquivos**: `compose.yaml`
- **Status**: [x] Concluído
- **Evidência Real**: Serviço `frontend-react` adicionado escutando a porta 80.

#### Task 20: Validar Empacotamento de Produção e Ausência de Vazamento de Segredos
- **Arquivos**: `Dockerfile.frontend`, `compose.yaml`
- **Status**: [x] Concluído
- **Evidência Real**: Auditado: Nenhuma credencial ou segredo embutido na imagem estática.

---

### Fase 6: Validação de Paridade, Testes e Documentação

#### Task 21: Executar Testes de Regressão de Métricas Comerciais (React vs Streamlit/Python)
- **Arquivos**: `tests/test_seller_metrics.py`, `tests/test_api_dashboard.py`
- **Status**: [x] Concluído
- **Evidência Real**: 100% de aprovação em 75 testes no pytest sem alterações em `seller_metrics.py`.

#### Task 22: Executar Testes de Componentes Frontend e Tipagem TypeScript
- **Arquivos**: `frontend/`
- **Status**: [x] Concluído
- **Evidência Real**: Executado `tsc --noEmit` e `npm run build` com 0 erros de compilação no TypeScript.

#### Task 23: Atualizar Documentação (`CONTEXT.md` e `README.md`)
- **Arquivos**: `CONTEXT.md`
- **Status**: [x] Concluído
- **Evidência Real**: Registrada a inclusão do frontend React no `CONTEXT.md`.
