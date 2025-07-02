document.addEventListener("DOMContentLoaded", function () {
    const votingArea = document.getElementById("voting-area");
    const countdown = document.getElementById("countdown");
    const partialResults = document.getElementById("partial-results");
    let voteForm = document.getElementById("vote-form");
    const deadline = new Date("2025-07-02T18:00:00-03:00").getTime(); // Atualizado para 18:00

    function updateCountdown() {
        const now = new Date().getTime();
        const distance = deadline - now;
        if (distance < 0) {
            countdown.innerHTML = "⛔ Votação Encerrada";
            return;
        }
        const h = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const m = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const s = Math.floor((distance % (1000 * 60)) / 1000);
        countdown.innerHTML = "Tempo disponível para votação: " + `${h}h ${m}min ${s}s`;
    }
    setInterval(updateCountdown, 1000);
    updateCountdown();

    if (!voteForm) {
        console.error("voteForm element not found. Looking for alternatives...");
        voteForm = document.querySelector('form[method="POST"]'); // Fallback to first POST form
        if (!voteForm) {
            console.error("No POST form found on the page.");
            alert("Erro: Formulário de votação não encontrado. Recarregue a página.");
            return;
        } else {
            console.log("Using fallback form:", voteForm);
        }
    }

    voteForm.addEventListener('submit', function (e) {
        e.preventDefault();
        console.log("Form submitted to:", window.location.origin + '/votar'); // Debug log
        // Captura manual dos checkboxes
        const allProfs = document.querySelectorAll('input[name="profissionais"]');
        const allLideres = document.querySelectorAll('input[name="lideres"]');
        const profs = Array.from(allProfs).filter(cb => cb.checked);
        const lideres = Array.from(allLideres).filter(cb => cb.checked);
        console.log("All profs checkboxes:", allProfs);
        console.log("All lideres checkboxes:", allLideres);
        console.log("Selected profs count:", profs.length, "values:", profs.map(cb => cb.value)); // Debug log
        console.log("Selected lideres count:", lideres.length, "values:", lideres.map(cb => cb.value)); // Debug log
        if (profs.length < 2 || lideres.length < 2) {
            alert("Por favor, selecione pelo menos 2 profissionais e 2 líderes. Contagem: Profs=" + profs.length + ", Líderes=" + lideres.length);
            return;
        }
        if (profs.length > 2 || lideres.length > 2) {
            alert("Limite excedido! Você pode selecionar no máximo 2 profissionais e 2 líderes.");
            return;
        }
        // Verificar se os dados estão sendo enviados corretamente
        const formData = new FormData(this);
        const formEntries = Array.from(formData.entries());
        console.log("FormData entries:", formEntries); // Debug log
        if (formEntries.length !== (profs.length + lideres.length)) {
            console.error("Mismatch in form data entries:", formEntries);
            alert("Erro: Dados do formulário não foram capturados corretamente. Recarregue a página.");
            return;
        }
        fetch('/votar', {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'multipart/form-data'
            }
        })
        .then(response => {
            console.log("Fetch response status:", response.status); // Debug log
            console.log("Fetch response headers:", response.headers); // Debug log
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            console.log("Server response:", data); // Debug log
            alert("Votos enviados com sucesso!"); // Visible feedback
            updatePartialResults();
            this.reset();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert("Erro ao enviar votos. Verifique o console para detalhes.");
        });
    });

    function updatePartialResults() {
        fetch('/get_partial_results')
            .then(response => response.json())
            .then(data => {
                let html = '<h3>Resultados Parciais</h3><ul>';
                for (let id in data) {
                    html += `<li>${data[id].nome} - Gestor: ${data[id].gestor} - Votos: ${data[id].votos}</li>`;
                }
                html += '</ul>';
                partialResults.innerHTML = html;
            });
    }

    // Test endpoint call to verify server connectivity
    fetch('/test', { method: 'POST' })
        .then(response => response.text())
        .then(data => console.log("Test endpoint response:", data))
        .catch(error => console.error("Test endpoint error:", error));

    // Função checkLimit movida de votacao.html
    function checkLimit(type, checkbox) {
        const checks = document.querySelectorAll(`input[name="${type}"]:checked`);
        if (checks.length > 2) {
            alert("Limite excedido! Você pode selecionar no máximo 2 profissionais e 2 líderes.");
            checkbox.checked = false;
        }
    }

    // Adicionar evento de mudança aos checkboxes
    document.querySelectorAll('input[name="profissionais"], input[name="lideres"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            checkLimit(this.name, this);
        });
    });

    // Fallback para hammer.min.js sem inline script
    function loadHammerFallback() {
        if (typeof Hammer === 'undefined') {
            const script = document.createElement('script');
            script.src = "{{ url_for('static', filename='js/hammer.min.js') }}";
            document.head.appendChild(script);
        }
    }
    loadHammerFallback();