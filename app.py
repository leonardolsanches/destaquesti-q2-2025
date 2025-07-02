from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_secreta"

DADOS_PATH = os.path.join("dados", "justificativas.json")
VOTOS_PATH = os.path.join("dados", "votos.json")

# Carregar dados de candidatos e justificativas
with open(DADOS_PATH, encoding="utf-8") as f:
    dados = json.load(f)

profissionais = dados["profissionais"]
lideres = dados["lideres"]
justificativas = dados["justificativas"]

# Função para validar email básico
def valida_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# Função para checar se email já votou
def email_ja_votou(email):
    if not os.path.exists(VOTOS_PATH):
        return False
    with open(VOTOS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                voto = json.loads(line)
                if voto.get("email") == email:
                    return True
            except:
                continue
    return False

@app.route("/")
def index():
    return redirect(url_for("votar"))

@app.route("/votar", methods=["GET", "POST"])
def votar():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        prof_selecionados = request.form.getlist("profissionais")
        lider_selecionados = request.form.getlist("lideres")

        # Validações
        if not email or not valida_email(email):
            flash("Email inválido ou não informado.")
            return redirect(url_for("votar"))
        if email_ja_votou(email):
            flash("Este email já registrou seu voto.")
            return redirect(url_for("votar"))
        if len(prof_selecionados) != 2:
            flash("Selecione exatamente 2 profissionais.")
            return redirect(url_for("votar"))
        if len(lider_selecionados) != 2:
            flash("Selecione exatamente 2 líderes.")
            return redirect(url_for("votar"))

        voto = {
            "email": email,
            "profissionais": prof_selecionados,
            "lideres": lider_selecionados,
            "timestamp": datetime.now().isoformat()
        }

        # Salvar voto (append JSON por linha)
        os.makedirs(os.path.dirname(VOTOS_PATH), exist_ok=True)
        with open(VOTOS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(voto, ensure_ascii=False) + "\n")

        flash("Voto registrado com sucesso!")
        return redirect(url_for("votar"))

    # GET
    candidatos = []
    # Preparar lista unificada com campo type, gestor e desc para o template
    for p in profissionais:
        candidatos.append({
            "id": p["id"],
            "nome": p["nome"],
            "foto": p.get("imagem", ""),
            "gestor": p.get("gestor", ""),
            "desc": justificativas.get(p["id"], ""),
            "type": "profissional"
        })
    for l in lideres:
        candidatos.append({
            "id": l["id"],
            "nome": l["nome"],
            "foto": l.get("imagem", ""),
            "gestor": l.get("gestor", ""),
            "desc": justificativas.get(l["id"], ""),
            "type": "lider"
        })

    return render_template("votacao.html", candidates=candidatos)

@app.route("/encerrado")
def encerrado():
    return render_template("encerrado.html")

@app.route("/resultado")
def resultado():
    # Exibir resultados apenas após a data/hora limite (exemplo 2025-07-02 18:00 -3UTC)
    limite = datetime(2025, 7, 2, 18, 0, 0)
    agora = datetime.now()
    if agora < limite:
        flash("A votação ainda está em andamento.")
        return redirect(url_for("votar"))

    votos = []
    if os.path.exists(VOTOS_PATH):
        with open(VOTOS_PATH, "r", encoding="utf-8") as f:
            votos = [json.loads(linha) for linha in f if linha.strip()]

    contagem_profissionais = {}
    contagem_lideres = {}

    for voto in votos:
        for prof_id in voto.get("profissionais", []):
            contagem_profissionais[prof_id] = contagem_profissionais.get(prof_id, 0) + 1
        for lider_id in voto.get("lideres", []):
            contagem_lideres[lider_id] = contagem_lideres.get(lider_id, 0) + 1

    # Montar listas para template, incluindo nome e votos
    def montar_lista(contagem, lista_candidatos):
        resultado = []
        for c in lista_candidatos:
            votos_c = contagem.get(c["id"], 0)
            resultado.append({"id": c["id"], "nome": c["nome"], "votos": votos_c})
        return sorted(resultado, key=lambda x: x["votos"], reverse=True)

    profissionais_result = montar_lista(contagem_profissionais, profissionais)
    lideres_result = montar_lista(contagem_lideres, lideres)

    return render_template("resultado.html",
                           profissionais=profissionais_result,
                           lideres=lideres_result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
