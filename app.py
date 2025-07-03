from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Arquivos JSON dentro da pasta dados/
JUSTIFICATIVAS_FILE = os.path.join('dados', 'justificativas.json')
VOTOS_FILE = os.path.join('dados', 'votos.json')
RESULTADO_FILE = os.path.join('dados', 'resultado.json')  # se precisar usar

# Define o prazo da votação: amanhã às 9h (horário local)
DATA_CORTE = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

def carregar_justificativas():
    with open(JUSTIFICATIVAS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_votos():
    try:
        with open(VOTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
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
        voto_profissional = request.form.get('voto_profissional')
        voto_lider = request.form.get('voto_lider')
        justificativa = request.form.get('justificativa')

        if not voto_profissional or not voto_lider:
            return render_template('votacao.html', dados=dados, votos=votos, erro="Selecione todos os votos")

        votos['profissionais'][voto_profissional] = votos['profissionais'].get(voto_profissional, 0) + 1
        votos['lideres'][voto_lider] = votos['lideres'].get(voto_lider, 0) + 1
        if justificativa:
            votos['justificativas'][justificativa] = votos['justificativas'].get(justificativa, 0) + 1

        salvar_votos(votos)
        return redirect(url_for('resultado'))

    return render_template('votacao.html', dados=dados, votos=votos)

@app.route('/resultado')
def resultado():
    dados = carregar_justificativas()
    votos = carregar_votos()
    return render_template('resultado.html', dados=dados, votos=votos)

if __name__ == '__main__':
    app.run()
