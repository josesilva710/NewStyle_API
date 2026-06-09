# 🛒 E-Commerce NewStyle API

> E-Commerce NewStyle API é uma API RESTful desenvolvida com **Django REST Framework**, criada para gerenciar produtos, pedidos e transações de forma integrada e escalável.

---

## 🌐 Acesso

* **API Base:** [](#)
* **Documentação Interativa (Swagger):** [](#)

---

## 🧰 Tecnologias Utilizadas

| Tecnologia | Descrição |
| :--- | :--- |
| **Python 3.14.3** | Linguagem principal do projeto |
| **Django 6.0.4** | Framework backend robusto e escalável |
| **Django REST Framework 3.7.1** | Criação e gerenciamento de APIs RESTful |

## 🏗️ Estrutura e Organização

A aplicação é composta por dois módulos principais (apps), dividindo as responsabilidades do e-commerce:

### 👥 Users

Gerencia a autenticação, perfis e o relacionamento com a plataforma:

* **Usuários** — Controle de contas customizadas, separando os acessos e permissões entre *Clientes* e *Lojistas*.
* **Endereços** — Cadastro de localização (Rua, CEP, Cidade) vinculado aos usuários.
* **Métodos de Pagamento** — Gerenciamento das opções preferidas do cliente (Pix, Crédito, Débito, Boleto).
* **Contato** — Sistema de tickets para gerenciar solicitações de suporte e atendimento.
* **Segurança** — Controle de tokens temporários para o fluxo de redefinição de senhas.

### 🛍️ Shop

Gerencia o catálogo da loja, o estoque e todo o fluxo de compras:

* **Produtos e SKUs** — Cadastro do catálogo e controle rigoroso de estoque segmentado por variações (cor e tamanho).
* **Carrinho** — Espaço dinâmico para os itens selecionados pelo usuário, com cálculo automático de subtotais e totais.
* **Pedidos** — Histórico de transações, registrando o status da compra, forma de pagamento e vinculando o cliente ao lojista.
* **Itens do Pedido** — Registro imutável (snapshot) dos produtos no momento da compra, garantindo que alterações futuras no catálogo não afetem o histórico de vendas.
