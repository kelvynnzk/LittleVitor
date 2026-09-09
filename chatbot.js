// Widget do chatbot "Vitinho" — botão flutuante no canto da tela.
// Esse arquivo se injeta sozinho na página (HTML + funcionamento),
// então pra usar em qualquer página do site basta incluir:
//   <script src="chatbot.js"></script>
// (sem precisar copiar HTML nenhum em cada página).

(function () {

    const CHAVE_HISTORICO = 'lv_chatbot_historico';

    // ------------------------------------------------------------------
    // MONTA O HTML DO WIDGET E INSERE NO FINAL DO <body>
    // ------------------------------------------------------------------
    function montarWidget() {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <button id="lv-chatbot-fab" class="lv-chatbot-fab" aria-label="Abrir assistente Vitinho" type="button">
                <span class="lv-chatbot-fab-icon">💬</span>
            </button>

            <div id="lv-chatbot-painel" class="lv-chatbot-painel hidden">
                <div class="lv-chatbot-header">
                    <div>
                        <strong>Vitinho</strong>
                        <span class="lv-chatbot-subtitulo">assistente do LittleVitor</span>
                    </div>
                    <button id="lv-chatbot-fechar" type="button" aria-label="Fechar chat">×</button>
                </div>

                <div id="lv-chatbot-mensagens" class="lv-chatbot-mensagens"></div>

                <form id="lv-chatbot-form" class="lv-chatbot-form">
                    <input type="text" id="lv-chatbot-input" placeholder="Digite sua mensagem..." autocomplete="off">
                    <button type="submit" aria-label="Enviar">➤</button>
                </form>
            </div>
        `;
        document.body.appendChild(wrapper);
    }

    // ------------------------------------------------------------------
    // HISTÓRICO DA CONVERSA (guardado na sessionStorage — continua
    // entre páginas do site, mas some se fechar o navegador)
    // ------------------------------------------------------------------
    function carregarHistorico() {
        try {
            const salvo = sessionStorage.getItem(CHAVE_HISTORICO);
            return salvo ? JSON.parse(salvo) : [];
        } catch (erro) {
            return [];
        }
    }

    function salvarHistorico(historico) {
        try {
            sessionStorage.setItem(CHAVE_HISTORICO, JSON.stringify(historico));
        } catch (erro) {
            // sessionStorage indisponível (modo privado, etc.) — sem problema,
            // a conversa só não sobrevive a uma troca de página.
        }
    }

    // ------------------------------------------------------------------
    // RENDERIZAÇÃO DAS MENSAGENS NA TELA
    // ------------------------------------------------------------------
    function criarBolhaMensagem(role, texto) {
        const bolha = document.createElement('div');
        bolha.className = `lv-chatbot-bolha lv-chatbot-bolha-${role === 'user' ? 'usuario' : 'assistente'}`;
        bolha.textContent = texto;
        return bolha;
    }

    function renderizarHistorico(container, historico) {
        container.innerHTML = '';

        if (historico.length === 0) {
            container.appendChild(criarBolhaMensagem('assistant',
                'Oi! Eu sou o Vitinho 👋 Me conta que tipo de evento você curte (música, gastronomia, arte, esporte...) que eu te indico algo daqui do site. Também posso te ajudar se você quiser organizar seu próprio evento.'
            ));
            return;
        }

        historico.forEach((mensagem) => {
            container.appendChild(criarBolhaMensagem(mensagem.role, mensagem.content));
        });
    }

    function rolarParaFinal(container) {
        container.scrollTop = container.scrollHeight;
    }

    // ------------------------------------------------------------------
    // LIGAÇÃO DOS EVENTOS, DEPOIS QUE O WIDGET JÁ ESTÁ NO DOM
    // ------------------------------------------------------------------
    function ligarEventos() {
        const fab = document.getElementById('lv-chatbot-fab');
        const painel = document.getElementById('lv-chatbot-painel');
        const btnFechar = document.getElementById('lv-chatbot-fechar');
        const form = document.getElementById('lv-chatbot-form');
        const input = document.getElementById('lv-chatbot-input');
        const containerMensagens = document.getElementById('lv-chatbot-mensagens');

        let historico = carregarHistorico();
        renderizarHistorico(containerMensagens, historico);

        fab.addEventListener('click', () => {
            painel.classList.toggle('hidden');
            if (!painel.classList.contains('hidden')) {
                rolarParaFinal(containerMensagens);
                input.focus();
            }
        });

        btnFechar.addEventListener('click', () => {
            painel.classList.add('hidden');
        });

        form.addEventListener('submit', async (evento) => {
            evento.preventDefault();

            const texto = input.value.trim();
            if (!texto) return;

            input.value = '';
            input.disabled = true;

            historico.push({ role: 'user', content: texto });
            containerMensagens.appendChild(criarBolhaMensagem('user', texto));
            rolarParaFinal(containerMensagens);

            const bolhaCarregando = criarBolhaMensagem('assistant', 'digitando...');
            bolhaCarregando.classList.add('lv-chatbot-carregando');
            containerMensagens.appendChild(bolhaCarregando);
            rolarParaFinal(containerMensagens);

            try {
                const resposta = await fetch('/chatbot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensagens: historico })
                });

                const dados = await resposta.json();
                bolhaCarregando.remove();

                if (resposta.ok) {
                    historico.push({ role: 'assistant', content: dados.resposta });
                    containerMensagens.appendChild(criarBolhaMensagem('assistant', dados.resposta));
                    salvarHistorico(historico);
                } else {
                    containerMensagens.appendChild(criarBolhaMensagem('assistant', dados.mensagem || 'Não consegui responder agora.'));
                }
            } catch (erro) {
                console.error('Erro ao falar com o chatbot:', erro);
                bolhaCarregando.remove();
                containerMensagens.appendChild(criarBolhaMensagem('assistant', 'Não foi possível conectar ao servidor. Tente novamente.'));
            }

            rolarParaFinal(containerMensagens);
            input.disabled = false;
            input.focus();
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        montarWidget();
        ligarEventos();
    });
})();
