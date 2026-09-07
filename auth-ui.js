// Verifica se tem usuário logado e, se tiver, troca o link/botão
// de "Entrar" pelo nome do usuário, direcionando pro painel.
// Reaproveitado em todas as páginas que têm esse botão visível.
function atualizarBotaoEntrar() {

    const usuarioSalvo = localStorage.getItem('usuario');
    const linkEntrar = document.getElementById('link-entrar');

    // Proteção extra: só executa se a página realmente tiver
    // um elemento com esse id (algumas páginas podem não ter).
    if (!linkEntrar) {
        return;
    }

    if (usuarioSalvo) {
        const usuario = JSON.parse(usuarioSalvo);
        linkEntrar.textContent = usuario.nome;
        linkEntrar.href = 'painel.html';
    }
}

// Espera o HTML inteiro carregar antes de tentar atualizar o botão,
// já que este arquivo é importado no <head>, que roda antes do
// <body> (onde está o elemento que estamos procurando) existir.
document.addEventListener('DOMContentLoaded', atualizarBotaoEntrar);