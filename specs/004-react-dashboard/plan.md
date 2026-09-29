# Implementation Plan: Feature 004-react-dashboard

**Feature Branch**: `004-react-dashboard`  
**Created**: 2026-09-28  
**Updated**: 2026-09-28  
**Status**: Plan / Ready for Implementation  

---

## 1. Visão Geral da Arquitetura

O objetivo desta feature é substituir o frontend legado em Streamlit por uma interface executiva moderna em **React + TypeScript** (Linear Design System), servida de forma desacoplada e alimentada via **FastAPI** por meio de endpoints de leitura.

```
+-------------------------------------------------------------------------+
|                              NAVEGADOR                                  |
|                 Dashboard React Executivo (Vite + TS)                   |
|   [ Sidebar ] [ KPIs ] [ Ranking ] [ Gráficos ] [ Filtros ] [ Tabela ]  |
+-------------------------------------------------------------------------+
                                    |
                                    | HTTP REST JSON (Somente Leitura)
                                    v
+-------------------------------------------------------------------------+
|                             FASTAPI (src/api.py)                        |
|  /health | /ready | /metrics | /overview | /conversations | /filters | /export|
+-------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
| src/seller_metrics.py |                       |src/dashboard_repo.py  |
|  (Lógica de Métricas) |                       | (Consultas PostgreSQL) |
+-----------------------+                       +-----------------------+
            |                                               |
            +-----------------------+-----------------------+
                                    v
+-------------------------------------------------------------------------+
|                         BANCO POSTGRESQL                                |
|   (Tabelas mensagens, sessoes, contatos, usuarios_botnext sem DDL)      |
+-------------------------------------------------------------------------+

===========================================================================
PROCESSO SEPARADO E INDEPENDENTE DE SINCRONIZAÇÃO (Features 002 e 003):
Coolify Cron / Manual Worker  --->  python -m src.sync_service  --->  PostgreSQL
(Sem alteração em src/sync_service.py ou src/sync_lock.py)
===========================================================================
```

---

## 2. Expansão da API Backend (FastAPI - `src/api.py`)

A FastAPI será expandida com os seguintes **5 endpoints de leitura** no prefixo `/api/v1/dashboard`:

### 2.1 Contratos de Endpoints HTTP

#### 1. `GET /api/v1/dashboard/metrics`
- **Parâmetros Query**: `data_inicial`, `data_final`, `canais` (opcional).
- **Descrição**: Invoca `src.seller_metrics.calcular_metricas_vendedores` e calcula os KPIs principais.
- **Resposta JSON**:
  ```json
  {
    "total_mensagens": 12450,
    "total_sessoes": 1420,
    "total_contatos": 980,
    "percentual_contatos_identificados": 87.5,
    "vendedores_total_mensagens_enviadas": 8450,
    "ranking": [
      {
        "posicao": 1,
        "vendedor": "Carlos Silva",
        "mensagens_enviadas": 3400,
        "participacao_percentual": 40.24
      }
    ]
  }
  ```

#### 2. `GET /api/v1/dashboard/overview`
- **Parâmetros Query**: `data_inicial`, `data_final`, `vendedores`, `canais`, `status`, `tipos`, `direcoes`, `origens`.
- **Descrição**: Retorna agregados temporais e distribuições para os 5 gráficos da interface.
- **Resposta JSON**:
  ```json
  {
    "mensagens_por_dia": [{"data": "2026-09-21", "mensagens": 450}],
    "mensagens_por_tipo": [{"tipo": "TEXT", "quantidade": 8900}],
    "sessoes_por_status": [{"status": "CLOSED", "conversas": 1200}],
    "mensagens_por_canal": [{"canal": "Comercial 1", "mensagens": 6500}],
    "contatos_por_vendedor": [{"vendedor": "Carlos Silva", "origem": "HUBSPOT", "contatos": 150}]
  }
  ```

