from app import ccb, conexao, cursor
from flask import redirect, request, url_for, render_template, session


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
        return render_template(
            "login.html",
            erro="E-mail ou senha inválidos."
        )

    if usuario[3] != senha:
        return render_template(
            "login.html",
            erro="E-mail ou senha inválidos."
        )

    session["usuario_id"] = usuario[0]
    session["usuario_nome"] = usuario[1]
    session["usuario_email"] = usuario[2]

    return redirect(url_for("home"))
