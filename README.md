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

<details>
<summary><b>Ver lista completa de dependências (requirements.txt)</b></summary>

```text
asgiref==3.11.1
attrs==26.1.0
Django==6.0.4
django-filter==25.2
djangorestframework==3.17.1
djangorestframework_simplejwt==5.5.1
drf-nested-routers==0.95.0
drf-spectacular==0.29.0
inflection==0.5.1
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
Markdown==3.10.2
pillow==12.2.0
PyJWT==2.13.0
PyYAML==6.0.3
referencing==0.37.0
rpds-py==2026.5.1
sqlparse==0.5.5
tzdata==2026.2
uritemplate==4.2.0
```
</details>

## 🚀 Instalação e Execução

Siga o passo a passo abaixo para configurar e rodar a aplicação no seu ambiente local:

**1. Clone o repositório:**
```bash
git clone https://github.com/josesilva710/NewStyle_API.git
cd NewStyle_API
```

**2. Crie e ative o ambiente virtual:**
* No Windows:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* No Linux/Mac:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Execute as migrações do banco de dados:**
```bash
python manage.py migrate
```

**5. Inicie o servidor local:**
```bash
python manage.py runserver
```
A API estará disponível em `http://127.0.0.1:8000/`.

## 🗄️ Modelagem de Dados

Abaixo está o diagrama UML (Entidade-Relacionamento) que modela a arquitetura do banco de dados da API, demonstrando as relações entre Usuários, Produtos, Carrinho e Pedidos:

![Diagrama UML da Modelagem de Dados](https://github.com/user-attachments/assets/2450d043-c382-4ff8-8abe-fe9312d39e56)

## 🏗️ Estrutura e Organização

A aplicação é composta por dois módulos principais:

### 👥 Users

Gerencia a autenticação, perfis e o relacionamento com a plataforma:

* **Autenticação e Segurança** — Gerenciamento de acessos via Tokens para controle de sessão e proteção de rotas.
* **Usuários e Perfis** — Controle de contas customizadas e informações pessoais (`fullname`, `national_id`).
* **Endereços** — Cadastro de localização (`street`, `city`, `state`, `cep`) vinculado aos usuários.
* **Métodos de Pagamento** — Gerenciamento das opções de pagamento (`PIX`, `CREDIT_CARD`, etc). Possui validação a nível de objeto para garantir que um cliente só possa acessar e deletar os seus próprios métodos cadastrados.
* **Contato** — Sistema de tickets para gerenciar solicitações de suporte.

### 🛍️ Shop

Gerencia o catálogo, estoque e fluxo de compras:

* **Produtos e SKUs** — Cadastro do catálogo (`Product`) e controle de estoque segmentado por variações (`color` e `size`). Inclui campos calculados dinamicamente em tempo de execução, como o total de variações (`variations_count`).
* **Pedidos** — Histórico de transações (`Order`), registrando o `status`, `payment_method` e vinculando o `customer` ao `merchant`. Por segurança, a transição de etapas do pedido é isolada em uma rota de ação customizada (`PATCH /orders/{id}/status/`).
* **Carrinho** — Espaço dinâmico para os itens selecionados (`Cart` e `CartItem`), com cálculo automático de subtotal e total.
* **Itens do Pedido** — Registro imutável (*snapshot*) dos produtos no momento da compra (`OrderItem`), garantindo histórico consistente.

## 🔍 Filtros e Buscas

### 📄 Parâmetros de Filtro
Abaixo estão os parâmetros aceitos pela API:

| Parâmetro | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `status` | String | Filtra pedidos por status (**ativos**: `PENDING`, `PROCESSING`, `SHIPPED`). | `?status=ativos` |
| `category` | String | Filtra produtos por uma categoria exata. | `?category=SHIRTS` |
| `category__in` | String | Filtra produtos combinando múltiplas categorias separadas por vírgula. | `?category__in=SHIRTS,PANTS` |

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
│   ├── filters.py
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