#### 3. `GET /api/v1/dashboard/conversations`
- **Parâmetros Query**: `page` (default 1), `limit` (default 50), `search_cliente`, `search_mensagem`, mais filtros de data/vendedor/canal/status.
- **Descrição**: Retorna a lista detalhada de mensagens para a tabela paginada com busca.
- **Resposta JSON**:
  ```json
  {
    "items": [
      {
        "timestamp_mensagem": "2026-09-21T14:32:00Z",
        "vendedor_responsavel": "Carlos Silva",
        "origem_vendedor": "HUBSPOT",
        "contato_nome": "João Souza",
        "telefone_formatado": "+55 11 99999-8888",
        "canal": "Comercial 1 — +55 11 00000-0001",
        "status_sessao": "CLOSED",
        "tipo_mensagem": "TEXT",
        "direcao": "TO_HUB",
        "usuario_mensagem": "Carlos Silva",
        "texto": "Olá! Segue a proposta comercial.",
        "sessao_id": "00000000-0000-4000-8000-000000000001"
      }
    ],
    "total": 12450,
    "page": 1,
    "pages": 249
  }
  ```

#### 4. `GET /api/v1/dashboard/filters`
- **Descrição**: Retorna listas únicas de opções para popular os selects de filtro da sidebar e os limites de data mínimo/máximo presentes no banco.
- **Resposta JSON**:
  ```json
  {
    "data_minima": "2026-01-01",
    "data_maxima": "2026-09-28",
    "vendedores": ["Carlos Silva", "Ana Oliveira", "Não identificado"],
    "canais": ["Comercial 1 — +55 11 00000-0001"],
    "status_sessao": ["OPEN", "CLOSED"],
    "tipos_mensagem": ["TEXT", "IMAGE", "AUDIO"],
    "direcoes": ["TO_HUB", "FROM_HUB"],
    "origens_vendedor": ["HUBSPOT", "MANUAL", "NAO_IDENTIFICADO"]
  }
  ```

#### 5. `GET /api/v1/dashboard/export`
- **Parâmetros Query**: `format` (`csv` ou `xlsx`) + mesmos filtros ativos.
- **Descrição**: Gera arquivo binário `CSV` (utf-8-sig com delimitador `;`) ou `XLSX` (OpenPyXL) para download.

---

## 3. Arquitetura do Frontend React (`frontend/`)

### 3.1 Estrutura de Diretórios
```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Badge.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ErrorBanner.tsx
│   │   │   └── Skeleton.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Layout.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── dashboard/
│   │   │   ├── ChartsGrid.tsx
│   │   │   ├── ConversationTable.tsx
│   │   │   ├── FilterBar.tsx
│   │   │   ├── KpiGrid.tsx
│   │   │   └── SellerLeaderboard.tsx
│   ├── hooks/
│   │   ├── useConversations.ts
│   │   ├── useDashboardMetrics.ts
│   │   └── useFilters.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── dashboard.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── export.ts
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

### 3.2 Hierarquia da Árvore de Componentes

```
App
 └── Layout (Sidebar recolhível + Header Executivo)
      └── DashboardPage
           ├── FilterBar (Filtros de data, vendedores, canais, status, busca text)
           ├── KpiGrid (4 Cards KPI com Skeletons shimmer)
           ├── SellerLeaderboard (Ranking destaque com badges Ouro/Prata/Bronze & barra %)
           ├── ChartsGrid (Recharts: Evolução Diária, Tipos, Status Donut, Canais, Origens)
           └── ConversationTable (Tabela paginada + busca rápida + Botões CSV/XLSX)
```

---

## 4. Plano de Containerização e Deploy no Coolify

### 4.1 Estratégia de Build Multi-Stage (Dockerfile.frontend)
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4.2 Nginx SPA Configuration (`frontend/nginx.conf`)
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://api:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 5. Fases de Execução

1. **Fase 1 (Backend API Expansion)**: Criar e testar os 5 endpoints de leitura da FastAPI em `src/api.py`.
2. **Fase 2 (React FE Setup & Tokens)**: Inicializar projeto Vite em `frontend/`, configurar TypeScript, Tailwind CSS com tokens do Linear no `DESIGN.md`.
3. **Fase 3 (Componentes de UI & Estados)**: Construir os componentes visuais (Sidebar, Header, KPIs, Leaderboard, Filtros, Gráficos Recharts, Tabela) com suporte nativo a Loading, Empty e Error states.
4. **Fase 4 (Integração & Exportação)**: Conectar o frontend às APIs de leitura via React Query/Axios, implementar busca em tempo real, paginação e exportação de CSV/XLSX.
5. **Fase 5 (Docker & Coolify Setup)**: Criar `Dockerfile.frontend`, `nginx.conf` e atualizar `compose.yaml` para deploy em produção.
6. **Fase 6 (Validação e Paridade)**: Executar a suíte completa de testes de regressão backend/frontend e validar paridade de métricas com o Streamlit.
