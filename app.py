import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'chave-super-secreta'  # Troque para chave forte

DATA_DIR = Path('./dados')

def carregar_justificativas():
    with open(DATA_DIR / 'justificativas.json', encoding='utf-8') as f:
        return json.load(f)

def carregar_votos():
    path = DATA_DIR / 'votos.json'
    if not path.exists():
        votos = {'profissionais': {}, 'lideres': {}}
        justs = carregar_justificativas()
        for p in justs['profissionais']:
            votos['profissionais'][p['id']] = 0
        for l in justs['lideres']:
            votos['lideres'][l['id']] = 0
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(votos, f, ensure_ascii=False, indent=2)
        return votos
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def salvar_votos(votos):
    with open(DATA_DIR / 'votos.json', 'w', encoding='utf-8') as f:
        json.dump(votos, f, ensure_ascii=False, indent=2)

GESTORES = sorted(list(set([
    'Aline', 'Marcus', 'Mario', 'Mezardi', 'Waldir', 'Wollinger', 'Fabio'
])))

@app.route('/', methods=['GET', 'POST'])
def validar_email():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        gestor = request.form.get('gestor', '')
        if not email.endswith('@claro.com.br'):
            flash('Digite um e-mail válido @claro.com.br')
            return redirect(url_for('validar_email'))
        if gestor not in GESTORES:
            flash('Selecione um gestor válido')
            return redirect(url_for('validar_email'))
        session['email'] = email
        session['gestor_usuario'] = gestor
        session['votou'] = False
        return redirect(url_for('votacao'))
    return render_template('validar_email.html', gestores=GESTORES)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('validar_email'))

@app.route('/votacao', methods=['GET', 'POST'])
def votacao():
    if 'email' not in session:
        return redirect(url_for('validar_email'))

    justs = carregar_justificativas()
    votos = carregar_votos()

    if request.method == 'POST':
        if session.get('votou', False):
            flash('Você já votou.')
            return redirect(url_for('resultado'))

        profissional = request.form.get('profissional')
        lider = request.form.get('lider')
        gestor_usuario = session.get('gestor_usuario')

        if not profissional or not lider:
            flash('Selecione um profissional e um líder.')
            return redirect(url_for('votacao'))

        prof_gestor = next((p['gestor'] for p in justs['profissionais'] if p['id'] == profissional), None)
        lider_gestor = next((l['gestor'] for l in justs['lideres'] if l['id'] == lider), None)

        if prof_gestor == gestor_usuario:
            flash(f'Você não pode votar em profissional do mesmo gestor: {gestor_usuario}')
            return redirect(url_for('votacao'))
        if lider_gestor == gestor_usuario:
            flash(f'Você não pode votar em líder do mesmo gestor: {gestor_usuario}')
            return redirect(url_for('votacao'))

        votos['profissionais'][profissional] = votos['profissionais'].get(profissional, 0) + 1
        votos['lideres'][lider] = votos['lideres'].get(lider, 0) + 1
        salvar_votos(votos)

        session['votou'] = True
        flash('Voto registrado com sucesso!')
        return redirect(url_for('resultado'))

    gestor_usuario = session.get('gestor_usuario')
    for p in justs['profissionais']:
        p['bloqueado'] = (p['gestor'] == gestor_usuario)
        p['votos'] = votos['profissionais'].get(p['id'], 0)
    for l in justs['lideres']:
        l['bloqueado'] = (l['gestor'] == gestor_usuario)
        l['votos'] = votos['lideres'].get(l['id'], 0)

    return render_template('votacao.html', profissionais=justs['profissionais'], lideres=justs['lideres'], gestor_usuario=gestor_usuario)

@app.route('/resultado')
def resultado():
    if 'email' not in session:
        return redirect(url_for('validar_email'))

    justs = carregar_justificativas()
    votos = carregar_votos()

    candidatos = []
    for p in justs['profissionais']:
        candidatos.append({
            "id": p['id'],
            "nome": p['nome'],
            "tipo": "PROFISSIONAL",
            "votos": votos['profissionais'].get(p['id'], 0),
            "imagem": url_for('static', filename='img/' + p['imagem'])
        })

    for l in justs['lideres']:
        candidatos.append({
            "id": l['id'],
            "nome": l['nome'],
            "tipo": "LÍDER",
            "votos": votos['lideres'].get(l['id'], 0),
            "imagem": url_for('static', filename='img/' + l['imagem'])
        })

    return render_template('resultado.html', candidatos=candidatos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
