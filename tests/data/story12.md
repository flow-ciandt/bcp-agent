### User Story 12: Restaurante (Sistema de Pedidos Online com Personalização)

Visão de Usuário:

Eu, como Cliente do Restaurante, desejo fazer pedidos online com opções de personalização (ex: ingredientes extras, remoção de itens, ajustes de tempero), para que eu possa montar o prato do meu jeito e receber em casa.

Pré-condições e Premissas:

O restaurante possui um sistema de pedidos online.
O cardápio está cadastrado no sistema, com descrições detalhadas, preços e opções de personalização para cada prato.
O sistema de entrega está integrado ao sistema de pedidos.
Fluxos:

Principal:
O cliente acessa o sistema de pedidos online do restaurante.
O cliente navega pelo cardápio e seleciona um prato.
O sistema exibe as opções de personalização disponíveis para o prato (ex: adicionar bacon, remover cebola, aumentar a pimenta).
O cliente seleciona as opções de personalização desejadas.
O sistema recalcula o preço do prato com base nas personalizações.
O cliente adiciona o prato personalizado ao carrinho.
O cliente finaliza o pedido e escolhe o endereço de entrega.
Alternativo: Personalização Indisponível
O cliente tenta personalizar um prato que não possui opções de personalização.
O sistema informa que a personalização não está disponível para esse prato.
Alternativo: Ingredientes Esgotados
O cliente tenta adicionar um ingrediente extra que está esgotado no restaurante.
O sistema informa que o ingrediente está indisponível e sugere alternativas.
Regras de Negócio:

O sistema deve permitir personalizações apenas para os pratos que possuem essa opção.
O sistema deve recalcular o preço do prato com base nas personalizações.
O sistema deve informar se algum ingrediente está esgotado.
Requisitos Não Funcionais:

Usabilidade: O sistema deve ser fácil de usar e intuitivo.
Performance: O pedido deve ser processado rapidamente.
Integração: O sistema deve estar integrado com o sistema de entrega.
Critérios de Aceite:

Verificar se o cliente consegue personalizar os pratos.
Verificar se o sistema recalcula o preço corretamente.
Verificar se o sistema informa sobre ingredientes esgotados.