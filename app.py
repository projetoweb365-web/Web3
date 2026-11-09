from flask import Flask, request, render_template
import mysql.connector
import sys
 
ccb = Flask(__name__)
 
sys.modules.setdefault("app", sys.modules[__name__])
 
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senha",
    database="centro_cidadania_do_brasil"
)
 
cursor = conexao.cursor()
 
 
@ccb.route("/")
def home():
    return render_template("index.html")
 
@ccb.route("/login")
def login_pagina():
    return render_template("login.html")
 
@ccb.route("/presenca")
def presenca_pagina():
    cursor.execute("SELECT matricula, nome FROM alunos ORDER BY nome")
    alunos = cursor.fetchall()
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
 
 
import criar_conta
import entrar
import formulario
 
if __name__ == "__main__":
    ccb.run(debug=True)
