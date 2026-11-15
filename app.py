from flask import Flask, request, render_template, session, redirect, url_for
import mysql.connector
import sys
import os

ccb = Flask(__name__)

ccb.secret_key = "ccb_sistema_2026"

sys.modules.setdefault("app", sys.modules[__name__])

conexao = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", 3306)),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", "senha"),
    database=os.environ.get("DB_NAME", "centro_cidadania_do_brasil")
)

cursor = conexao.cursor()


def executar_script_sql(nome_arquivo):
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arquivo)
    if not os.path.exists(caminho):
        return

    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()

    linhas_limpas = [
        linha for linha in conteudo.splitlines()
        if not linha.strip().startswith("--")
    ]
    comandos = "\n".join(linhas_limpas).split(";")

    for cmd in comandos:
        cmd = cmd.strip()
        if not cmd:
            continue
        try:
            cursor.execute(cmd)
        except mysql.connector.Error as err:
            if err.errno in (1060, 1061, 1826):
                pass
            else:
                print(f"Aviso SQL ({nome_arquivo}): {err}")

    conexao.commit()


executar_script_sql("banco.sql")


def usuario_logado():
    return "usuario_id" in session


def dados_usuario_atual():
    nome = session.get("usuario_nome") or "Admin"
    return nome, nome[0].upper()


def _um_valor(sql, padrao=0):
    """Executa uma consulta e devolve o primeiro valor da primeira linha."""
    cursor.execute(sql)
    linha = cursor.fetchone()
    return linha[0] if linha and linha[0] is not None else padrao


def _plural(n, singular, plural):
    return f"{n} {singular if n == 1 else plural}"


def resumo_dashboard():
    """Calcula, a partir do banco, tudo o que o dashboard mostra."""

    # ---- Alunos e turmas (página Presença)
    total_alunos = int(_um_valor("SELECT COUNT(*) FROM alunos"))
    total_turmas = int(_um_valor("SELECT COUNT(*) FROM turmas"))
    alunos_sem_turma = int(_um_valor("SELECT COUNT(*) FROM alunos WHERE turma_id IS NULL"))

    # ---- Chamada de hoje
    cursor.execute("""
        SELECT COALESCE(SUM(presente = 1), 0), COALESCE(SUM(presente = 0), 0)
        FROM chamadas_alunos
        WHERE data_aula = CURDATE()
    """)
    presentes_hoje, ausentes_hoje = (int(v) for v in cursor.fetchone())
    registros_hoje = presentes_hoje + ausentes_hoje
    presenca_pct = round(presentes_hoje * 100 / registros_hoje) if registros_hoje else None

    # ---- Presença acumulada no mês
    cursor.execute("""
        SELECT COALESCE(SUM(presente = 1), 0), COUNT(*)
        FROM chamadas_alunos
        WHERE YEAR(data_aula) = YEAR(CURDATE()) AND MONTH(data_aula) = MONTH(CURDATE())
    """)
    presentes_mes, registros_mes = (int(v) for v in cursor.fetchone())
    presenca_mes_pct = round(presentes_mes * 100 / registros_mes) if registros_mes else None

    # ---- Turmas com alunos que ainda não tiveram chamada hoje
    cursor.execute("""
        SELECT t.id, t.nome, t.horario
        FROM turmas t
        WHERE EXISTS (SELECT 1 FROM alunos a WHERE a.turma_id = t.id)
          AND NOT EXISTS (
              SELECT 1
              FROM chamadas_alunos c
              INNER JOIN alunos a ON a.matricula = c.aluno_matricula
              WHERE a.turma_id = t.id AND c.data_aula = CURDATE()
          )
        ORDER BY t.horario, t.nome
    """)
    turmas_sem_chamada = cursor.fetchall()

    # ---- Documentos (página Documentos)
    total_docs = int(_um_valor("SELECT COUNT(*) FROM arquivos"))
    alunos_sem_doc = int(_um_valor("""
        SELECT COUNT(*)
        FROM alunos a
        WHERE NOT EXISTS (SELECT 1 FROM arquivos f WHERE f.aluno_matricula = a.matricula)
    """))
    alunos_com_doc = total_alunos - alunos_sem_doc
    pct_docs = round(alunos_com_doc * 100 / total_alunos) if total_alunos else 0

    cursor.execute("""
        SELECT nome_original, categoria, DATE_FORMAT(data_upload, '%d/%m/%Y %H:%i')
        FROM arquivos
        ORDER BY data_upload DESC, id DESC
        LIMIT 2
    """)
    docs_recentes = cursor.fetchall()

    # ---- Inscrições (página Formulário)
    try:
        total_inscricoes = int(_um_valor("SELECT COUNT(*) FROM inscricoes"))
        ultima_inscricao = _um_valor("SELECT nome_aluno FROM inscricoes ORDER BY id DESC LIMIT 1", None)
    except mysql.connector.Error:
        total_inscricoes, ultima_inscricao = 0, None

    # ---- Lista "Pendências e atividade recente"
    pendencias = []
    for _id, nome_turma, horario in turmas_sem_chamada[:3]:
        pendencias.append({
            "tipo": "vermelho",
            "titulo": f"Chamada: {nome_turma}",
            "texto": f"Sem chamada registrada hoje (turma das {horario})",
            "link": "/presenca"
        })
    if alunos_sem_doc:
        pendencias.append({
            "tipo": "laranja",
            "titulo": "Documentos de alunos pendentes",
            "texto": f"{_plural(alunos_sem_doc, 'aluno', 'alunos')} sem nenhum documento enviado",
            "link": "/documentos"
        })
    for nome_arq, categoria, data_fmt in docs_recentes:
        pendencias.append({
            "tipo": "azul",
            "titulo": nome_arq,
            "texto": f"{categoria} · enviado em {data_fmt}",
            "link": "/documentos"
        })

    # ---- Banner de atenção
    partes = []
    if turmas_sem_chamada:
        partes.append(f"{_plural(len(turmas_sem_chamada), 'turma', 'turmas')} sem chamada registrada hoje")
    if alunos_sem_doc:
        partes.append(f"{_plural(alunos_sem_doc, 'aluno', 'alunos')} sem documentos enviados")

    if total_alunos == 0:
        banner_titulo = "Comece por aqui"
        banner_texto = "Nenhum aluno cadastrado ainda. Cadastre turmas e alunos na página de Presença."
    elif partes:
        banner_titulo = "Atenção necessária"
        banner_texto = "Pendências: " + " e ".join(partes) + "."
    else:
        banner_titulo = "Tudo em dia"
        banner_texto = "Todas as turmas têm chamada hoje e todos os alunos têm documentos enviados."

    return {
        "banner_titulo": banner_titulo,
        "banner_texto": banner_texto,
        "presenca_pct": presenca_pct,
        "chamada_hoje": registros_hoje > 0,
        "presentes_hoje": presentes_hoje,
        "ausentes_hoje": ausentes_hoje,
        "presenca_mes_pct": presenca_mes_pct,
        "total_docs": total_docs,
        "alunos_sem_doc": alunos_sem_doc,
        "alunos_com_doc": alunos_com_doc,
        "pct_docs": pct_docs,
        "total_alunos": total_alunos,
        "total_turmas": total_turmas,
        "alunos_sem_turma": alunos_sem_turma,
        "total_inscricoes": total_inscricoes,
        "ultima_inscricao": ultima_inscricao,
        "pendencias": pendencias,
    }


