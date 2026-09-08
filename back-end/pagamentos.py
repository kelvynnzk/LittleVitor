import mercadopago

from mp_config import MP_ACCESS_TOKEN
from compras import buscar_tipo_ingresso_por_id, registrar_compra
from eventos import buscar_evento_por_id
from ingresso_pdf import gerar_pdf_ingresso
from email_service import enviar_email_confirmacao


# Status de pagamento com cartão que o Mercado Pago devolve quando o
# número do cartão em si é o problema (não existe, formato inválido,
# bandeira não reconhece) — nesses casos mostramos a mensagem "não
# foi possível encontrar este cartão", como pedido. Outros motivos de
# recusa (saldo insuficiente, etc.) mostram uma mensagem mais genérica.
MOTIVOS_CARTAO_NAO_ENCONTRADO = {
    "cc_rejected_bad_filled_card_number",
    "cc_rejected_card_type_not_allowed",
    "cc_rejected_card_disabled",
    "cc_rejected_other_reason",
}


def _sdk():
    """
    Cria o cliente do SDK do Mercado Pago usando o Access Token
    configurado em mp_config.py. Devolve None se ainda não foi
    configurado — quem chamar essa função decide como avisar o
    usuário (ver pagar_com_cartao/pagar_com_pix), do mesmo jeito que
    email_service.py faz quando o e-mail não está configurado.
    """
    if not MP_ACCESS_TOKEN:
        print("[pagamento] MP_ACCESS_TOKEN não configurado em mp_config.py.")
        return None
    return mercadopago.SDK(MP_ACCESS_TOKEN)


def _finalizar_compra_aprovada(tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular, mp_payment_id, forma_pagamento):
    """
    Depois que o Mercado Pago aprova o pagamento (cartão na hora, ou
    Pix quando o pagador confirma no banco dele), registra a compra
    de verdade no banco, gera o PDF do ingresso e manda por e-mail —
    a mesma lógica que a antiga rota /comprar (simulada) já fazia.
    """
    resultado = registrar_compra(
        tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular,
        mp_payment_id=mp_payment_id, forma_pagamento=forma_pagamento
    )

    # "ja_registrada" vem True quando esse payment_id já tinha sido
    # processado antes (ex: o Pix foi consultado de novo depois de já
    # ter sido aprovado uma vez) — não manda o e-mail de novo.
    if resultado["sucesso"] and not resultado.get("ja_registrada"):
        try:
            evento = buscar_evento_por_id(resultado["tipo"]["evento_id"])
            codigo_ingresso = f"LV-{resultado['compra_id']:06d}"

            pdf_bytes = gerar_pdf_ingresso(
                resultado["compra_id"], evento, resultado["tipo"],
                quantidade, nome_titular, resultado["valor_total"]
            )

            enviar_email_confirmacao(
                email_titular, nome_titular, evento, resultado["tipo"],
                quantidade, resultado["valor_total"], pdf_bytes, codigo_ingresso
            )
        except Exception as e:
            print(f"Erro ao gerar/enviar o ingresso por e-mail: {e}")

    return resultado


def pagar_com_cartao(form_data, tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular):
    """
    Recebe o "formData" que o Card Payment Brick (SDK do Mercado
    Pago, no navegador) já monta sozinho — incluindo o token seguro
    do cartão, que representa os dados sem que eles nunca cheguem
    até este servidor. Aqui só completamos com o valor real (nunca
    confiamos em um valor vindo do navegador) e mandamos cobrar.
    """
    sdk = _sdk()
    if sdk is None:
        return {"sucesso": False, "mensagem": "Pagamento por cartão ainda não está configurado neste servidor."}

    if not tipo_ingresso_id or not usuario_id or not quantidade or quantidade < 1:
        return {"sucesso": False, "mensagem": "Dados da compra incompletos."}

    tipo = buscar_tipo_ingresso_por_id(tipo_ingresso_id)
    if tipo is None:
        return {"sucesso": False, "mensagem": "Tipo de ingresso não encontrado."}

    if tipo["disponivel"] < quantidade:
        return {"sucesso": False, "mensagem": f"Restam apenas {tipo['disponivel']} ingresso(s) desse tipo."}

    valor_total = round(tipo["preco"] * quantidade, 2)

    dados_pagamento = {
        "transaction_amount": valor_total,
        "token": form_data.get("token"),
        "description": f"{quantidade}x {tipo['nome']}",
        "installments": int(form_data.get("installments") or 1),
        "payment_method_id": form_data.get("payment_method_id"),
        "issuer_id": form_data.get("issuer_id"),
        "payer": form_data.get("payer"),
    }

    try:
        resposta = sdk.payment().create(dados_pagamento)
        pagamento = resposta["response"]
    except Exception as e:
        print(f"Erro ao processar pagamento com cartão: {e}")
        return {"sucesso": False, "mensagem": "Não foi possível processar o pagamento agora. Tente novamente."}

    status = pagamento.get("status")
    status_detail = pagamento.get("status_detail", "")

    if status == "approved":
        return _finalizar_compra_aprovada(
            tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular,
            mp_payment_id=pagamento.get("id"), forma_pagamento="cartao"
        )

    if status_detail in MOTIVOS_CARTAO_NAO_ENCONTRADO:
        return {"sucesso": False, "mensagem": "Não foi possível encontrar este cartão.", "status_detail": status_detail}

    return {"sucesso": False, "mensagem": "O pagamento não foi aprovado. Verifique os dados do cartão e tente novamente.", "status_detail": status_detail}


