function logout() {
  localStorage.removeItem("usuario_logado");
  window.location.href = "cadastro.html";
}
const usuario = localStorage.getItem("usuario_logado");
if (!usuario) {
  alert("⚠️ Você precisa fazer login para acessar o sistema.");
  window.location.href = "cadastro.html";
}

async function buscarTransacoes() {
  const nome = document.getElementById("nomeCliente").value.trim();
  const mensagem = document.getElementById("mensagem");
  const tabela = document.getElementById("tabelaRelatorio");
  const corpoTabela = document.getElementById("corpoTabela");
  tabela.style.display = "none";
  mensagem.textContent = "";

  if (!nome) {
    mensagem.textContent = "Por favor, digite o nome do cliente.";
    return;
  }

  try {
    const response = await fetch(
      `http://localhost:5000/transacoes?nome=${encodeURIComponent(nome)}`,
    );
    const dados = await response.json();

    if (response.status !== 200) {
      mensagem.textContent = dados.erro || "Erro ao buscar transações.";
      return;
    }

    if (dados.length === 0) {
      mensagem.textContent = "Nenhuma transação encontrada.";
      return;
    }

    corpoTabela.innerHTML = ""; // Limpa a tabela

    dados.forEach((transacao) => {
      const linha = document.createElement("tr");
      linha.innerHTML = `
            <td>${transacao.produto}</td>
            <td>${transacao.quantidade}</td>
            <td>R$ ${transacao.valor_total.toFixed(2)}</td>
            <td>R$ ${transacao.valor_pago.toFixed(2)}</td>
            <td>R$ ${transacao.deve.toFixed(2)}</td>
            <td>${transacao.data}</td>
          `;
      corpoTabela.appendChild(linha);
    });

    tabela.style.display = "table";
  } catch (error) {
    mensagem.textContent = "Erro ao buscar dados.";
    console.error(error);
  }
}

function irParaEstoque() {
  window.location.href = "estoque.html";
}
function irParaVendas() {
  window.location.href = "vendas.html";
}
