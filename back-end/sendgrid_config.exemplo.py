# ============================================================
# MODELO de configuração do SendGrid — NÃO é usado diretamente.
# ============================================================
# 1. Copie este arquivo e renomeie a cópia para "sendgrid_config.py"
#    (esse nome já está no .gitignore, então nunca vai parar no Git).
# 2. Crie uma conta grátis em https://sendgrid.com (o plano free
#    manda até 100 e-mails/dia, de graça, pra sempre).
# 3. Verifique um "Single Sender" com o e-mail que o site usa pra
#    mandar mensagem (o mesmo que já está em email_config.py, ex:
#    littlevitor.eventos@gmail.com):
#    Settings -> Sender Authentication -> Verify a Single Sender
#    (chega um e-mail de confirmação nessa caixa — precisa clicar
#    nele antes do envio funcionar).
# 4. Gere uma API Key: Settings -> API Keys -> Create API Key
#    (permissão "Full Access" ou, se preferir mais restrito,
#    "Restricted Access" com "Mail Send" habilitado).
# 5. Cole a chave gerada abaixo. Ela só aparece uma vez na tela do
#    SendGrid — se perder, precisa gerar outra.
#
# NUNCA compartilhe esse arquivo nem cole a chave no chat com a IA.
# ============================================================

SENDGRID_API_KEY = ""   # ex: "SG.abcdefgh...."
