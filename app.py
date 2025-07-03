import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'seu_seguro_secret_key'

DATA_DIR = 'dados'

def carregar_json(nome_arquivo):
    caminho = os.path.join(DATA_DIR, nome_arquivo)
    if not os.path.isfile(caminho):
        return {}
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_json(nome_arquivo, dados):
    caminho = os.path.join(DATA_DIR, nome_arquivo)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def ordenar_por_codigo(lista_candidatos):
    def extrair_numero(candidato):
        codigo = candidato['id']
        letra = codigo[0].upper()
        numero = int(codigo[1:])
        offset = 100 if letra == 'L' else 0
        return numero + offset
    return sorted(lista_candidatos, key=extrair_numero)

@app.route('/', methods=['GET', 'POST'])
def validar_email():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        gestor = request.form.get('gestor', '').strip()

        if not email.endswith('@claro.com.br'):
            flash('O e-mail deve ser @claro.com.br', 'error')
            return render_template('validar_email.html')

        session['email'] = email
        session['gestor_usuario'] = gestor

        votos = carregar_json('votos.json')
        if email in votos:
            flash('Você já realizou sua votação.', 'error')
            return redirect(url_for('resultado'))

        return redirect(url_for('votacao'))

    return render_template('validar_email.html')

@app.route('/votacao', methods=['GET', 'POST'])
def votacao():
    if 'email' not in session:
        return redirect(url_for('validar_email'))

    dados = carregar_json('justificativas.json')
    votos = carregar_json('resultado.json')  # Contagem dos votos

    dados['profissionais'] = ordenar_por_codigo(dados.get('profissionais', []))
    dados['lideres'] = ordenar_por_codigo(dados.get('lideres', []))

    if request.method == 'POST':
        email = session['email']
        gestor_usuario = session.get('gestor_usuario')

        voto_profissional = request.form.get('voto_profissional')
        voto_lider = request.form.get('voto_lider')

        if not voto_profissional or not voto_lider:
            flash('Você deve selecionar 1 profissional e 1 líder.', 'error')
            return render_template('votacao.html', dados=dados, resultado=votos)

        gestor_profissional = next((p['gestor'] for p in dados['profissionais'] if p['id'] == voto_profissional), None)
        gestor_lider = next((l['gestor'] for l in dados['lideres'] if l['id'] == voto_lider), None)

        if gestor_usuario == gestor_profissional or gestor_usuario == gestor_lider:
            flash('Você não pode votar em candidatos do seu próprio gestor.', 'error')
            return render_template('votacao.html', dados=dados, resultado=votos)

        votos_usuarios = carregar_json('votos.json')
        if email in votos_usuarios:
            flash('Você já realizou sua votação.', 'error')
            return redirect(url_for('resultado'))

        votos_usuarios[email] = {
            'profissional': voto_profissional,
            'lider': voto_lider,
            'gestor_usuario': gestor_usuario
        }
        salvar_json('votos.json', votos_usuarios)

        votos.setdefault('profissionais', {})
        votos.setdefault('lideres', {})

        votos['profissionais'][voto_profissional] = votos['profissionais'].get(voto_profissional, 0) + 1
        votos['lideres'][voto_lider] = votos['lideres'].get(voto_lider, 0) + 1
        salvar_json('resultado.json', votos)

        flash('Voto registrado com sucesso!', 'success')
        return redirect(url_for('votacao'))

    return render_template('votacao.html', dados=dados, resultado=votos)

@app.route('/resultado')
def resultado():
    dados = carregar_json('justificativas.json')
    resultado = carregar_json('resultado.json')

    dados['profissionais'] = ordenar_por_codigo(dados.get('profissionais', []))
    dados['lideres'] = ordenar_por_codigo(dados.get('lideres', []))

    return render_template('resultado.html', dados=dados, resultado=resultado)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('validar_email'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
