# ============================================================
# MODELO de configuração de e-mail — NÃO é usado diretamente.
# ============================================================
# 1. Copie este arquivo e renomeie a cópia para "email_config.py"
#    (esse nome já está no .gitignore, então nunca vai parar no Git).
# 2. Preencha o e-mail remetente abaixo — é o endereço que aparece
#    como "De:" nos e-mails que o site manda (confirmação de
#    cadastro, redefinição de senha, etc.).
#
# Esse mesmo e-mail também precisa ser verificado como "Single
# Sender" no SendGrid (ver sendgrid_config.exemplo.py) — é o
# SendGrid que realmente envia, este arquivo só diz qual endereço
# aparece como remetente.
# ============================================================

EMAIL_REMETENTE = ""   # ex: "seuevento@gmail.com"
