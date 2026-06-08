function logout() {
  localStorage.removeItem("usuario_logado");
  window.location.href = "cadastro.html";
}

const usuario = localStorage.getItem("usuario_logado");
if (!usuario) {
  alert("⚠️ Você precisa fazer login para acessar o sistema.");
  window.location.href = "cadastro.html";
}

const API_URL = "http://localhost:5000";

async function cadastrarProduto() {
  const nome = document.getElementById("nome").value;
  const preco = parseFloat(document.getElementById("preco").value);
  const estoque = parseInt(document.getElementById("estoque").value);

  if (!nome || isNaN(preco) || isNaN(estoque)) {
    alert("Preencha todos os campos corretamente.");
    return;
  }

  const produto = { nome, preco, estoque };

  try {
    const response = await fetch(`${API_URL}/produtos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(produto),
    });

    if (!response.ok) throw new Error("Erro ao cadastrar produto");

    alert("Produto cadastrado com sucesso!");
    document.getElementById("nome").value = "";
    document.getElementById("preco").value = "";
    document.getElementById("estoque").value = "";
    carregarProdutos();
  } catch (error) {
    console.error("Erro ao cadastrar:", error);
    alert("Erro ao cadastrar produto.");
  }
}

function carregarProdutos() {
  fetch(`${API_URL}/produtos`)
    .then((response) => response.json())
    .then((produtos) => {
      const tabela = document.getElementById("tabelaProdutos");
      tabela.innerHTML = "";

      produtos.forEach((produto) => {
        const row = tabela.insertRow();
        row.insertCell(0).textContent = produto.id;
        row.insertCell(1).textContent = produto.nome;
        row.insertCell(2).textContent = `R$ ${parseFloat(produto.preco).toFixed(
          2,
        )}`;
        row.insertCell(3).textContent = produto.estoque;
      });
    })
    .catch((error) => {
      console.error("Erro ao carregar produtos:", error);
    });
}

async function buscarProduto() {
  const nome = document.getElementById("buscaNome").value.trim();

  if (!nome) {
    alert("Digite o nome do produto para buscar.");
    return;
  }

  try {
    const response = await fetch(
      `${API_URL}/produtos/nome/${encodeURIComponent(nome)}`,
    );
    if (!response.ok) throw new Error("Produto não encontrado.");

    const produto = await response.json();
    document.getElementById("resultadoBusca").innerText =
      `Produto encontrado: "${produto.nome}" - Quantidade em estoque: ${produto.estoque}`;
  } catch (error) {
    document.getElementById("resultadoBusca").innerText =
      "Produto não encontrado ou erro na busca.";
  }
}

function irParaRelatorios() {
  window.location.href = "relatorio.html";
}
function irParaVendas() {
  window.location.href = "vendas.html";
}
