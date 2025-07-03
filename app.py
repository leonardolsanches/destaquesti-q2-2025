from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

JUSTIFICATIVAS_FILE = os.path.join('dados', 'justificativas.json')
VOTOS_FILE = os.path.join('dados', 'votos.json')

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

@app.route('/')
def index():
    return redirect(url_for('votacao'))

@app.route('/votacao', methods=['GET', 'POST'])
def votacao():
    agora = datetime.now()
    if agora >= DATA_CORTE:
        return redirect(url_for('resultado'))

    dados = carregar_justificativas()
    votos = carregar_votos()

    if request.method == 'POST':
        voto_profissionais = request.form.getlist('voto_profissional')
        voto_lider = request.form.get('voto_lider')

        if not voto_profissionais or len(voto_profissionais) == 0:
            return render_template('votacao.html', dados=dados, votos=votos, erro="Selecione pelo menos um profissional (máximo 4).")

        if len(voto_profissionais) > 4:
            return render_template('votacao.html', dados=dados, votos=votos, erro="Você pode selecionar no máximo 4 profissionais.")

        if not voto_lider:
            return render_template('votacao.html', dados=dados, votos=votos, erro="Selecione um líder.")

        for prof_id in voto_profissionais:
            votos['profissionais'][prof_id] = votos['profissionais'].get(prof_id, 0) + 1

        votos['lideres'][voto_lider] = votos['lideres'].get(voto_lider, 0) + 1

        salvar_votos(votos)
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
