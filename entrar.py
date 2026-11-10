from app import ccb, conexao, cursor
from flask import request


@ccb.route("/login", methods=["POST"])
def entrar():

    email = request.form.get("email")
    senha = request.form.get("senha")

    if not email or not senha:
        return {
            "success": False,
            "message": "Preencha todos os campos."
        }

    cursor.execute(
        "SELECT * FROM usuarios WHERE email = %s",
        (email,)
    )

    usuario = cursor.fetchone()

    if not usuario:
        return {
            "success": False,
            "message": "E-mail ou senha inválidos."
        }

    if usuario[3] != senha:
        return {
            "success": False,
            "message": "E-mail ou senha inválidos."
        }

    return {
        "success": True,
        "message": "Login realizado com sucesso!"
    }