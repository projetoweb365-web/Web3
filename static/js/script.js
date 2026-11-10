/* Secoes: 1) Sidebar  2) Login  3) Formulário  4) Presença (inclui salvar a chamada)  5) Envio do login */


/* SIDEBAR  */

const ITENS_MENU = [
  { id: 'inicio',        href: '/',              icone: '/static/images/inicio.png',     alt: 'Página Inicial' },
  { id: 'presenca',      href: '/presenca',      icone: '/static/images/presenca.png',   alt: 'Presença' },
  { id: 'documentos',    href: '/documentos',    icone: '/static/images/documentos.png', alt: 'Documentos' },
  { id: 'formulario',    href: '/formulario',    icone: '/static/images/formulario.png', alt: 'Formulário' },
  { id: 'configuracoes', href: '/configuracoes', icone: '/static/images/config.png',     alt: 'Configurações' }
];

function renderizarSidebar() {
  const alvo = document.getElementById('sidebar');
  if (!alvo) return;

  const paginaAtual = document.body.dataset.pagina;

  const links = ITENS_MENU.map(item => `
        <li>
          <a href="${item.href}" class="${item.id === paginaAtual ? 'ativo' : ''}">
            <img src="${item.icone}" class="icones" alt="${item.alt}">
          </a>
        </li>`).join('');

  alvo.outerHTML = `
    <aside class="sidebar">
      <a href="/"><img src="/static/images/logo.png" width="280" alt="Logo"></a>
      <ul class="nav-links">${links}
      </ul>

      <div class="sidebar-footer">
        <div class="perfil-usuario">
          <div class="avatar-placeholder"></div>
          <div class="info-usuario">
            <span class="nome-usuario">Nome</span>
            <span class="plano-usuario">Plano</span>
          </div>
        </div>
        <a href="/login" class="btn-sair">
          <img src="/static/images/logout.png" alt="Sair" class="icone-sair">
          <span>Sair</span>
        </a>
      </div>
    </aside>`;
}

renderizarSidebar();


/* LOGIN: alterna entre "Entrar" e "Criar Conta" */

function alternarAba(aba) {
  const btnEntrar = document.getElementById('btn-tab-entrar');
  const btnCriar = document.getElementById('btn-tab-criar');
  const campoNome = document.getElementById('campo-nome');
  const inputNome = document.getElementById('nome');
  const btnSubmit = document.getElementById('btn-submit');

  if (aba === 'criar') {
    btnCriar.classList.add('ativo');
    btnEntrar.classList.remove('ativo');

    campoNome.style.display = 'block';
    inputNome.required = true;
    btnSubmit.innerText = 'Criar Conta';
  } else {
    btnEntrar.classList.add('ativo');
    btnCriar.classList.remove('ativo');

    campoNome.style.display = 'none';
    inputNome.required = false;
    btnSubmit.innerText = 'Entrar';
  }
}


/* 3) FORMULÁRIO: botão "Enviar". Por enquanto só leva para a tela de relatórios;
   quando houver backend, é aqui que os dados do formulário devem ser enviados. */

function mostrarRelatorio() {
  window.location.href = '/relatorios';
}


/* 4) PRESENÇA: seleção de alunos, marcar presente/ausente e atualização dos cartões.
   Por enquanto só altera a tela; quando houver backend, é aqui que a chamada deve ser enviada. */

