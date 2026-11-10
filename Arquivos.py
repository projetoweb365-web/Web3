from app import ccb
from database import conectar_banco

from flask import (
    request,
    jsonify,
    send_from_directory
)

from datetime import date, timedelta

import os
import uuid


# =====================================================
# CONFIGURAÇÃO DOS ARQUIVOS
# =====================================================

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "uploads"
)

ccb.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


EXTENSOES_PERMITIDAS = {
    "pdf",
    "xlsx",
    "xls"
}


# =====================================================
# VERIFICAR EXTENSÃO
# =====================================================

def arquivo_permitido(nome):

    if "." not in nome:
        return False

    extensao = nome.rsplit(
        ".",
        1
    )[1].lower()

    return extensao in EXTENSOES_PERMITIDAS


# =====================================================
# LISTAR INSCRIÇÕES
# =====================================================

@ccb.route("/inscricoes")
def listar_inscricoes():

    conexao = conectar_banco()

    cursor = conexao.cursor(
        dictionary=True
    )

    cursor.execute("""
        SELECT
            id,
            nome_aluno,
            data_nascimento,
            sexo,
            rg,
            cpf,
            bairro,
            modalidade,
            dias,
            horario,
            recebe_auxilio,
            participa_outro_projeto

        FROM inscricoes

        ORDER BY nome_aluno
    """)

    inscricoes = cursor.fetchall()

    cursor.close()

    conexao.close()

    return jsonify(
        inscricoes
    )


# =====================================================
# LISTAR MODALIDADES
# =====================================================

@ccb.route("/modalidades")
def listar_modalidades():

    conexao = conectar_banco()

    cursor = conexao.cursor()

    cursor.execute("""
        SELECT DISTINCT modalidade

        FROM inscricoes

        WHERE modalidade IS NOT NULL

        AND modalidade != ''

        ORDER BY modalidade
    """)

    modalidades = cursor.fetchall()

    cursor.close()

    conexao.close()


    resultado = []


    for modalidade in modalidades:

        resultado.append({
            "modalidade":
                modalidade[0]
        })


    return jsonify(
        resultado
    )


# =====================================================
# REGISTRAR FREQUÊNCIA
# =====================================================

@ccb.route(
    "/frequencia",
    methods=["POST"]
)
def registrar_frequencia():

    dados = request.get_json()


    inscricao_id = \
        dados["inscricao_id"]

    data_aula = \
        dados["data_aula"]

    presente = \
        dados["presente"]


    conexao = conectar_banco()

    cursor = conexao.cursor()


    sql = """
        INSERT INTO frequencias
        (
            inscricao_id,
            data_aula,
            presente
        )

        VALUES (%s, %s, %s)
    """


    valores = (
        inscricao_id,
        data_aula,
        presente
    )


    cursor.execute(
        sql,
        valores
    )


    conexao.commit()


    cursor.close()

    conexao.close()


    return jsonify({

        "mensagem":
            "Frequência registrada com sucesso"

    })


# =====================================================
# RELATÓRIO DE FREQUÊNCIA
# =====================================================

@ccb.route(
    "/relatorio/frequencia"
)
def gerar_relatorio():

    periodo = request.args.get(
        "periodo"
    )


    modalidade = request.args.get(
        "modalidade"
    )


    frequencia_minima = request.args.get(
        "frequencia_minima",
        0
    )


    frequencia_maxima = request.args.get(
        "frequencia_maxima",
        100
    )


    frequencia_minima = float(
        frequencia_minima
    )

    frequencia_maxima = float(
        frequencia_maxima
    )


    # =================================================
    # DEFINIR DATAS
    # =================================================

    hoje = date.today()


    if periodo == "semanal":

        data_inicio = (
            hoje -
            timedelta(days=6)
        )

        data_fim = hoje


    elif periodo == "mensal":

        data_inicio = hoje.replace(
            day=1
        )

        data_fim = hoje


    elif periodo == "anual":

        data_inicio = hoje.replace(
            month=1,
            day=1
        )

        data_fim = hoje


    elif periodo == "personalizado":

        data_inicio = request.args.get(
            "data_inicio"
        )

        data_fim = request.args.get(
            "data_fim"
        )


    else:

        return jsonify({

            "erro":
                "Período inválido"

        }), 400


    # =================================================
    # CONEXÃO
    # =================================================

    conexao = conectar_banco()

    cursor = conexao.cursor(
        dictionary=True
    )


    # =================================================
    # SQL
    # =================================================

    sql = """

        SELECT

            inscricoes.id,

            inscricoes.nome_aluno,

            inscricoes.modalidade,

            inscricoes.dias,

            inscricoes.horario,

            COUNT(frequencias.id)
                AS total_aulas,

            COALESCE(
                SUM(
                    CASE

                        WHEN frequencias.presente = 1

                        THEN 1

                        ELSE 0

                    END
                ),
                0
            ) AS presencas,

            COALESCE(
                SUM(
                    CASE

                        WHEN frequencias.presente = 0

                        THEN 1

                        ELSE 0

                    END
                ),
                0
            ) AS faltas


        FROM inscricoes


        LEFT JOIN frequencias

        ON inscricoes.id =
           frequencias.inscricao_id

        AND frequencias.data_aula
            BETWEEN %s AND %s


        WHERE 1 = 1

    """


    parametros = [
        data_inicio,
        data_fim
    ]


    # =================================================
    # FILTRO DE MODALIDADE
    # =================================================

    if (
        modalidade
        and
        modalidade != "todas"
    ):

        sql += """

            AND inscricoes.modalidade = %s

        """

        parametros.append(
            modalidade
        )


    # =================================================
    # AGRUPAMENTO
    # =================================================

    sql += """

        GROUP BY

            inscricoes.id,

            inscricoes.nome_aluno,

            inscricoes.modalidade,

            inscricoes.dias,

            inscricoes.horario


        ORDER BY
            inscricoes.nome_aluno

    """


    # =================================================
    # EXECUTAR
    # =================================================

    cursor.execute(
        sql,
        parametros
    )


    alunos = cursor.fetchall()


    resultado = []


    # =================================================
    # CALCULAR PERCENTUAL
    # =================================================

    for aluno in alunos:

        total_aulas = \
            aluno["total_aulas"]

        presencas = \
            aluno["presencas"]

        faltas = \
            aluno["faltas"]


        if total_aulas > 0:

            percentual = (
                presencas /
                total_aulas
            ) * 100

        else:

            percentual = 0


        percentual = round(
            percentual,
            2
        )


        # =============================================
        # FILTRO
        # =============================================

        if (

            percentual >=
            frequencia_minima

            and

            percentual <=
            frequencia_maxima

        ):

            resultado.append({

                "id":
                    aluno["id"],

                "nome":
                    aluno["nome_aluno"],

                "modalidade":
                    aluno["modalidade"],

                "dias":
                    aluno["dias"],

                "horario":
                    aluno["horario"],

                "total_aulas":
                    total_aulas,

                "presencas":
                    presencas,

                "faltas":
                    faltas,

                "frequencia":
                    percentual

            })


    cursor.close()

    conexao.close()


    return jsonify({

        "data_inicio":
            str(data_inicio),

        "data_fim":
            str(data_fim),

        "alunos":
            resultado

    })


