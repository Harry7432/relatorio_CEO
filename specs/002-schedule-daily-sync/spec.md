# Feature Specification: Sincronizacao automatica diaria

**Feature Branch**: `main`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Executar automaticamente a sincronizacao completa todos os dias as 00:00 no ambiente de producao, sem depender do frontend, impedindo concorrencia e mantendo logs rastreaveis."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manter dados atualizados diariamente (Priority: P1)

Como CEO, quero que a sincronizacao completa seja executada automaticamente todos os dias no servidor para que o dashboard use dados atualizados sem depender de uma pessoa ou computador conectado.

**Why this priority**: Esta e a finalidade central da feature e elimina a dependencia operacional que atualmente pode deixar o banco desatualizado.

**Independent Test**: Pode ser testada mantendo o frontend desligado durante o horario programado e verificando que uma execucao completa foi iniciada no servidor, concluida e refletida nos dados persistidos.

**Acceptance Scenarios**:

1. **Given** que o ambiente de producao esta disponivel e o frontend esta desligado, **When** chega 00:00 no fuso de Sao Paulo, **Then** uma sincronizacao completa e iniciada automaticamente no servidor.
2. **Given** que a fonte possui dados novos e a execucao termina com sucesso, **When** o CEO consulta o dashboard depois da sincronizacao, **Then** os dados diarios atualizados estao disponiveis.
3. **Given** que nao existem dados novos na fonte, **When** a sincronizacao diaria termina sem erros, **Then** a execucao e registrada como concluida e os dados existentes permanecem consistentes.

---

### User Story 2 - Acompanhar resultado e falhas (Priority: P2)

Como operador, quero identificar quando cada sincronizacao iniciou, terminou e qual foi seu resultado para diagnosticar rapidamente falhas completas ou parciais.

**Why this priority**: A automacao sem rastreabilidade pode falhar silenciosamente e comprometer a confianca nos indicadores do dashboard.

**Independent Test**: Pode ser testada executando um caso bem-sucedido e um caso com falha controlada, verificando que os registros informam inicio, fim, duracao, resultado e etapa afetada sem expor dados sensiveis.

**Acceptance Scenarios**:

1. **Given** uma sincronizacao concluida com sucesso, **When** o operador consulta os registros da execucao, **Then** encontra inicio, fim, duracao, resultado final e confirmacao das etapas executadas.
2. **Given** uma falha durante qualquer etapa, **When** o operador consulta os registros, **Then** identifica a execucao, a etapa afetada e o erro relevante sem encontrar credenciais ou dados sensiveis.
3. **Given** uma execucao que falhou hoje, **When** chega o horario programado do dia seguinte, **Then** uma nova tentativa e iniciada normalmente.

---

### User Story 3 - Executar manualmente sem concorrencia (Priority: P3)

Como operador, quero continuar iniciando a mesma sincronizacao manualmente quando necessario sem permitir que ela concorra com uma execucao automatica.

**Why this priority**: A operacao manual continua necessaria para recuperacao e verificacao, mas execucoes sobrepostas podem gerar carga desnecessaria e resultados dificeis de interpretar.

**Independent Test**: Pode ser testada iniciando uma execucao e tentando iniciar outra, manual ou automatica, antes do termino; somente a primeira deve prosseguir e a segunda deve ser registrada como ignorada por concorrencia.

**Acceptance Scenarios**:

1. **Given** que nao ha sincronizacao em andamento, **When** o operador inicia uma execucao manual, **Then** a mesma operacao completa usada pelo agendamento e executada.
2. **Given** que uma sincronizacao automatica esta em andamento, **When** uma execucao manual e solicitada, **Then** a segunda execucao nao inicia e o motivo fica registrado.
3. **Given** que uma sincronizacao manual esta em andamento, **When** chega o horario automatico, **Then** nao ocorre sobreposicao e a tentativa automatica fica registrada como ignorada.

---

### Edge Cases

