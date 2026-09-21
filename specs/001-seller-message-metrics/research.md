# Research: Metricas de utilizacao por vendedor

## Decision 1: Reutilizar a leitura atual do dashboard

**Decision**: Calcular a metrica sobre os registros retornados por `buscar_dados_dashboard()` e ja carregados por `carregar_dados()`. Incluir `mensagem.user_id` na projecao de leitura apenas se necessario para identificar envio humano sem depender de texto de apresentacao.

**Rationale**: O dashboard ja consulta `mensagens`, `sessoes`, `contatos` e `usuarios_botnext`, converte datas e disponibiliza canal e vendedor. Isso atende a exigencia de usar dados persistidos sem tocar na sincronizacao. A projecao de `user_id` e uma alteracao de leitura pequena e auditavel.

**Alternatives considered**:

- Criar uma consulta agregada no PostgreSQL: rejeitada nesta fase porque duplicaria filtros e regras ja presentes e nao ha evidencia de que o volume atual descumpra a meta de 5 segundos.
- Criar tabela ou materializacao de metricas: rejeitada por exigir schema, migration e atualizacao adicional sem necessidade concreta.
- Consultar o BotNext durante a visualizacao: rejeitada porque violaria a fonte persistente definida para a feature.

## Decision 2: Definir mensagem enviada por vendedor

**Decision**: Uma mensagem e elegivel quando `direcao == "TO_HUB"` e `usuario_id_mensagem` esta preenchido. Registros sem usuario remetente, incluindo campanhas, API e automacoes observadas, nao representam utilizacao individual e ficam fora da metrica.

**Rationale**: A inspecao agregada dos dados persistidos mostrou que `TO_HUB` concentra mensagens com `user_id` de usuarios, enquanto `FROM_HUB` nao possui usuario e representa o fluxo recebido. Exigir remetente evita atribuir automacoes ao vendedor responsavel pelo contato.

**Alternatives considered**:

- Filtrar somente por `TO_HUB`: rejeitada porque incluiria mensagens de campanha e API sem remetente humano.
- Usar o texto `Automacao/BotNext` preenchido pela UI: rejeitada por acoplar uma regra critica a um rotulo de apresentacao.
- Alterar a sincronizacao para classificar mensagens: rejeitada porque os campos necessarios ja estao persistidos.

## Decision 3: Preservar a identificacao atual de vendedor

**Decision**: Agrupar mensagens elegiveis por `vendedor_responsavel`, usando `Não identificado` quando o valor estiver ausente ou vazio.

**Rationale**: O projeto ja identifica o vendedor a partir de carteira e etiquetas em `vendedor_service.py` e persiste o resultado no contato. O usuario determinou que essa logica deve ser preservada e que a feature deve consumir a identificacao atual.

**Alternatives considered**:

- Agrupar por `usuario_mensagem`: rejeitada porque substituiria a regra de identificacao de vendedor existente por identidade do remetente.
- Reexecutar `identificar_vendedor()` no dashboard: rejeitada porque duplicaria processamento e separacao de responsabilidades.
- Dividir contatos com multiplas carteiras entre vendedores: rejeitada porque alteraria uma regra de identificacao fora do escopo.

## Decision 4: Deduplicar por identidade da mensagem

**Decision**: Depois de aplicar os criterios de elegibilidade e filtros de periodo/canal, considerar no maximo uma linha por `mensagem_id`. Identificador ausente ou uma mesma identidade associada a vendedores conflitantes deve gerar erro rastreavel, nao uma escolha silenciosa.

**Rationale**: `mensagem_id` e a identidade persistida e o repositorio usa `ON CONFLICT (id)`, mas a deduplicacao defensiva protege a metrica contra repeticoes produzidas pela origem ou por joins futuros. Validar conflitos evita resultados dependentes da ordem dos dados.

**Alternatives considered**:

- Contar linhas: rejeitada porque nao garante o criterio de aceite contra duplicidade.
- Usar `nunique()` apenas no total: rejeitada porque poderia fazer o total divergir da soma por vendedor.
- Remover linhas totalmente iguais: rejeitada porque a identidade de negocio e `mensagem_id`, nao o conjunto completo de colunas.

