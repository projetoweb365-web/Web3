/*Seções: 1) Sidebar  2) Login  3) Formulário  4) Presenca  5) Documentos */


/* 1) SIDEBAR */

const ITENS_MENU = [
  { id: "pagina_inicial", href: '/',              icone: '/static/images/pagina_inicial.png', alt: 'Home' },
  { id: 'presenca',       href: '/presenca',      icone: '/static/images/presenca.png',       alt: 'Presença' },
  { id: 'documentos',     href: '/documentos',    icone: '/static/images/documentos.png',     alt: 'Documentos' },
  { id: 'formulario',     href: '/formulario',    icone: '/static/images/formulario.png',     alt: 'Formulário' },
  { id: 'configuracoes',  href: '/configuracoes', icone: '/static/images/config.png',         alt: 'Configurações' }
];

function renderizarSidebar() {
  const alvo = document.getElementById('sidebar');
  if (!alvo) return;

  const paginaAtual = document.body.dataset.pagina;
  const nomeUsuario = document.body.dataset.nome || "Usuário";
  const inicialUsuario = document.body.dataset.inicial || "U";
  const coresAvatar = {
    A: "#EF4444", B: "#F97316", C: "#EAB308", D: "#22C55E",
    E: "#14B8A6", F: "#06B6D4", G: "#3B82F6", H: "#6366F1",
    I: "#8B5CF6", J: "#A855F7", K: "#D946EF", L: "#EC4899",
    M: "#2563EB", N: "#0EA5E9", O: "#10B981", P: "#84CC16",
    Q: "#F59E0B", R: "#DC2626", S: "#9333EA", T: "#0891B2",
    U: "#059669", V: "#65A30D", W: "#CA8A04", X: "#EA580C",
    Y: "#C026D3", Z: "#7C3AED"
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
          <div class="avatar-placeholder" style="background-color:${corAvatar}">${inicialUsuario}</div>
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


/* 2) LOGIN: alterna entre o formulário de "Entrar" e "Criar Conta" */

function alternarAba(aba) {
  const btnEntrar = document.getElementById('btn-tab-entrar');
  const btnCriar = document.getElementById('btn-tab-criar');
  const formLogin = document.getElementById('form-login');
  const formCadastro = document.getElementById('form-cadastro');

  if (aba === 'criar') {
    btnCriar.classList.add('ativo');
    btnEntrar.classList.remove('ativo');
    formLogin.style.display = 'none';
    formCadastro.style.display = 'block';
  } else {
    btnEntrar.classList.add('ativo');
    btnCriar.classList.remove('ativo');
    formCadastro.style.display = 'none';
    formLogin.style.display = 'block';
  }
}


/* 4) PRESENCA: 4 Abas (Chamada, Turmas, Alunos, Histórico) */

document.addEventListener('DOMContentLoaded', () => {
  // --- Toggle Pílula das Abas ---
  const botoesToggle = document.querySelectorAll('.toggle-presenca .toggle-btn');
  const abasPresenca = document.querySelectorAll('.aba-presenca');

  botoesToggle.forEach((btn) => {
    btn.addEventListener('click', () => {
      botoesToggle.forEach((b) => b.classList.remove('ativo'));
      abasPresenca.forEach((aba) => (aba.style.display = 'none'));

      btn.classList.add('ativo');
      const alvo = document.getElementById(btn.dataset.alvo);
      if (alvo) alvo.style.display = 'block';

      if (btn.dataset.alvo === 'aba-historico') {
        recarregarHistorico();
      }
    });
  });

  // --- Referências da Chamada ---
  const tbodyChamada = document.getElementById('tbody-chamada');
  if (!tbodyChamada) return;

  const filtroTurma = document.getElementById('filtro-turma-chamada');
  const inputDataAula = document.getElementById('data-aula');
  const btnSalvarChamada = document.getElementById('btn-salvar-chamada');
  const msgChamada = document.getElementById('msg-chamada');

  // Define data de hoje por padrão no input de data
  if (inputDataAula && !inputDataAula.value) {
    inputDataAula.value = new Date().toISOString().split('T')[0];
  }

  const checkTodos = document.getElementById('check-todos');
  const textoSelecionados = document.getElementById('texto-selecionados');
  const btnPresentes = document.getElementById('btn-marcar-presentes');
  const btnAusentes = document.getElementById('btn-marcar-ausentes');

  const elTotal = document.getElementById('valor-total');
  const elPresentes = document.getElementById('valor-presentes');
  const elAusentes = document.getElementById('valor-ausentes');
  const elTaxa = document.getElementById('valor-taxa');

  const getTodasLinhas = () => Array.from(tbodyChamada.querySelectorAll('tr:not(.linha-vazia)'));
  const getLinhasVisiveis = () => getTodasLinhas().filter((tr) => tr.style.display !== 'none');
  const getCheck = (tr) => tr.querySelector('input[type="checkbox"]');
  const getBadge = (tr) => tr.querySelector('.badge');
  const estaPresente = (tr) => getBadge(tr).classList.contains('badge-presente');

  function definirStatus(tr, presente) {
    const badge = getBadge(tr);
    badge.classList.toggle('badge-presente', presente);
    badge.classList.toggle('badge-ausente', !presente);
    badge.textContent = presente ? 'Presente' : 'Ausente';
  }

  function atualizarChamada() {
    const linhas = getLinhasVisiveis();
    const selecionadas = linhas.filter((tr) => getCheck(tr).checked);

    linhas.forEach((tr) => {
      tr.classList.toggle('linha-selecionada', getCheck(tr).checked);
    });

    const n = selecionadas.length;
    textoSelecionados.textContent =
      n === 0 ? 'Nenhum aluno selecionado'
      : n === 1 ? '1 aluno selecionado'
      : `${n} alunos selecionados`;

    btnPresentes.disabled = n === 0;
    btnAusentes.disabled = n === 0;

    checkTodos.checked = linhas.length > 0 && n === linhas.length;
    checkTodos.indeterminate = n > 0 && n < linhas.length;

    const total = linhas.length;
    const presentes = linhas.filter(estaPresente).length;
    elTotal.textContent = total;
    elPresentes.textContent = presentes;
    elAusentes.textContent = total - presentes;
    elTaxa.textContent = (total ? Math.round((presentes / total) * 100) : 0) + '%';
  }

  function aplicarFiltroTurma() {
    if (!filtroTurma) return;
    const turmaSelecionada = filtroTurma.value;
    getTodasLinhas().forEach((tr) => {
      const match = turmaSelecionada === 'todas' || tr.dataset.turma === turmaSelecionada;
      tr.style.display = match ? '' : 'none';
      if (!match) getCheck(tr).checked = false;
    });
    atualizarChamada();
  }

  if (filtroTurma) {
    filtroTurma.addEventListener('change', aplicarFiltroTurma);
  }

  checkTodos.addEventListener('change', () => {
    getLinhasVisiveis().forEach((tr) => {
      getCheck(tr).checked = checkTodos.checked;
    });
    atualizarChamada();
  });

  tbodyChamada.addEventListener('click', (e) => {
    const tr = e.target.closest('tr:not(.linha-vazia)');
    if (!tr) return;
    const check = getCheck(tr);
    if (e.target !== check) check.checked = !check.checked;
    atualizarChamada();
  });

  btnPresentes.addEventListener('click', () => {
    getLinhasVisiveis().forEach((tr) => {
      const check = getCheck(tr);
      if (check.checked) {
        definirStatus(tr, true);
        check.checked = false;
      }
    });
    atualizarChamada();
  });

  btnAusentes.addEventListener('click', () => {
    getLinhasVisiveis().forEach((tr) => {
      const check = getCheck(tr);
      if (check.checked) {
        definirStatus(tr, false);
        check.checked = false;
      }
    });
    atualizarChamada();
  });

  // --- Salvar Chamada no Banco ---
  if (btnSalvarChamada) {
    btnSalvarChamada.addEventListener('click', async () => {
      const dataAula = inputDataAula.value;
      const linhas = getLinhasVisiveis();

      if (!dataAula) {
        msgChamada.textContent = 'Selecione a data da aula.';
        msgChamada.className = 'msg-chamada aviso';
        return;
      }

      if (linhas.length === 0) {
        msgChamada.textContent = 'Não há alunos visíveis para salvar.';
        msgChamada.className = 'msg-chamada aviso';
        return;
      }

      const registros = linhas.map((tr) => ({
        matricula: tr.dataset.id,
        presente: estaPresente(tr)
      }));

      btnSalvarChamada.disabled = true;
      const resp = await fetch('/presenca/salvar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data_aula: dataAula, registros })
      });
      const dados = await resp.json();
      btnSalvarChamada.disabled = false;

      msgChamada.textContent = dados.message;
      msgChamada.className = 'msg-chamada ' + (dados.success ? 'ok' : 'erro');

      if (dados.success) {
        recarregarHistorico();
      }
    });
  }

  // =====================================================
  // ABA 4: HISTÓRICO (Atualização e Filtros)
  // =====================================================
  const tbodyHistorico = document.getElementById('tbody-historico');
  const filtroHistBusca = document.getElementById('filtro-historico-busca');
  const filtroHistTurma = document.getElementById('filtro-historico-turma');
  const filtroHistData = document.getElementById('filtro-historico-data');
  const btnLimparHist = document.getElementById('btn-limpar-filtros-historico');
  const contadorHistorico = document.getElementById('contador-historico');

  function filtrarHistorico() {
    if (!tbodyHistorico) return;
    const termo = (filtroHistBusca?.value || '').trim().toLowerCase();
    const turma = filtroHistTurma?.value || 'todas';
    const data = filtroHistData?.value || '';

    const linhas = Array.from(tbodyHistorico.querySelectorAll('tr:not(.linha-vazia)'));
    let visiveis = 0;

    linhas.forEach((tr) => {
      const matchBusca = !termo || tr.dataset.busca.includes(termo);
      const matchTurma = turma === 'todas' || tr.dataset.turma === turma;
      const matchData = !data || tr.dataset.data === data;

      const mostrar = matchBusca && matchTurma && matchData;
      tr.style.display = mostrar ? '' : 'none';
      if (mostrar) visiveis++;
    });

    if (contadorHistorico) {
      contadorHistorico.textContent = `${visiveis} registro(s)`;
    }
  }

  async function recarregarHistorico() {
    if (!tbodyHistorico) return;
    const resp = await fetch('/presenca/historico');
    const dados = await resp.json();
    if (!dados.success) return;

    if (dados.historico.length === 0) {
      tbodyHistorico.innerHTML = '<tr class="linha-vazia"><td colspan="5">Nenhuma chamada registrada ainda. Salve uma chamada na primeira aba para visualizar aqui.</td></tr>';
      if (contadorHistorico) contadorHistorico.textContent = '0 registro(s)';
      return;
    }

    tbodyHistorico.innerHTML = dados.historico.map((h) => `
      <tr data-data="${h.data_iso}" data-turma="${h.turma_id}" data-busca="${h.matricula.toLowerCase()} ${h.aluno_nome.toLowerCase()}">
        <td>${h.data_formatada}</td>
        <td>${h.matricula}</td>
        <td>${h.aluno_nome}</td>
        <td>${h.turma_nome}</td>
        <td>
          <span class="badge ${h.presente ? 'badge-presente' : 'badge-ausente'}">
            ${h.presente ? 'Presente' : 'Ausente'}
          </span>
        </td>
      </tr>
    `).join('');

    filtrarHistorico();
  }

  if (filtroHistBusca) filtroHistBusca.addEventListener('input', filtrarHistorico);
  if (filtroHistTurma) filtroHistTurma.addEventListener('change', filtrarHistorico);
  if (filtroHistData) filtroHistData.addEventListener('change', filtrarHistorico);

  if (btnLimparHist) {
    btnLimparHist.addEventListener('click', () => {
      if (filtroHistBusca) filtroHistBusca.value = '';
      if (filtroHistTurma) filtroHistTurma.value = 'todas';
      if (filtroHistData) filtroHistData.value = '';
      filtrarHistorico();
    });
  }

  // =====================================================
  // ABA 2: TURMAS (Adicionar, Alterar e Remover)
  // =====================================================
  const formTurma = document.getElementById('form-turma');
  const tbodyTurmas = document.getElementById('tbody-turmas');
  const msgTurma = document.getElementById('msg-turma');
  const tituloFormTurma = document.getElementById('titulo-form-turma');
  const subtituloFormTurma = document.getElementById('subtitulo-form-turma');
  const btnSubmitTurma = document.getElementById('btn-submit-turma');
  const btnCancelarTurma = document.getElementById('btn-cancelar-edicao-turma');
  const inputEditTurmaId = document.getElementById('edit_turma_id');

  function resetarModoEdicaoTurma() {
    formTurma.reset();
    inputEditTurmaId.value = '';
    tituloFormTurma.textContent = 'Adicionar Turma';
    subtituloFormTurma.textContent = 'Preencha os dados para criar uma nova turma';
    btnSubmitTurma.textContent = 'Adicionar Turma';
    btnCancelarTurma.style.display = 'none';
  }

  if (btnCancelarTurma) {
    btnCancelarTurma.addEventListener('click', () => {
      resetarModoEdicaoTurma();
      msgTurma.textContent = '';
    });
  }

  if (tbodyTurmas) {
    tbodyTurmas.addEventListener('click', async (e) => {
      const tr = e.target.closest('tr:not(.linha-vazia)');
      if (!tr) return;

      if (e.target.classList.contains('btn-editar-turma')) {
        inputEditTurmaId.value = tr.dataset.id;
        document.getElementById('nome_turma').value = tr.dataset.nome;
        document.getElementById('modalidade').value = tr.dataset.modalidade;
        document.getElementById('dias').value = tr.dataset.dias;
        document.getElementById('horario').value = tr.dataset.horario;

        tituloFormTurma.textContent = `Alterar Turma #${tr.dataset.id}`;
        subtituloFormTurma.textContent = 'Edite os dados e clique em Salvar Alterações';
        btnSubmitTurma.textContent = 'Salvar Alterações';
        btnCancelarTurma.style.display = 'inline-block';
        msgTurma.textContent = '';
      }

      if (e.target.classList.contains('btn-remover-turma')) {
        if (!confirm(`Deseja realmente remover a turma "${tr.dataset.nome}"?`)) return;

        const formData = new FormData();
        formData.append('id', tr.dataset.id);

        const resp = await fetch('/presenca/turma/remover', {
          method: 'POST',
          body: formData
        });
        const dados = await resp.json();

        msgTurma.textContent = dados.message;
        msgTurma.className = 'msg-chamada ' + (dados.success ? 'ok' : 'erro');

        if (dados.success) {
          const idRemovido = String(dados.id);
          tr.remove();

          if (tbodyTurmas.querySelectorAll('tr').length === 0) {
            tbodyTurmas.innerHTML = '<tr class="linha-vazia"><td colspan="6">Nenhuma turma cadastrada ainda.</td></tr>';
          }

          document.querySelectorAll(`#turma_id option[value="${idRemovido}"], #filtro-turma-chamada option[value="${idRemovido}"], #filtro-historico-turma option[value="${idRemovido}"]`)
            .forEach(opt => opt.remove());

          document.querySelectorAll(`#tbody-chamada tr[data-turma="${idRemovido}"]`).forEach(row => {
            row.dataset.turma = '';
            row.children[3].textContent = 'Sem turma';
          });
          document.querySelectorAll(`#tbody-alunos-crud tr[data-turma="${idRemovido}"]`).forEach(row => {
            row.dataset.turma = '';
            row.children[2].textContent = 'Sem turma';
          });

          if (inputEditTurmaId.value === idRemovido) resetarModoEdicaoTurma();
          aplicarFiltroTurma();
        }
      }
    });
  }

  if (formTurma) {
    formTurma.addEventListener('submit', async (e) => {
      e.preventDefault();
      const editando = Boolean(inputEditTurmaId.value);
      const url = editando ? '/presenca/turma/editar' : '/presenca/turma/adicionar';
      const formData = new FormData(formTurma);

      const resp = await fetch(url, { method: 'POST', body: formData });
      const dados = await resp.json();

      msgTurma.textContent = dados.message;
      msgTurma.className = 'msg-chamada ' + (dados.success ? 'ok' : 'erro');

      if (dados.success && dados.turma) {
        const t = dados.turma;
        const selectAluno = document.getElementById('turma_id');

        if (editando) {
          const tr = tbodyTurmas.querySelector(`tr[data-id="${t.id}"]`);
          if (tr) {
            tr.dataset.nome = t.nome;
            tr.dataset.modalidade = t.modalidade;
            tr.dataset.dias = t.dias;
            tr.dataset.horario = t.horario;
            tr.children[1].textContent = t.nome;
            tr.children[2].textContent = t.modalidade;
            tr.children[3].textContent = t.dias;
            tr.children[4].textContent = t.horario;
          }

          if (selectAluno) {
            const opt = selectAluno.querySelector(`option[value="${t.id}"]`);
            if (opt) opt.textContent = `${t.nome} (${t.modalidade})`;
          }
          if (filtroTurma) {
            const opt = filtroTurma.querySelector(`option[value="${t.id}"]`);
            if (opt) opt.textContent = `${t.nome} (${t.modalidade})`;
          }
          if (filtroHistTurma) {
            const opt = filtroHistTurma.querySelector(`option[value="${t.id}"]`);
            if (opt) opt.textContent = t.nome;
          }

          document.querySelectorAll(`#tbody-chamada tr[data-turma="${t.id}"]`).forEach(row => {
            row.children[3].textContent = t.nome;
          });
          document.querySelectorAll(`#tbody-alunos-crud tr[data-turma="${t.id}"]`).forEach(row => {
            row.children[2].textContent = t.nome;
          });

          resetarModoEdicaoTurma();
        } else {
          const vazia = tbodyTurmas.querySelector('.linha-vazia');
          if (vazia) vazia.remove();

          tbodyTurmas.insertAdjacentHTML('beforeend', `
            <tr data-id="${t.id}" data-nome="${t.nome}" data-modalidade="${t.modalidade}" data-dias="${t.dias}" data-horario="${t.horario}">
              <td>${t.id}</td>
              <td>${t.nome}</td>
              <td>${t.modalidade}</td>
              <td>${t.dias}</td>
              <td>${t.horario}</td>
              <td class="celula-acoes">
                <button type="button" class="btn-tabela-editar btn-editar-turma">Alterar</button>
                <button type="button" class="btn-tabela-remover btn-remover-turma">Remover</button>
              </td>
            </tr>
          `);

          if (selectAluno) {
            selectAluno.insertAdjacentHTML('beforeend', `<option value="${t.id}">${t.nome} (${t.modalidade})</option>`);
          }
          if (filtroTurma) {
            filtroTurma.insertAdjacentHTML('beforeend', `<option value="${t.id}">${t.nome} (${t.modalidade})</option>`);
          }
          if (filtroHistTurma) {
            filtroHistTurma.insertAdjacentHTML('beforeend', `<option value="${t.id}">${t.nome}</option>`);
          }
          formTurma.reset();
        }
      }
    });
  }

  // =====================================================
  // ABA 3: ALUNOS (Adicionar, Alterar e Remover)
  // =====================================================
  const formAluno = document.getElementById('form-aluno');
  const tbodyAlunosCrud = document.getElementById('tbody-alunos-crud');
  const msgAluno = document.getElementById('msg-aluno');
  const tituloFormAluno = document.getElementById('titulo-form-aluno');
  const subtituloFormAluno = document.getElementById('subtitulo-form-aluno');
  const btnSubmitAluno = document.getElementById('btn-submit-aluno');
  const btnCancelarAluno = document.getElementById('btn-cancelar-edicao-aluno');
  const inputEditMatriculaOriginal = document.getElementById('edit_matricula_original');

  function resetarModoEdicaoAluno() {
    formAluno.reset();
    inputEditMatriculaOriginal.value = '';
    tituloFormAluno.textContent = 'Adicionar Aluno';
    subtituloFormAluno.textContent = 'Cadastre um aluno e associe a uma turma';
    btnSubmitAluno.textContent = 'Adicionar Aluno';
    btnCancelarAluno.style.display = 'none';
  }

  if (btnCancelarAluno) {
    btnCancelarAluno.addEventListener('click', () => {
      resetarModoEdicaoAluno();
      msgAluno.textContent = '';
    });
  }

  if (tbodyAlunosCrud) {
    tbodyAlunosCrud.addEventListener('click', async (e) => {
      const tr = e.target.closest('tr:not(.linha-vazia)');
      if (!tr) return;

      if (e.target.classList.contains('btn-editar-aluno')) {
        inputEditMatriculaOriginal.value = tr.dataset.matricula;
        document.getElementById('matricula').value = tr.dataset.matricula;
        document.getElementById('nome_aluno').value = tr.dataset.nome;
        document.getElementById('turma_id').value = tr.dataset.turma || '';

        tituloFormAluno.textContent = `Alterar Aluno (${tr.dataset.matricula})`;
        subtituloFormAluno.textContent = 'Edite os dados e clique em Salvar Alterações';
        btnSubmitAluno.textContent = 'Salvar Alterações';
        btnCancelarAluno.style.display = 'inline-block';
        msgAluno.textContent = '';
      }

      if (e.target.classList.contains('btn-remover-aluno')) {
        if (!confirm(`Deseja realmente remover o aluno "${tr.dataset.nome}"?`)) return;

        const formData = new FormData();
        formData.append('matricula', tr.dataset.matricula);

        const resp = await fetch('/presenca/aluno/remover', {
          method: 'POST',
          body: formData
        });
        const dados = await resp.json();

        msgAluno.textContent = dados.message;
        msgAluno.className = 'msg-chamada ' + (dados.success ? 'ok' : 'erro');

        if (dados.success) {
          const matRemovida = dados.matricula;
          tr.remove();

          if (tbodyAlunosCrud.querySelectorAll('tr').length === 0) {
            tbodyAlunosCrud.innerHTML = '<tr class="linha-vazia"><td colspan="4">Nenhum aluno cadastrado ainda.</td></tr>';
          }

          const trChamada = tbodyChamada.querySelector(`tr[data-id="${matRemovida}"]`);
          if (trChamada) trChamada.remove();

          if (tbodyChamada.querySelectorAll('tr').length === 0) {
            tbodyChamada.innerHTML = '<tr class="linha-vazia"><td colspan="5">Nenhum aluno inscrito ainda.</td></tr>';
          }

          if (inputEditMatriculaOriginal.value === matRemovida) resetarModoEdicaoAluno();
          atualizarChamada();
          recarregarHistorico();
        }
      }
    });
  }

  if (formAluno) {
    formAluno.addEventListener('submit', async (e) => {
      e.preventDefault();
      const editando = Boolean(inputEditMatriculaOriginal.value);
      const url = editando ? '/presenca/aluno/editar' : '/presenca/aluno/adicionar';
      const formData = new FormData(formAluno);

      const resp = await fetch(url, { method: 'POST', body: formData });
      const dados = await resp.json();

      msgAluno.textContent = dados.message;
      msgAluno.className = 'msg-chamada ' + (dados.success ? 'ok' : 'erro');

      if (dados.success && dados.aluno) {
        const a = dados.aluno;

        if (editando) {
          const matAntiga = dados.matricula_original;

          const trCrud = tbodyAlunosCrud.querySelector(`tr[data-matricula="${matAntiga}"]`);
          if (trCrud) {
            trCrud.dataset.matricula = a.matricula;
            trCrud.dataset.nome = a.nome;
            trCrud.dataset.turma = a.turma_id;
            trCrud.children[0].textContent = a.matricula;
            trCrud.children[1].textContent = a.nome;
            trCrud.children[2].textContent = a.turma_nome;
          }

          const trChamada = tbodyChamada.querySelector(`tr[data-id="${matAntiga}"]`);
          if (trChamada) {
            trChamada.dataset.id = a.matricula;
            trChamada.dataset.turma = a.turma_id;
            trChamada.children[1].textContent = a.matricula;
            trChamada.children[2].textContent = a.nome;
            trChamada.children[3].textContent = a.turma_nome;
          }

          resetarModoEdicaoAluno();
          aplicarFiltroTurma();
          recarregarHistorico();
        } else {
          const vaziaCrud = tbodyAlunosCrud.querySelector('.linha-vazia');
          if (vaziaCrud) vaziaCrud.remove();

          tbodyAlunosCrud.insertAdjacentHTML('beforeend', `
            <tr data-matricula="${a.matricula}" data-nome="${a.nome}" data-turma="${a.turma_id}">
              <td>${a.matricula}</td>
              <td>${a.nome}</td>
              <td>${a.turma_nome}</td>
              <td class="celula-acoes">
                <button type="button" class="btn-tabela-editar btn-editar-aluno">Alterar</button>
                <button type="button" class="btn-tabela-remover btn-remover-aluno">Remover</button>
              </td>
            </tr>
          `);

          const vaziaChamada = tbodyChamada.querySelector('.linha-vazia');
          if (vaziaChamada) vaziaChamada.remove();

          tbodyChamada.insertAdjacentHTML('beforeend', `
            <tr data-id="${a.matricula}" data-turma="${a.turma_id}">
              <td><input type="checkbox"></td>
              <td>${a.matricula}</td>
              <td>${a.nome}</td>
              <td>${a.turma_nome}</td>
              <td><span class="badge badge-presente">Presente</span></td>
            </tr>
          `);

          formAluno.reset();
          aplicarFiltroTurma();
        }
      }
    });
  }

  atualizarChamada();
});


/* 5) DOCUMENTOS: Toggle de Categoria, Upload e Edição na própria linha da tabela */

document.addEventListener('DOMContentLoaded', () => {
  const formUpload = document.getElementById('form-upload-documento');
  if (!formUpload) return;

  const toggleCategoria = document.getElementById('toggle-categoria-doc');
  const inputCategoria = document.getElementById('input-categoria-doc');
  const campoAluno = document.getElementById('campo-selecionar-aluno');
  const selectAluno = document.getElementById('select-aluno-doc');
  const btnEnviar = document.getElementById('btn-enviar-doc');
  const msgUpload = document.getElementById('msg-upload-doc');
  const tbodyDocs = document.getElementById('tbody-documentos');
  const filtroCategoriaTabela = document.getElementById('filtro-categoria-tabela');

  const CATEGORIAS = ['Aluno', 'Financeiro', 'Frequência', 'Jurídico', 'Geral'];
  const TIPOS = ['PDF', 'DOCX', 'XLSX', 'XLS', 'JPG', 'JPEG', 'PNG'];

  // Escapa texto antes de colocar em HTML/atributos
  function esc(valor) {
    return String(valor ?? '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function linhaDocumento(d) {
    const textoAluno = d.aluno_nome ? `${esc(d.aluno_nome)} (${esc(d.aluno_matricula)})` : '—';
    return `
      <tr data-id="${d.id}" data-categoria="${esc(d.categoria)}" data-aluno="${esc(d.aluno_matricula)}">
        <td style="text-align: left; font-weight: bold;">${esc(d.nome_original)}</td>
        <td><span class="badge-categoria">${esc(d.categoria)}</span></td>
        <td>${textoAluno}</td>
        <td>${esc(d.tipo)}</td>
        <td>${esc(d.responsavel)}</td>
        <td>${esc(d.data_upload)}</td>
        <td>
          <div class="acoes-tabela">
            <a href="/documentos/ver/${d.id}" target="_blank" title="Visualizar">
              <img src="/static/images/eye-icon.png" alt="Ver" class="icone-acao">
            </a>
            <button type="button" class="btn-icone-editar" data-id="${d.id}" title="Editar">
              <img src="/static/images/edit-icon.png" alt="Editar" class="icone-acao">
            </button>
            <a href="/documentos/baixar/${d.id}" title="Baixar">
              <img src="/static/images/download-icon.png" alt="Baixar" class="icone-acao">
            </a>
            <button type="button" class="btn-icone-remover" data-id="${d.id}" title="Remover">
              <img src="/static/images/trash-icon.png" alt="Apagar" class="icone-acao">
            </button>
          </div>
        </td>
      </tr>`;
  }

  /* ---------- Formulário de upload (categoria + envio) ---------- */

  function definirCategoria(categoria) {
    inputCategoria.value = categoria;
    toggleCategoria.querySelectorAll('.toggle-btn').forEach((b) => {
      b.classList.toggle('ativo', b.dataset.categoria === categoria);
    });
    if (categoria === 'Aluno') {
      campoAluno.style.display = 'flex';
      selectAluno.required = true;
    } else {
      campoAluno.style.display = 'none';
      selectAluno.required = false;
      selectAluno.value = '';
    }
  }

  if (toggleCategoria) {
    toggleCategoria.querySelectorAll('.toggle-btn').forEach((btn) => {
      btn.addEventListener('click', () => definirCategoria(btn.dataset.categoria));
    });
  }

  formUpload.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (inputCategoria.value === 'Aluno' && !selectAluno.value) {
      msgUpload.textContent = 'Selecione o aluno antes de enviar.';
      msgUpload.className = 'msg-upload-doc erro';
      return;
    }

    const formData = new FormData(formUpload);
    btnEnviar.disabled = true;
    btnEnviar.textContent = 'Enviando...';

    try {
      const resp = await fetch('/documentos/upload', { method: 'POST', body: formData });
      const dados = await resp.json();

      msgUpload.textContent = dados.message;
      msgUpload.className = 'msg-upload-doc ' + (dados.success ? 'ok' : 'erro');

      if (dados.success && dados.documento) {
        const vazia = tbodyDocs.querySelector('.linha-vazia-docs');
        if (vazia) vazia.remove();

        tbodyDocs.insertAdjacentHTML('afterbegin', linhaDocumento(dados.documento));
        document.getElementById('input-arquivo-doc').value = '';
        if (filtroCategoriaTabela) filtroCategoriaTabela.dispatchEvent(new Event('change'));
      }
    } finally {
      btnEnviar.disabled = false;
      btnEnviar.textContent = 'Fazer Upload';
    }
  });

  /* ---------- Filtro da tabela ---------- */

  if (filtroCategoriaTabela) {
    filtroCategoriaTabela.addEventListener('change', () => {
      const cat = filtroCategoriaTabela.value;
      tbodyDocs.querySelectorAll('tr:not(.linha-vazia-docs)').forEach((tr) => {
        tr.style.display = (cat === 'todas' || tr.dataset.categoria === cat) ? '' : 'none';
      });
    });
  }

  /* ---------- Edição na própria linha ---------- */

  const originais = new Map(); // tr -> innerHTML original (para Cancelar)

  // "15/11/2026 14:30" -> "2026-11-15T14:30" (formato do input datetime-local)
  function dataParaInput(texto) {
    const m = texto.trim().match(/^(\d{2})\/(\d{2})\/(\d{4})\s+(\d{2}):(\d{2})/);
    return m ? `${m[3]}-${m[2]}-${m[1]}T${m[4]}:${m[5]}` : '';
  }

  function opcoes(lista, atual) {
    return lista.map((o) => `<option value="${esc(o)}"${o === atual ? ' selected' : ''}>${esc(o)}</option>`).join('');
  }

  function cancelarEdicao(tr) {
    if (!originais.has(tr)) return;
    tr.innerHTML = originais.get(tr);
    tr.classList.remove('editando');
    originais.delete(tr);
  }

  function entrarEdicao(tr) {
    // só uma linha em edição por vez
    tbodyDocs.querySelectorAll('tr.editando').forEach(cancelarEdicao);

    const c = tr.children;
    const nome = c[0].textContent.trim();
    const categoria = tr.dataset.categoria;
    const matricula = tr.dataset.aluno || '';
    const tipo = c[3].textContent.trim();
    const responsavel = c[4].textContent.trim();
    const dataInput = dataParaInput(c[5].textContent);

    originais.set(tr, tr.innerHTML);
    tr.classList.add('editando');

    c[0].innerHTML = `<input type="text" class="input-edicao-doc" data-campo="nome_original" maxlength="255" value="${esc(nome)}">`;
    c[1].innerHTML = `<select class="input-edicao-doc" data-campo="categoria">${opcoes(CATEGORIAS, categoria)}</select>`;
    c[2].innerHTML = `<select class="input-edicao-doc" data-campo="aluno_matricula">${selectAluno.innerHTML}</select>`;
    c[3].innerHTML = `<select class="input-edicao-doc" data-campo="tipo">${opcoes(TIPOS, tipo)}</select>`;
    c[4].innerHTML = `<input type="text" class="input-edicao-doc" data-campo="responsavel" maxlength="100" value="${esc(responsavel)}">`;
    c[5].innerHTML = `<input type="datetime-local" class="input-edicao-doc" data-campo="data_upload" value="${dataInput}">`;
    c[6].innerHTML = `
      <div class="acoes-tabela">
        <button type="button" class="btn-salvar-linha">Salvar</button>
        <button type="button" class="btn-cancelar-linha">Cancelar</button>
      </div>`;

    const selAluno = c[2].querySelector('select');
    const selCat = c[1].querySelector('select');
    selAluno.value = matricula;
    selAluno.disabled = categoria !== 'Aluno';

    // Aluno só faz sentido na categoria "Aluno"
    selCat.addEventListener('change', () => {
      const ehAluno = selCat.value === 'Aluno';
      selAluno.disabled = !ehAluno;
      if (!ehAluno) selAluno.value = '';
    });

    c[0].querySelector('input').focus();
  }

  async function salvarEdicao(tr) {
    const campo = (nome) => tr.querySelector(`[data-campo="${nome}"]`);
    const payload = {
      nome_original: campo('nome_original').value.trim(),
      categoria: campo('categoria').value,
      aluno_matricula: campo('aluno_matricula').value,
      tipo: campo('tipo').value,
      responsavel: campo('responsavel').value.trim(),
      data_upload: campo('data_upload').value
    };

    if (!payload.nome_original) return alert('Informe o nome do arquivo.');
    if (!payload.responsavel) return alert('Informe o responsável.');
    if (!payload.data_upload) return alert('Informe a data de upload.');
    if (payload.categoria === 'Aluno' && !payload.aluno_matricula) {
      return alert('Selecione o aluno para a categoria Aluno.');
    }

    const btnSalvar = tr.querySelector('.btn-salvar-linha');
    btnSalvar.disabled = true;
    btnSalvar.textContent = 'Salvando...';

    try {
      const resp = await fetch(`/documentos/editar/${tr.dataset.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const dados = await resp.json();

      if (dados.success && dados.documento) {
        originais.delete(tr);
        tr.outerHTML = linhaDocumento(dados.documento);
        if (filtroCategoriaTabela) filtroCategoriaTabela.dispatchEvent(new Event('change'));
      } else {
        alert(dados.message || 'Não foi possível salvar.');
        btnSalvar.disabled = false;
        btnSalvar.textContent = 'Salvar';
      }
    } catch (err) {
      alert('Erro de conexão ao salvar.');
      btnSalvar.disabled = false;
      btnSalvar.textContent = 'Salvar';
    }
  }

  /* ---------- Cliques na tabela (editar, salvar, cancelar, remover) ---------- */

  tbodyDocs.addEventListener('click', async (e) => {
    const tr = e.target.closest('tr');
    if (!tr) return;

    if (e.target.closest('.btn-icone-editar')) return entrarEdicao(tr);
    if (e.target.closest('.btn-salvar-linha')) return salvarEdicao(tr);
    if (e.target.closest('.btn-cancelar-linha')) return cancelarEdicao(tr);

    const btnRemover = e.target.closest('.btn-icone-remover');
    if (!btnRemover) return;

    const docId = btnRemover.dataset.id;
    if (!confirm('Deseja realmente remover este documento?')) return;

    const resp = await fetch(`/documentos/remover/${docId}`, { method: 'POST' });
    const dados = await resp.json();

    if (dados.success) {
      originais.delete(tr);
      tr.remove();

      if (tbodyDocs.querySelectorAll('tr').length === 0) {
        tbodyDocs.innerHTML = '<tr class="linha-vazia-docs"><td colspan="7" style="padding: 25px; color: #666;">Nenhum documento salvo ainda.</td></tr>';
      }
    } else {
      alert(dados.message);
    }
  });

  // Enter salva, Esc cancela
  tbodyDocs.addEventListener('keydown', (e) => {
    const tr = e.target.closest('tr.editando');
    if (!tr) return;
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') { e.preventDefault(); salvarEdicao(tr); }
    if (e.key === 'Escape') cancelarEdicao(tr);
  });
});

function alternarModoNoturno() {
    document.body.classList.toggle('dark-mode');
    
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('tema', 'escuro');
    } else {
        localStorage.setItem('tema', 'claro');
    }
}
