from app import ccb, conexao, cursor
from flask import request

@ccb.route("/formulario", methods=["POST"])
@ccb.route("/formulario", methods=["POST"])
def formulario():

    nome_aluno = request.form.get("nome_aluno")
    data_nascimento = request.form.get("data_nascimento")
    sexo = request.form.get("sexo")
    rg = request.form.get("rg")
    cpf = request.form.get("cpf")
    endereco = request.form.get("endereco")
    bairro = request.form.get("bairro")
    cep = request.form.get("cep")
    nome_mae = request.form.get("nome_mae")
    nome_pai = request.form.get("nome_pai")

    problema_cardiaco = request.form.get("problema_cardiaco")
    dor_peito_atividade = request.form.get("dor_peito_atividade")
    dor_peito_recente = request.form.get("dor_peito_recente")
    tontura_ou_perda_consciencia = request.form.get("tontura_ou_perda_consciencia")
    problema_osseo_articular = request.form.get("problema_osseo_articular")
    medicacao_continua = request.form.get("medicacao_continua")
    tratamento_pressao = request.form.get("tratamento_pressao")
    outra_condicao_saude = request.form.get("outra_condicao_saude")

    modalidade = request.form.get("modalidade")
    dias = request.form.get("dias")
    horario = request.form.get("horario")

    motivo_inscricao = request.form.get("motivo_inscricao")
    outro_motivo = request.form.get("outro_motivo")

    recebe_auxilio = request.form.get("recebe_auxilio")
    participa_outro_projeto = request.form.get("participa_outro_projeto")
    nome_projeto = request.form.get("nome_projeto")
    numero_pessoas_casa = request.form.get("numero_pessoas_casa")
    contato_emergencia = request.form.get("contato_emergencia")
    parentesco = request.form.get("parentesco")
    telefone_emergencia = request.form.get("telefone_emergencia")

    nome_responsavel = request.form.get("nome_responsavel")
    cpf_responsavel = request.form.get("cpf_responsavel")
    rg_responsavel = request.form.get("rg_responsavel")
    data_autorizacao = request.form.get("data_autorizacao")
    assinatura_responsavel = request.form.get("assinatura_responsavel")


    if (not nome_aluno or not data_nascimento or not sexo or not rg or not cpf or not endereco or not bairro or not cep or not nome_mae or not nome_pai):
        return {
            "success": False,
            "message": "Preencha todas as informações gerais."
        }

    if (not problema_cardiaco or not dor_peito_atividade or not dor_peito_recente or not tontura_ou_perda_consciencia or not problema_osseo_articular or not medicacao_continua or not tratamento_pressao or not outra_condicao_saude):
        return {
            "success": False,
            "message": "Responda todas as perguntas do Questionário."
        }

    if not modalidade or not dias or not horario:
        return {
            "success": False,
            "message": "Selecione modalidade, dias e horário."
        }

    if not motivo_inscricao and not outro_motivo:
        return {
            "success": False,
            "message": "Informe o motivo da inscrição."
        }

    if (not recebe_auxilio or not participa_outro_projeto or not contato_emergencia or not parentesco or not telefone_emergencia):
        return {
            "success": False,
            "message": "Preencha os dados obrigatórios das observações."
        }

    if (not nome_responsavel or not cpf_responsavel or not rg_responsavel or not data_autorizacao or not assinatura_responsavel):
        return {
            "success": False,
            "message": "Preencha todos os dados da autorização."
        }

    cursor.execute(
        """
        INSERT INTO inscricoes (
            nome_aluno,
            data_nascimento,
            sexo,
            rg,
            cpf,
            endereco,
            bairro,
            cep,
            nome_mae,
            nome_pai,
            problema_cardiaco,
            dor_peito_atividade,
            dor_peito_recente,
            tontura_ou_perda_consciencia,
            problema_osseo_articular,
            medicacao_continua,
            tratamento_pressao,
            outra_condicao_saude,
            modalidade,
            dias,
            horario,
            motivo_inscricao,
            outro_motivo,
            recebe_auxilio,
            participa_outro_projeto,
            nome_projeto,
            numero_pessoas_casa,
            contato_emergencia,
            parentesco,
            telefone_emergencia,
            nome_responsavel,
            cpf_responsavel,
            rg_responsavel,
            data_autorizacao,
            assinatura_responsavel
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            nome_aluno,
            data_nascimento,
            sexo,
            rg,
            cpf,
            endereco,
            bairro,
            cep,
            nome_mae,
            nome_pai,
            problema_cardiaco,
            dor_peito_atividade,
            dor_peito_recente,
            tontura_ou_perda_consciencia,
            problema_osseo_articular,
            medicacao_continua,
            tratamento_pressao,
            outra_condicao_saude,
            modalidade,
            dias,
            horario,
            motivo_inscricao,
            outro_motivo,
            recebe_auxilio,
            participa_outro_projeto,
            nome_projeto,
            numero_pessoas_casa,
            contato_emergencia,
            parentesco,
            telefone_emergencia,
            nome_responsavel,
            cpf_responsavel,
            rg_responsavel,
            data_autorizacao,
            assinatura_responsavel
        )
    )

    conexao.commit()

    return {
        "success": True,
        "message": "Inscrição realizada com sucesso!"
    }
