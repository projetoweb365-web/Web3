/*Seções: 1) Sidebar  2) Login  3) Formulário 4) Presenca */


/* SIDEBAR  */

const ITENS_MENU = [
  { id: "pagina_inicial",          href: '/',          icone: '/static/images/pagina_inicial.png',        alt: 'Home' },
  { id: 'presenca',      href: '/presenca',      icone: '/static/images/presenca.png',   alt: 'Presença' },
  { id: 'documentos',    href: '/documentos',    icone: '/static/images/documentos.png', alt: 'Documentos' },
  { id: 'formulario',    href: '/formulario',    icone: '/static/images/formulario.png', alt: 'Formulário' },
  { id: 'configuracoes', href: '/configuracoes', icone: '/static/images/config.png',     alt: 'Configurações' }
];

function renderizarSidebar() {
  const alvo = document.getElementById('sidebar');
  if (!alvo) return;

  const paginaAtual = document.body.dataset.pagina;
  const nomeUsuario = document.body.dataset.nome || "Usuário";
  const inicialUsuario = document.body.dataset.inicial || "U";
  const coresAvatar = {
  A: "#EF4444",
  B: "#F97316",
  C: "#EAB308",
  D: "#22C55E",
  E: "#14B8A6",
  F: "#06B6D4",
  G: "#3B82F6",
  H: "#6366F1",
  I: "#8B5CF6",
  J: "#A855F7",
  K: "#D946EF",
  L: "#EC4899",
  M: "#2563EB",
  N: "#0EA5E9",
  O: "#10B981",
  P: "#84CC16",
  Q: "#F59E0B",
  R: "#DC2626",
  S: "#9333EA",
  T: "#0891B2",
  U: "#059669",
  V: "#65A30D",
  W: "#CA8A04",
  X: "#EA580C",
  Y: "#C026D3",
  Z: "#7C3AED"
};

const corAvatar = coresAvatar[inicialUsuario] || "#2563EB";

  const links = ITENS_MENU.map(item => `
        <li>
          <a href="${item.href}" class="${item.id === paginaAtual ? 'ativo' : ''}">
            <img src="${item.icone}" class="icones" alt="${item.alt}">
          </a>
        </li>`).join('');

  alvo.outerHTML = `
    <aside class="sidebar">
      <a href="/"><img src="static/images/logo.png" width="280" alt="Logo"></a>
      <ul class="nav-links">${links}
      </ul>

      <div class="sidebar-footer">
        <div class="perfil-usuario">
          <div class="avatar-placeholder"
          style="background-color:${corAvatar}">${inicialUsuario}</div>
          <div class="info-usuario">
            <span class="nome-usuario">${nomeUsuario}</span>
            <span class="plano-usuario">Plano</span>
          </div>
        </div>
        <a href="/logout" class="btn-sair">
          <img src="static/images/logout.png" alt="Sair" class="icone-sair">
          <span>Sair</span>
        </a>
      </div>
    </aside>`;
}

renderizarSidebar();

/* LOGIN: alterna entre o formulário de "Entrar" e "Criar Conta" */
function alternarAba(aba) {
  const btnEntrar = document.getElementById('btn-tab-entrar');
  const btnCriar = document.getElementById('btn-tab-criar');
  const formLogin = document.getElementById('form-login');
  const formCadastro = document.getElementById('form-cadastro');

  if (aba === 'criar') {
    // Estiliza os botões do topo
    btnCriar.classList.add('ativo');
    btnEntrar.classList.remove('ativo');
    
    // Esconde o form de login e mostra o form de cadastro
    formLogin.style.display = 'none';
    formCadastro.style.display = 'block';
  } else {
    // Estiliza os botões do topo
    btnEntrar.classList.add('ativo');
    btnCriar.classList.remove('ativo');
    
    // Esconde o form de cadastro e mostra o form de login
    formCadastro.style.display = 'none';
    formLogin.style.display = 'block';
  }
}

/* 3) FORMULARIO: botão "Enviar" Por enquanto só leva para a tela de relatorios; quando houver backend,
   é aqui que os dados do formulário devem ser enviados. */



/*4)PRESENCA: seleção de alunos, marcar presente/ausente e atualização dos cartões.
Por enquanto só altera a tela quando houver backend, é aqui que a chamada deve ser enviada*/

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
