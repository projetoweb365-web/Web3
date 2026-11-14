from app import ccb, conexao, cursor
from flask import request
import mysql.connector


# =====================================================
# SALVAR CHAMADA E CONSULTAR HISTÓRICO
# =====================================================

@ccb.route("/presenca/salvar", methods=["POST"])
def salvar_chamada():
    dados = request.get_json()
    if not dados:
        return {"success": False, "message": "Dados inválidos."}

    data_aula = dados.get("data_aula", "").strip()
    registros = dados.get("registros", [])

    if not data_aula:
        return {"success": False, "message": "Selecione a data da aula antes de salvar."}

    if not registros:
        return {"success": False, "message": "Nenhum aluno na lista para salvar."}

    try:
        for item in registros:
            matricula = item.get("matricula")
            presente = 1 if item.get("presente") else 0

            cursor.execute(
                """
                INSERT INTO chamadas_alunos (aluno_matricula, data_aula, presente)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE presente = VALUES(presente)
                """,
                (matricula, data_aula, presente)
            )

        conexao.commit()
        return {
            "success": True,
            "message": f"Chamada do dia {data_aula} salva com sucesso!"
        }
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Erro ao salvar chamada: {err.msg}"}


@ccb.route("/presenca/historico", methods=["GET"])
def listar_historico():
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
    rows = cursor.fetchall()

    historico = [
        {
            "id": r[0],
            "data_formatada": r[1],
            "data_iso": str(r[2]),
            "matricula": r[3],
            "aluno_nome": r[4],
            "turma_nome": r[5],
            "turma_id": str(r[6]),
            "presente": bool(r[7])
        }
        for r in rows
    ]
    return {"success": True, "historico": historico}


# =====================================================
# ROTAS DE TURMAS (Adicionar, Alterar, Remover)
# =====================================================

@ccb.route("/presenca/turma/adicionar", methods=["POST"])
def adicionar_turma():
    nome = request.form.get("nome_turma", "").strip()
    modalidade = request.form.get("modalidade", "").strip()
    dias = request.form.get("dias", "").strip()
    horario = request.form.get("horario", "").strip()

    if not nome or not modalidade or not dias or not horario:
        return {"success": False, "message": "Preencha todos os campos da turma."}

    try:
        cursor.execute(
            """
            INSERT INTO turmas (nome, modalidade, dias, horario)
            VALUES (%s, %s, %s, %s)
            """,
            (nome, modalidade, dias, horario)
        )
        conexao.commit()

        return {
            "success": True,
            "message": "Turma adicionada com sucesso!",
            "turma": {
                "id": cursor.lastrowid,
                "nome": nome,
                "modalidade": modalidade,
                "dias": dias,
                "horario": horario
            }
        }
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Erro ao adicionar turma: {err.msg}"}


@ccb.route("/presenca/turma/editar", methods=["POST"])
def editar_turma():
    turma_id = request.form.get("id", "").strip()
    nome = request.form.get("nome_turma", "").strip()
    modalidade = request.form.get("modalidade", "").strip()
    dias = request.form.get("dias", "").strip()
    horario = request.form.get("horario", "").strip()

    if not turma_id or not nome or not modalidade or not dias or not horario:
        return {"success": False, "message": "Preencha todos os campos para alterar a turma."}

    try:
        cursor.execute(
            """
            UPDATE turmas
            SET nome = %s, modalidade = %s, dias = %s, horario = %s
            WHERE id = %s
            """,
            (nome, modalidade, dias, horario, turma_id)
        )
        conexao.commit()

        return {
            "success": True,
            "message": "Informações da turma atualizadas!",
            "turma": {
                "id": int(turma_id),
                "nome": nome,
                "modalidade": modalidade,
                "dias": dias,
                "horario": horario
            }
        }
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Erro ao alterar turma: {err.msg}"}


@ccb.route("/presenca/turma/remover", methods=["POST"])
def remover_turma():
    turma_id = request.form.get("id", "").strip()

    if not turma_id:
        return {"success": False, "message": "ID da turma não informado."}

    try:
        cursor.execute("DELETE FROM turmas WHERE id = %s", (turma_id,))
        conexao.commit()

        return {
            "success": True,
            "message": "Turma removida com sucesso!",
            "id": int(turma_id)
        }
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Erro ao remover turma: {err.msg}"}


# =====================================================
# ROTAS DE ALUNOS (Adicionar, Alterar, Remover)
# =====================================================

@ccb.route("/presenca/aluno/adicionar", methods=["POST"])
def adicionar_aluno():
    matricula = request.form.get("matricula", "").strip()
    nome = request.form.get("nome_aluno", "").strip()
    turma_id = request.form.get("turma_id") or None

    if not matricula or not nome:
        return {"success": False, "message": "Preencha matrícula e nome do aluno."}

    try:
        cursor.execute(
            """
            INSERT INTO alunos (matricula, nome, turma_id)
            VALUES (%s, %s, %s)
            """,
            (matricula, nome, turma_id)
        )
        conexao.commit()

        nome_turma = "Sem turma"
        if turma_id:
            cursor.execute("SELECT nome FROM turmas WHERE id = %s", (turma_id,))
            row = cursor.fetchone()
            if row:
                nome_turma = row[0]

        return {
            "success": True,
            "message": "Aluno adicionado com sucesso!",
            "aluno": {
                "matricula": matricula,
                "nome": nome,
                "turma_id": turma_id or "",
                "turma_nome": nome_turma
            }
        }
    except mysql.connector.IntegrityError:
        return {"success": False, "message": "Esta matrícula já está cadastrada."}
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Erro ao adicionar aluno: {err.msg}"}


@ccb.route("/presenca/aluno/editar", methods=["POST"])
def editar_aluno():
    matricula_original = request.form.get("matricula_original", "").strip()
    matricula = request.form.get("matricula", "").strip()
    nome = request.form.get("nome_aluno", "").strip()
    turma_id = request.form.get("turma_id") or None

    if not matricula_original or not matricula or not nome:
        return {"success": False, "message": "Preencha matrícula e nome do aluno."}

    try:
        cursor.execute(
            """
            UPDATE alunos
            SET matricula = %s, nome = %s, turma_id = %s
            WHERE matricula = %s
            """,
            (matricula, nome, turma_id, matricula_original)
        )
        conexao.commit()

        nome_turma = "Sem turma"
        if turma_id:
            cursor.execute("SELECT nome FROM turmas WHERE id = %s", (turma_id,))
            row = cursor.fetchone()
            if row:
                nome_turma = row[0]

        return {
            "success": True,
            "message": "Informações do aluno atualizadas!",
            "matricula_original": matricula_original,
            "aluno": {
                "matricula": matricula,
                "nome": nome,
                "turma_id": turma_id or "",
                "turma_nome": nome_turma
            }
        }
    except mysql.connector.IntegrityError:
        return {"success": False, "message": "Já existe outro aluno com essa matrícula."}
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Erro ao alterar aluno: {err.msg}"}


@ccb.route("/presenca/aluno/remover", methods=["POST"])
def remover_aluno():
    matricula = request.form.get("matricula", "").strip()

    if not matricula:
        return {"success": False, "message": "Matrícula não informada."}

    try:
        cursor.execute("DELETE FROM alunos WHERE matricula = %s", (matricula,))
        conexao.commit()

        return {
            "success": True,
            "message": "Aluno removido com sucesso!",
            "matricula": matricula
        }
    except mysql.connector.Error as err:
        return {"success": False, "message": f"Erro ao remover aluno: {err.msg}"}