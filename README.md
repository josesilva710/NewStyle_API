<img width="1365" height="767" alt="image" src="https://github.com/user-attachments/assets/502512f4-92d9-471c-9669-1165956c7bad" /># 🛒 E-Commerce NewStyle API

> E-Commerce NewStyle API é uma API RESTful desenvolvida com **Django REST Framework**, criada para gerenciar produtos, pedidos e clientes/lojistas de forma integrada e escalável.

---

## 🌐 Acesso

* **API Base:** [LINK DA API](https://newstyleapi.pythonanywhere.com/)
* **Documentação Interativa (Swagger):** [](https://newstyleapi.pythonanywhere.com/api/docs/)

---

## 🧰 Tecnologias Utilizadas

| Tecnologia | Descrição |
| :--- | :--- |
| **Python 3.14.3** | Linguagem principal do projeto |
| **Django 6.0.4** | Framework backend robusto e escalável |
| **Django REST Framework 3.7.1** | Criação e gerenciamento de APIs RESTful |

## 🏗️ Estrutura e Organização

A aplicação é composta por dois módulos principais, dividindo as responsabilidades do e-commerce:

### 👥 Users

Gerencia a autenticação, perfis e o relacionamento com a plataforma:

* **Autenticação e Segurança** — Gerenciamento de acessos via Tokens (como JWT) para controle de sessão e proteção de rotas, garantindo as permissões corretas para *Clientes* e *Lojistas*, além de controlar o fluxo temporário de redefinição de senhas.
* **Usuários e Perfis** — Controle de contas customizadas e informações pessoais.
* **Endereços** — Cadastro de localização (Rua, CEP, Cidade) vinculado aos usuários.
* **Métodos de Pagamento** — Gerenciamento das opções preferidas do cliente (Pix, Crédito, Débito, Boleto).
* **Contato** — Sistema de tickets para gerenciar solicitações de suporte e atendimento.

### 🛍️ Shop

Gerencia o catálogo da loja, o estoque e todo o fluxo de compras:

* **Produtos e SKUs** — Cadastro do catálogo e controle rigoroso de estoque segmentado por variações (cor e tamanho).
* **Carrinho** — Espaço dinâmico para os itens selecionados pelo usuário, com cálculo automático de subtotais e totais.
* **Pedidos** — Histórico de transações, registrando o status da compra, forma de pagamento e vinculando o cliente ao lojista.
* **Itens do Pedido** — Registro imutável (snapshot) dos produtos no momento da compra, garantindo que alterações futuras no catálogo não afetem o histórico de vendas.

## 🔍 Filtros e Buscas - E-Commerce API

📄 **Filtros Disponíveis**

A API oferece diversos parâmetros para facilitar a busca e organização do catálogo e das vendas. Abaixo estão os filtros disponíveis e como utilizá-los:

🎯 **Filtros Básicos**

| Parâmetro | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `status` | String | Filtra pedidos em andamento (**ativos**: `pendente`, `em processamento`, `enviado`). Exclui entregues ou cancelados. | `?status=ativos` |
| `categoria` | String | Filtra produtos por uma categoria específica. | `?categoria=camisas` |

🔎 **Busca por Texto**

| Parâmetro | Descrição | Campos Pesquisados | Exemplo |
| :--- | :--- | :--- | :--- |
| `search` | Busca textual em Produtos | `nome`, `categoria` | `?search=vestido+preto` |
| `search` | Busca textual em Pedidos | `status` | `?search=pendente` |

📊 **Ordenação**

| Parâmetro | Descrição | Campos Disponíveis | Exemplo |
| :--- | :--- | :--- | :--- |
| `ordering` | Ordena os Produtos | `preco`, `nome` | `?ordering=preco` |
| `ordering` | Ordena os Pedidos | `status` | `?ordering=-status` |

*Dica: Utilize um sinal de menos (`-`) antes do campo para ordenação decrescente (ex: `?ordering=-preco`).*

📄 **Paginação**

A API utiliza paginação nativa configurada para retornar **10 itens por página**.

| Parâmetro | Descrição | Exemplo |
| :--- | :--- | :--- |
| `page` | Número da página desejada | `?page=2` |

## 🧱 Estrutura do Projeto

```text
NewStyle_API/
├── ecommerce/                          # Configurações do projeto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Shop/                               # App do catálogo e pedidos
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── Users/                              # App de contas e perfis
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── .gitignore
├── db.sqlite3
├── manage.py
├── README.md
├── requirements.txt
└── schema.yml
```
## 👨‍💻 Autor

**José Fernandes**<br>
Desenvolvedor Backend | Estudante de Ciência e Tecnologia com ênfase em Computação<br>
[GitHub](https://github.com/josesilva710) • [LinkedIn](https://linkedin.com/in/josesilvags)
