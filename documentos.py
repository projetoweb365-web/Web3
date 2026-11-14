from app import ccb, conexao, cursor
from flask import request, session, jsonify, send_from_directory
import mysql.connector
import os
import uuid

# =====================================================
# CONFIGURAÇÃO DA PASTA DE UPLOADS E EXTENSÕES
# =====================================================

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ccb.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTENSOES_PERMITIDAS = {"pdf", "docx", "xlsx", "xls", "jpg", "jpeg", "png"}

# Garante que a tabela arquivos e todas as colunas novas existam no MySQL
cursor.execute("""
    CREATE TABLE IF NOT EXISTS arquivos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome_original VARCHAR(255) NOT NULL,
        nome_salvo VARCHAR(255) NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        categoria VARCHAR(100) NOT NULL DEFAULT 'Geral',
        aluno_matricula VARCHAR(20) NULL,
        responsavel VARCHAR(100) NOT NULL DEFAULT 'Admin',
        data_upload DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

for coluna, definicao in [
    ("categoria", "VARCHAR(100) NOT NULL DEFAULT 'Geral'"),
    ("aluno_matricula", "VARCHAR(20) NULL"),
    ("responsavel", "VARCHAR(100) NOT NULL DEFAULT 'Admin'")
]:
    cursor.execute(f"SHOW COLUMNS FROM arquivos LIKE '{coluna}'")
    if not cursor.fetchone():
        cursor.execute(f"ALTER TABLE arquivos ADD COLUMN {coluna} {definicao}")

conexao.commit()


def arquivo_permitido(nome):
    if "." not in nome:
        return False
    ext = nome.rsplit(".", 1)[1].lower()
    return ext in EXTENSOES_PERMITIDAS


# =====================================================
# UPLOAD DE DOCUMENTOS (Com Categoria e Aluno)
# =====================================================

@ccb.route("/documentos/upload", methods=["POST"])
@ccb.route("/upload", methods=["POST"])
def upload_documento():
    if "arquivo" not in request.files:
        return {"success": False, "message": "Nenhum arquivo enviado."}

    arquivo = request.files["arquivo"]
    if arquivo.filename == "":
        return {"success": False, "message": "Selecione um arquivo antes de enviar."}

    if not arquivo_permitido(arquivo.filename):
        return {
            "success": False,
            "message": "Formato inválido. Use .pdf, .docx, .xlsx, .xls, .jpg ou .png."
        }

    categoria = request.form.get("categoria", "Geral").strip()
    aluno_matricula = request.form.get("aluno_matricula", "").strip() or None
    responsavel = session.get("usuario_nome") or "Admin"

    if categoria == "Aluno" and not aluno_matricula:
        return {
            "success": False,
            "message": "Selecione o aluno para documentos da categoria Aluno."
        }

    if categoria != "Aluno":
        aluno_matricula = None

    nome_original = arquivo.filename
    extensao = nome_original.rsplit(".", 1)[1].lower()
    nome_salvo = f"{uuid.uuid4()}.{extensao}"
    caminho = os.path.join(UPLOAD_FOLDER, nome_salvo)

    try:
        arquivo.save(caminho)

        cursor.execute(
            """
            INSERT INTO arquivos (nome_original, nome_salvo, tipo, categoria, aluno_matricula, responsavel)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nome_original, nome_salvo, extensao.upper(), categoria, aluno_matricula, responsavel)
        )
        conexao.commit()
        novo_id = cursor.lastrowid

        cursor.execute(
            """
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
            WHERE arq.id = %s
            """,
            (novo_id,)
        )
        r = cursor.fetchone()

        return {
            "success": True,
            "message": "Documento salvo com sucesso!",
            "documento": {
                "id": r[0],
                "nome_original": r[1],
                "tipo": r[2],
                "categoria": r[3],
                "aluno_nome": r[4],
                "aluno_matricula": r[5],
                "responsavel": r[6],
                "data_upload": r[7]
            }
        }
    except Exception as err:
        return {"success": False, "message": f"Erro ao salvar no banco: {str(err)}"}


# =====================================================
# LISTAR ARQUIVOS (JSON)
# =====================================================

@ccb.route("/arquivos")
@ccb.route("/documentos/listar")
def listar_arquivos():
    cursor.execute("""
        SELECT
            arq.id,
            arq.nome_original,
            arq.tipo,
            arq.categoria,
            COALESCE(al.nome, '') AS aluno_nome,
            COALESCE(arq.aluno_matricula, '') AS aluno_matricula,
            arq.responsavel,
            DATE_FORMAT(arq.data_upload, '%d/%m/%Y %H:%i') AS data_upload
        FROM arquivos arq
        LEFT JOIN alunos al ON arq.aluno_matricula = al.matricula
        ORDER BY arq.data_upload DESC
    """)
    rows = cursor.fetchall()

    resultado = [
        {
            "id": r[0],
            "nome_original": r[1],
            "tipo": r[2],
            "categoria": r[3],
            "aluno_nome": r[4],
            "aluno_matricula": r[5],
            "responsavel": r[6],
            "data_upload": str(r[7])
        }
        for r in rows
    ]
    return jsonify(resultado)


# =====================================================
# VISUALIZAR, BAIXAR E REMOVER DOCUMENTO
# =====================================================

@ccb.route("/documentos/ver/<int:doc_id>")
def ver_documento(doc_id):
    cursor.execute("SELECT nome_original, nome_salvo FROM arquivos WHERE id = %s", (doc_id,))
    row = cursor.fetchone()
    if not row:
        return "Arquivo não encontrado.", 404
    return send_from_directory(UPLOAD_FOLDER, row[1], as_attachment=False, download_name=row[0])


@ccb.route("/documentos/baixar/<int:doc_id>")
@ccb.route("/download/<int:doc_id>")
def baixar_documento(doc_id):
    cursor.execute("SELECT nome_original, nome_salvo FROM arquivos WHERE id = %s", (doc_id,))
    row = cursor.fetchone()
    if not row:
        return "Arquivo não encontrado.", 404
    return send_from_directory(UPLOAD_FOLDER, row[1], as_attachment=True, download_name=row[0])


@ccb.route("/documentos/remover/<int:doc_id>", methods=["POST"])
def remover_documento(doc_id):
    cursor.execute("SELECT nome_salvo FROM arquivos WHERE id = %s", (doc_id,))
    row = cursor.fetchone()
    if not row:
        return {"success": False, "message": "Arquivo não encontrado."}

    caminho = os.path.join(UPLOAD_FOLDER, row[0])
    if os.path.exists(caminho):
        os.remove(caminho)

    cursor.execute("DELETE FROM arquivos WHERE id = %s", (doc_id,))
    conexao.commit()
    return {"success": True, "message": "Documento removido com sucesso!"}