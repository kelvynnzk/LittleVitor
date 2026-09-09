import smtplib
from email.message import EmailMessage

from email_config import EMAIL_REMETENTE, SENHA_APP

# Endereço base de onde o site é servido no seu navegador (VS Code
# Live Server) — usado pra montar o link "Ver no painel" nos e-mails.
# Se um dia você passar a abrir o site de outro jeito (outra porta,
# um domínio de verdade, etc.), só precisa trocar essa linha.
URL_BASE_SITE = "http://127.0.0.1:5501"


def _envolver_html(subtitulo, conteudo_html):
    """
    Monta o "cartão" escuro que envolve o conteúdo de todos os
    e-mails do site (mesmo cabeçalho "LittleVitor.com" + subtítulo),
    pra manter os três e-mails (confirmação de compra, boas-vindas,
    evento criado) com a cara igual.
    """
    return f"""\
<html>
  <body style="font-family: Arial, sans-serif; background:#0e0c14; padding:24px; color:#f0eef5;">
    <div style="max-width:480px; margin:0 auto; background:#17141f; border:1px solid #2c2740; border-radius:12px; padding:28px;">
      <h1 style="color:#a78bfa; font-size:20px; margin:0 0 4px;">LittleVitor.com</h1>
      <p style="color:#9c96ad; margin:0 0 20px;">{subtitulo}</p>
      {conteudo_html}
    </div>
  </body>
</html>
"""


def _enviar(mensagem, destinatario, rotulo):
    """
    Faz a parte repetida de todo envio: confere se a conta remetente
    está configurada e, se estiver, manda o e-mail de verdade pelo
    Gmail. Usada pelas três funções de e-mail do site, pra não
    repetir esse bloco em cada uma.
    """
    if not EMAIL_REMETENTE or not SENHA_APP:
        print(
            f"[e-mail] EMAIL_REMETENTE/SENHA_APP não configurados em "
            f"email_config.py — pulei o envio do e-mail de {rotulo}."
        )
        return False

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, SENHA_APP)
            servidor.send_message(mensagem)

        print(f"[e-mail] {rotulo.capitalize()} enviado(a) para {destinatario}.")
        return True

    except Exception as e:
        # Um problema no envio do e-mail não deve derrubar a ação que
        # já aconteceu (cadastro, criação de evento, compra) — ela já
        # foi concluída antes desta função ser chamada.
        print(f"[e-mail] Erro ao enviar {rotulo}: {e}")
        return False


def enviar_email_boas_vindas(destinatario, nome, token):
    """
    Manda o e-mail de confirmação de cadastro — a conta já foi
    criada no banco, mas fica "pendente" até a pessoa clicar no link
    deste e-mail. Isso prova que o endereço realmente existe e que
    quem cadastrou tem acesso a essa caixa de entrada.
    """
    link_confirmacao = f"{URL_BASE_SITE}/confirmar-email.html?token={token}"

    mensagem = EmailMessage()
    mensagem["Subject"] = "Confirme seu e-mail — LittleVitor.com"
    mensagem["From"] = EMAIL_REMETENTE or "littlevitor@exemplo.com"
    mensagem["To"] = destinatario

    mensagem.set_content(
        f"Olá, {nome}!\n\n"
        f"Falta só um passo pra sua conta no LittleVitor.com ficar pronta: "
        f"confirme seu e-mail clicando no link abaixo.\n\n"
        f"{link_confirmacao}\n\n"
        f"Se você não criou essa conta, pode ignorar este e-mail.\n\n"
        f"LittleVitor.com"
    )

    conteudo = f"""\
      <h2 style="font-size:18px; margin:0 0 12px; color:#f0eef5;">Olá, {nome}!</h2>
      <p style="color:#c9c4d6; font-size:14px; line-height:1.6; margin:0 0 20px;">
        Falta só um passo pra sua conta ficar pronta: confirme que este
        e-mail é seu, clicando no botão abaixo. Depois disso você já
        pode entrar e usar o LittleVitor.com normalmente.
      </p>
      <a href="{link_confirmacao}"
         style="display:inline-block; background:#22c55e; color:#05130a; font-weight:bold;
                text-decoration:none; padding:12px 22px; border-radius:8px; font-size:14px;">
        Confirmar meu e-mail
      </a>
      <p style="color:#726c82; font-size:12px; margin-top:28px;">
        Se você não criou essa conta, pode ignorar este e-mail — ninguém
        consegue entrar sem confirmar.
      </p>
    """
    mensagem.add_alternative(_envolver_html("Confirme sua conta", conteudo), subtype="html")

    return _enviar(mensagem, destinatario, "confirmação de cadastro")