def pagar_com_pix(tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular, cpf=None):
    """
    Cria uma cobrança Pix no Mercado Pago e devolve o QR Code (em
    base64, pronto pra virar <img>) e o código "copia e cola". O
    pagamento fica com status "pending" até a pessoa realmente pagar
    no aplicativo do banco dela — ver consultar_status_pix() para o
    passo seguinte.
    """
    sdk = _sdk()
    if sdk is None:
        return {"sucesso": False, "mensagem": "Pagamento por Pix ainda não está configurado neste servidor."}

    if not tipo_ingresso_id or not usuario_id or not quantidade or quantidade < 1:
        return {"sucesso": False, "mensagem": "Dados da compra incompletos."}

    tipo = buscar_tipo_ingresso_por_id(tipo_ingresso_id)
    if tipo is None:
        return {"sucesso": False, "mensagem": "Tipo de ingresso não encontrado."}

    if tipo["disponivel"] < quantidade:
        return {"sucesso": False, "mensagem": f"Restam apenas {tipo['disponivel']} ingresso(s) desse tipo."}

    valor_total = round(tipo["preco"] * quantidade, 2)
    primeiro_nome = (nome_titular or "Comprador").split(" ")[0]

    payer = {"email": email_titular, "first_name": primeiro_nome}
    if cpf:
        payer["identification"] = {"type": "CPF", "number": cpf}

    dados_pagamento = {
        "transaction_amount": valor_total,
        "description": f"{quantidade}x {tipo['nome']}",
        "payment_method_id": "pix",
        "payer": payer,
    }

    try:
        resposta = sdk.payment().create(dados_pagamento)
        pagamento = resposta["response"]
    except Exception as e:
        print(f"Erro ao gerar pagamento Pix: {e}")
        return {"sucesso": False, "mensagem": "Não foi possível gerar o Pix agora. Tente novamente."}

    dados_transacao = (pagamento.get("point_of_interaction") or {}).get("transaction_data") or {}
    qr_code_copiaecola = dados_transacao.get("qr_code")

    if not qr_code_copiaecola:
        print(f"[pagamento] Resposta do Mercado Pago sem QR Code Pix: {pagamento}")
        return {"sucesso": False, "mensagem": "Não foi possível gerar o Pix agora. Tente novamente."}

    return {
        "sucesso": True,
        "payment_id": pagamento.get("id"),
        "qr_code_base64": dados_transacao.get("qr_code_base64"),
        "qr_code": qr_code_copiaecola,
        "status": pagamento.get("status"),
    }


def consultar_status_pix(payment_id, tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular):
    """
    Consulta o status atual de um pagamento Pix no Mercado Pago —
    chamada repetidamente pelo frontend (a cada poucos segundos)
    enquanto a pessoa não confirma o pagamento no banco dela. Assim
    que o status virar "approved" pela primeira vez, finaliza a
    compra de verdade (ver _finalizar_compra_aprovada).
    """
    sdk = _sdk()
    if sdk is None:
        return {"status": "erro", "mensagem": "Pagamento ainda não está configurado neste servidor."}

    try:
        resposta = sdk.payment().get(payment_id)
        pagamento = resposta["response"]
    except Exception as e:
        print(f"Erro ao consultar status do pagamento Pix: {e}")
        return {"status": "erro"}

    status = pagamento.get("status")

    if status == "approved":
        resultado = _finalizar_compra_aprovada(
            tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular,
            mp_payment_id=payment_id, forma_pagamento="pix"
        )
        return {"status": "approved", "resultado": resultado}

    return {"status": status}
