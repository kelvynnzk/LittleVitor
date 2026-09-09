// Monta o botão redondo "Meu perfil" + o menu suspenso (Meu perfil /
// Sair) logo depois do elemento de referência passado. Reaproveitado
// tanto aqui (páginas públicas, via atualizarBotaoEntrar) quanto
// direto em painel.html/pagamento.html (páginas sempre logadas, que
// não passam pelo fluxo de "Entrar" -> vira nome -> vira esse menu).
function criarMenuPerfil(referencia, nome) {
    if (document.getElementById('user-menu-trigger')) {
        return; // já existe — evita duplicar se a função rodar de novo
    }

    // Saudação "Olá, Nome!" ao lado do menu — mesmo texto/estilo que
    // painel.html já usava, agora em todas as páginas.
    if (nome && !document.getElementById('user-menu-saudacao')) {
        const saudacao = document.createElement('span');
        saudacao.id = 'user-menu-saudacao';
        saudacao.className = 'painel-user';
        saudacao.textContent = `Olá, ${nome}!`;
        referencia.insertAdjacentElement('afterend', saudacao);
        referencia = saudacao;
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'user-menu';
    wrapper.innerHTML = `
        <button type="button" class="user-menu-trigger" id="user-menu-trigger">Meu perfil</button>
        <div class="user-menu-dropdown hidden" id="user-menu-dropdown">
            <a href="perfil.html" class="user-menu-item">Meu perfil</a>
            <button type="button" class="user-menu-item user-menu-item-sair" id="user-menu-sair">Sair</button>
        </div>
    `;
    referencia.insertAdjacentElement('afterend', wrapper);

    const trigger = wrapper.querySelector('#user-menu-trigger');
    const dropdown = wrapper.querySelector('#user-menu-dropdown');

    trigger.addEventListener('click', (evento) => {
        evento.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    // Clicar em qualquer outro lugar da página fecha o menu.
    document.addEventListener('click', (evento) => {
        if (!wrapper.contains(evento.target)) {
            dropdown.classList.add('hidden');
        }
    });

    wrapper.querySelector('#user-menu-sair').addEventListener('click', async (evento) => {
        evento.preventDefault();
        dropdown.classList.add('hidden');
        const confirmou = await mostrarConfirmacao('Tem certeza que deseja sair da sua conta?', 'Sair');
        if (confirmou) {
            removerUsuarioLogado();
            window.location.href = 'index.html';
        }
    });
}

// Verifica se tem usuário logado e, se tiver, esconde o link
// "Entrar" (e "Criar conta") e coloca o menu "Meu perfil" no lugar.
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
        linkEntrar.hidden = true;

        // Esconde o link de "Criar conta" (só existe na home) — não
        // faz sentido oferecer criar conta pra quem já está logado.
        const linkCriarConta = document.querySelector('.home-signup');
        if (linkCriarConta) {
            linkCriarConta.hidden = true;
        }

        criarMenuPerfil(linkEntrar, usuario.nome);
    }
}

// Em telas pequenas, a barra de navegação normal (Explorar,
// Categorias, Criar evento, Dashboard) fica escondida — sem isso, não
// haveria como acessar essas páginas pelo celular. Em vez de duplicar
// esses links numa lista separada, essa função move o próprio
// elemento ".home-links" de cada página (já com o link certo marcado
// como atual) pra dentro do menu "Meu perfil", que nessa largura de
// tela passa a se chamar só "Menu" e funciona como o menu principal
// do site inteiro. Em telas grandes, devolve tudo pro lugar de sempre.
function ativarMenuResponsivo() {
    const linksNav = document.querySelector('.home-links');
    const trigger = document.getElementById('user-menu-trigger');
    const dropdown = document.getElementById('user-menu-dropdown');

    if (!linksNav || !trigger || !dropdown) {
        return;
    }

    // Marcador invisível que guarda o lugar original de ".home-links"
    // na barra de navegação, pra devolver ele lá quando a tela voltar
    // a ficar grande.
    const posicaoOriginal = document.createComment('posicao-home-links');
    linksNav.after(posicaoOriginal);

    const telaPequena = window.matchMedia('(max-width: 900px)');

    function aplicar(ehTelaPequena) {
        if (ehTelaPequena) {
            dropdown.insertBefore(linksNav, dropdown.firstChild);
            trigger.textContent = 'Menu';
        } else {
            posicaoOriginal.after(linksNav);
            trigger.textContent = 'Meu perfil';
        }
    }

    aplicar(telaPequena.matches);
    telaPequena.addEventListener('change', (evento) => aplicar(evento.matches));
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
    ativarMenuResponsivo();
    ligarBuscaDoMenu();
});