# ============================================================
# MODELO de configuração do Mercado Pago — NÃO é usado diretamente.
# ============================================================
# 1. Copie este arquivo e renomeie a cópia para "mp_config.py"
#    (esse nome já está no .gitignore, então nunca vai parar no Git).
# 2. Crie uma conta gratuita em:
#    https://www.mercadopago.com.br/developers/panel
# 3. No painel, crie uma aplicação e abra a aba "Credenciais de teste"
#    (comece sempre pelas credenciais de TESTE — nenhum dinheiro real
#    é movido nesse modo, e existem números de cartão de teste
#    prontos pra simular aprovação/recusa).
# 4. Copie o "Public Key" e o "Access Token" de teste e cole abaixo.
#
# O Public Key pode ficar exposto no navegador (é assim que o
# Mercado Pago funciona), mas o Access Token é uma chave SECRETA:
# nunca cole ele no chat com a IA, nunca compartilhe esse arquivo e
# nunca o coloque em nenhum HTML/JS do frontend — ele só deve viver
# aqui, no back-end.
# ============================================================

MP_PUBLIC_KEY = ""     # ex: "TEST-1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6"
MP_ACCESS_TOKEN = ""   # ex: "TEST-1234567890123456-010203-abcdef..."
