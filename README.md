# 🛍️ Karol Milly

Sistema de **gestão de vendas** e **controle de clientes, produtos e pagamentos**, desenvolvido para uma cliente.  
A aplicação possui frontend em **HTML, CSS e JavaScript**, e backend em **Flask** com **PostgreSQL**.

---

## 🚀 Funcionalidades

- Cadastro e listagem de **clientes** (com telefone e verificação de duplicidade)
- Cadastro e controle de **produtos e estoque**
- Registro de **vendas** e **pagamentos**
- Histórico de transações por cliente
- **Geração de relatórios em PDF**
- Sistema de **login com criptografia de senha**

---

## 🧰 Tecnologias

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask, psycopg2, Flask-CORS
- **Banco de Dados:** PostgreSQL
- **Outros:** reportlab (PDF), bcrypt (senhas)

---

## ⚙️ Execução

### Backend

```bash
python app.py
```

A API roda em:  
👉 http://localhost:5000

### Frontend

Abra `vendas.html` ou `produtos.html` no navegador.

---

## 📦 Estrutura Simplificada

```
KarolMilly/
├── backend/
│   ├── app.py
│   └── routes/
│       ├── clientes.py
│       ├── produtos.py
│       ├── vendas.py
│       └── pagamentos.py
└── frontend/
    └── static/
        ├── css/
            ├── cadastro.css
            ├── estoque.css
            ├── login.css
            ├── relatorio.css
            ├── vendas.css
            └── produtos.css
        ├── js/
            ├── cadastro.js
            ├── estoque.js
            ├── login.js
            ├── relatorio.js
            ├── vendas.js
            └── produtos.js
    ├── vendas.html
    ├── produtos.html
    ├── cadastro.html
    ├── estoque.html
    ├── login.html
    ├── relatorios.html

```

---

## 👨‍💻 Autor

**Desenvolvido por:** Mailton Correa
**Telefone:** (91) 98499-0954
📧 **Contato:** benicorrea2@gmail.com
