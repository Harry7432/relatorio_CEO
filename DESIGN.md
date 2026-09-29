# DESIGN.md — Linear Design System (SaaS Executive UI)

> **Fonte da Verdade Visual** para a feature `004-react-dashboard` (`relatorio_CEO`).
> Baseado estritamente nas diretrizes do repositório `VoltAgent/awesome-design-md` para o **Linear Design System**.

---

## 1. Visão Geral e Filosofia de Design

O dashboard **Relatório Comercial CEO (BotNext)** adota com fidelidade a linguagem visual do **Linear**:
- **Alta Densidade e Precisão Executiva**: Apresentação clara e direta de KPIs, rankings e tabelas analíticas sem elementos supérfluos.
- **Superfícies Escuras Profundas e Bordas Sutis**: Divisores ultrafinos (`1px border-slate-800`), fundos escuros e sombras de elevação discretas.
- **Tipografia Numérica Tabular**: Uso de fontes mono/tabulares para KPIs, percentuais, IDs e timestamps.
- **Microinterações Fluídas**: Feedback tátil imediato (150ms cubic-bezier), hover states responsivos e iluminação semântica por status.
- **Estados Visuais Globais**: Tratamento rigoroso de **Loading (Skeletons Shimmer)**, **Empty States** e **Error States (Banners com ação de retry)**.

> [!NOTE]
> **Extensibilidade de Branding (Marca Falavinha)**:
> Futuras adaptações de marca da empresa (como a identidade da Falavinha) devem ocorrer exclusivamente através da alteração dos tokens de marca (tokens de cor primária, logos e variáveis em `tailwind.config.js` e CSS Variables), preservando intactos o layout, a densidade de informação, a estrutura de componentes e a filosofia do design system.

---

## 2. Paleta de Cores e Tokens do Design System

### 2.1 Tema Escuro (Linear Dark Principal)
- **Fundo Principal (Background)**: `#0B0E14` (Slate-950 ultradark)
- **Superfície / Cards (Surface)**: `#131822` (Slate-900 dark)
- **Superfície Elevada / Modais (Surface Elevated)**: `#1C2333` (Slate-850)
- **Bordas Sutis (Border Default)**: `#2A3447` (Slate-800)
- **Bordas em Destaque (Border Focus/Active)**: `#6366F1` (Indigo-500)

### 2.2 Cores de Ação e Destaques (Accents)
- **Primary Accent (Linear Indigo)**: `#6366F1` (Hover: `#4F46E5`, Active: `#4338CA`) — *Ponto de entrada para futura marca Falavinha*.
- **Secondary Accent (Cyan/Teal)**: `#0EA5E9` (Para gráficos de evolução e indicadores secundários)
- **Gold/Amber Accent (Ranking 1º Lugar)**: `#F59E0B` (Badge do vendedor líder no leaderboard)

### 2.3 Cores Semânticas de Status
- **Sucesso / Ativo / Identificado**: `#10B981` (Emerald-500) | Fundo Badge: `rgba(16, 185, 129, 0.12)`
- **Aviso / Pendente / Em Aberto**: `#F59E0B` (Amber-500) | Fundo Badge: `rgba(245, 158, 11, 0.12)`
- **Erro / Indisponível / Inativo**: `#EF4444` (Rose-500) | Fundo Badge: `rgba(239, 68, 68, 0.12)`
- **Neutro / Não Identificado / Automação**: `#64748B` (Slate-500) | Fundo Badge: `rgba(100, 116, 139, 0.12)`

### 2.4 Hierarquia de Texto
- **Texto Primário (Text Primary)**: `#F8FAFC` (Slate-50)
- **Texto Secundário (Text Secondary)**: `#94A3B8` (Slate-400)
- **Texto Muted / Caption (Text Muted)**: `#64748B` (Slate-500)

---

## 3. Tipografia e Escala

