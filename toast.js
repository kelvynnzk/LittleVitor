// Função reutilizável para mostrar mensagens de forma mais elegante
// que o alert() nativo do navegador.
function mostrarToast(mensagem, tipo = 'sucesso') {
    // Cria um novo elemento <div> na memória (ainda não visível na página)
    const toast = document.createElement('div');

    // Define as classes CSS: a base "toast" + o tipo ("sucesso" ou "erro")
    toast.className = `toast ${tipo}`;

    // Define o texto que vai aparecer dentro do toast
    toast.textContent = mensagem;

    // Adiciona o toast de fato na página, dentro do <body>
    document.body.appendChild(toast);

    // Pequeno atraso antes de adicionar a classe "mostrar" —
    // isso é necessário para a animação de transição funcionar
    // (o navegador precisa "perceber" o estado inicial primeiro).
    setTimeout(() => {
        toast.classList.add('mostrar');
    }, 10);

    // Depois de 3 segundos, remove a classe "mostrar" (inicia a
    // animação de saída) e, um pouco depois, remove o elemento
    // da página por completo.
    setTimeout(() => {
        toast.classList.remove('mostrar');
        setTimeout(() => {
            toast.remove();
        }, 300); // espera a transição de saída (0.3s) terminar
    }, 3000);
}

// Versão do toast com botões de "Cancelar"/confirmar, no lugar do
// confirm() nativo do navegador (que abre um popup feio e fora do
// visual do site). Aparece centralizada na tela (com um fundo
// escurecido atrás, pra ficar claro que é uma pergunta importante) e
// não some sozinha — só fecha quando a pessoa clica em um dos dois
// botões. Devolve uma Promise<boolean>: true se confirmou, false se
// cancelou (ou clicou fora, no fundo escurecido).
function mostrarConfirmacao(mensagem, textoConfirmar = 'Confirmar') {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'toast-confirmacao-overlay';

        const toast = document.createElement('div');
        toast.className = 'toast toast-confirmacao';
        toast.innerHTML = `
            <p class="toast-confirmacao-texto">${mensagem}</p>
            <div class="toast-confirmacao-acoes">
                <button type="button" class="toast-btn toast-btn-cancelar">Cancelar</button>
                <button type="button" class="toast-btn toast-btn-confirmar">${textoConfirmar}</button>
            </div>
        `;
        document.body.appendChild(overlay);
        document.body.appendChild(toast);

        setTimeout(() => {
            overlay.classList.add('mostrar');
            toast.classList.add('mostrar');
        }, 10);

        function fechar(resultado) {
            overlay.classList.remove('mostrar');
            toast.classList.remove('mostrar');
            setTimeout(() => {
                overlay.remove();
                toast.remove();
            }, 300);
            resolve(resultado);
        }

        overlay.addEventListener('click', () => fechar(false));
        toast.querySelector('.toast-btn-cancelar').addEventListener('click', () => fechar(false));
        toast.querySelector('.toast-btn-confirmar').addEventListener('click', () => fechar(true));
    });
}