## Decision 5: Isolar a agregacao em funcao pura pandas

**Decision**: Criar uma funcao sem dependencias de Streamlit ou banco que receba o dataframe e devolva tabela com vendedor, quantidade e percentual em precisao integral.

**Rationale**: A regra inclui elegibilidade, desconhecidos, deduplicacao, reconciliacao, percentuais e desempate. Isola-la permite testes rapidos e deterministas sem executar a aplicacao monolitica. `groupby(..., dropna=False)` e `.size()` preservam grupos desconhecidos e contam linhas deduplicadas corretamente.

**Alternatives considered**:

- Implementar diretamente dentro da aba Streamlit: rejeitada porque tornaria a regra critica dificil de testar e reutilizar.
- Criar camadas de dominio e DTOs adicionais: rejeitada como abstracao prematura para uma unica agregacao.
- Arredondar percentuais na funcao: rejeitada porque arredondamento e apresentacao; os calculos e testes devem manter precisao.

## Decision 6: Ordenacao e percentual

**Decision**: Ordenar por quantidade decrescente e, em empates, por nome do vendedor crescente, com `Não identificado` seguindo a mesma regra textual. Calcular `quantidade / total * 100` antes de formatar visualmente.

**Rationale**: O criterio secundario garante resultado estavel. Usar o mesmo conjunto deduplicado no numerador e denominador garante que a soma dos volumes reconcilie com o total.

**Alternatives considered**:

- Preservar ordem de entrada: rejeitada por variar com a consulta.
- Ordenar apenas por quantidade: rejeitada por deixar empates indeterminados.
- Forcar percentuais arredondados a somar 100%: rejeitada porque distorceria participacoes individuais; o total absoluto e a referencia.

## Decision 7: Escopo dos filtros

**Decision**: A metrica responde aos filtros globais existentes de periodo e canal. Filtros de direcao, tipo, status, vendedor e pesquisas textuais nao alteram essa metrica, pois sua definicao deve permanecer fixa e comparavel.

**Rationale**: A especificacao e o contexto do usuario pedem explicitamente periodo e canal. Permitir que o filtro de direcao inclua recebidas ou que buscas textuais alterem o total violaria a definicao de utilizacao.

**Alternatives considered**:

- Usar `df_filtrado` depois de todos os filtros: rejeitada porque filtros nao relacionados mudariam silenciosamente a metrica.
- Criar filtros novos exclusivos: rejeitada porque duplicaria controles existentes.

## Decision 8: Estrategia de testes

**Decision**: Cobrir a funcao pura com pytest e manter uma validacao manual curta da integracao Streamlit. Adiar `AppTest` enquanto `app.py` executar carga de banco no nivel do modulo e nao houver seam simples para substituir essa dependencia.

**Rationale**: Testes unitarios cobrem exaustivamente as regras de negocio com baixo custo. Um teste de UI agora exigiria refatoracao estrutural maior do que a feature.

**Alternatives considered**:

- Somente teste manual: rejeitada porque as regras criticas sao facilmente automatizaveis.
- Cobertura completa por Streamlit `AppTest`: adiada para evitar ampliar o escopo e acoplar testes ao banco real.

## Primary references

- pandas `drop_duplicates`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html
- pandas `groupby`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html
- pandas `DataFrameGroupBy.size`: https://pandas.pydata.org/docs/reference/api/pandas.api.typing.DataFrameGroupBy.size.html
- pandas `sort_values`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
- pandas `assert_frame_equal`: https://pandas.pydata.org/docs/reference/api/pandas.testing.assert_frame_equal.html
- Streamlit `st.date_input`: https://docs.streamlit.io/1.62.0/develop/api-reference/widgets/st.date_input
- Streamlit `st.multiselect`: https://docs.streamlit.io/1.62.0/develop/api-reference/widgets/st.multiselect
- Streamlit app testing: https://docs.streamlit.io/develop/concepts/app-testing/get-started
- pytest parametrization: https://docs.pytest.org/en/stable/how-to/parametrize.html
