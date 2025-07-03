from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@claro\.com\.br$')

JUSTIFICATIVAS_FILE = 'dados/justificativas.json'
VOTOS_FILE = 'dados/votos.json'
USUARIOS_FILE = 'dados/usuarios.json'

DATA_CORTE = datetime.strptime('2025-07-04 09:00:00', '%Y-%m-%d %H:%M:%S')

def carregar_json(arquivo, default):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

def salvar_json(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def validar_email():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        gestor = request.form.get('gestor', '').strip()
        if not EMAIL_REGEX.match(email):
            flash('Digite um e-mail válido @claro.com.br', 'error')
            return render_template('validar_email.html')
        if not gestor:
            flash('Selecione um gestor válido.', 'error')
            return render_template('validar_email.html')
        usuarios = carregar_json(USUARIOS_FILE, [])
        if any(u['email'] == email for u in usuarios):
            flash('Este e-mail já votou.', 'error')
            return render_template('validar_email.html')
        session['user_email'] = email
        session['user_gestor'] = gestor
        return redirect(url_for('votacao'))
    return render_template('validar_email.html')

@app.route('/votacao', methods=['GET', 'POST'])
def votacao():
    if 'user_email' not in session or 'user_gestor' not in session:
        return redirect(url_for('validar_email'))
    if datetime.now() >= DATA_CORTE:
        return redirect(url_for('resultado'))

    user_gestor = session['user_gestor']
    dados = carregar_json(JUSTIFICATIVAS_FILE, {})
    votos = carregar_json(VOTOS_FILE, {"profissionais": {}, "lideres": {}, "justificativas": {}})
    usuarios = carregar_json(USUARIOS_FILE, [])
    user_email = session['user_email']

    if any(u['email'] == user_email for u in usuarios):
        return redirect(url_for('resultado'))

    profissionais_filtrados = [p for p in dados.get('profissionais', []) if p['gestor'] != user_gestor]
    lideres_filtrados = [l for l in dados.get('lideres', []) if l['gestor'] != user_gestor]

    if request.method == 'POST':
        profs = request.form.getlist('voto_profissional')
        lider = request.form.get('voto_lider')
        if not profs or len(profs) != 1:
            flash("Selecione exatamente 1 profissional.", 'error')
            return render_template('votacao.html', dados={'profissionais': profissionais_filtrados, 'lideres': lideres_filtrados}, votos=votos)
        if not lider:
            flash("Selecione 1 líder.", 'error')
            return render_template('votacao.html', dados={'profissionais': profissionais_filtrados, 'lideres': lideres_filtrados}, votos=votos)

        candidato_prof = next((p for p in profissionais_filtrados if p['id'] == profs[0]), None)
        candidato_lider = next((l for l in lideres_filtrados if l['id'] == lider), None)
        if not candidato_prof or not candidato_lider:
            flash("Seleção inválida de candidato(s).", 'error')
            return render_template('votacao.html', dados={'profissionais': profissionais_filtrados, 'lideres': lideres_filtrados}, votos=votos)

        votos['profissionais'][profs[0]] = votos['profissionais'].get(profs[0], 0) + 1
        votos['lideres'][lider] = votos['lideres'].get(lider, 0) + 1
        salvar_json(VOTOS_FILE, votos)

        usuarios.append({'email': user_email, 'gestor': user_gestor})
        salvar_json(USUARIOS_FILE, usuarios)

        flash('Voto registrado com sucesso! Obrigado por participar.', 'success')
        return redirect(url_for('resultado'))

    return render_template('votacao.html', dados={'profissionais': profissionais_filtrados, 'lideres': lideres_filtrados}, votos=votos)

@app.route('/resultado')
def resultado():
    dados = carregar_json(JUSTIFICATIVAS_FILE, {})
    votos = carregar_json(VOTOS_FILE, {"profissionais": {}, "lideres": {}, "justificativas": {}})
    return render_template('resultado.html', dados=dados, votos=votos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('validar_email'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
