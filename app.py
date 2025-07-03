from flask import Flask, render_template, request, redirect, url_for, flash, session
import re
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'chave-secreta-muito-segura'  # Troque por algo seguro

EMAIL_REGEX = re.compile(r'^[\w\.-]+@claro\.com\.br$', re.IGNORECASE)

JUSTIFICATIVAS_FILE = os.path.join('dados', 'justificativas.json')
VOTOS_FILE = os.path.join('dados', 'votos.json')
USUARIOS_FILE = os.path.join('dados', 'usuarios.json')

DATA_CORTE = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

def carregar_justificativas():
    with open(JUSTIFICATIVAS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_votos():
    try:
        with open(VOTOS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key in ['profissionais', 'lideres', 'justificativas']:
                if key not in data or not isinstance(data[key], dict):
                    data[key] = {}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"profissionais": {}, "lideres": {}, "justificativas": {}}

def salvar_votos(votos):
    with open(VOTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(votos, f, ensure_ascii=False, indent=2)

def carregar_usuarios():
    try:
        with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_usuarios(usuarios):
    with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def validar_email():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not EMAIL_REGEX.match(email):
            flash('Digite um e-mail válido @claro.com.br', 'error')
            return render_template('validar_email.html')

        usuarios = carregar_usuarios()
        if email in usuarios:
            flash('Este e-mail já votou.', 'error')
            return render_template('validar_email.html')

        session['user_email'] = email
        return redirect(url_for('votacao'))

    return render_template('validar_email.html')

@app.route('/votacao', methods=['GET', 'POST'])
def votacao():
    if 'user_email' not in session:
        return redirect(url_for('validar_email'))

    agora = datetime.now()
    if agora >= DATA_CORTE:
        return redirect(url_for('resultado'))

    dados = carregar_justificativas()
    votos = carregar_votos()
    usuarios = carregar_usuarios()
    user_email = session['user_email']

    if user_email in usuarios:
        return redirect(url_for('resultado'))

    if request.method == 'POST':
        voto_profissionais = request.form.getlist('voto_profissional')
        voto_lider = request.form.get('voto_lider')

        if not voto_profissionais or len(voto_profissionais) == 0:
            flash("Selecione um profissional.", 'error')
            return render_template('votacao.html', dados=dados, votos=votos)

        if len(voto_profissionais) > 1:
            flash("Você pode selecionar apenas 1 profissional.", 'error')
            return render_template('votacao.html', dados=dados, votos=votos)

        if not voto_lider:
            flash("Selecione um líder.", 'error')
            return render_template('votacao.html', dados=dados, votos=votos)

        for prof_id in voto_profissionais:
            votos['profissionais'][prof_id] = votos['profissionais'].get(prof_id, 0) + 1

        votos['lideres'][voto_lider] = votos['lideres'].get(voto_lider, 0) + 1

        salvar_votos(votos)

        usuarios.append(user_email)
        salvar_usuarios(usuarios)

        flash('Voto registrado com sucesso! Obrigado por participar.', 'success')
        return redirect(url_for('resultado'))

    return render_template('votacao.html', dados=dados, votos=votos)

@app.route('/resultado')
def resultado():
    dados = carregar_justificativas()
    votos = carregar_votos()

    def ordenar_por_votos(lista, votos_dict):
        return sorted(lista, key=lambda x: votos_dict.get(x['id'], 0), reverse=True)

    dados['profissionais'] = ordenar_por_votos(dados['profissionais'], votos['profissionais'])
    dados['lideres'] = ordenar_por_votos(dados['lideres'], votos['lideres'])

    return render_template('resultado.html', dados=dados, votos=votos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('validar_email'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