def enviar_email_redefinicao_senha(destinatario, nome, token):
    """
    Manda o e-mail de redefinição de senha, com um link que expira em
    30 minutos — depois disso a pessoa precisa pedir um novo na tela
    "Esqueci minha senha".
    """
    link_redefinicao = f"{URL_BASE_SITE}/redefinir-senha.html?token={token}"

    mensagem = EmailMessage()
    mensagem["Subject"] = "Redefinir sua senha — LittleVitor.com"
    mensagem["From"] = EMAIL_REMETENTE or "littlevitor@exemplo.com"
    mensagem["To"] = destinatario

    mensagem.set_content(
        f"Olá, {nome}!\n\n"
        f"Recebemos um pedido para redefinir a senha da sua conta. "
        f"Clique no link abaixo para criar uma nova senha (ele expira em 30 minutos).\n\n"
        f"{link_redefinicao}\n\n"
        f"Se você não pediu isso, pode ignorar este e-mail — sua senha continua a mesma.\n\n"
        f"LittleVitor.com"
    )

    conteudo = f"""\
      <h2 style="font-size:18px; margin:0 0 12px; color:#f0eef5;">Olá, {nome}!</h2>
      <p style="color:#c9c4d6; font-size:14px; line-height:1.6; margin:0 0 20px;">
        Recebemos um pedido para redefinir a senha da sua conta. Clique
        no botão abaixo para criar uma nova senha. Esse link expira em
        <strong>30 minutos</strong>.
      </p>
      <a href="{link_redefinicao}"
         style="display:inline-block; background:#8b5cf6; color:#fff; font-weight:bold;
                text-decoration:none; padding:12px 22px; border-radius:8px; font-size:14px;">
        Criar nova senha
      </a>
      <p style="color:#726c82; font-size:12px; margin-top:28px;">
        Se você não pediu essa redefinição, pode ignorar este e-mail —
        sua senha continua a mesma.
      </p>
    """
    mensagem.add_alternative(_envolver_html("Redefinição de senha", conteudo), subtype="html")

    return _enviar(mensagem, destinatario, "redefinição de senha")


def enviar_email_evento_criado(destinatario, nome_organizador, evento):
    """
    Manda um e-mail pra quem organizou o evento, assim que ele é
    publicado — com todos os dados do evento e um link direto pro
    painel, pra acompanhar vendas e editar depois.
    """
    link_painel = f"{URL_BASE_SITE}/painel.html"

    mensagem = EmailMessage()
    mensagem["Subject"] = f"Seu evento \"{evento['titulo']}\" foi publicado!"
    mensagem["From"] = EMAIL_REMETENTE or "littlevitor@exemplo.com"
    mensagem["To"] = destinatario

    mensagem.set_content(
        f"Seu evento foi publicado!\n\n"
        f"Título: {evento['titulo']}\n"
        f"Categoria: {evento['categoria']}\n"
        f"Descrição: {evento.get('descricao') or '(sem descrição)'}\n"
        f"Quando: {evento['data']} - {evento['horario']}\n"
        f"Onde: {evento['local']}, {evento['cidade']}\n\n"
        f"Veja e gerencie no painel: {link_painel}\n\n"
        f"LittleVitor.com"
    )

    conteudo = f"""\
      <h2 style="font-size:18px; margin:0 0 12px; color:#f0eef5;">{evento['titulo']}</h2>
      <p style="color:#c9c4d6; font-size:14px; margin:0 0 18px;">
        Olá, {nome_organizador}! Seu evento já está publicado e visível na agenda pública.
      </p>

      <table style="width:100%; border-collapse:collapse; font-size:14px;">
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Categoria</td>
          <td style="padding:6px 0; text-align:right;">{evento['categoria']}</td>
        </tr>
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Quando</td>
          <td style="padding:6px 0; text-align:right;">{evento['data']} · {evento['horario']}</td>
        </tr>
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Onde</td>
          <td style="padding:6px 0; text-align:right;">{evento['local']}, {evento['cidade']}</td>
        </tr>
      </table>

      <p style="color:#c9c4d6; font-size:14px; line-height:1.6; margin:16px 0 20px;">
        {evento.get('descricao') or '(sem descrição)'}
      </p>

      <a href="{link_painel}"
         style="display:inline-block; background:#8b5cf6; color:#fff; font-weight:bold;
                text-decoration:none; padding:12px 22px; border-radius:8px; font-size:14px;">
        Ver no painel
      </a>

      <p style="color:#726c82; font-size:12px; margin-top:28px;">
        Você recebeu este e-mail porque publicou este evento no LittleVitor.com.
      </p>
    """
    mensagem.add_alternative(_envolver_html("Evento publicado!", conteudo), subtype="html")

    return _enviar(mensagem, destinatario, "evento criado")


