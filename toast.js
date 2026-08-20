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