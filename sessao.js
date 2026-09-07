// ------------------------------------------------------------------
// CONTROLE DE SESSÃO ("manter conectado")
// Todas as páginas usam essas três funções pra ler/gravar/apagar o
// usuário logado, em vez de mexer direto no localStorage — assim,
// nenhuma outra página precisa saber ONDE essa informação está
// guardada, só usar essas funções.
//
// Se "manter conectado" foi marcado no login, o usuário vai pro
// localStorage (sobrevive mesmo fechando o navegador e abrindo de
// novo depois). Se não foi marcado, vai pro sessionStorage (existe
// só enquanto a aba/navegador continuar aberto — fechou, desloga).
// ------------------------------------------------------------------

function salvarUsuarioLogado(usuario, manterConectado) {
    const texto = JSON.stringify(usuario);

    if (manterConectado) {
        localStorage.setItem('usuario', texto);
        sessionStorage.removeItem('usuario');
    } else {
        sessionStorage.setItem('usuario', texto);
        localStorage.removeItem('usuario');
    }
}

function obterUsuarioLogado() {
    // Procura nos dois lugares — não importa em qual dos dois o
    // usuário foi guardado, essa função sempre encontra.
    return localStorage.getItem('usuario') || sessionStorage.getItem('usuario');
}

function removerUsuarioLogado() {
    // Remove dos dois, pra garantir que o "Sair" funciona
    // independente de como a pessoa tinha logado.
    localStorage.removeItem('usuario');
    sessionStorage.removeItem('usuario');
}
