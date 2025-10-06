### User Story 9: Indústria (Manutenção Preventiva)

Visão de Usuário:

Eu, como Técnico de Manutenção, desejo receber alertas automáticos sobre a necessidade de manutenção preventiva de equipamentos, para que possa evitar paradas não programadas na linha de produção.

Pré-condições e Premissas:

O sistema de gestão de ativos da empresa está implementado.
Os equipamentos estão cadastrados no sistema, com informações sobre fabricante, modelo e data de instalação.
Os planos de manutenção preventiva estão definidos para cada equipamento, com frequência e tarefas a serem realizadas.
Fluxos:

Principal:
O sistema verifica diariamente os planos de manutenção preventiva.
Quando um plano de manutenção está próximo do vencimento (ex: 7 dias), o sistema gera um alerta.
O alerta é enviado para o técnico responsável pelo equipamento.
O técnico visualiza o alerta no sistema, com detalhes sobre o equipamento, plano de manutenção e tarefas a serem realizadas.
O técnico agenda a manutenção preventiva.
Após a realização da manutenção, o técnico registra as atividades no sistema.
Alternativo: Alerta Ignorado
O técnico não agenda a manutenção preventiva dentro do prazo.
O sistema envia um novo alerta para o supervisor do técnico.
Alternativo: Plano de Manutenção Inexistente
O sistema não encontra um plano de manutenção preventiva para o equipamento.
O sistema notifica o administrador do sistema.
Regras de Negócio:

Os alertas devem ser gerados com antecedência mínima de 7 dias.
Os alertas devem ser enviados para o técnico responsável pelo equipamento.
O supervisor deve ser notificado caso o técnico não agende a manutenção.
O sistema deve registrar todas as atividades de manutenção preventiva.
Requisitos Não Funcionais:

Performance: A geração de alertas não deve impactar o desempenho do sistema.
Disponibilidade: O sistema deve estar disponível 24/7.
Segurança: O acesso aos alertas deve ser restrito aos técnicos e supervisores autorizados.
Critérios de Aceite:

Verificar se os alertas são gerados corretamente.
Verificar se os alertas são enviados para os técnicos responsáveis.
Verificar se o supervisor é notificado caso o técnico não agende a manutenção.
Verificar se as atividades de manutenção são registradas no sistema.