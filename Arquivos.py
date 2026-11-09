from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory
)

from database import conectar_banco

from datetime import date, timedelta

import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTENSOES_PERMITIDAS = {
    "pdf",
    "xlsx",
    "xls"
}

def arquivo_permitido(nome):

    if "." not in nome:
        return False

    extensao = nome.rsplit(".", 1)[1].lower()

    return extensao in EXTENSOES_PERMITIDAS

@app.route("/upload", methods=["POST"])
def upload_arquivo():

    if "arquivo" not in request.files:
        return jsonify({
            "erro": "Nenhum arquivo foi enviado"
        }), 400

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":
        return jsonify({
            "erro": "Nenhum arquivo foi selecionado"
        }), 400

    if not arquivo_permitido(arquivo.filename):
        return jsonify({
            "erro": "Formato de arquivo não permitido"
        }), 400

    nome_original = arquivo.filename

    extensao = nome_original.rsplit(".", 1)[1].lower()

    nome_salvo = str(uuid.uuid4()) + "." + extensao

    caminho = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nome_salvo
    )

    arquivo.save(caminho)

    conexao = conectar_banco()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO arquivos
        (
            nome_original,
            nome_salvo,
            tipo
        )

        VALUES (%s, %s, %s)
    """

    valores = (
        nome_original,
        nome_salvo,
        extensao
    )

    cursor.execute(sql, valores)

    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({
        "mensagem": "Arquivo enviado com sucesso"
    })

@app.route("/arquivos")
def listar_arquivos():

    conexao = conectar_banco()

    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            nome_original,
            tipo,
            data_upload
        FROM arquivos
        ORDER BY data_upload DESC
    """)

    arquivos = cursor.fetchall()

    cursor.close()
    conexao.close()

    for arquivo in arquivos:

        arquivo["data_upload"] = str(
            arquivo["data_upload"]
        )

    return jsonify(arquivos)

@app.route("/download/<int:id>")
def baixar_arquivo(id):

    conexao = conectar_banco()

    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT nome_original, nome_salvo
        FROM arquivos
        WHERE id = %s
    """, (id,))

    arquivo = cursor.fetchone()

    cursor.close()
    conexao.close()

    if arquivo is None:
        return jsonify({
            "erro": "Arquivo não encontrado"
        }), 404

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        arquivo["nome_salvo"],
        as_attachment=True,
        download_name=arquivo["nome_original"]
    )

@app.route("/arquivos/pagina")
def pagina_arquivos():

    return render_template(
        "arquivos.html"
    )
