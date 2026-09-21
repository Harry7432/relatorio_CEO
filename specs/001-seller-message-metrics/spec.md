# Feature Specification: Metricas de utilizacao por vendedor

**Feature Branch**: `main`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Permitir que o CEO visualize quantas mensagens cada vendedor enviou em um periodo, com filtros por periodo e canal, ranking, total geral e participacao percentual."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar utilizacao por vendedor (Priority: P1)

Como CEO, quero escolher um periodo e visualizar o volume de mensagens enviadas por cada vendedor para entender quem utiliza a plataforma comercial e com qual intensidade.

**Why this priority**: Esta e a entrega central da feature e fornece a visao minima necessaria para medir a adocao individual da plataforma.

**Independent Test**: Pode ser testada com um conjunto conhecido de mensagens enviadas e recebidas, selecionando um periodo e conferindo que a tabela apresenta somente as mensagens enviadas, agrupadas pelo vendedor correto.

**Acceptance Scenarios**:

1. **Given** que existem mensagens enviadas por diferentes vendedores no periodo, **When** o CEO seleciona esse periodo, **Then** visualiza cada vendedor e sua quantidade total de mensagens enviadas.
2. **Given** que o periodo tambem contem mensagens recebidas de clientes, **When** os indicadores sao exibidos, **Then** essas mensagens recebidas nao entram em nenhuma contagem de utilizacao.
3. **Given** que uma mesma mensagem consta mais de uma vez nos dados disponiveis, **When** o volume e calculado, **Then** ela contribui uma unica vez para a contagem.

---

### User Story 2 - Comparar participacao dos vendedores (Priority: P2)

Como CEO, quero ver os vendedores ordenados por volume, o total geral e a participacao percentual de cada pessoa para comparar a distribuicao de uso da plataforma.

**Why this priority**: A comparacao transforma contagens isoladas em uma visao gerencial, permitindo identificar concentracao ou baixa utilizacao.

**Independent Test**: Pode ser testada com volumes conhecidos para tres vendedores, verificando a ordenacao, a soma do total geral e o calculo percentual de cada linha.

**Acceptance Scenarios**:

1. **Given** que ha vendedores com volumes diferentes, **When** o CEO consulta o periodo, **Then** a apresentacao os ordena do maior para o menor volume de mensagens enviadas.
2. **Given** que ha mensagens enviadas no periodo, **When** os resultados sao exibidos, **Then** o total geral corresponde exatamente a soma das quantidades apresentadas por vendedor.
3. **Given** um vendedor com parte das mensagens do periodo, **When** sua participacao e exibida, **Then** ela corresponde a sua quantidade dividida pelo total geral, respeitando o arredondamento visual informado.

---

### User Story 3 - Refinar analise por canal (Priority: P3)

Como CEO, quero filtrar a utilizacao por canal para comparar o uso da plataforma em contextos comerciais diferentes.

**Why this priority**: O recorte por canal aprofunda a analise, mas depende da visao principal por periodo para gerar valor.

**Independent Test**: Pode ser testada selecionando um canal com mensagens conhecidas e verificando que tabela, ranking, total e percentuais passam a considerar somente esse canal.

**Acceptance Scenarios**:

1. **Given** que o periodo possui mensagens em mais de um canal, **When** o CEO seleciona um canal, **Then** todos os indicadores consideram exclusivamente as mensagens enviadas nesse canal.
2. **Given** que um canal selecionado nao possui mensagens enviadas no periodo, **When** o filtro e aplicado, **Then** o dashboard apresenta claramente que nao ha dados para a selecao e nao exibe valores enganosos.

---

### Edge Cases

