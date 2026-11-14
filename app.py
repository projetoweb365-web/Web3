from flask import Flask, request, render_template, session, redirect, url_for
import mysql.connector
import sys
import os

ccb = Flask(__name__)

ccb.secret_key = "ccb_sistema_2026"

sys.modules.setdefault("app", sys.modules[__name__])

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senha",
    database="centro_cidadania_do_brasil"
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


@ccb.route("/")
def home():
    nome, inicial = dados_usuario_atual()
    return render_template(
        "index.html",
        nome=nome,
        inicial=inicial
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
    nome, inicial = dados_usuario_atual()
    return render_template(
        "documentos.html",
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

if __name__ == "__main__":
    ccb.run(debug=True)
