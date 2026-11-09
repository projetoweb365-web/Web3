from flask import Flask, render_template, request, jsonify

from database import conectar_banco

from datetime import date, timedelta


app = Flask(__name__)


# ==========================================================
# PÁGINA DE RELATÓRIOS
# ==========================================================

@app.route("/")
def pagina_relatorios():

    return render_template("relatorios.html")


# ==========================================================
# LISTAR MODALIDADES
# ==========================================================

@app.route("/modalidades")
def listar_modalidades():

    conexao = conectar_banco()

    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT DISTINCT modalidade
        FROM inscricoes
        ORDER BY modalidade
    """)

    modalidades = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(modalidades)


# ==========================================================
# LISTAR INSCRIÇÕES
# ==========================================================

@app.route("/inscricoes")
def listar_inscricoes():

    conexao = conectar_banco()

    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            nome_aluno,
            modalidade,
            dias,
            horario
        FROM inscricoes
        ORDER BY nome_aluno
    """)

    alunos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(alunos)


# ==========================================================
# REGISTRAR FREQUÊNCIA
# ==========================================================

@app.route("/frequencia", methods=["POST"])
def registrar_frequencia():

    dados = request.get_json()

    inscricao_id = dados.get("inscricao_id")
    data_aula = dados.get("data_aula")
    presente = dados.get("presente")


    if inscricao_id is None:
        return jsonify({
            "erro": "ID da inscrição não informado."
        }), 400


    if data_aula is None:
        return jsonify({
            "erro": "Data da aula não informada."
        }), 400


    if presente is None:
        return jsonify({
            "erro": "Status de presença não informado."
        }), 400


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

        ON DUPLICATE KEY UPDATE
            presente = VALUES(presente)
    """


    valores = (
        inscricao_id,
        data_aula,
        presente
    )


    cursor.execute(sql, valores)

    conexao.commit()

    cursor.close()
    conexao.close()


    return jsonify({
        "mensagem": "Frequência registrada com sucesso."
    })


# ==========================================================
# RELATÓRIO DE FREQUÊNCIA
# ==========================================================

@app.route("/relatorio/frequencia")
def gerar_relatorio():

    periodo = request.args.get("periodo")

    modalidade = request.args.get(
        "modalidade"
    )


    frequencia_minima = float(
        request.args.get(
            "frequencia_minima",
            0
        )
    )


    frequencia_maxima = float(
        request.args.get(
            "frequencia_maxima",
            100
        )
    )


    hoje = date.today()


    # ======================================================
    # DEFINIR PERÍODO
    # ======================================================

    if periodo == "semanal":

        data_inicio = hoje - timedelta(days=6)

        data_fim = hoje


    elif periodo == "mensal":

        data_inicio = hoje.replace(day=1)

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
            "erro": "Período inválido."
        }), 400


    # ======================================================
    # CONECTAR AO BANCO
    # ======================================================

    conexao = conectar_banco()

    cursor = conexao.cursor(
        dictionary=True
    )


    # ======================================================
    # SQL
    # ======================================================

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


    # ======================================================
    # FILTRO DE MODALIDADE
    # ======================================================

    if modalidade and modalidade != "todas":

        sql += """
            AND inscricoes.modalidade = %s
        """

        parametros.append(
            modalidade
        )


    # ======================================================
    # AGRUPAMENTO
    # ======================================================

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


    cursor.execute(
        sql,
        parametros
    )


    alunos = cursor.fetchall()


    # ======================================================
    # CALCULAR PERCENTUAL
    # ======================================================

    resultado = []


    for aluno in alunos:

        total_aulas = aluno["total_aulas"]

        presencas = aluno["presencas"]

        faltas = aluno["faltas"]


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


        # ==================================================
        # FILTRO DE FREQUÊNCIA
        # ==================================================

        if (
            percentual >= frequencia_minima
            and
            percentual <= frequencia_maxima
        ):

            resultado.append({

                "id": aluno["id"],

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


    # ======================================================
    # DEVOLVER JSON
    # ======================================================

    return jsonify({

        "data_inicio":
            str(data_inicio),

        "data_fim":
            str(data_fim),

        "alunos":
            resultado

    })


# ==========================================================
# INICIAR SERVIDOR
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
