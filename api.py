from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import psycopg2
from database import conectar
import os
from datetime import datetime 

app = Flask(__name__)
CORS(app)  # Libera todas as origens

# CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}})

bcrypt = Bcrypt(app)

@app.route("/api/cadastrar", methods=["POST"])
def cadastrar():
    if not request.is_json:
        return jsonify({"erro": "Content-Type deve ser application/json"}), 400

    data = request.json

    required_fields = ["usuario", "senha", "nome"]
    if not all(field in data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in data]
        return jsonify({"erro": f"Campos obrigatórios ausentes: {', '.join(missing_fields)}"}), 400

    usuario = data["usuario"]
    senha = data["senha"]
    nome = data["nome"]

    try:
        # CORREÇÃO AQUI: Usando a instância 'bcrypt' inicializada
        senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")
    except Exception as e:
        print(f"Erro ao gerar hash da senha: {e}")
        return jsonify({"erro": "Erro interno ao processar senha"}), 500

    conn = None
    try:
        conn = conectar()
        if not conn:
            return jsonify({"erro": "Falha ao conectar ao banco de dados"}), 500

        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nome, usuario, senha_hash) VALUES (%s, %s, %s)",
                    (nome, usuario, senha_hash))
        conn.commit()
        cur.close()
        return jsonify({"mensagem": "Usuário cadastrado com sucesso"}), 201

    except psycopg2.errors.UniqueViolation:
        if conn:
            conn.rollback()
        return jsonify({"erro": "Usuário já existe"}), 409
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro no cadastro: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    usuario = data['usuario']
    senha = data['senha']

    conn = conectar()
    if not conn:
        return jsonify({"erro": "Falha ao conectar ao banco"}), 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT senha_hash FROM usuarios WHERE usuario = %s", (usuario,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and bcrypt.check_password_hash(result[0], senha):
            return jsonify({"mensagem": "Login realizado com sucesso"}), 200
        else:
            return jsonify({"erro": "Usuário ou senha inválidos"}), 401
    except Exception as e:
        print("Erro no login:", e)
        return jsonify({"erro": "Erro no servidor"}), 500
    
    

