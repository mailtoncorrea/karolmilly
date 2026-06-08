const form = document.getElementById("loginForm");
const mensagem = document.getElementById("mensagem");
const titulo = document.getElementById("titulo");
const campoNome = document.getElementById("campoNome");
const alternar = document.getElementById("alternar");
const btnAcao = document.getElementById("btnAcao");

let modoCadastro = false;

alternar.addEventListener("click", () => {
  modoCadastro = !modoCadastro;
  if (modoCadastro) {
    titulo.textContent = "Cadastro";
    campoNome.style.display = "block";
    btnAcao.textContent = "Cadastrar";
    alternar.textContent = "Já tem uma conta? Faça login";
  } else {
    titulo.textContent = "Login";
    campoNome.style.display = "none";
    btnAcao.textContent = "Entrar";
    alternar.textContent = "Não tem uma conta? Cadastre-se";
  }
  mensagem.textContent = "";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  mensagem.textContent = "";

  const usuario = document.getElementById("usuario").value.trim();
  const senha = document.getElementById("senha").value.trim();
  const nome = document.getElementById("nome").value.trim();

  if (modoCadastro && (!usuario || !senha || !nome)) {
    mensagem.textContent = "Preencha todos os campos.";
    return;
  }

  if (!modoCadastro && (!usuario || !senha)) {
    mensagem.textContent = "Preencha usuário e senha.";
    return;
  }

  try {
    const url = modoCadastro
      ? "http://localhost:5000/api/cadastrar"
      : "http://localhost:5000/api/login";

    const body = modoCadastro
      ? JSON.stringify({ nome, usuario, senha })
      : JSON.stringify({ usuario, senha });

    const resposta = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });

    const dados = await resposta.json();

    if (resposta.ok) {
      mensagem.style.color = "green";
      mensagem.textContent = dados.mensagem;

      if (!modoCadastro) {
        localStorage.setItem("usuario_logado", usuario);
        setTimeout(() => {
          window.location.href = "vendas.html";
        }, 1000);
      } else {
        // após cadastro, volta para o login
        setTimeout(() => {
          alternar.click();
        }, 1200);
      }
    } else {
      mensagem.style.color = "#d44";
      mensagem.textContent = dados.erro || "Erro inesperado.";
    }
  } catch (erro) {
    mensagem.style.color = "#d44";
    mensagem.textContent = "Erro ao conectar com o servidor.";
  }
});
