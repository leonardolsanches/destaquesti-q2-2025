from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'supersecretkey'

JUSTIFICATIVAS_PATH = 'dados/justificativas.json'
VOTOS_PATH = os.path.join(os.path.dirname(__file__), 'dados', 'votos.json')
RESULTADO_PATH = os.path.join(os.path.dirname(__file__), 'dados', 'resultado.json')

# Load justificativas.json (para compatibilidade, mas não será usado diretamente)
with open(JUSTIFICATIVAS_PATH, 'r', encoding='utf-8') as f:
    justificativas = json.load(f)

# Define candidates with updated list
candidates = [
    {'id': 'L1', 'nome': 'André Salgado', 'foto': 'L1.png', 'desc': 'André Salgado tem se destacado de forma notável na liderança dos projetos PME, sendo uma peça chave nas transformações em curso. Profissional sempre disponível, a determinação e o foco em conduzir projetos, mesmo diante de desafios, refletem seu comprometimento e profissionalismo. Soube lidar com a velocidade exigida do negócio.', 'gestor': 'Aline', 'type': 'lider'},
    {'id': 'L2', 'nome': 'Eduardo Padilha', 'foto': 'L2.png', 'desc': 'Liderou seu time com muito empenho superando obstáculos e conseguindo realizar a entrega antecipada na entrega do Portabilidade Cruzada – CPC, projeto estratégico para o PME com resultado reconhecido pela diretoria de negócios.', 'gestor': 'Marcus', 'type': 'lider'},
    {'id': 'L3', 'nome': 'Rosangela Teressani', 'foto': 'L3.png', 'desc': 'Possui uma dedicação incansável e se destacou recentemente por estar responsável por muitas frentes críticas e importantes ao mesmo tempo, com destaque ao projeto NFCOM Travas e 6 frentes paralelas do RGC. É muito responsável e busca um alinhamento minucioso entre as frentes envolvidas para mitigar os riscos do projeto e viabilizar a entrega.', 'gestor': 'Aline', 'type': 'lider'},
    {'id': 'L4', 'nome': 'Tiago Barbosa', 'foto': 'L4.png', 'desc': 'Realizado um trabalho excepcional junto com o seu time, gerando grande valor para o negócio. Sua habilidade em gerenciar múltiplos projetos simultaneamente, mantendo um alto nível de entrega e resultados, é admirável. A dedicação e o comprometimento não apenas contribuem para o sucesso da equipe, mas também para o fortalecimento dos objetivos organizacionais. Projetos como Esim, PIX, Cross-Sell, eCommerce.', 'gestor': 'Aline', 'type': 'lider'},
    {'id': 'P1', 'nome': 'Antonio Carlos Geraldi', 'foto': 'P1.png', 'desc': 'Atuação essencial para o sucesso do projeto PIX Recorrente para o Residencial, demonstrou comprometimento com os prazos e entregou seu trabalho com qualidade.', 'gestor': 'Wollinger', 'type': 'profissional'},
    {'id': 'P2', 'nome': 'Camila Faraco', 'foto': 'P2.png', 'desc': 'Liderou o projeto, garantindo que as atividades fossem feitas no prazo e com qualidade na Implementação do PIX Automático, feature do Open Finance, iniciativa BACEN substituta do Débito Automático.', 'gestor': 'Mario', 'type': 'profissional'},
    {'id': 'P3', 'nome': 'Diogo Camada', 'foto': 'P3.png', 'desc': 'Foi fundamental no projeto MOVE2VIRGINIA com protagonismo e liderança, grande capacidade de alinhamento e entendimento de aspectos cruciais para o sucesso. Também vem assumindo responsabilidades no sistema de Ressarcimento, evidenciando forte senso de pertencimento e comprometimento.', 'gestor': 'Mezadri', 'type': 'profissional'},
    {'id': 'P4', 'nome': 'Erick Nakamura', 'foto': 'P4.png', 'desc': 'Relevância na implantação do faturador pré-pago para o projeto NFCom e uma forte atuação que garantiu estabilidade dos processos e assegurou a aderência técnica às necessidades de detalhamento do consumo dos segmentos Pré-Pago, Controle Facil e Tradicional.', 'gestor': 'Mezadri', 'type': 'profissional'},
    {'id': 'P5', 'nome': 'José Antenor Penna', 'foto': 'P5.png', 'desc': 'Colaborador mostrou senso de "dono" ao liderar o processo de UAT da frente de Cobilling Sainte do NFCOM, até sua implementação final. Além disso, aceitou o desafio de assumir o sistema de faturamento Orbill, demonstrando comprometimento com auto desenvolvimento.', 'gestor': 'Wollinger', 'type': 'profissional'},
    {'id': 'P6', 'nome': 'Luiz Fernando Gonçalves de Mattos', 'foto': 'P6.png', 'desc': 'Colaborador tem se mostrado um profissional dedicado e participado ativamente de projetos importantes como NFCOM, RGC e Código Único, sempre com alto nível técnico. Além disso, foi responsável por uma entrega fundamental no serviço de Acordos de Pagamento, que solucionou um problema crítico no sistema Solar.', 'gestor': 'Wollinger', 'type': 'profissional'},
    {'id': 'P7', 'nome': 'Rafael dos Santos', 'foto': 'P7.png', 'desc': 'Referência técnica incontestável, facilitador para diversos times e stakeholders. Durante o Q2, fez a entrega do projeto de Melhoria de Heapsize que trouxe a simplificação de atributos de catálogo e resolveu o problema de quebra de carrinho devido à quantidade de atributos de produtos na jornada do Solar.', 'gestor': 'Waldir', 'type': 'profissional'},
    {'id': 'P8', 'nome': 'Robson Carvalho de Oliveira', 'foto': 'P8.png', 'desc': 'Liderou o projeto para evitar compartilhamento de ShortCode de SMS por parceiro junto ao MSE, desenvolveu a solução garantindo que as atividades fossem feitas no prazo e com qualidade.', 'gestor': 'Mario', 'type': 'profissional'},
    {'id': 'P9', 'nome': 'Vagner Vieira', 'foto': 'P9.png', 'desc': 'Excelente trabalho a frente do núcleo de performance melhorando os indicadores do ambiente Salesforce em mais de 40% quando comparado com dezembro/24.', 'gestor': 'Aline', 'type': 'profissional'},
    {'id': 'P10', 'nome': 'Wilson Neves', 'foto': 'P10.png', 'desc': 'Liderança técnica nos projetos modernização do SOA e upgrade do SMP que entregou o primeiro rollout em Bauru-SP e habilitou os próximos rollouts em aproximadamente 10 milhões de assinantes da rede HFC.', 'gestor': 'Marcus', 'type': 'profissional'}
]

