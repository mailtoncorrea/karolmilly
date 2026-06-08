function logout() {
  localStorage.removeItem("usuario_logado");
  window.location.href = "cadastro.html";
}

const loginForm = document.getElementById("loginForm");
const cadastroForm = document.getElementById("cadastroForm");

// Alternar entre login e cadastro
function mostrarLogin() {
  document.getElementById("loginFormContainer").classList.remove("hidden");
  document.getElementById("cadastroFormContainer").classList.add("hidden");
}

function mostrarCadastro() {
  document.getElementById("cadastroFormContainer").classList.remove("hidden");
  document.getElementById("loginFormContainer").classList.add("hidden");
}

// Login
loginForm.addEventListener("submit", async function (e) {
  e.preventDefault();
  const usuario = document.getElementById("loginUsuario").value;
  const senha = document.getElementById("loginSenha").value;

  const resposta = await fetch("http://localhost:5000/api/login", {
    method: "POST",
    mode: "cors",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario, senha }),
  });

  const dados = await resposta.json();
  const mensagem = document.getElementById("loginMensagem");

  if (resposta.ok) {
    localStorage.setItem("usuario_logado", usuario);
    window.location.href = "vendas.html"; // Redireciona pro sistema
  } else {
    mensagem.style.color = "red";
    mensagem.textContent = dados.erro;
  }
});

// Cadastro
cadastroForm.addEventListener("submit", async function (e) {
  e.preventDefault();

  const nome = document.getElementById("nome").value;
  const usuario = document.getElementById("usuario").value;
  const senha = document.getElementById("senha").value;
  const mensagem = document.getElementById("cadastroMensagem");

  if (senha.length < 6) {
    mensagem.style.color = "red";
    mensagem.textContent = "A senha deve ter no mínimo 6 caracteres.";
    return;
  }

  const resposta = await fetch("http://localhost:5000/api/cadastrar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, usuario, senha }),
  });

  const dados = await resposta.json();

  if (resposta.ok) {
    mensagem.style.color = "green";
    mensagem.textContent = "Cadastro realizado com sucesso!";
    cadastroForm.reset();
    setTimeout(() => {
      mostrarLogin();
      document.getElementById("loginMensagem").textContent =
        "Cadastro feito! Faça login.";
      document.getElementById("loginMensagem").style.color = "green";
    }, 1000);
  } else {
    mensagem.style.color = "red";
    mensagem.textContent = dados.erro || "Erro ao cadastrar.";
  }
});
