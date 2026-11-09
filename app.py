from flask import Flask, request, render_template
import mysql.connector

ccb = Flask(__name__)

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

import criar_conta
import entrar
import formulario

if __name__ == "__main__":
    ccb.run(debug=True)