@ccb.route("/")
def home():
    nome, inicial = dados_usuario_atual()
    return render_template(
        "index.html",
        nome=nome,
        inicial=inicial,
        **resumo_dashboard()
    )


@ccb.route("/login")
def login_pagina():
    return render_template("login.html")


@ccb.route("/presenca")
def presenca_pagina():
    cursor.execute("""
        SELECT a.matricula, a.nome, COALESCE(t.nome, 'Sem turma') AS turma_nome, a.turma_id
        FROM alunos a
        LEFT JOIN turmas t ON a.turma_id = t.id
        ORDER BY a.nome
    """)
    alunos = cursor.fetchall()

    cursor.execute("""
        SELECT id, nome, modalidade, dias, horario
        FROM turmas
        ORDER BY nome
    """)
    turmas = cursor.fetchall()

    cursor.execute("""
        SELECT
            c.id,
            DATE_FORMAT(c.data_aula, '%d/%m/%Y') AS data_formatada,
            c.data_aula,
            a.matricula,
            a.nome AS aluno_nome,
            COALESCE(t.nome, 'Sem turma') AS turma_nome,
            COALESCE(a.turma_id, '') AS turma_id,
            c.presente
        FROM chamadas_alunos c
        INNER JOIN alunos a ON c.aluno_matricula = a.matricula
        LEFT JOIN turmas t ON a.turma_id = t.id
        ORDER BY c.data_aula DESC, a.nome ASC
    """)
    historico = cursor.fetchall()

    nome, inicial = dados_usuario_atual()
    return render_template(
        "presenca.html",
        alunos=alunos,
        turmas=turmas,
        historico=historico,
        nome=nome,
        inicial=inicial
    )


@ccb.route("/relatorios")
def relatorios_pagina():
    nome, inicial = dados_usuario_atual()
    return render_template(
        "relatorios.html",
        nome=nome,
        inicial=inicial
    )


@ccb.route("/documentos")
def documentos_pagina():
    cursor.execute("""
        SELECT matricula, nome
        FROM alunos
        ORDER BY nome
    """)
    alunos = cursor.fetchall()

    cursor.execute("""
        SELECT
            arq.id,
            arq.nome_original,
            arq.tipo,
            arq.categoria,
            COALESCE(al.nome, '') AS aluno_nome,
            COALESCE(arq.aluno_matricula, '') AS aluno_matricula,
            arq.responsavel,
            DATE_FORMAT(arq.data_upload, '%d/%m/%Y %H:%i') AS data_fmt
        FROM arquivos arq
        LEFT JOIN alunos al ON arq.aluno_matricula = al.matricula
        ORDER BY arq.data_upload DESC
    """)
    documentos = cursor.fetchall()

    nome, inicial = dados_usuario_atual()
    return render_template(
        "documentos.html",
        alunos=alunos,
        documentos=documentos,
        nome=nome,
        inicial=inicial
    )


@ccb.route("/formulario")
def formulario_pagina():
    nome, inicial = dados_usuario_atual()
    return render_template(
        "formulario.html",
        nome=nome,
        inicial=inicial
    )


@ccb.route("/configuracoes")
def configuracoes_pagina():
    nome, inicial = dados_usuario_atual()
    return render_template(
        "configuracoes.html",
        nome=nome,
        inicial=inicial
    )


@ccb.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_pagina"))


import criar_conta
import entrar
import formulario
import presenca
import documentos

if __name__ == "__main__":
    ccb.run(debug=True)
