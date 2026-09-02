# LittleVitor

Plataforma de eventos front-end — descoberta de eventos, compra de ingressos e criação de eventos por organizadores.

Projeto construído **exclusivamente** com **HTML5 + CSS3 + JavaScript Vanilla**, sem frameworks, sem bibliotecas externas de UI e sem build step. Basta abrir os arquivos `.html` em um navegador (ou servir com qualquer servidor estático) para rodar.

## Como rodar

Não há instalação nem dependências. Duas opções:

1. **Direto no navegador**: dê duplo clique em `index.html`.
2. **Servidor local** (recomendado, evita restrições de CORS/`file://` em alguns navegadores):
   ```bash
   python3 -m http.server 8080
   # depois acesse http://localhost:8080/index.html
   ```

## Estrutura

```
LittleVitor/
├── index.html          # Home: hero, categorias, busca, filtros, eventos em destaque/próximos/populares
├── login.html           # Autenticação (login simulado)
├── cadastro.html         # Cadastro com indicador de força de senha
├── recuperar-senha.html  # Recuperação de senha (estados de sucesso/erro simulados)
├── evento.html           # Página individual do evento + seleção e compra de ingressos
├── criar-evento.html     # Wizard de criação de evento em 5 etapas, com prévia ao vivo
├── perfil.html           # Perfil do usuário: informações, favoritos, ingressos, configurações
├── dashboard.html        # Dashboard do organizador: métricas e gráficos nativos (SVG/CSS)
├── css/
│   ├── style.css         # Tokens de design (cores, tipografia, espaçamento), reset, utilitários
│   ├── components.css    # Design system: botões, inputs, cards, navbar, modais, toasts, tabs...
│   ├── responsive.css    # Regras de responsividade globais (360/390/768/1024/1440/1920px)
│   ├── auth.css           # Estilos das páginas de autenticação
│   ├── event.css           # Estilos da Home e da página de evento
│   ├── profile.css         # Estilos do wizard "Criar evento" e do Perfil
│   └── dashboard.css       # Estilos do Dashboard
└── assets/               # Reservado para imagens/ícones locais (o projeto usa picsum.photos como placeholder de fotos de eventos)
```

## Decisões de design

- **Paleta**: preto azulado (`#0B0A10`) como base, roxo (`#7C5CFF`) como cor de marca/identidade e verde (`#2FE6A6`) para ações e sucesso.
- **Tipografia**: General Sans (display/títulos) + Inter (corpo de texto), carregadas via `@import` no `style.css`.
- **Motivo visual assinatura**: cartões com "recorte de ingresso" (`.ticket-cut`, bordas tracejadas) reforçando o tema de eventos.
- Sem dados reais: todo conteúdo (eventos, vendas, pedidos) é mockado diretamente nos arquivos `.js` embutidos em cada página.
- **Persistência simulada** via `localStorage`: sessão de usuário (`lv_user`) e favoritos (`lv_favoritos`) — não há backend.

## Convenções de código

- Todo o CSS fica em arquivos `.css` separados (nunca `<style>` inline).
- Todo o JavaScript fica embutido em `<script>` no fim de cada HTML (sem arquivos `.js` externos, por especificação do projeto).
- Todos os comentários de código estão em português do Brasil.
- Nomes de classes, IDs e variáveis em inglês (convenção de mercado), comentários em PT-BR.

## Checklist de qualidade (auditoria realizada)

- [x] Sintaxe de todo o JavaScript validada (`node --check`)
- [x] Nenhum ID duplicado / nenhuma referência quebrada a elementos
- [x] Nenhum link interno quebrado
- [x] Acessibilidade básica: `aria-label` em botões só-ícone, foco visível, `prefers-reduced-motion` respeitado, skip-link
- [x] Responsivo testado em 360/390/768/1024/1440px
- [x] Fluxos testados ponta a ponta: login, cadastro, recuperação de senha, wizard de criação de evento (5 etapas), favoritos, compra de ingresso, dashboard

## Observação sobre as imagens

As fotos de capa dos eventos usam o serviço `picsum.photos` como placeholder. Isso requer conexão com a internet no navegador em que o site for aberto — sem internet, os `<img>` aparecem quebrados (o `alt` continua correto). Para produção, basta trocar as URLs em `imagem:` nos arrays `eventosDB` de cada página pelas imagens reais, ou colocar arquivos locais em `assets/images/`.
