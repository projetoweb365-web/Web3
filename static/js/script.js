/*Seções: 1) Sidebar  2) Login  3) Formulário */


/* SIDEBAR  */

const ITENS_MENU = [
  { id: 'presenca',      href: 'presenca.html',      icone: 'images/presenca.png',   alt: 'Presença' },
  { id: 'documentos',    href: 'documentos.html',    icone: 'images/documentos.png', alt: 'Documentos' },
  { id: 'alunos',        href: 'alunos.html',        icone: 'images/alunos.png',     alt: 'Alunos' },
  { id: 'formulario',    href: 'formulario.html',    icone: 'images/formulario.png', alt: 'Formulário' },
  { id: 'configuracoes', href: 'configuracoes.html', icone: 'images/config.png',     alt: 'Configurações' }
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
      <a href="index.html"><img src="images/logo.png" width="280" alt="Logo"></a>
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
        <a href="login.html" class="btn-sair">
          <img src="images/logout.png" alt="Sair" class="icone-sair">
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


/* 3) FORMULARIO: botão "Enviar" Por enquanto só leva para a tela de relatorios; quando houver backend,
   é aqui que os dados do formulário devem ser enviados. */

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
 
  const getLinhas = () => Array.from(tbody.querySelectorAll('tr'));
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
 
    // checkbox do cabeçalho (marcado, vazio ou indeterminado)
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
    getLinhas().forEach((tr) => {
      const check = getCheck(tr);
      if (check.checked) {
        definirStatus(tr, presente);
        check.checked = false; // limpa a seleção depois de marcar
      }
    });
    atualizar();
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
    if (!tr) return;
    const check = getCheck(tr);
    if (e.target !== check) check.checked = !check.checked;
    atualizar();
  });
 
  btnPresentes.addEventListener('click', () => marcarSelecionados(true));
  btnAusentes.addEventListener('click', () => marcarSelecionados(false));
 
  atualizar();
});