def votacao_encerrada():
    tz = pytz.timezone('America/Sao_Paulo')  # GMT-3
    now = datetime.now(tz)
    return now >= datetime(2025, 7, 2, 18, 0, tzinfo=tz)  # Prazo: 18:00 PM on July 02, 2025

def get_user_votes(email):
    votos = []
    if os.path.exists(VOTOS_PATH) and os.path.getsize(VOTOS_PATH) > 0:
        with open(VOTOS_PATH, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                print(f"Loaded votes from {VOTOS_PATH}: {content}")  # Debug log
                if not isinstance(content, list):
                    print(f"Content is not a list, converting to empty list")
                    content = []
                votos = content
            except json.JSONDecodeError as e:
                print(f"JSON decode error in {VOTOS_PATH}: {e}")
                votos = []
    return [v['candidate_id'] for v in votos if v.get('email') == email]

@app.route('/')
def index():
    if votacao_encerrada():
        return redirect(url_for('encerrado'))
    if not session.get('email_validated'):
        return redirect(url_for('validate_email'))
    return redirect(url_for('votar'))

@app.route('/validate_email', methods=['GET', 'POST'])
def validate_email():
    if request.method == 'POST':
        email = request.form.get('identificador')
        if not email or not email.endswith('@claro.com.br'):
            flash('Somente e-mails @claro.com.br são permitidos.')
            return redirect(url_for('validate_email'))
        session['email_validated'] = email
        return redirect(url_for('votar'))
    return render_template('validate_email.html')

@app.route('/votar', methods=['GET', 'POST'])
def votar():
    if votacao_encerrada():
        return redirect(url_for('encerrado'))
    if not session.get('email_validated'):
        return redirect(url_for('validate_email'))
    email = session['email_validated']
    user_votes = get_user_votes(email)
    prof_votes = [v for v in user_votes if v.startswith('P')]
    lider_votes = [v for v in user_votes if v.startswith('L')]

    if request.method == 'POST':
        profs = request.form.getlist('profissionais')
        lideres = request.form.getlist('lideres')
        print(f"Received POST data - Request method: {request.method}")
        print(f"Received POST data - Request headers: {request.headers}")
        print(f"Received POST data - Request form: {dict(request.form)}")
        print(f"Received POST data - Profs: {profs}, Lideres: {lideres}")

        if len(profs) < 2 or len(lideres) < 2:
            flash('Por favor, selecione pelo menos 2 profissionais e 2 líderes.')
            return redirect(url_for('votar'))
        if len(profs) > 2 or len(lideres) > 2:
            flash('Limite excedido! Você pode selecionar no máximo 2 profissionais e 2 líderes.')
            return redirect(url_for('votar'))
        new_prof_votes = [p for p in profs if p not in prof_votes]
        new_lider_votes = [l for l in lideres if l not in lider_votes]

        # Criar diretório e arquivo se não existirem
        os.makedirs(os.path.dirname(VOTOS_PATH) or '.', exist_ok=True)
        if not os.path.exists(VOTOS_PATH):
            with open(VOTOS_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f)  # Inicializa como lista vazia
        votos_existentes = []
        if os.path.exists(VOTOS_PATH) and os.path.getsize(VOTOS_PATH) > 0:
            with open(VOTOS_PATH, 'r', encoding='utf-8') as f:
                try:
                    content = json.load(f)
                    print(f"Existing votes from {VOTOS_PATH}: {content}")  # Debug log
                    if isinstance(content, list):
                        votos_existentes = content
                    else:
                        votos_existentes = []
                except json.JSONDecodeError as e:
                    print(f"JSON decode error in {VOTOS_PATH}: {e}")
                    votos_existentes = []
        novos_votos = []
        for p in new_prof_votes:
            novos_votos.append({'email': email, 'candidate_id': p})
            print(f"Preparing to register vote for professional: {p}")
        for l in new_lider_votes:
            novos_votos.append({'email': email, 'candidate_id': l})
            print(f"Preparing to register vote for leader: {l}")
        votos = votos_existentes + novos_votos  # Adiciona novos votos aos existentes
        print(f"Combined votes to save: {votos}")  # Debug log
        try:
            # Teste de escrita em um arquivo temporário primeiro
            temp_path = os.path.join(os.path.dirname(__file__), 'temp_test.json')
            with open(temp_path, 'w', encoding='utf-8') as f_temp:
                json.dump(votos, f_temp, ensure_ascii=False)
            print(f"Successfully wrote to temp_test.json for verification: {votos}")
            # Agora escreve no arquivo principal
            with open(VOTOS_PATH, 'w', encoding='utf-8') as f:
                json.dump(votos, f, ensure_ascii=False)
            print(f"Successfully wrote to {VOTOS_PATH} with {len(votos)} votes")
            # Verificar o conteúdo escrito
            with open(VOTOS_PATH, 'r', encoding='utf-8') as f:
                written_content = json.load(f)
                print(f"Verified written content: {written_content}")
        except Exception as e:
            print(f"Error writing to {VOTOS_PATH}: {e}")
            # Tentar escrever em um local alternativo para diagnóstico
            debug_path = os.path.join(os.path.dirname(__file__), 'debug_votos.json')
            with open(debug_path, 'w', encoding='utf-8') as f_debug:
                json.dump(votos, f_debug, ensure_ascii=False)
            print(f"Debug file written to {debug_path} with {len(votos)} votes")
        flash('Votos registrados com sucesso!')
        return redirect(url_for('votar'))
    return render_template('votacao.html', candidates=candidates, prof_votes=prof_votes, lider_votes=lider_votes)

@app.route('/partial_results')
def partial_results():
    if not session.get('email_validated'):
        return redirect(url_for('validate_email'))
    votos = []
    if os.path.exists(VOTOS_PATH) and os.path.getsize(VOTOS_PATH) > 0:
        with open(VOTOS_PATH, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                print(f"Loaded votes from {VOTOS_PATH}: {content}")  # Debug log
                if not isinstance(content, list):
                    print(f"Content is not a list, converting to empty list")
                    content = []
                votos = content
            except json.JSONDecodeError as e:
                print(f"JSON decode error in {VOTOS_PATH}: {e}")
                votos = []
    vote_counts = {}
    print(f"Starting vote count with votos: {votos}")  # Debug log
    for voto in votos:
        if isinstance(voto, dict) and 'candidate_id' in voto:
            candidate_id = voto['candidate_id']
            vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1
            print(f"Counting vote for {candidate_id}, total: {vote_counts[candidate_id]}")
        else:
            print(f"Invalid vote format: {voto}")
    partial_results = {c['id']: {'nome': c['nome'], 'votos': vote_counts.get(c['id'], 0), 'gestor': c['gestor'], 'foto': c['foto']} for c in candidates}
    print(f"Partial results: {partial_results}")  # Debug log
    return render_template('partial_results.html', partial_results=partial_results, candidates=candidates)

@app.route('/view_votes')
def view_votes():
    if not os.path.exists(VOTOS_PATH):
        return jsonify({"error": "Arquivo votos.json não encontrado"}), 404
    try:
        with open(VOTOS_PATH, 'r', encoding='utf-8') as f:
            votos = json.load(f) if os.path.getsize(VOTOS_PATH) > 0 else []
        return jsonify(votos)
    except Exception as e:
        return jsonify({"error": f"Erro ao ler votos.json: {e}"}), 500

@app.route('/encerrado')
def encerrado():
    return render_template('encerrado.html')

@app.route('/resultado')
def resultado():
    if not votacao_encerrada():
        flash('A votação ainda não foi encerrada.')
        return redirect(url_for('votar'))
    votos = []
    if os.path.exists(VOTOS_PATH) and os.path.getsize(VOTOS_PATH) > 0:
        with open(VOTOS_PATH, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                if isinstance(content, list):
                    votos = content
                else:
                    votos = []
            except json.JSONDecodeError:
                votos = []
    vote_counts = {}
    for voto in votos:
        vote_counts[voto['candidate_id']] = vote_counts.get(voto['candidate_id'], 0) + 1
    # Sort candidates by vote count in descending order
    sorted_resultado = sorted(
        [(id, {'nome': c['nome'], 'votos': vote_counts.get(id, 0), 'gestor': c['gestor'], 'foto': c['foto']}) 
         for id, c in [(c['id'], c) for c in candidates]],
        key=lambda x: x[1]['votos'],
        reverse=True
    )
    resultado = dict(sorted_resultado)
    with open(RESULTADO_PATH, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False)
    return render_template('resultado.html', resultado=resultado, candidates=candidates)

@app.route('/get_partial_results')
def get_partial_results():
    votos = []
    if os.path.exists(VOTOS_PATH) and os.path.getsize(VOTOS_PATH) > 0:
        with open(VOTOS_PATH, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                if isinstance(content, list):
                    votos = content
                else:
                    votos = []
            except json.JSONDecodeError:
                votos = []
    vote_counts = {}
    for voto in votos:
        vote_counts[voto['candidate_id']] = vote_counts.get(voto['candidate_id'], 0) + 1
    partial_results = {c['id']: {'nome': c['nome'], 'votos': vote_counts.get(c['id'], 0), 'gestor': c['gestor'], 'foto': c['foto']} for c in candidates}
    return jsonify(partial_results)

@app.route('/test', methods=['POST'])
def test():
    print(f"Test endpoint hit - Request headers: {request.headers}")
    print(f"Test endpoint - Request form: {dict(request.form)}")
    return "Test successful", 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)  # Modo de depuração desativado