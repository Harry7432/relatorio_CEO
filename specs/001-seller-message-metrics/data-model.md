# Data Model: Metricas de utilizacao por vendedor

## Scope

Este desenho nao cria nem altera tabelas. Ele define a projecao de leitura e os modelos logicos usados para calcular a metrica a partir dos dados ja persistidos.

## Entity: Message Projection

Representa uma mensagem persistida enriquecida com sessao, canal, contato e vendedor atual.

| Field | Source | Required | Rule |
|-------|--------|----------|------|
| `mensagem_id` | `mensagens.id` | Yes | Identidade logica usada para deduplicacao; nao pode estar vazia nas mensagens elegiveis. |
| `timestamp_mensagem` | `mensagens.timestamp_mensagem` | Yes | Convertido para a referencia de data atual do dashboard antes do filtro inclusivo. |
| `direcao` | `mensagens.direcao` | Yes | Somente `TO_HUB` e elegivel para utilizacao do vendedor. |
| `usuario_id_mensagem` | `mensagens.user_id` | Conditional | Deve estar preenchido para comprovar remetente humano; valores vazios excluem automacoes. |
| `channel_id` | `sessoes.channel_id` | Yes | Identidade persistida do canal. |
| `canal` | Derivado de `channel_id` | Yes | Rotulo reaproveitado pelo filtro atual; IDs sem mapeamento permanecem visiveis. |
| `vendedor_responsavel` | `contatos.vendedor_responsavel` | No | Identificacao atual do projeto; ausencia ou texto vazio vira `Não identificado`. |

### Eligibility Rules

Uma projecao participa da metrica quando todas as condicoes forem verdadeiras:

1. A data da mensagem esta entre inicio e fim, inclusive.
2. O canal esta entre os selecionados; selecao vazia significa todos os canais.
3. `direcao` e exatamente `TO_HUB`.
4. `usuario_id_mensagem` esta preenchido.
5. `mensagem_id` e valido.

## Entity: Analysis Selection

Representa os controles que definem o universo da metrica.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `data_inicial` | Date | Yes | Deve ser menor ou igual a `data_final`. |
| `data_final` | Date | Yes | Inclusiva e limitada ao intervalo disponivel no dashboard. |
| `canais` | List of channel labels | No | Lista vazia significa todos os canais; valores devem vir das opcoes existentes. |

Filtros globais de vendedor, status, tipo, direcao e texto nao pertencem a esta entidade e nao alteram a metrica.

## Entity: Seller Metric

Representa uma linha do ranking calculada a partir das mensagens elegiveis e deduplicadas.

| Field | Type | Required | Rule |
|-------|------|----------|------|
| `vendedor` | Text | Yes | `vendedor_responsavel` normalizado ou `Não identificado`. |
| `mensagens_enviadas` | Non-negative integer | Yes | Quantidade de identidades unicas de mensagem atribuidas ao vendedor. |
| `participacao_percentual` | Decimal | Yes for non-empty result | `mensagens_enviadas / total_geral * 100`, sem arredondamento interno. |
| `posicao` | Positive integer | Presentation only | Sequencia apos ordenar por volume decrescente e vendedor crescente. |

## Aggregate: Seller Usage Summary

| Field | Type | Rule |
|-------|------|------|
| `total_geral` | Non-negative integer | Soma exata de `mensagens_enviadas` de todas as linhas. |
| `ranking` | Ordered list of Seller Metric | Uma linha por vendedor, incluindo `Não identificado` quando aplicavel. |
| `sem_dados` | Boolean | Verdadeiro quando `total_geral == 0`; nao ha percentuais nesse estado. |

## Relationships

```text
Analysis Selection
        |
        v filters
Message Projection -- deduplicate by mensagem_id --> Eligible Message
        |                                              |
        | vendedor_responsavel                         | group by seller
        v                                              v
Current Seller Identification ----------------> Seller Metric
                                                       |
                                                       v
                                             Seller Usage Summary
```

## Integrity Rules

- Cada `mensagem_id` elegivel contribui no maximo uma vez para todo o resumo.
- Cada mensagem deduplicada pertence a exatamente um vendedor ou a `Não identificado`.
- A soma das linhas e sempre igual a `total_geral`.
- Para resultado nao vazio, os percentuais sem arredondamento totalizam 100% dentro de tolerancia numerica.
- Duplicatas com o mesmo ID e vendedores conflitantes sao erro de integridade e nao devem ser resolvidas pela ordem de entrada.
- A funcao de agregacao nao altera o dataframe recebido.

## State Transitions

Nao ha entidade persistente ou ciclo de estado novo. A interface possui somente estados derivados:

```text
Selecao incompleta/invalida -> Orientacao de correcao
Selecao valida sem elegiveis -> Total zero + estado sem dados
Selecao valida com elegiveis -> Total + ranking + percentuais
Erro de integridade          -> Mensagem de falha rastreavel, sem numeros parciais
```

## Schema Impact

- Migrations: none.
- New tables or columns: none.
- Write paths: unchanged.
- Synchronization payload and pagination: unchanged.
