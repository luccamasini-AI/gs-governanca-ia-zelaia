"use strict";
const el = (id) => document.getElementById(id);
const historico = [];
let ocupado = false;
let fontesCarregadas = false;

function texto(tag, conteudo, classe) {
  const elemento = document.createElement(tag);
  elemento.textContent = conteudo;
  if (classe) elemento.className = classe;
  return elemento;
}

function linkFonte(fonte, rotulo, classe) {
  const link = texto("a", rotulo, classe);
  const url = new URL(fonte.url);
  if (url.protocol === "https:" && (url.hostname === "prefeitura.sp.gov.br" || url.hostname.endsWith(".prefeitura.sp.gov.br"))) link.href = url.href;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.title = fonte.titulo;
  return link;
}

function mensagem(conteudo, tipo) {
  const bloco = texto("div", conteudo, `mensagem ${tipo}`);
  el("mensagens").append(bloco);
  el("inicio").hidden = true;
  el("nova").hidden = false;
  return bloco;
}

function rolar() {
  const area = document.querySelector(".area-conversa");
  area.scrollTop = area.scrollHeight;
}

function estadoCarregando(valor) {
  ocupado = valor;
  el("enviar").disabled = valor;
  el("nova").disabled = valor;
  el("andamento").hidden = !valor;
  el("pergunta").readOnly = valor;
  el("formulario").setAttribute("aria-busy", String(valor));
}

document.querySelectorAll("[data-pergunta]").forEach((botao) => {
  botao.addEventListener("click", () => {
    if (ocupado) return;
    el("pergunta").value = botao.dataset.pergunta;
    document.querySelectorAll(".materiais button").forEach((b) => b.classList.toggle("selecionado", b === botao));
    el("pergunta").focus();
  });
});

el("formulario").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const pergunta = el("pergunta").value.trim();
  if (!pergunta || ocupado) return;
  el("erro").hidden = true;
  const mensagemUsuario = mensagem(pergunta, "usuario");
  estadoCarregando(true);
  rolar();
  const controle = new AbortController();
  const limite = setTimeout(() => controle.abort(), 180000);
  try {
    const retorno = await fetch("/api/conversar", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({pergunta, historico: historico.slice(-4)}), signal: controle.signal
    });
    const dados = await retorno.json();
    if (!retorno.ok && !dados.status) throw new Error(dados.erro || "Não foi possível concluir a consulta.");
    const bloco = mensagem("", "resposta");
    if (dados.status === "respondido") {
      const fontes = new Map(dados.fontes.map((f, i) => [f.id, {...f, numero: i + 1}]));
      dados.afirmacoes.forEach((afirmacao) => {
        const paragrafo = texto("p", afirmacao.texto);
        afirmacao.evidencias.forEach((id) => {
          const fonte = fontes.get(id);
          if (fonte) paragrafo.append(linkFonte(fonte, String(fonte.numero), "referencia"));
        });
        bloco.append(paragrafo);
      });
      if (dados.mensagem) bloco.append(texto("p", dados.mensagem));
      const lista = texto("div", "", "fontes-resposta");
      dados.fontes.forEach((f, i) => lista.append(linkFonte(f, `${i + 1}. ${f.titulo} ↗`)));
      bloco.append(lista);
    } else {
      bloco.append(texto("p", dados.mensagem));
    }
    if (!["bloqueado", "dados_pessoais", "entrada_invalida", "indisponivel"].includes(dados.status)) {
      historico.push(pergunta);
      el("pergunta").value = "";
    }
    if (dados.status === "dados_pessoais") {
      mensagemUsuario.remove();
      el("pergunta").value = "";
    }
  } catch (erro) {
    el("erro").textContent = erro.name === "AbortError" ? "A consulta excedeu o tempo disponível. Uma nova tentativa poderá ser realizada." : erro.message;
    el("erro").hidden = false;
  } finally {
    clearTimeout(limite);
    estadoCarregando(false);
    rolar();
    el("pergunta").focus();
  }
});

el("pergunta").addEventListener("keydown", (evento) => {
  if (evento.key === "Enter" && !evento.shiftKey && !evento.isComposing) {
    evento.preventDefault();
    el("formulario").requestSubmit();
  }
});

el("nova").addEventListener("click", () => {
  if (ocupado) return;
  historico.length = 0;
  el("mensagens").replaceChildren();
  el("inicio").hidden = false;
  el("nova").hidden = true;
  el("erro").hidden = true;
  el("pergunta").value = "";
  el("pergunta").focus();
});

async function mudarAba(fontes) {
  el("tela-assistente").hidden = fontes;
  el("tela-fontes").hidden = !fontes;
  for (const nome of ["assistente", "fontes"]) {
    const ativo = (nome === "fontes") === fontes;
    el(`aba-${nome}`).classList.toggle("ativo", ativo);
    if (ativo) el(`aba-${nome}`).setAttribute("aria-current", "page");
    else el(`aba-${nome}`).removeAttribute("aria-current");
  }
  if (fontes && !fontesCarregadas) {
    try {
      const resposta = await fetch("/api/fontes");
      if (!resposta.ok) throw new Error();
      const dados = await resposta.json();
      el("lista-fontes").replaceChildren();
      dados.fontes.forEach((fonte) => {
        const linha = texto("article", "", "fonte");
        const cabecalho = texto("div", "");
        cabecalho.append(texto("h2", fonte.titulo), texto("p", `${fonte.escopo} · Consulta: ${fonte.consultado_em.split("-").reverse().join("/")}`));
        linha.append(cabecalho, linkFonte(fonte, "Abrir fonte ↗"));
        el("lista-fontes").append(linha);
      });
      fontesCarregadas = true;
    } catch {
      el("lista-fontes").textContent = "As fontes estão temporariamente indisponíveis.";
    }
  }
}
el("aba-assistente").addEventListener("click", () => mudarAba(false));
el("aba-fontes").addEventListener("click", () => mudarAba(true));
