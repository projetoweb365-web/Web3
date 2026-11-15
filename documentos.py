from app import ccb, conexao, cursor
from flask import request, session, jsonify, send_from_directory
import mysql.connector
import os
import uuid
from datetime import datetime

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


# =====================================================
# EDITAR DOCUMENTO (todos os campos da linha da tabela)
# =====================================================

CATEGORIAS_PERMITIDAS = {"Aluno", "Financeiro", "Frequência", "Jurídico", "Geral"}
TIPOS_PERMITIDOS = {ext.upper() for ext in EXTENSOES_PERMITIDAS}


def buscar_documento(doc_id):
    cursor.execute(
        """
        SELECT
            arq.id, arq.nome_original, arq.tipo, arq.categoria,
            COALESCE(al.nome, '') AS aluno_nome,
            COALESCE(arq.aluno_matricula, '') AS aluno_matricula,
            arq.responsavel,
            DATE_FORMAT(arq.data_upload, '%d/%m/%Y %H:%i') AS data_fmt
        FROM arquivos arq
        LEFT JOIN alunos al ON arq.aluno_matricula = al.matricula
        WHERE arq.id = %s
        """,
        (doc_id,)
    )
    r = cursor.fetchone()
    if not r:
        return None
    return {
        "id": r[0],
        "nome_original": r[1],
        "tipo": r[2],
        "categoria": r[3],
        "aluno_nome": r[4],
        "aluno_matricula": r[5],
        "responsavel": r[6],
        "data_upload": r[7]
    }


def _parse_data_upload(texto):
    for formato in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(texto, formato)
        except (ValueError, TypeError):
            continue
    return None


@ccb.route("/documentos/editar/<int:doc_id>", methods=["POST"])
def editar_documento(doc_id):
    cursor.execute("SELECT id FROM arquivos WHERE id = %s", (doc_id,))
    if not cursor.fetchone():
        return {"success": False, "message": "Arquivo não encontrado."}

    dados = request.get_json(silent=True) or {}

    nome_original = (dados.get("nome_original") or "").strip()
    categoria = (dados.get("categoria") or "").strip()
    aluno_matricula = (dados.get("aluno_matricula") or "").strip() or None
    tipo = (dados.get("tipo") or "").strip().upper()
    responsavel = (dados.get("responsavel") or "").strip()
    data_upload = _parse_data_upload((dados.get("data_upload") or "").strip())

    if not nome_original or len(nome_original) > 255:
        return {"success": False, "message": "Nome do arquivo inválido (1 a 255 caracteres)."}
    if categoria not in CATEGORIAS_PERMITIDAS:
        return {"success": False, "message": "Categoria inválida."}
    if tipo not in TIPOS_PERMITIDOS:
        return {"success": False, "message": "Tipo inválido."}
    if not responsavel or len(responsavel) > 100:
        return {"success": False, "message": "Responsável inválido (1 a 100 caracteres)."}
    if data_upload is None:
        return {"success": False, "message": "Data de upload inválida."}

    if categoria == "Aluno":
        if not aluno_matricula:
            return {"success": False, "message": "Selecione o aluno para a categoria Aluno."}
        cursor.execute("SELECT 1 FROM alunos WHERE matricula = %s", (aluno_matricula,))
        if not cursor.fetchone():
            return {"success": False, "message": "Aluno não encontrado."}
    else:
        aluno_matricula = None

    try:
        cursor.execute(
            """
            UPDATE arquivos
            SET nome_original=%s, categoria=%s, aluno_matricula=%s,
                tipo=%s, responsavel=%s, data_upload=%s
            WHERE id=%s
            """,
            (nome_original, categoria, aluno_matricula, tipo, responsavel, data_upload, doc_id)
        )
        conexao.commit()
        return {
            "success": True,
            "message": "Documento atualizado com sucesso!",
            "documento": buscar_documento(doc_id)
        }
    except Exception as err:
        return {"success": False, "message": f"Erro ao atualizar: {str(err)}"}
