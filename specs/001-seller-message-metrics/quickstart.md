# Quickstart: Validacao das metricas por vendedor

## Purpose

Validar que o dashboard calcula o volume de mensagens efetivamente enviadas por vendedor a partir dos dados persistidos, sem duplicidade e com filtros de periodo e canal.

## Prerequisites

- Ambiente virtual atual do projeto ativo.
- Variaveis de ambiente locais ja configuradas; nao imprimir nem versionar seus valores.
- PostgreSQL acessivel com dados sincronizados em `usuarios_botnext`, `contatos`, `sessoes` e `mensagens`.
- Dependencias do dashboard e pytest instalados.

## Automated Validation

Na raiz do repositorio:

```powershell
python -m pytest tests/test_seller_metrics.py -q
```

Os testes devem provar:

1. Somente `TO_HUB` com usuario remetente participa.
2. `FROM_HUB` e automacoes sem usuario ficam fora.
3. IDs repetidos contam uma unica vez.
4. Vendedor vazio vira `Não identificado`.
5. Total geral e igual a soma por vendedor.
6. Percentuais usam o mesmo total deduplicado.
7. Empates sao ordenados pelo nome.
8. Resultado vazio possui schema estavel e nenhum percentual invalido.
9. Identidade ausente ou atribuicao conflitante falha de forma explicita.
10. O dataframe de entrada nao e alterado.

Resultado esperado: todos os testes passam sem acesso ao banco ou ao BotNext.

## Run Dashboard

```powershell
streamlit run app.py
```

Abra a URL local exibida pelo Streamlit e acesse a aba **Vendedores**.

## End-to-End Scenarios

### 1. Period and total reconciliation

1. Selecione um periodo com mensagens enviadas.
2. Deixe **Canal comercial** sem selecao para representar todos os canais.
3. Localize **Mensagens enviadas por vendedores** e a tabela de ranking.
4. Some a coluna **Mensagens enviadas**.

Expected: a soma e exatamente igual ao total exibido, e a tabela esta em ordem decrescente de volume.

### 2. Channel filter

1. Anote o total com todos os canais.
2. Selecione um unico canal existente.
3. Compare total, linhas e percentuais.

Expected: todos os elementos da secao sao atualizados para o canal escolhido. Remover a selecao restaura a visao de todos os canais.

### 3. Received-message exclusion

1. Escolha um periodo conhecido por conter mensagens enviadas e recebidas.
2. Compare a metrica com um conjunto de controle ou consulta revisada dos dados persistidos.

Expected: registros `FROM_HUB` nao contribuem para nenhuma linha nem para o total.

### 4. Automation exclusion

1. Escolha um periodo com campanhas ou mensagens de API sem usuario remetente.
2. Revise o total da metrica.

Expected: automacoes sem usuario nao sao atribuidas ao vendedor do contato e nao aumentam o total.

### 5. Unidentified seller

1. Escolha um periodo com mensagem elegivel ligada a contato sem vendedor identificado.
2. Localize a linha **Não identificado**.

Expected: a linha permanece separada, participa do total e possui percentual correto.

### 6. No-data state

1. Escolha periodo e canal sem mensagens elegiveis.

Expected: total zero e mensagem explicita de ausencia de mensagens enviadas; ranking e percentuais nao aparecem. As demais secoes continuam acessiveis.

### 7. Filter isolation

1. Anote a metrica para um periodo e canal.
2. Altere filtros de status, tipo, direcao ou pesquisa mantendo periodo e canal.

Expected: a metrica de utilizacao nao muda. Alterar periodo ou canal atualiza a metrica.

## Performance Check

1. Com o volume operacional normal carregado, altere periodo e canal tres vezes.
2. Cronometre do fim da interacao ate a apresentacao coerente do total e ranking.

Expected: cada atualizacao conclui em ate 5 segundos.

## Traceability

- Regras de dados: [data-model.md](./data-model.md)
- Contrato de interface: [contracts/dashboard-ui.md](./contracts/dashboard-ui.md)
- Decisoes tecnicas: [research.md](./research.md)