def enviar_email_confirmacao(destinatario, nome_titular, evento, tipo_ingresso, quantidade, valor_total, pdf_bytes, codigo_ingresso):
    """
    Manda o e-mail de confirmação de compra: as informações do
    ingresso já aparecem no corpo do e-mail (em HTML), e o mesmo
    ingresso em formato de documento vai anexado como PDF.

    Se "email_config.py" ainda não tiver sido preenchido (conta/senha
    de app vazias), não tenta enviar de verdade — só avisa no console.
    Isso permite testar o resto do fluxo de compra sem precisar
    configurar e-mail antes.
    """
    valor_formatado = f"R$ {valor_total:.2f}".replace(".", ",")

    mensagem = EmailMessage()
    mensagem["Subject"] = f"Seu ingresso para {evento['titulo']} — LittleVitor.com"
    mensagem["From"] = EMAIL_REMETENTE or "littlevitor@exemplo.com"
    mensagem["To"] = destinatario

    # Versão em texto simples, usada por clientes de e-mail que não
    # conseguem mostrar HTML.
    mensagem.set_content(
        f"Compra confirmada!\n\n"
        f"Evento: {evento['titulo']}\n"
        f"Quando: {evento['data']} - {evento['horario']}\n"
        f"Onde: {evento['local']}, {evento['cidade']}\n"
        f"Titular: {nome_titular}\n"
        f"Tipo de ingresso: {tipo_ingresso['nome']}\n"
        f"Quantidade: {quantidade}\n"
        f"Valor pago: {valor_formatado}\n"
        f"Código do ingresso: {codigo_ingresso}\n\n"
        f"Seu ingresso também está em anexo, em PDF.\n"
        f"LittleVitor.com"
    )

    # Versão em HTML, com as mesmas informações do ingresso — igual
    # foi pedido, os dados aparecem tanto no corpo do e-mail quanto
    # no PDF anexado, não só num ou só no outro.
    conteudo = f"""\
      <h2 style="font-size:18px; margin:0 0 12px; color:#f0eef5;">{evento['titulo']}</h2>

      <table style="width:100%; border-collapse:collapse; font-size:14px;">
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Quando</td>
          <td style="padding:6px 0; text-align:right;">{evento['data']} · {evento['horario']}</td>
        </tr>
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Onde</td>
          <td style="padding:6px 0; text-align:right;">{evento['local']}, {evento['cidade']}</td>
        </tr>
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Titular</td>
          <td style="padding:6px 0; text-align:right;">{nome_titular}</td>
        </tr>
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Tipo de ingresso</td>
          <td style="padding:6px 0; text-align:right;">{tipo_ingresso['nome']}</td>
        </tr>
        <tr>
          <td style="padding:6px 0; color:#9c96ad;">Quantidade</td>
          <td style="padding:6px 0; text-align:right;">{quantidade}</td>
        </tr>
        <tr>
          <td style="padding:10px 0 0; color:#9c96ad; border-top:1px solid #2c2740;">Valor pago</td>
          <td style="padding:10px 0 0; text-align:right; border-top:1px solid #2c2740; font-weight:bold; font-size:16px;">{valor_formatado}</td>
        </tr>
      </table>

      <p style="margin:20px 0 0; font-family: monospace; color:#a78bfa; font-size:15px; font-weight:bold;">
        {codigo_ingresso}
      </p>

      <p style="color:#726c82; font-size:12px; margin-top:24px;">
        Seu ingresso também está em anexo, em PDF — apresente na entrada do evento.
        Compra simulada, feita só para fins de estudo/teste.
      </p>
    """
    mensagem.add_alternative(_envolver_html("Compra confirmada!", conteudo), subtype="html")

    mensagem.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=f"ingresso-{codigo_ingresso}.pdf"
    )

    return _enviar(mensagem, destinatario, "confirmação de compra")
