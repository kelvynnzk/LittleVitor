# ============================================================
# MODELO de configuração do login com Google — NÃO é usado diretamente.
# ============================================================
# 1. Copie este arquivo e renomeie a cópia para "google_config.py".
# 2. Acesse https://console.cloud.google.com/apis/credentials
#    (crie um projeto novo se ainda não tiver nenhum).
# 3. Clique em "Criar credenciais" -> "ID do cliente OAuth".
#    - Tipo de aplicativo: "Aplicativo da Web"
#    - Em "Origens JavaScript autorizadas", adicione o endereço onde
#      o site roda (ex: http://127.0.0.1:5500)
# 4. Copie o "ID do cliente" gerado (termina com
#    ".apps.googleusercontent.com") e cole abaixo.
#
# Diferente do Access Token do Mercado Pago, esse "Client ID" NÃO é
# secreto — ele é feito pra ficar público (o navegador precisa dele
# pra mostrar o botão de login). Por isso o mesmo valor também vai
# no arquivo google-client-id.js, na raiz do projeto.
# ============================================================

GOOGLE_CLIENT_ID = ""   # ex: "123456789-abc123def456.apps.googleusercontent.com"