- **Família de Fonte Principal**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif`
- **Família Numérica / Códigos**: `JetBrains Mono`, `Fira Code`, `ui-monospace`, `monospace`

| Nível | Tamanho | Peso | Line Height | Aplicação |
| :--- | :--- | :--- | :--- | :--- |
| **Display 1** | `28px (1.75rem)` | Bold (`700`) | `1.2` | KPIs Principais (Valores em destaque) |
| **Heading 1** | `20px (1.25rem)` | SemiBold (`600`) | `1.3` | Título da Página / Header Executivo |
| **Heading 2** | `16px (1.0rem)` | SemiBold (`600`) | `1.4` | Títulos de Cards, Seções e Gráficos |
| **Subheading** | `14px (0.875rem)`| Medium (`500`) | `1.4` | Rótulos de Filtros, Headers de Tabelas |
| **Body Standard**| `14px (0.875rem)`| Regular (`400`) | `1.5` | Linhas de Tabelas, Textos de Mensagens |
| **Caption / Badge**|`12px (0.75rem)` | Medium (`500`) | `1.4` | Status, Timestamps, Metadados |

---

## 4. Layout, Grid e Estrutura Executiva

```
+-----------------------------------------------------------------------------------+
|  SIDEBAR  |  TOP BAR EXEC-HEADER (Título, Indicador de Atualização do Banco)       |
|  COMPACTA |-----------------------------------------------------------------------|
|  (64px /  |  KPI GRID (4 Cards: Mensagens, Conversas, Contatos, % Identificados) |
|   220px)  |-----------------------------------------------------------------------|
|           |  DESTACADO: RANKING DE VENDEDORES (Leaderboard + Métricas de Uso)    |
|           |-----------------------------------------------------------------------|
|           |  GRID DE GRÁFICOS (Evolução Diária, Por Tipo, Por Status, Por Canal)   |
|           |-----------------------------------------------------------------------|
|           |  BARRA DE FILTROS & SEARCH (Período, Vendedor, Canal, Status, Busca)  |
|           |-----------------------------------------------------------------------|
|           |  TABELA DE MENSAGENS / CONVERSAS (Paginação, Ordenação, Export CSV/XLSX)|
+-----------------------------------------------------------------------------------+
```

### 4.1 Sidebar Compacta
- Largura recolhida: `64px` (Apenas ícones Lucide React com tooltips).
- Largura expandida: `220px` (Ícone + Rótulo + Indicador de seção ativa).
- Itens de navegação:
  1. `📊 Visão Geral` (Dashboard Principal)
  2. `👥 Vendedores` (Ranking & Atribuição)
  3. `💬 Conversas` (Tabela Detalhada & Busca)

### 4.2 Grid de KPIs (Top Cards)
- 4 Colunas responsivas (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`).
- Contém rótulo, valor principal numérico formatado, ícone indicativo e borda sutil.

### 4.3 Leaderboard de Vendedores (Seção Destaque)
- Card amplo com fundo `#131822` e borda accent `#6366F1`.
- Medalhas visuais (1º Ouro, 2º Prata, 3º Bronze) e barra de progresso de participação percentual.

### 4.4 Gráficos Modernos (Recharts / Chart Engine)
- Gráfico de Linha (Evolução Diária), Barras (Mensagens por Tipo / Canal), Donut (Status da Sessão) e Barras Horizontais (Contatos por Vendedor/Origem).

### 4.5 Tabela de Conversas e Mensagens
- Layout denso (`44px` por linha), ordenação por coluna, campo de busca em tempo real e exportação (CSV/Excel).

---

## 5. Especificação de Componentes e Estados

### 5.1 Estado de Carregamento (Loading Skeleton)
- Shimmer animado (`animate-pulse` com gradiente `#1E232B` a `#2A3447`).

### 5.2 Estado Vazio (Empty State)
- Container centralizado com ícone ilustrativo desbotado e botão acionável "Limpar Filtros".

### 5.3 Estado de Erro (Error State)
- Banner com borda lateral vermelha (`border-l-4 border-rose-500`), mensagem amigável sanitizada e botão "Tentar Novamente" (Retry).

---

## 6. Responsividade

- Adaptável para `sm` (640px), `md` (768px), `lg` (1024px) e `xl` (1280px+).

---

## 7. Regras Estritas de Implementação Visual

1. **USAR EXCLUSIVAMENTE** o Linear como referência de design system.
2. **APLICAR** adaptações de marca (Falavinha) apenas sobre os tokens do design system (`tailwind.config.js`).
3. **PRESERVAR** a identidade dos status `TO_HUB` e `FROM_HUB`.
4. **NUNCA** duplicar lógica de métricas comerciais no frontend.
