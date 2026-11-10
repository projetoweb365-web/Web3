from flask import Flask, request, render_template
from database import conectar_banco
import sys

ccb = Flask(__name__)

# Faz "from app import ccb, conexao, cursor" (nos outros arquivos) usar ESTE módulo,
# em vez de carregar o app.py uma segunda vez. Deve ficar antes dos imports lá embaixo.
sys.modules.setdefault("app", sys.modules[__name__])

# Conexão compartilhada, usada por criar_conta.py, entrar.py e formulario.py.
# (As credenciais ficam só no database.py.)
conexao = conectar_banco()

cursor = conexao.cursor()


# ---------- Páginas ----------

@ccb.route("/")
def home():
    return render_template("index.html")

@ccb.route("/login")
def login_pagina():
    return render_template("login.html")

@ccb.route("/presenca")
def presenca_pagina():
    # conexão própria: sempre lê os alunos atuais do banco
    conn = conectar_banco()
    cur = conn.cursor()
    cur.execute("SELECT id, nome_aluno FROM inscricoes ORDER BY nome_aluno")
    alunos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("presenca.html", alunos=alunos)

@ccb.route("/relatorios")
def relatorios_pagina():
    return render_template("relatorios.html")

@ccb.route("/documentos")
def documentos_pagina():
    return render_template("documentos.html")

@ccb.route("/formulario")
def formulario_pagina():
    return render_template("formulario.html")

@ccb.route("/configuracoes")
def configuracoes_pagina():
    return render_template("configuracoes.html")


# ---------- Rotas dos outros arquivos (devem vir DEPOIS de ccb, conexao e cursor) ----------

import criar_conta
import entrar
import formulario
import arquivos_relatorios

if __name__ == "__main__":
    ccb.run(debug=True)