- Se uma execucao ainda estiver ativa no horario do dia seguinte, a nova tentativa nao deve concorrer e deve ser registrada como ignorada.
- Se o processo terminar inesperadamente, o mecanismo de exclusao nao deve permanecer bloqueado indefinidamente.
- Se o servidor reiniciar proximo de 00:00, a ocorrencia ou ausencia da execucao deve ser verificavel nos registros.
- Mudancas de deslocamento horario devem continuar respeitando 00:00 no fuso de Sao Paulo.
- Se uma etapa falhar depois de etapas anteriores terem persistido dados, o resultado deve indicar execucao parcial ou falha e identificar a etapa afetada.
- Se a fonte externa estiver indisponivel, a falha deve encerrar a tentativa atual sem impedir o agendamento futuro.
- Se uma solicitacao manual e automatica chegarem simultaneamente, apenas uma deve adquirir o direito de executar.
- Se nao houver dados novos, a execucao deve terminar com sucesso sem criar registros duplicados.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST iniciar uma sincronizacao completa automaticamente todos os dias as 00:00 no horario local de Sao Paulo.
- **FR-002**: O agendamento MUST interpretar o horario pelo fuso `America/Sao_Paulo`, inclusive quando houver mudanca de deslocamento horario.
- **FR-003**: A execucao automatica MUST ocorrer no ambiente hospedado de producao sem depender de navegador, frontend ativo, computador local ou usuario conectado.
- **FR-004**: A execucao automatica MUST reutilizar a mesma operacao completa disponivel para execucao manual.
- **FR-005**: O sistema MUST manter a execucao manual disponivel independentemente do agendamento diario.
- **FR-006**: O sistema MUST garantir que no maximo uma sincronizacao completa esteja ativa por vez no ambiente de producao.
- **FR-007**: O controle de concorrencia MUST abranger execucoes manuais e automaticas.
- **FR-008**: Uma tentativa iniciada enquanto outra sincronizacao estiver ativa MUST ser impedida de executar e registrada como ignorada por concorrencia.
- **FR-009**: O controle de concorrencia MUST ser liberado apos sucesso, falha ou encerramento inesperado, sem bloquear indefinidamente execucoes futuras.
- **FR-010**: Cada tentativa MUST registrar horario de inicio, horario de fim, duracao e resultado final.
- **FR-011**: O resultado final MUST distinguir pelo menos sucesso, falha, conclusao parcial e tentativa ignorada por concorrencia.
- **FR-012**: Os registros MUST permitir identificar as etapas iniciadas, concluidas e afetadas por falha.
- **FR-013**: Falhas MUST ser registradas com contexto suficiente para diagnostico, sem incluir credenciais, tokens, connection strings, conteudo de mensagens ou outros dados sensiveis.
- **FR-014**: Uma execucao com falha MUST terminar sem impedir a tentativa automatica programada para o dia seguinte.
- **FR-015**: A sincronizacao diaria e eventuais repeticoes manuais MUST preservar a ausencia de duplicidades nos dados persistidos.
- **FR-016**: A feature MUST reutilizar a ordem e o comportamento das etapas atuais de sincronizacao, salvo mudanca minima necessaria para concorrencia e rastreabilidade.
- **FR-017**: A feature MUST operar sem nova tabela ou alteracao de schema, a menos que o planejamento demonstre necessidade concreta e registre explicitamente a mudanca.
- **FR-018**: A indisponibilidade do frontend MUST NOT impedir, pausar ou cancelar a execucao automatica.
- **FR-019**: O sistema MUST programar uma tentativa por dia; repeticoes automaticas no mesmo dia ficam fora do escopo inicial.

### Key Entities *(include if feature involves data)*

- **Agenda de sincronizacao**: Regra recorrente que define 00:00 no fuso de Sao Paulo como horario diario de inicio.
- **Execucao de sincronizacao**: Uma tentativa manual ou automatica, com origem, inicio, fim, duracao, resultado e etapas percorridas.
- **Controle de concorrencia**: Direito exclusivo e temporario de executar a sincronizacao completa no ambiente de producao.
- **Registro de execucao**: Evidencia operacional usada para confirmar sucesso, diagnosticar falha ou explicar por que uma tentativa foi ignorada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em uma observacao de 30 dias com o ambiente disponivel, 100% das tentativas diarias sao iniciadas entre 00:00 e 00:05 no horario de Sao Paulo.
- **SC-002**: Em testes com solicitacoes simultaneas manuais e automaticas, zero pares de sincronizacoes executam de forma sobreposta.
- **SC-003**: Em 100% das tentativas, o operador consegue consultar inicio, fim, duracao e resultado final nos registros operacionais.
- **SC-004**: Em teste com o frontend desligado, a sincronizacao automatica inicia e conclui sem intervencao humana.
- **SC-005**: Apos uma falha controlada, a tentativa programada para o dia seguinte inicia sem desbloqueio manual.
- **SC-006**: Em conjuntos de validacao com repeticao da mesma sincronizacao, a quantidade de registros unicos permanece consistente e nenhuma identidade persistente e duplicada.
- **SC-007**: Em pelo menos 95% dos testes operacionais, um operador identifica em menos de 2 minutos se a ultima execucao teve sucesso, falha, conclusao parcial ou foi ignorada.
- **SC-008**: Quando a fonte disponibiliza dados novos e a execucao termina com sucesso, os dados correspondentes ficam disponiveis no dashboard no mesmo ciclo diario.

## Assumptions

- O ambiente de producao atual oferece agendamento recorrente e preserva os registros de saida das execucoes.
- O fuso oficial do agendamento e `America/Sao_Paulo`, independentemente do fuso padrao do servidor.
- A operacao completa atual permanece como fonte unica para execucoes manuais e automaticas.
- As operacoes de persistencia existentes continuam idempotentes para identidades ja sincronizadas.
- Uma tentativa automatica e feita por dia; retry automatico, alertas externos e escalonamento ficam fora do escopo inicial.
- O tempo normal de uma sincronizacao completa e inferior a 24 horas.
- As mesmas configuracoes seguras de acesso a fonte e ao banco estao disponiveis para o processo agendado no ambiente hospedado.
- A plataforma de producao atual e o Coolify; a escolha do recurso especifico de agendamento sera definida no planejamento tecnico.
