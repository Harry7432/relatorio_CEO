export interface SellerRankingItem {
  posicao: number;
  vendedor: string;
  mensagens_enviadas: number;
  participacao_percentual: number;
}

export interface MetricSummary {
  total_mensagens: number;
  total_sessoes: number;
  total_contatos: number;
  percentual_contatos_identificados: number;
  vendedores_total_mensagens_enviadas: number;
  ranking: SellerRankingItem[];
}

export interface MensagemPorDia {
  data: string;
  mensagens: number;
}

export interface MensagemPorTipo {
  tipo: string;
  quantidade: number;
}

export interface SessaoPorStatus {
  status: string;
  conversas: number;
}

export interface MensagemPorCanal {
  canal: string;
  mensagens: number;
}

export interface ContatoPorVendedor {
  vendedor: string;
  origem: string;
  contatos: number;
}

export interface DashboardOverview {
  mensagens_por_dia: MensagemPorDia[];
  mensagens_por_tipo: MensagemPorTipo[];
  sessoes_por_status: SessaoPorStatus[];
  mensagens_por_canal: MensagemPorCanal[];
  contatos_por_vendedor: ContatoPorVendedor[];
}

export interface ConversationItem {
  timestamp_mensagem: string;
  vendedor_responsavel: string;
  origem_vendedor: string;
  contato_nome: string;
  telefone_formatado: string;
  canal: string;
  status_sessao: string;
  tipo_mensagem: string;
  direcao: string;
  usuario_mensagem: string;
  texto: string;
  sessao_id: string;
}

export interface ConversationsResponse {
  items: ConversationItem[];
  total: number;
  page: number;
  pages: number;
}

export interface FilterOptions {
  data_minima: string;
  data_maxima: string;
  vendedores: string[];
  canais: string[];
  status_sessao: string[];
  tipos_mensagem: string[];
  direcoes: string[];
  origens_vendedor: string[];
}

export interface ActiveFilters {
  data_inicial?: string;
  data_final?: string;
  vendedores?: string[];
  canais?: string[];
  status_sessao?: string[];
  tipos_mensagem?: string[];
  direcoes?: string[];
  origens_vendedor?: string[];
  search_cliente?: string;
  search_mensagem?: string;
}
