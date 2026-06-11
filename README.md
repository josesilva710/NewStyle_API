# 🛒 E-Commerce NewStyle API

> E-Commerce NewStyle API é uma API RESTful desenvolvida com **Django REST Framework**, criada para gerenciar produtos, pedidos e clientes/lojistas de forma integrada e escalável.

---

## 🌐 Acesso

* **API Base:** [LINK DA API](https://newstyleapi.pythonanywhere.com/)
* **Documentação Interativa (Swagger):** [DOCUMENTAÇÃO DA API](https://newstyleapi.pythonanywhere.com/api/docs/)

---

## 🧰 Tecnologias Utilizadas

| Tecnologia | Descrição |
| :--- | :--- |
| **Python 3.14.3** | Linguagem principal do projeto |
| **Django 6.0.4** | Framework backend robusto e escalável |
| **Django REST Framework 3.7.1** | Criação e gerenciamento de APIs RESTful |

## 🏗️ Estrutura e Organização

A aplicação é composta por dois módulos principais:

### 👥 Users

Gerencia a autenticação, perfis e o relacionamento com a plataforma:

* **Autenticação e Segurança** — Gerenciamento de acessos via Tokens para controle de sessão e proteção de rotas.
* **Usuários e Perfis** — Controle de contas customizadas e informações pessoais (`fullname`, `national_id`).
* **Endereços** — Cadastro de localização (`street`, `city`, `state`, `cep`) vinculado aos usuários.
* **Métodos de Pagamento** — Gerenciamento das opções de pagamento (`PIX`, `CREDIT_CARD`, `DEBIT_CARD`, `BOLETO`).
* **Contato** — Sistema de tickets para gerenciar solicitações de suporte.

### 🛍️ Shop

Gerencia o catálogo, estoque e fluxo de compras:

* **Produtos e SKUs** — Cadastro do catálogo (`Product`) e controle de estoque segmentado por variações (`color` e `size`).
* **Carrinho** — Espaço dinâmico para os itens selecionados (`Cart` e `CartItem`), com cálculo automático de subtotal e total.
* **Pedidos** — Histórico de transações (`Order`), registrando o `status` (ex: `PENDING`), `payment_method` e vinculando o `customer` ao `merchant`.
* **Itens do Pedido** — Registro imutável (*snapshot*) dos produtos no momento da compra (`OrderItem`), garantindo histórico consistente.

## 🔍 Filtros e Buscas

### 📄 Parâmetros de Filtro
Abaixo estão os parâmetros aceitos pela API:

| Parâmetro | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `status` | String | Filtra pedidos por status (**ativos**: `PENDING`, `PROCESSING`, `SHIPPED`). | `?status=ativos` |
| `category` | String | Filtra produtos por uma categoria específica (ex: `PANTS`, `SHIRTS`). | `?category=SHIRTS` |

### 🔎 Busca por Texto
| Parâmetro | Descrição | Campos Pesquisados | Exemplo |
| :--- | :--- | :--- | :--- |
| `search` | Busca textual em Produtos | `name`, `category` | `?search=shirt` |

### 📊 Ordenação
| Parâmetro | Descrição | Campos Disponíveis | Exemplo |
| :--- | :--- | :--- | :--- |
| `ordering` | Ordena os Produtos | `price`, `name` | `?ordering=price` |
| `ordering` | Ordena os Pedidos | `status` | `?ordering=-status` |

*Dica: Utilize um sinal de menos (`-`) antes do campo para ordenação decrescente (ex: `?ordering=-price`).*

## 🔒 Autenticação e Segurança

A API utiliza **JSON Web Token (JWT)** para garantir a segurança e o controle de acesso. Os endpoints estão protegidos e organizados da seguinte forma:

* **Autenticação (`/auth/`):** Fluxo completo de `login`, `register`, `forgot-password` e `reset-password`. Ao realizar o login com sucesso, a API retorna um par de tokens (Access/Refresh) para autorização das requisições.
* **Controle de Acesso:** Os endpoints que exigem ações específicas (como manipulação de `orders`, `cart` ou `addresses`) são protegidos e exigem o envio do Token no cabeçalho da requisição (`Authorization: Bearer <seu_token>`).
* **Permissões:** O sistema diferencia usuários comuns de lojistas/staff, garantindo que cada um tenha acesso apenas aos recursos permitidos pelo seu perfil.

---
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
