import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

from app import cbb, conexao

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
cbb.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@cbb.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        nome_completo = request.form.get('nome_completo')
        data_nascimento = request.form.get('data_nascimento')
        sexo = request.form.get('sexo')
        cpf = request.form.get('cpf')
        renda = request.form.get('renda')
        cep = request.form.get('cep')
        horarios = request.form.get('horarios')
        email = request.form.get('email')
        telefone = request.form.get('telefone')

        caminho_foto = None
        if 'foto' in request.files:
            arquivo = request.files['foto']
            if arquivo and arquivo.filename != '':
                extensao = os.path.splitext(secure_filename(arquivo.filename))[1]
                nome_unico = f"{uuid.uuid4()}{extensao}"
                arquivo.save(os.path.join(cbb.config['UPLOAD_FOLDER'], nome_unico))
                caminho_foto = nome_unico

        return redirect(url_for('perfil'))

    return render_template('perfil.html')

if __name__ == '__main__':
    cbb.run(debug=True)
