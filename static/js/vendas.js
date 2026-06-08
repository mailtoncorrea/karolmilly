function logout() {
  localStorage.removeItem("usuario_logado");
  window.location.href = "cadastro.html";
}

function realizarPagamento() {
  const nome = document.getElementById("clienteNome").value.trim();
  const valor = parseFloat(document.getElementById("valorPagamento").value);

  if (!nome || isNaN(valor) || valor <= 0) {
    alert("Informe o nome do cliente e um valor de pagamento válido.");
    return;
  }

  fetch("http://localhost:5000/pagamentos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome_cliente: nome, valor_pago: valor }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.erro) {
        alert("❌ " + data.erro);
      } else {
        alert("✅ " + data.mensagem);
        document.getElementById("valorPagamento").value = "";
      }
    })
    .catch((erro) => console.error("Erro ao registrar pagamento:", erro));
}

function buscarCliente() {
  let nomeCliente = document
    .getElementById("clienteNome")
    .value.trim()
    .toLowerCase();

  if (!nomeCliente) {
    alert("Digite um nome para buscar!");
    return;
  }

  fetch(
    `http://localhost:5000/clientes/buscar?nome=${encodeURIComponent(
      nomeCliente,
    )}`,
  )
    .then((response) => response.json())
    .then((data) => {
      if (data.erro) {
        alert("❌ " + data.erro);
      } else {
        alert(
          `✅ Cliente encontrado:\nNome: ${data.nome}\nTelefone: ${data.telefone}\nSaldo devedor: ${data.saldo_devedor}`,
        );
      }
    })
    .catch((error) => console.error("Erro ao buscar cliente:", error));
}

async function buscarTransacoes() {
  try {
    const nomeCliente = document
      .getElementById("buscarTransacaoNome")
      .value.trim();
    if (!nomeCliente) {
      alert("Digite um nome para buscar transações.");
      return;
    }

    const lista = document.getElementById("transacaoLista");
    lista.innerHTML = "";

    const resposta = await fetch(
      `http://localhost:5000/transacoes?nome=${encodeURIComponent(
        nomeCliente,
      )}`,
    );
    const transacoes = await resposta.json();

    if (!Array.isArray(transacoes)) {
      console.error("Erro: Resposta inesperada da API", transacoes);
      return;
    }

    transacoes.forEach((t) => {
      if (
        !t.produto ||
        !t.quantidade ||
        t.valor_total === undefined ||
        t.valor_pago === undefined
      ) {
        return;
      }

      let valorTotal = parseFloat(t.valor_total) || 0;
      let valorPago = parseFloat(t.valor_pago) || 0;
      let troco = valorPago - valorTotal;

      const item = document.createElement("li");
      item.textContent = `${t.data} - ${t.produto} - Qtd: ${
        t.quantidade
      } - R$ ${valorTotal.toFixed(2)} - Pago: R$ ${valorPago.toFixed(
        2,
      )} - Troco: R$ ${troco.toFixed(2)}`;
      lista.appendChild(item);
    });
  } catch (erro) {
    console.error("Erro ao buscar transações:", erro);
  }
}

function adicionarCliente() {
  let nomeInput = document.getElementById("clienteNome");
  let telefoneInput = document.getElementById("telefone");

  if (!nomeInput) return;

  let nome = nomeInput.value.trim();
  let telefone = telefoneInput ? telefoneInput.value.trim() : "";

  if (nome === "") {
    alert("O nome do cliente é obrigatório.");
    return;
  }

  let dados = { nome: nome };
  if (telefone !== "") dados.telefone = telefone;

  fetch("http://localhost:5000/clientes/cadastrar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  })
    .then(async (response) => {
      const data = await response.json();

      if (!response.ok) {
        alert("❌ " + (data?.mensagem || data?.erro));
        return;
      }

      alert("✅ " + (data?.mensagem || "Cliente cadastrado com sucesso!"));
      nomeInput.value = "";
      if (telefoneInput) telefoneInput.value = "";
    })
    .catch((error) => {
      console.error("Erro ao cadastrar cliente:", error);
      alert("❌ Erro inesperado ao cadastrar cliente.");
    });
}

function registrarCompra() {
  let clienteNome = document.getElementById("compraCliente").value.trim();
  let produtoNome = document.getElementById("compraProduto").value.trim();
  let quantidade = document.getElementById("compraQtd").value;
  let valorPago = document.getElementById("valorPago").value;

  if (!clienteNome || !produtoNome || !quantidade) {
    alert("Preencha todos os campos obrigatórios!");
    return;
  }

  let dadosCompra = {
    cliente_nome: clienteNome,
    produto_nome: produtoNome,
    quantidade: parseInt(quantidade),
    valor_pago: parseFloat(valorPago) || 0,
  };

  fetch("http://localhost:5000/vendas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dadosCompra),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.erro) {
        alert("❌ Erro: " + data.erro);
      } else {
        alert("✅ Compra registrada com sucesso!");
        location.reload();
      }
    })
    .catch((error) => console.error("Erro ao registrar compra:", error));
}

function irParaEstoque() {
  window.location.href = "estoque.html";
}

function irParaRelatorios() {
  window.location.href = "relatorio.html";
}
