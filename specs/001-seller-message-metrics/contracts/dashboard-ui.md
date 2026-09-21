# Dashboard UI Contract: Utilizacao por vendedor

## Surface

A metrica sera exibida na aba existente **Vendedores** do dashboard. Os componentes atuais que nao fazem parte desta feature permanecem disponiveis.

## Inputs

### Period

- Reutiliza o controle lateral **Periodo das mensagens**.
- Exige data inicial e final.
- As duas datas sao inclusivas.
- Se apenas uma data estiver informada, a secao orienta o usuario a completar o intervalo e nao apresenta metricas parciais.
- Se a data inicial for posterior a final, a secao informa o erro e nao calcula resultados.

### Channel

- Reutiliza o controle lateral **Canal comercial**.
- Nenhum canal selecionado significa todos os canais disponiveis.
- Um ou mais canais selecionados limitam toda a secao ao conjunto escolhido.

### Filter Isolation

Os filtros globais de vendedor responsavel, status de sessao, tipo, direcao, origem do vendedor e pesquisas nao alteram esta metrica. Essa separacao preserva a definicao comparavel de utilizacao, que depende somente de periodo e canal.

## Business Eligibility

Uma mensagem conta como utilizacao quando:

1. Esta no periodo e canal selecionados.
2. Possui direcao persistida `TO_HUB`.
3. Possui usuario remetente identificado no registro da mensagem.
4. Ainda nao foi contada para o mesmo `mensagem_id`.

Mensagens `FROM_HUB`, campanhas ou automacoes sem usuario remetente e repeticoes da mesma identidade nao entram no resultado.

## Seller Attribution

- A atribuicao usa `vendedor_responsavel`, produzido pela regra atual do projeto.
- Valor ausente ou vazio aparece como **Não identificado**.
- A feature nao recalcula nem altera carteira, etiqueta ou regra de identificacao.

## Outputs

### Total

- Rotulo: **Mensagens enviadas por vendedores**.
- Valor: numero inteiro de mensagens elegiveis e unicas na selecao.
- O valor deve ser igual a soma da coluna **Mensagens enviadas**.

### Ranking Table

| Column | Contract |
|--------|----------|
| `Posicao` | Inteiro sequencial iniciado em 1 apos a ordenacao. |
| `Vendedor` | Nome identificado ou `Não identificado`. |
| `Mensagens enviadas` | Inteiro de mensagens elegiveis e unicas. |
| `Participacao` | Percentual calculado sobre o total antes da formatacao. |

### Ordering

1. `Mensagens enviadas` decrescente.
2. `Vendedor` crescente para desempate.

### Percentage Presentation

- Exibir com uma casa decimal e separador adequado ao dashboard.
- Manter precisao integral no calculo.
- Diferenca visual de arredondamento na soma dos percentuais e aceitavel; o total absoluto e a referencia.

## Empty State

Quando nenhuma mensagem elegivel corresponder ao periodo e canal:

- Exibir total igual a zero.
- Exibir mensagem explicita: **Nenhuma mensagem enviada por vendedores no periodo e canal selecionados.**
- Nao exibir ranking vazio nem percentuais indefinidos.
- Nao interromper as demais abas ou secoes do dashboard.

## Error State

Se faltar identidade de mensagem ou houver a mesma identidade associada a vendedores conflitantes:

- Nao exibir numeros parciais da metrica.
- Exibir mensagem segura de indisponibilidade da metrica.
- Registrar apenas contexto operacional necessario, sem texto de mensagens, credenciais ou dados pessoais.

## Acceptance Mapping

| Requirement | Contract evidence |
|-------------|-------------------|
| FR-001, FR-002, FR-013, FR-016 | Inputs and Filter Isolation |
| FR-003, FR-004, FR-005 | Business Eligibility |
| FR-006 to FR-011 | Total, Ranking Table, Ordering and Percentage Presentation |
| FR-012 | Seller Attribution |
| FR-014 | Empty State |
| FR-015, FR-017 | Existing dashboard surface and persisted projection only |
