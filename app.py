from flask import Flask, request, render_template, session, redirect, url_for
import mysql.connector
import sys
 
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

def usuario_logado():
    return "usuario_id" in session

@ccb.route("/")
def home():
    if not usuario_logado():
        return redirect(url_for("login_pagina"))

    return render_template(
        "index.html",
        nome=session.get("usuario_nome"),
        inicial=session.get("usuario_nome")[0].upper()
        )
 
@ccb.route("/login")
def login_pagina():
    return render_template("login.html")
 
@ccb.route("/presenca")
def presenca_pagina():
    if not usuario_logado():
        return redirect(url_for("login_pagina"))

    cursor.execute(
        "SELECT matricula, nome FROM alunos ORDER BY nome"
    )

    alunos = cursor.fetchall()

    return render_template(
        "presenca.html",
        alunos=alunos,
        nome=session.get("usuario_nome"),
        inicial=session.get("usuario_nome")[0].upper()
    )
 
@ccb.route("/relatorios")
def relatorios_pagina():
    if not usuario_logado():
        return redirect(url_for("login_pagina"))

    return render_template(
        "relatorios.html",
        nome=session.get("usuario_nome"),
        inicial=session.get("usuario_nome")[0].upper()
    )
 
@ccb.route("/documentos")
def documentos_pagina():
    if not usuario_logado():
        return redirect(url_for("login_pagina"))

    return render_template(
        "documentos.html",
        nome=session.get("usuario_nome"),
        inicial=session.get("usuario_nome")[0].upper()
    )
 
@ccb.route("/formulario")
def formulario_pagina():
    if not usuario_logado():
        return redirect(url_for("login_pagina"))

    return render_template(
        "formulario.html",
        nome=session.get("usuario_nome"),
        inicial=session.get("usuario_nome")[0].upper()
    )
 
@ccb.route("/configuracoes")
def configuracoes_pagina():
    if not usuario_logado():
        return redirect(url_for("login_pagina"))

    return render_template(
        "configuracoes.html",
        nome=session.get("usuario_nome"),
        inicial=session.get("usuario_nome")[0].upper()
    )

@ccb.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("login_pagina"))
 
 
import criar_conta
import entrar
import formulario
 
if __name__ == "__main__":
    ccb.run(debug=True)