# =====================================================
# UPLOAD DE ARQUIVO
# =====================================================

@ccb.route(
    "/upload",
    methods=["POST"]
)
def upload_arquivo():

    # -----------------------------------------------
    # VERIFICAR SE EXISTE ARQUIVO
    # -----------------------------------------------

    if "arquivo" not in request.files:

        return jsonify({

            "erro":
                "Nenhum arquivo foi enviado"

        }), 400


    arquivo = request.files[
        "arquivo"
    ]


    # -----------------------------------------------
    # VERIFICAR NOME
    # -----------------------------------------------

    if arquivo.filename == "":

        return jsonify({

            "erro":
                "Nenhum arquivo foi selecionado"

        }), 400


    # -----------------------------------------------
    # VERIFICAR EXTENSÃO
    # -----------------------------------------------

    if not arquivo_permitido(
        arquivo.filename
    ):

        return jsonify({

            "erro":
                "Formato de arquivo não permitido"

        }), 400


    # -----------------------------------------------
    # NOME ORIGINAL
    # -----------------------------------------------

    nome_original = \
        arquivo.filename


    # -----------------------------------------------
    # EXTENSÃO
    # -----------------------------------------------

    extensao = \
        nome_original.rsplit(
            ".",
            1
        )[1].lower()


    # -----------------------------------------------
    # CRIAR NOME ÚNICO
    # -----------------------------------------------

    nome_salvo = (
        str(uuid.uuid4())
        +
        "."
        +
        extensao
    )


    # -----------------------------------------------
    # CAMINHO
    # -----------------------------------------------

    caminho = os.path.join(

        ccb.config[
            "UPLOAD_FOLDER"
        ],

        nome_salvo

    )


    # -----------------------------------------------
    # SALVAR ARQUIVO
    # -----------------------------------------------

    arquivo.save(
        caminho
    )


    # -----------------------------------------------
    # SALVAR NO BANCO
    # -----------------------------------------------

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


    cursor.execute(
        sql,
        valores
    )


    conexao.commit()


    cursor.close()

    conexao.close()


    return jsonify({

        "mensagem":
            "Arquivo enviado com sucesso"

    })


# =====================================================
# LISTAR ARQUIVOS
# =====================================================

@ccb.route("/arquivos")
def listar_arquivos():

    conexao = conectar_banco()

    cursor = conexao.cursor(
        dictionary=True
    )


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

        arquivo["data_upload"] = \
            str(
                arquivo["data_upload"]
            )


    return jsonify(
        arquivos
    )


# =====================================================
# DOWNLOAD
# =====================================================

@ccb.route(
    "/download/<int:id>"
)
def baixar_arquivo(id):

    conexao = conectar_banco()

    cursor = conexao.cursor(
        dictionary=True
    )


    cursor.execute("""

        SELECT

            nome_original,

            nome_salvo

        FROM arquivos

        WHERE id = %s

    """, (id,))


    arquivo = \
        cursor.fetchone()


    cursor.close()

    conexao.close()


    if arquivo is None:

        return jsonify({

            "erro":
                "Arquivo não encontrado"

        }), 404


    return send_from_directory(

        ccb.config[
            "UPLOAD_FOLDER"
        ],

        arquivo[
            "nome_salvo"
        ],

        as_attachment=True,

        download_name=
            arquivo[
                "nome_original"
            ]

    )