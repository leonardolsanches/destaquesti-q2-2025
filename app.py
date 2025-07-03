from flask import Flask, render_template, request, redirect, url_for, flash, session
import re, os, json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'chave-secreta-muito-segura'

EMAIL_REGEX = re.compile(r'^[\w\.-]+@claro\.com\.br$', re.I)
DATA_CORTE = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

DIR_DADOS = 'dados'
USUARIOS_FILE = os.path.join(DIR_DADOS, 'usuarios.json')
VOTOS_FILE = os.path.join(DIR_DADOS, 'votos.json')
JUSTIFICATIVAS_FILE = os.path.join(DIR_DADOS, 'justificativas.json')

def carregar_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def salvar_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def validar_email():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        if not EMAIL_REGEX.match(email):
            flash('Digite um e-mail válido @claro.com.br', 'error')
            return render_template('validar_email.html')
        usuarios = carregar_json(USUARIOS_FILE, [])
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
    if datetime.now() >= DATA_CORTE:
        return redirect(url_for('resultado'))
    dados = carregar_json(JUSTIFICATIVAS_FILE, {})
    votos = carregar_json(VOTOS_FILE, {"profissionais": {}, "lideres": {}, "justificativas": {}})
    usuarios = carregar_json(USUARIOS_FILE, [])
    user_email = session['user_email']
    if user_email in usuarios:
        return redirect(url_for('resultado'))
    if request.method == 'POST':
        profs = request.form.getlist('voto_profissional')
        lider = request.form.get('voto_lider')
        if not profs or len(profs) != 1:
            flash("Selecione exatamente 1 profissional.", 'error')
            return render_template('votacao.html', dados=dados, votos=votos)
        if not lider:
            flash("Selecione 1 líder.", 'error')
            return render_template('votacao.html', dados=dados, votos=votos)
        votos['profissionais'][profs[0]] = votos['profissionais'].get(profs[0], 0) + 1
        votos['lideres'][lider] = votos['lideres'].get(lider, 0) + 1
        salvar_json(VOTOS_FILE, votos)
        usuarios.append(user_email)
        salvar_json(USUARIOS_FILE, usuarios)
        flash('Voto registrado com sucesso! Obrigado por participar.', 'success')
        return redirect(url_for('resultado'))
    return render_template('votacao.html', dados=dados, votos=votos)

@app.route('/resultado')
def resultado():
    dados = carregar_json(JUSTIFICATIVAS_FILE, {})
    votos = carregar_json(VOTOS_FILE, {"profissionais": {}, "lideres": {}, "justificativas": {}})
    def ordenar(lista, votos_dict):
        return sorted(lista, key=lambda x: votos_dict.get(x['id'], 0), reverse=True)
    dados['profissionais'] = ordenar(dados.get('profissionais', []), votos.get('profissionais', {}))
    dados['lideres'] = ordenar(dados.get('lideres', []), votos.get('lideres', {}))
    return render_template('resultado.html', dados=dados, votos=votos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('validar_email'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