# 📌 1️⃣ ROTA PARA CADASTRAR CLIENTES (AGORA EVITA DUPLICADOS)
@app.route("/clientes/cadastrar", methods=["POST"])
def cadastrar_cliente():
    dados = request.json
    nome = dados.get("nome")
    telefone = dados.get("telefone", None)  # Agora permite telefone opcional

    if not nome:
        return jsonify({"erro": "Nome do cliente é obrigatório."}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    # Verifica se o cliente já existe
    cursor.execute("SELECT id FROM clientes WHERE LOWER(nome) = LOWER(%s)", (nome,))
    cliente_existente = cursor.fetchone()

    if cliente_existente:
        return jsonify({"erro": "Cliente já cadastrado."}), 400
    
    # Insere o cliente com telefone na tabela clientes
    cursor.execute("INSERT INTO clientes (nome, telefone) VALUES (%s, %s) RETURNING id", (nome, telefone))
    conexao.commit()
    
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Cliente cadastrado com sucesso!"})



@app.route("/clientes/atualizar_telefone", methods=["PUT"])
def atualizar_telefone():
    dados = request.json
    nome = dados.get("nome")
    telefone = dados.get("telefone")

    if not nome or not telefone:
        return jsonify({"erro": "Nome e telefone são obrigatórios para atualizar."}), 400

    conexao = conectar()
    cursor = conexao.cursor()

# Verifica se o cliente existe
    cursor.execute("SELECT id FROM clientes WHERE LOWER(nome) = LOWER(%s)", (nome,))
    cliente = cursor.fetchone()

    if not cliente:
        return jsonify({"erro": "Cliente não encontrado."}), 404

    cliente_id = cliente[0]

    # Atualiza o telefone diretamente na tabela clientes
    cursor.execute("UPDATE clientes SET telefone = %s WHERE id = %s", (telefone, cliente_id))

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Telefone atualizado com sucesso!"})

#  2️⃣ ROTA PARA REGISTRAR VENDAS (AGORA VALOR PAGO É OPCIONAL)
@app.route("/vendas", methods=["POST"])
def registrar_venda():
    try:
        dados = request.json
        cliente_nome = dados.get("cliente_nome", "").strip()
        produto_nome = dados.get("produto_nome", "").strip()
        quantidade = dados.get("quantidade")
        valor_pago = dados.get("valor_pago", 0)  # 🔹 Se não informado, assume 0

        if not all([cliente_nome, produto_nome, quantidade]):
            return jsonify({"erro": "Dados incompletos para registrar a venda"}), 400

        conn = conectar()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500

        cur = conn.cursor()

        # Verificar se o cliente existe
        cur.execute("SELECT id FROM clientes WHERE TRIM(nome) = %s", (cliente_nome,))
        cliente = cur.fetchone()
        if not cliente:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        cliente_id = cliente[0]

        # Verificar se o produto existe e obter o preço
        cur.execute("SELECT id, preco, estoque FROM produtos WHERE TRIM(nome) = %s", (produto_nome,))
        produto = cur.fetchone()
        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404

        produto_id, preco_unitario, estoque = produto

        # Verificar se há estoque suficiente
        if quantidade > estoque:
            return jsonify({"erro": "Estoque insuficiente"}), 400

        # Calcular total da compra e saldo devedor
        valor_total = preco_unitario * quantidade
        deve = valor_total - valor_pago

        # Registrar venda
        cur.execute(
            "INSERT INTO vendas (cliente_id, valor_total, valor_pago, deve, data) VALUES (%s, %s, %s, %s, NOW()) RETURNING id",
            (cliente_id, valor_total, valor_pago, deve)
        )
        venda_id = cur.fetchone()[0]

        # Registrar os itens vendidos
        cur.execute(
            "INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)",
            (venda_id, produto_id, quantidade, preco_unitario)
        )

        # Atualizar o estoque do produto
        cur.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s", (quantidade, produto_id))

        # Atualizar saldo devedor do cliente
        cur.execute("UPDATE clientes SET saldo_devedor = saldo_devedor + %s WHERE id = %s", (deve, cliente_id))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Venda registrada com sucesso", "venda_id": venda_id})

    except Exception as e:
        print("❌ Erro ao registrar venda:", e)
        return jsonify({"erro": "Erro interno ao registrar a venda"}), 500
    

@app.route('/produtos/nome/<string:nome>', methods=['GET'])
def buscar_produto_por_nome(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco, estoque FROM produtos WHERE nome ILIKE %s", (f"%{nome}%",))
    produto = cursor.fetchone()
    conn.close()

    if produto:
        return jsonify({
            "id": produto[0],
            "nome": produto[1],
            "preco": float(produto[2]),
            "estoque": produto[3]
        })
    else:
        return jsonify({"erro": "Produto não encontrado"}), 404


# 📌 ROTA PARA CADASTRAR PRODUTOS (EVITA DUPLICADOS)
@app.route("/produtos", methods=["POST"])
def adicionar_produto():
    dados = request.json
    nome = dados.get("nome", "").strip().lower()  # Convertendo para minúsculas
    preco = float(dados.get("preco", 0))
    estoque = int(dados.get("estoque", 0))

    if not nome or preco <= 0:
        return jsonify({"erro": "Nome e preço devem ser válidos!"}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    # Verifica se o produto já existe (ignora maiúsculas/minúsculas)
    cursor.execute("SELECT id, estoque FROM produtos WHERE LOWER(nome) = %s", (nome,))
    produto = cursor.fetchone()

    if produto:
        novo_estoque = produto[1] + estoque
        cursor.execute(
            "UPDATE produtos SET estoque = %s WHERE id = %s",
            (novo_estoque, produto[0]),
        )
        mensagem = "Estoque atualizado com sucesso!"
    else:
        cursor.execute(
            "INSERT INTO produtos (nome, preco, estoque) VALUES (%s, %s, %s)",
            (nome, preco, estoque),
        )
        mensagem = "Produto cadastrado com sucesso!"

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": mensagem})
# 🔄 ROTA PARA ATUALIZAR PRODUTO (PUT)
@app.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    dados = request.json
    nome = dados.get("nome", "").strip().lower()
    preco = float(dados.get("preco", 0))
    estoque = int(dados.get("estoque", 0))

    if not nome or preco <= 0:
        return jsonify({"erro": "Nome e preço devem ser válidos!"}), 400

    conn = conectar()
    if conn is None:
        return jsonify({"erro": "Erro ao conectar ao banco"}), 500

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE produtos SET nome = %s, preco = %s, estoque = %s WHERE id = %s",
            (nome, preco, estoque, produto_id),
        )
        if cur.rowcount == 0:
            conn.rollback()
            return jsonify({"erro": "Produto não encontrado para atualização."}), 404
            
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensagem": "Produto atualizado com sucesso!"}), 200

    except Exception as e:
        conn.rollback()
        print("❌ Erro ao atualizar produto:", e)
        return jsonify({"erro": "Erro interno ao atualizar produto."}), 500


# ❌ ROTA PARA EXCLUIR PRODUTO (DELETE)
@app.route("/produtos/<int:produto_id>", methods=["DELETE"])
def excluir_produto(produto_id):
    conn = conectar()
    if conn is None:
        return jsonify({"erro": "Erro ao conectar ao banco"}), 500

    try:
        cur = conn.cursor()
        # Verifica se o produto está em alguma venda antes de excluir (Boa Prática de Integridade)
        cur.execute("SELECT 1 FROM itens_venda WHERE produto_id = %s LIMIT 1", (produto_id,))
        if cur.fetchone():
            return jsonify({"erro": "Não é possível excluir: Produto já está em uma ou mais vendas registradas."}), 400

        cur.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
        
        if cur.rowcount == 0:
            conn.rollback()
            return jsonify({"erro": "Produto não encontrado para exclusão."}), 404

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensagem": "Produto excluído com sucesso!"}), 200

    except Exception as e:
        conn.rollback()
        print("❌ Erro ao excluir produto:", e)
        return jsonify({"erro": "Erro interno ao excluir produto."}), 500


@app.route("/produtos", methods=["GET"])
def listar_produtos():
    try:
        conn = conectar()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500

        cur = conn.cursor()
        cur.execute("SELECT id, nome, preco, estoque FROM produtos")
        produtos = [{"id": p[0], "nome": p[1], "preco": p[2], "estoque": p[3]} for p in cur.fetchall()]

        cur.close()
        conn.close()
        return jsonify(produtos)

    except Exception as e:
        print("❌ Erro ao listar produtos:", e)
        return jsonify({"erro": "Erro ao buscar produtos"}), 500


# 📌 3️⃣ ROTA PARA REGISTRAR PAGAMENTOS (EVITA PAGAMENTOS SEM COMPRA)
@app.route("/pagamento", methods=["POST"])
def registrar_pagamento():
    try:
        dados = request.json
        cliente_nome = dados.get("cliente_nome", "").strip()
        valor_pago = dados.get("valor_pago", 0)

        if not cliente_nome:
            return jsonify({"erro": "Nome do cliente é obrigatório"}), 400

        if valor_pago <= 0:
            return jsonify({"erro": "Valor pago deve ser maior que zero"}), 400

        conn = conectar()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500

        cur = conn.cursor()

        # Buscar cliente
        cur.execute("SELECT id, saldo_devedor FROM clientes WHERE TRIM(nome) = %s", (cliente_nome,))
        cliente = cur.fetchone()
        if not cliente:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        cliente_id, saldo_atual = cliente

        if saldo_atual <= 0:
            return jsonify({"erro": "Cliente não tem saldo devedor para pagar"}), 400

        # Atualizar saldo devedor do cliente
        novo_saldo = max(saldo_atual - valor_pago, 0)
        cur.execute("UPDATE clientes SET saldo_devedor = %s WHERE id = %s", (novo_saldo, cliente_id))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Pagamento registrado com sucesso!", "novo_saldo": novo_saldo})

    except Exception as e:
        print("❌ Erro ao registrar pagamento:", e)
        return jsonify({"erro": "Erro interno ao registrar pagamento"}), 500


# 📌 4️⃣ ROTA PARA LISTAR VENDAS (AGORA COM OS DIAS EM PORTUGUÊS)
@app.route("/vendas", methods=["GET"])
def listar_vendas():
    try:
        conn = conectar()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500

        cur = conn.cursor()
        cur.execute("""
            SELECT v.id, c.nome, v.valor_total, v.valor_pago, v.deve, 
                   TO_CHAR(v.data, 'FMDay, DD/MM/YYYY') 
            FROM vendas v
            JOIN clientes c ON v.cliente_id = c.id
        """)
        vendas = cur.fetchall()

        cur.close()
        conn.close()

        # Traduzir os dias da semana
        dias_traduzidos = {
            "Monday": "Segunda-feira", "Tuesday": "Terça-feira",
            "Wednesday": "Quarta-feira", "Thursday": "Quinta-feira",
            "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
        }

        vendas_formatadas = [
            {
                "id": v[0],
                "cliente": v[1],
                "valor_total": v[2],
                "valor_pago": v[3],
                "deve": v[4],
                "data": dias_traduzidos.get(v[5].split(",")[0], v[5])  # Traduzir dia da semana
            }
            for v in vendas
        ]

        return jsonify(vendas_formatadas)

    except Exception as e:
        print("❌ Erro ao listar vendas:", e)
        return jsonify({"erro": "Erro ao buscar vendas"}), 500
    
@app.route("/clientes", methods=["GET"])
def listar_clientes():
    
    try:
        conn = conectar()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500

        cur = conn.cursor()
        cur.execute("SELECT id, nome, saldo_devedor FROM clientes")
        clientes = [{"id": c[0], "nome": c[1], "saldo_devedor": c[2]} for c in cur.fetchall()]

        cur.close()
        conn.close()
        return jsonify(clientes)

    except Exception as e:
        print("❌ Erro ao listar clientes:", e)
        return jsonify({"erro": "Erro ao buscar clientes"}), 500
    
@app.route("/clientes/buscar", methods=["GET"])
def buscar_cliente():
    nome_cliente = request.args.get("nome", "").strip().lower()  # Converte para minúsculas

    if not nome_cliente:
        return jsonify({"erro": "Nome do cliente é obrigatório!"}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT id, nome, telefone, saldo_devedor FROM clientes WHERE LOWER(nome) = %s", (nome_cliente,))
    cliente = cursor.fetchone()

    cursor.close()
    conexao.close()

    if cliente:
        return jsonify({"id": cliente[0], "nome": cliente[1], "telefone": cliente[2], "saldo_devedor": cliente[3]})
    else:
        return jsonify({"erro": "Cliente não encontrado!"}), 404

@app.route("/transacoes", methods=["GET"])
def listar_transacoes():
    try:
        nome_cliente = request.args.get("nome", "").strip()

        conn = conectar()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500

        cur = conn.cursor()

        cur.execute("""
    SELECT v.id, p.nome, iv.quantidade, v.valor_total, v.valor_pago, v.deve, 
        TO_CHAR(v.data, 'FMDay, DD/MM/YYYY') 
    FROM vendas v
    JOIN clientes c ON v.cliente_id = c.id
    JOIN itens_venda iv ON v.id = iv.venda_id
    JOIN produtos p ON iv.produto_id = p.id
    WHERE TRIM(c.nome) = %s
""", (nome_cliente,))

        transacoes = [
            {
                "id": t[0],
                "produto": t[1],  # Nome do produto
                "quantidade": t[2],  # Quantidade comprada
                "valor_total": float(t[3]),
                "valor_pago": float(t[4]),
                "deve": float(t[5]),
                "data": t[6]  # Agora já está em português
            }
            for t in cur.fetchall()
        ]

        cur.close()
        conn.close()

        return jsonify(transacoes)

    except Exception as e:
        print("❌ Erro ao listar transações:", e)
        return jsonify({"erro": "Erro ao buscar transações"}), 500

  # ajuste conforme sua estrutura de pastas

@app.route('/pagamentos', methods=['POST'])
def realiar_pagamento():
    data = request.get_json()
    nome_cliente = data.get('nome_cliente')
    valor_pago = data.get('valor_pago')

    if not nome_cliente or not valor_pago:
        return jsonify({'erro': 'Nome do cliente e valor do pagamento são obrigatórios.'}), 400

    conn = conectar()
    if conn is None:
        return jsonify({'erro': 'Erro ao conectar ao banco de dados.'}), 500

    try:
        cur = conn.cursor()

        # Verifica se o cliente existe
        cur.execute("SELECT id, saldo_devedor FROM clientes WHERE LOWER(nome) = LOWER(%s)", (nome_cliente,))
        cliente = cur.fetchone()

        if not cliente:
            return jsonify({'erro': 'Cliente não encontrado.'}), 404

        cliente_id, saldo_devedor = cliente

        # Atualiza o saldo devedor do cliente
        novo_saldo = max(saldo_devedor - valor_pago, 0)
        cur.execute("UPDATE clientes SET saldo_devedor = %s WHERE id = %s", (novo_saldo, cliente_id))

        # ✅ Agora o pagamento será registrado no histórico
        cur.execute("""
            INSERT INTO pagamentos (cliente_id, valor_pago, data_pagamento)
            VALUES (%s, %s, NOW())
        """, (cliente_id, valor_pago))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'mensagem': 'Pagamento registrado com sucesso!'}), 200

    except Exception as e:
        print("Erro ao registrar pagamento:", e)
        return jsonify({'erro': 'Erro interno ao registrar pagamento.'}), 500


# 📜 NOVA ROTA: HISTÓRICO DE PAGAMENTOS POR CLIENTE
@app.route("/pagamentos/historico", methods=["GET"])
def historico_pagamentos():
    nome_cliente = request.args.get("nome", "").strip()

    if not nome_cliente:
        return jsonify({"erro": "Nome do cliente é obrigatório"}), 400

    conn = conectar()
    if conn is None:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500

    try:
        cur = conn.cursor()

        # Verifica se o cliente existe
        cur.execute("SELECT id FROM clientes WHERE LOWER(nome) = LOWER(%s)", (nome_cliente,))
        cliente = cur.fetchone()

        if not cliente:
            cur.close()
            conn.close()
            return jsonify({"erro": "Cliente não encontrado"}), 404

        cliente_id = cliente[0]

        # Busca o histórico de pagamentos (tabela 'pagamentos')
        cur.execute("""
            SELECT data_pagamento, valor_pago
            FROM pagamentos
            WHERE cliente_id = %s
            ORDER BY data_pagamento DESC
        """, (cliente_id,))

        pagamentos = cur.fetchall()
        cur.close()
        conn.close()

        lista = [
            {
                "data_pagamento": p[0].strftime("%d/%m/%Y %H:%M") if p[0] else None,
                "valor_pago": float(p[1])
            }
            for p in pagamentos
        ]

        return jsonify({"historico": lista}), 200

    except Exception as e:
        print("❌ Erro ao buscar histórico:", e)
        return jsonify({"erro": "Erro interno ao buscar histórico de pagamentos."}), 500


# 📜 NOVA ROTA: RELATÓRIO DE TRANSAÇÕES DETALHADAS COM FILTRO POR CLIENTE
# 📜 NOVA ROTA: RELATÓRIO DE TRANSAÇÕES DETALHADAS COM FILTRO POR CLIENTE
@app.route("/relatorios/transacoes", methods=["GET"])
def relatorio_transacoes():
    conn = conectar()
    if conn is None:
        return jsonify({"erro": "Erro ao conectar ao banco de dados"}), 500

    nome_cliente = request.args.get("cliente", "").strip()
    
    try:
        cur = conn.cursor()
        
        # SQL base para buscar as transações detalhadas
        sql = """
            SELECT
                c.nome AS nome_cliente,
                p.nome AS produto,
                iv.quantidade,
                v.valor_total,
                v.valor_pago,
                v.deve,
                v.data
            FROM vendas v
            JOIN clientes c ON v.cliente_id = c.id
            JOIN itens_venda iv ON v.id = iv.venda_id
            JOIN produtos p ON iv.produto_id = p.id
        """
        params = []
        
        # Adiciona a cláusula WHERE para filtrar por cliente, se o nome for fornecido
        if nome_cliente:
            sql += " WHERE c.nome ILIKE %s"
            params.append(f"%{nome_cliente}%") # ILIKE permite busca parcial e ignora maiúsculas/minúsculas

        sql += " ORDER BY v.data DESC"
        
        cur.execute(sql, params)
        transacoes = cur.fetchall()
        
        cur.close()
        conn.close()

        # Formata o resultado para JSON
        colunas = ["nome_cliente", "produto", "quantidade", "valor_total", "valor_pago", "deve", "data_transacao"]
        
        lista_transacoes = []
        for t in transacoes:
            transacao = dict(zip(colunas, t))
            # Formata a data para um formato mais legível
            transacao["data_transacao"] = transacao["data_transacao"].strftime('%d/%m/%Y %H:%M')
            # Converte valores decimais para float
            transacao["valor_total"] = float(transacao["valor_total"])
            transacao["valor_pago"] = float(transacao["valor_pago"])
            transacao["deve"] = float(transacao["deve"])
            lista_transacoes.append(transacao)

        return jsonify(lista_transacoes), 200

    except Exception as e:
        print("❌ Erro ao buscar relatório de transações:", e)
        return jsonify({"erro": "Erro interno ao buscar relatório de transações."}), 500


@app.route("/relatorios/total-recebido", methods=["GET"])
def total_recebido():
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE_TRUNC('month', data_pagamento) AS mes, SUM(valor_pago)
            FROM pagamentos
            GROUP BY mes
            ORDER BY mes DESC
        """)
        dados = cursor.fetchall()
        conn.close()

        return jsonify([{"mes": r[0].strftime('%m/%Y'), "total": float(r[1])} for r in dados])
    return jsonify({"erro": "Erro ao gerar relatório."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