- Quando o periodo nao possui mensagens enviadas, o total geral deve ser zero e o estado sem dados deve ser explicito; percentuais nao devem ser apresentados como se fossem validos.
- Quando uma mensagem enviada nao pode ser associada a um vendedor, ela deve compor uma unica linha chamada "Não identificado" e continuar fazendo parte do total geral.
- Quando todas as mensagens do periodo pertencem a vendedores nao identificados, a linha "Não identificado" deve representar 100% do total.
- Quando ha empate no volume, a ordenacao secundaria deve ser deterministica para que a apresentacao nao mude arbitrariamente entre consultas equivalentes.
- Quando o intervalo informado e invalido, a consulta nao deve ser executada e o usuario deve receber orientacao clara para corrigi-lo.
- Quando existem registros duplicados da mesma mensagem, apenas uma ocorrencia deve contribuir para os indicadores.
- Quando os percentuais exibidos sao arredondados, pequenas diferencas visuais na soma dos percentuais nao devem alterar nem contradizer o total absoluto.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O dashboard MUST permitir que o CEO selecione um periodo de analise com data inicial e data final.
- **FR-002**: O dashboard MUST permitir que o CEO considere todos os canais ou selecione um canal disponivel.
- **FR-003**: O sistema MUST contar exclusivamente mensagens efetivamente enviadas por vendedores dentro do periodo e do canal selecionados.
- **FR-004**: O sistema MUST excluir mensagens recebidas de clientes de todos os indicadores de utilizacao por vendedor.
- **FR-005**: O sistema MUST contar cada mensagem distinta no maximo uma vez, mesmo quando houver registros duplicados nos dados de origem.
- **FR-006**: O dashboard MUST apresentar a quantidade total de mensagens enviadas por vendedor para a selecao atual.
- **FR-007**: O dashboard MUST apresentar os vendedores em uma tabela ou ranking ordenado por volume decrescente de mensagens enviadas, com criterio secundario deterministico em caso de empate.
- **FR-008**: O dashboard MUST apresentar o total geral de mensagens enviadas para a selecao atual.
- **FR-009**: O total geral MUST ser exatamente igual a soma das quantidades apresentadas por vendedor, incluindo a categoria "Não identificado".
- **FR-010**: O dashboard MUST apresentar a participacao percentual de cada vendedor no total geral da selecao atual.
- **FR-011**: A participacao percentual MUST ser calculada a partir da quantidade do vendedor dividida pelo total geral antes do arredondamento visual.
- **FR-012**: Mensagens enviadas sem vendedor identificado MUST ser agrupadas e exibidas em uma unica categoria denominada "Não identificado".
- **FR-013**: Alteracoes nos filtros MUST atualizar de forma consistente a tabela ou ranking, o total geral e as participacoes percentuais.
- **FR-014**: Quando a selecao nao possuir mensagens enviadas, o dashboard MUST exibir um estado sem dados claro e um total geral igual a zero.
- **FR-015**: O sistema MUST usar como fonte os dados persistentes ja sincronizados e disponiveis no projeto, sem iniciar nova sincronizacao para produzir a consulta.
- **FR-016**: O sistema MUST rejeitar intervalos em que a data inicial seja posterior a data final e informar como corrigir a selecao.
- **FR-017**: O escopo MUST permanecer restrito a volume de mensagens enviadas; tempo de resposta, SLA, receita, conversao, agendamento e mudancas na identificacao de vendedores nao devem integrar esta entrega.

### Key Entities *(include if feature involves data)*

- **Mensagem**: Interacao comercial individual, identificada de forma unica, com momento de ocorrencia, direcao de envio, canal e associacao opcional a um vendedor.
- **Vendedor**: Pessoa cuja utilizacao e medida pelo volume de mensagens que efetivamente enviou; sua identificacao segue as regras existentes.
- **Canal**: Origem comercial usada para limitar a consulta a um meio especifico de comunicacao.
- **Selecao de analise**: Combinacao do periodo inclusivo e do canal opcional que determina quais mensagens participam dos indicadores.
- **Metrica por vendedor**: Quantidade de mensagens enviadas e participacao percentual de um vendedor, ou da categoria "Não identificado", dentro da selecao.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos conjuntos de validacao, a soma das quantidades por vendedor e igual ao total geral apresentado para os mesmos filtros.
- **SC-002**: Em 100% dos conjuntos de validacao, mensagens recebidas e ocorrencias duplicadas nao aumentam o volume atribuido aos vendedores.
- **SC-003**: O CEO consegue selecionar um periodo, interpretar o total e identificar os vendedores com maior volume em menos de 1 minuto, sem apoio tecnico.
- **SC-004**: Em pelo menos 95% das tentativas de uso avaliadas, o CEO aplica um filtro de canal corretamente na primeira tentativa e reconhece que todos os indicadores refletem o filtro.
- **SC-005**: Toda mensagem enviada incluida no total e atribuida a exatamente um vendedor exibido ou a categoria "Não identificado".
- **SC-006**: Uma alteracao valida de periodo ou canal apresenta os indicadores correspondentes em ate 5 segundos para o volume normal de dados operacionais do projeto.
- **SC-007**: Em 100% das selecoes sem mensagens enviadas, o usuario visualiza uma indicacao explicita de ausencia de dados e nenhum percentual enganoso.

## Assumptions

- O acesso ao dashboard e aos indicadores para o perfil de CEO ja e controlado pelos mecanismos existentes do projeto.
- O periodo considera as datas inicial e final de forma inclusiva e usa a referencia de data adotada atualmente pelo negocio.
- A lista de canais disponiveis e derivada dos dados ja sincronizados e oferece uma opcao para considerar todos os canais.
- A direcao da mensagem, seu identificador unico, o canal, o momento de ocorrencia e a associacao existente com vendedor estao disponiveis nos dados sincronizados.
- As regras atuais de identificacao de vendedor permanecem inalteradas; esta feature apenas consome o resultado dessas regras.
- Percentuais sao exibidos com precisao visual consistente, e o volume absoluto permanece a referencia para reconciliacao do total.
- Esta feature consulta somente dados ja sincronizados; disponibilidade, atualizacao e correcao da sincronizacao permanecem responsabilidades dos fluxos existentes.