document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.querySelector('.tabela-frequencia tbody');
  if (!tbody) return;
 
  const checkTodos = document.getElementById('check-todos');
  const textoSelecionados = document.getElementById('texto-selecionados');
  const btnPresentes = document.getElementById('btn-marcar-presentes');
  const btnAusentes = document.getElementById('btn-marcar-ausentes');
 
  const elTotal = document.getElementById('valor-total');
  const elPresentes = document.getElementById('valor-presentes');
  const elAusentes = document.getElementById('valor-ausentes');
  const elTaxa = document.getElementById('valor-taxa');
 
  const getLinhas = () => Array.from(tbody.querySelectorAll('tr[data-id]'));
  const getCheck = (tr) => tr.querySelector('input[type="checkbox"]');
  const getBadge = (tr) => tr.querySelector('.badge');
  const estaPresente = (tr) => getBadge(tr).classList.contains('badge-presente');
 
  function definirStatus(tr, presente) {
    const badge = getBadge(tr);
    badge.classList.toggle('badge-presente', presente);
    badge.classList.toggle('badge-ausente', !presente);
    badge.textContent = presente ? 'Presente' : 'Ausente';
  }
 
  function atualizar() {
    const linhas = getLinhas();
    const selecionadas = linhas.filter((tr) => getCheck(tr).checked);
 
    // destaque das linhas selecionadas
    linhas.forEach((tr) => {
      tr.classList.toggle('linha-selecionada', getCheck(tr).checked);
    });
 
    // texto da barra de ações
    const n = selecionadas.length;
    textoSelecionados.textContent =
      n === 0 ? 'Nenhum aluno selecionado'
      : n === 1 ? '1 aluno selecionado'
      : `${n} alunos selecionados`;
 
    // botões só ativos com seleção
    btnPresentes.disabled = n === 0;
    btnAusentes.disabled = n === 0;
 
    // checkbox "selecionar todos" (marcado, vazio ou indeterminado)
    checkTodos.checked = linhas.length > 0 && n === linhas.length;
    checkTodos.indeterminate = n > 0 && n < linhas.length;
 
    // cartões de métricas, calculados a partir da tabela
    const total = linhas.length;
    const presentes = linhas.filter(estaPresente).length;
    elTotal.textContent = total;
    elPresentes.textContent = presentes;
    elAusentes.textContent = total - presentes;
    elTaxa.textContent = (total ? Math.round((presentes / total) * 100) : 0) + '%';
  }
 
  function marcarSelecionados(presente) {
    let mudou = false;
    getLinhas().forEach((tr) => {
      const check = getCheck(tr);
      if (check.checked) {
        definirStatus(tr, presente);
        check.checked = false; // limpa a seleção depois de marcar
        mudou = true;
      }
    });
    atualizar();
    if (mudou && typeof avisarNaoSalvo === 'function') avisarNaoSalvo();
  }
 
  // checkbox "selecionar todos"
  checkTodos.addEventListener('change', () => {
    getLinhas().forEach((tr) => {
      getCheck(tr).checked = checkTodos.checked;
    });
    atualizar();
  });
 
  // clicar em qualquer ponto da linha alterna a seleção
  tbody.addEventListener('click', (e) => {
    const tr = e.target.closest('tr');
    if (!tr || !tr.dataset.id) return;
    const check = getCheck(tr);
    if (e.target !== check) check.checked = !check.checked;
    atualizar();
  });
 
  btnPresentes.addEventListener('click', () => marcarSelecionados(true));
  btnAusentes.addEventListener('click', () => marcarSelecionados(false));
 
  atualizar();


  /* ---- Salvar e carregar a chamada no banco (rotas do Flask) ---- */

  const dataAula = document.getElementById('data-aula');
  const btnSalvar = document.getElementById('btn-salvar-chamada');
  const msgChamada = document.getElementById('msg-chamada');
  if (!dataAula || !btnSalvar || !msgChamada) return;


  function hoje() {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 10);
  }

  function mostrar(texto, tipo) {
    if (!msgChamada) return;
    msgChamada.textContent = texto;
    msgChamada.className = 'msg-chamada ' + (tipo || '');
  }

  function avisarNaoSalvo() {
    mostrar('Alterações ainda não salvas.', 'aviso');
  }

  // volta todos para "Presente", aplica o que está salvo no banco para a data e limpa a seleção
  async function carregarDia() {
    mostrar('');
    try {
      const resp = await fetch('/frequencia/dia?data=' + encodeURIComponent(dataAula.value));
      if (!resp.ok) throw new Error();
      const salvos = await resp.json();

      const porId = new Map(salvos.map((s) => [String(s.inscricao_id), s.presente === 1]));
      getLinhas().forEach((tr) => {
        definirStatus(tr, porId.has(tr.dataset.id) ? porId.get(tr.dataset.id) : true);
        getCheck(tr).checked = false;
      });
      atualizar();

      if (salvos.length > 0) mostrar('Chamada salva para este dia.', 'ok');
      else mostrar('Chamada ainda não salva para este dia.', 'aviso');
    } catch (erro) {
      mostrar('Não foi possível carregar a chamada.', 'erro');
    }
  }

  // manda o status de todos os alunos da tela para o Flask
  async function salvarChamada() {
    if (!dataAula.value) {
      mostrar('Escolha a data da aula.', 'erro');
      return;
    }

    const registros = getLinhas().map((tr) => ({
      inscricao_id: Number(tr.dataset.id),
      presente: estaPresente(tr)
    }));

    btnSalvar.disabled = true;
    mostrar('Salvando...');
    try {
      const resp = await fetch('/frequencia/lote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data_aula: dataAula.value, registros })
      });
      const dados = await resp.json();
      if (resp.ok) mostrar(dados.mensagem, 'ok');
      else mostrar(dados.erro || 'Erro ao salvar a chamada.', 'erro');
    } catch (erro) {
      mostrar('Não foi possível conectar ao servidor.', 'erro');
    } finally {
      btnSalvar.disabled = getLinhas().length === 0;
    }
  }

  btnSalvar.disabled = getLinhas().length === 0;
  btnSalvar.addEventListener('click', salvarChamada);
  dataAula.addEventListener('change', carregarDia);

  dataAula.value = hoje();
  carregarDia();
});


/* 5) ENVIO DO LOGIN: manda o formulário para o Flask (fetch) e trata a resposta JSON
      {"success": true/false, "message": "..."} sem recarregar a página. */

const ROTA_LOGIN = '/login';
const ROTA_CRIAR_CONTA = '/criar_conta'; // troque pelo caminho da rota do criar_conta.py

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-login');
  if (!form) return;

  const msg = document.getElementById('msg-login');
  const btn = document.getElementById('btn-submit');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '';

    const criando = document.getElementById('btn-tab-criar').classList.contains('ativo');
    btn.disabled = true;

    try {
      const resp = await fetch(criando ? ROTA_CRIAR_CONTA : ROTA_LOGIN, {
        method: 'POST',
        body: new FormData(form)
      });
      const dados = await resp.json();

      if (!dados.success) {
        msg.textContent = dados.message;
      } else if (criando) {
        alternarAba('entrar');           // conta criada: volta para a aba "Entrar"
        msg.style.color = '#10b981';
        msg.textContent = dados.message;
      } else {
        window.location.href = '/';      // login ok: vai para o dashboard
      }
    } catch (erro) {
      msg.style.color = '#ef4444';
      msg.textContent = 'Não foi possível conectar ao servidor.';
    } finally {
      btn.disabled = false;
    }
  });
});