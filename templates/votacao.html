<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Votação Q2/2025</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}" />
</head>
<body>
    <div class="container">
        <img src="{{ url_for('static', filename='img/claro_logo.png') }}" alt="Claro Logo" class="logo" />
        <div id="countdown" class="countdown">Tempo disponível para votação</div>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul class="flash-messages">
              {% for msg in messages %}
                <li style="color: white;">{{ msg }}</li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form id="vote-form" method="POST">
            <div class="candidate-grid">
                <h2>SELECIONE DOIS PROFISSIONAIS PARA DESTAQUE NA TI</h2>
                {% for candidate in candidates if candidate.tipo == 'profissional' %}
                    <div class="candidate-card">
                        <div class="candidate-info">
                            <div class="left-section">
                                <img src="{{ url_for('static', filename='img/' + candidate.foto) }}" alt="{{ candidate.nome }}" class="candidate-photo" />
                                <div class="vote-section">
                                    <input type="checkbox" name="profissionais" value="{{ candidate.id }}" id="{{ candidate.id }}" />
                                    <label for="{{ candidate.id }}" class="checkbox-label">Selecionar</label>
                                </div>
                            </div>
                            <div class="candidate-text">
                                <h2 class="candidate-code">{{ candidate.id }}</h2>
                                <h3 class="candidate-name">{{ candidate.nome|upper }}</h3>
                                <p class="candidate-gestor"><strong>Gestor:</strong> {{ candidate.gestor }}</p>
                                <p class="candidate-desc-full"><strong>Justificativa:</strong> {{ candidate.desc }}</p>
                            </div>
                        </div>
                    </div>
                {% endfor %}
                <h2>SELECIONE DOIS LÍDERES PARA DESTAQUE NA TI</h2>
                {% for candidate in candidates if candidate.tipo == 'lider' %}
                    <div class="candidate-card">
                        <div class="candidate-info">
                            <div class="left-section">
                                <img src="{{ url_for('static', filename='img/' + candidate.foto) }}" alt="{{ candidate.nome }}" class="candidate-photo" />
                                <div class="vote-section">
                                    <input type="checkbox" name="lideres" value="{{ candidate.id }}" id="{{ candidate.id }}" />
                                    <label for="{{ candidate.id }}" class="checkbox-label">Selecionar</label>
                                </div>
                            </div>
                            <div class="candidate-text">
                                <h2 class="candidate-code">{{ candidate.id }}</h2>
                                <h3 class="candidate-name">{{ candidate.nome|upper }}</h3>
                                <p class="candidate-gestor"><strong>Gestor:</strong> {{ candidate.gestor }}</p>
                                <p class="candidate-desc-full"><strong>Justificativa:</strong> {{ candidate.desc }}</p>
                            </div>
                        </div>
                    </div>
                {% endfor %}
                <button type="submit" class="btn submit-btn">VOTAR</button>
            </div>
        </form>
        <div id="partial-results"></div>
    </div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
