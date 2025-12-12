const usuario = localStorage.getItem("usuario_logado");
if (!usuario) {
  alert("⚠️ Você precisa fazer login para acessar o sistema.");
  window.location.href = "cadastro.html";
}

const API_URL = "http://192.168.18.14:5000"; // URL da API

// Função para carregar produtos do banco de dados via API
function carregarProdutos() {
  fetch(`${API_URL}/produtos`)
    .then((response) => response.json())
    .then((produtos) => {
      console.log("Produtos carregados:", produtos);
      listarProdutos(produtos);
    })
    .catch((error) => console.error("Erro ao carregar produtos:", error));
}

// Função para exibir os produtos na lista
function listarProdutos(produtos) {
  if (!Array.isArray(produtos)) {
    console.error("Erro: resposta inválida da API", produtos);
    return;
  }

  const lista = document.getElementById("listaProdutos");
  lista.innerHTML = "";

  produtos.forEach((produto) => {
    if (!produto || typeof produto.preco !== "number") {
      console.error("Produto inválido:", produto);
      return;
    }

    const item = document.createElement("li");
    item.textContent = `${produto.nome} - R$ ${produto.preco.toFixed(
      2
    )} - Estoque: ${produto.estoque}`;
    lista.appendChild(item);
  });
}

// Função para adicionar um novo produto
function adicionarProduto() {
  let nomeProduto = document
    .getElementById("produtoNome")
    .value.trim()
    .toLowerCase(); // Convertendo para minúsculas
  let precoProduto = parseFloat(document.getElementById("produtoPreco").value);
  let estoqueProduto =
    parseInt(document.getElementById("quantidadeProduto").value) || 0;

  if (!nomeProduto || isNaN(precoProduto) || precoProduto <= 0) {
    alert("Preencha o nome do produto e um preço válido!");
    return;
  }

  let dadosProduto = {
    nome: nomeProduto,
    preco: precoProduto,
    estoque: estoqueProduto,
  };

  fetch("http://192.168.18.14:5000/produtos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dadosProduto),
  })
    .then((response) => response.json())
    .then((data) => {
      alert("✅ " + data.mensagem);
      location.reload();
    })
    .catch((error) => console.error("Erro ao adicionar produto:", error));
}
