// Funções compartilhadas por todas as páginas (JavaScript puro)

// Chama a API em JSON; se a sessão expirou (401), volta para o login
async function api(url, metodo = "GET", corpo) {
  const r = await fetch(url, {
    method: metodo,
    headers: {
      "Content-Type": "application/json"
    },
    body: corpo ? JSON.stringify(corpo) : undefined,
    credentials: "same-origin"
  });

  const d = await r.json().catch(() => ({}));

  if (r.status === 401 && url !== "/api/login") {
    location.href = "/login?expirou=1";
    throw new Error(d.erro || "Sessão expirada.");
  }

  if (!r.ok) {
    throw new Error(d.erro || "Erro na requisição.");
  }

  return d;
}

// Cria um elemento HTML; usa textContent para evitar XSS
function el(tag, texto, attrs = {}) {
  const e = document.createElement(tag);

  if (texto != null) {
    e.textContent = texto;
  }

  return Object.assign(e, attrs);
}

// Mostra no topo uma mensagem de sucesso ("ok") ou de erro ("erro")
function mensagem(tipo, texto) {
  const msgEl = document.getElementById("msg");
  if (msgEl) {
    msgEl.className = "msg " + tipo;
    msgEl.textContent = texto;
    msgEl.style.display = "block";
  }
}

// Executa uma ação; se der certo mostra textoOk (se houver),
// se der erro mostra a mensagem da API
async function tentar(acao, textoOk) {
  try {
    await acao();

    if (textoOk) {
      mensagem("ok", textoOk);
    }
  } catch (er) {
    mensagem("erro", er.message);
  }
}

// Lê os campos (pelos ids) e devolve um objeto { campo: valor }
const lerCampos = campos =>
  Object.fromEntries(
    campos.map(c => [
      c,
      document.getElementById(c) ? document.getElementById(c).value : ""
    ])
  );

// Coloca os valores de um registro nos campos do formulário (para editar)
function preencher(campos, dados) {
  campos.forEach(c => {
    const elemento = document.getElementById(c);
    if (elemento) {
      elemento.value = dados[c] ?? "";
    }
  });
}

// Botão com texto, ação ao clicar e classe CSS opcional ("sec" ou "perigo")
const botao = (texto, acao, classe = "") =>
  el("button", texto, {
    className: classe,
    onclick: acao
  });

// Botão Excluir: confirma, chama DELETE na url e recarrega a lista
const botaoExcluir = (url, pergunta, recarregar) =>
  botao(
    "Excluir",
    () =>
      confirm(pergunta) &&
      tentar(
        async () => {
          await api(url, "DELETE");
          await recarregar();
        },
        "Excluído com sucesso."
      ),
    "perigo"
  );

// Linha da tabela: uma coluna para cada valor e os botões na última coluna
function linha(valores, ...botoes) {
  const tr = el("tr");

  valores.forEach(v => {
    const td = el("td");
    td.append(v ?? "");
    tr.append(td);
  });

  const td = el("td");
  td.append(...botoes);
  tr.append(td);

  return tr;
}

// Preenche um <select> com "Selecione..." e uma opção por item
function opcoes(select, itens, texto) {
  if (!select) return;
  select.replaceChildren(
    el("option", "Selecione...", { value: "" }),
    ...itens.map(i =>
      el("option", texto(i), { value: i.id })
    )
  );
}

function fmtData(s) {
  return s ? String(s).replace("T", " ").slice(0, 16) : "";
}

// Monta o menu do topo (Navbar) e devolve o nome do usuário logado 
async function montarMenu() {
  const { nome } = await api("/api/me");
  const topoEl = document.getElementById("topo");

  if (topoEl) {
    topoEl.replaceChildren(
      el("strong", "📱 Assistência"),
      el("a", "🏠 Início", { href: "/principal" }),
      el("a", "Clientes", { href: "/clientes" }),
      el("a", "Aparelhos", { href: "/aparelhos" }),
      el("a", "Agendamentos", { href: "/agendamentos" }),
      el("span", "Olá, " + (nome || ""), { className: "user" })
    );
  }

  return nome;
}