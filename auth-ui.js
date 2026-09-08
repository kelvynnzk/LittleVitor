// Verifica se tem usuário logado e, se tiver, troca o link/botão
// de "Entrar" pelo nome do usuário, direcionando pro painel.
// Reaproveitado em todas as páginas que têm esse botão visível.
function atualizarBotaoEntrar() {

    const usuarioSalvo = obterUsuarioLogado();
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

        // Esconde o link de "Criar conta" (só existe na home) — não
        // faz sentido oferecer criar conta pra quem já está logado.
        const linkCriarConta = document.querySelector('.home-signup');
        if (linkCriarConta) {
            linkCriarConta.hidden = true;
        }

        // Acrescenta um link "Sair" logo depois do nome, com
        // confirmação antes de encerrar a sessão. Só cria uma vez,
        // mesmo se essa função rodar de novo.
        if (!document.getElementById('link-sair')) {
            const linkSair = document.createElement('a');
            linkSair.id = 'link-sair';
            linkSair.href = '#';
            linkSair.className = linkEntrar.className;
            linkSair.style.marginLeft = '8px';
            linkSair.textContent = 'Sair';
            linkSair.addEventListener('click', async (evento) => {
                evento.preventDefault();
                const confirmou = await mostrarConfirmacao('Tem certeza que deseja sair da sua conta?', 'Sair');
                if (confirmou) {
                    removerUsuarioLogado();
                    window.location.href = 'index.html';
                }
            });
            linkEntrar.insertAdjacentElement('afterend', linkSair);
        }
    }
}

// Liga a busca do menu (o campo com id "nav-search-input") em todas
// as páginas que não têm sua própria grade de eventos pra filtrar —
// pressionar Enter manda direto pra eventos.html já com o termo
// digitado. A home (index.html) NÃO usa esse id: ela filtra os
// cards que já estão na tela, sem sair da página.
function ligarBuscaDoMenu() {
    const campoBusca = document.getElementById('nav-search-input');
    if (!campoBusca) {
        return;
    }

    campoBusca.addEventListener('keydown', (evento) => {
        if (evento.key === 'Enter') {
            evento.preventDefault();
            const termo = campoBusca.value.trim();
            window.location.href = `evento.html?busca=${encodeURIComponent(termo)}`;
        }
    });
}

// Espera o HTML inteiro carregar antes de tentar atualizar o botão,
// já que este arquivo é importado no <head>, que roda antes do
// <body> (onde está o elemento que estamos procurando) existir.
document.addEventListener('DOMContentLoaded', () => {
    atualizarBotaoEntrar();
    ligarBuscaDoMenu();
});