from app import ccb, conexao, cursor
from flask import request

@ccb.route("/cadastro", methods=["POST"])
def criar_conta():

    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")

    if not nome or not email or not senha:
        return {
            "success": False,
            "message": "Preencha todos os campos."
        }

    if len(senha) < 8:
        return {
            "success": False,
            "message": "A senha deve ter no mínimo 8 caracteres."
        }

    cursor.execute(
        "SELECT * FROM usuarios WHERE email = %s",
        (email,)
    )

    usuario = cursor.fetchone()

    if usuario:
        return {
            "success": False,
            "message": "E-mail já cadastrado."
        }

    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha)
        VALUES (%s, %s, %s)
        """,
        (nome, email, senha)
    )

    conexao.commit()

    return {
        "success": True,
        "message": "Conta criada com sucesso!"
    }
