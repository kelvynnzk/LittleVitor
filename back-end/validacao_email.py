import dns.resolver

def dominio_aceita_email(email):
    """
    Confere se o domínio do e-mail (a parte depois do @) tem
    servidores de e-mail configurados de verdade (registros MX no
    DNS) — ou seja, se esse domínio consegue receber e-mail.

    Isso pega a maioria dos e-mails inventados ou com erro de
    digitação (ex: "gmial.com" em vez de "gmail.com", ou um domínio
    que simplesmente não existe). Não garante que a CAIXA específica
    (a parte antes do @) realmente existe — só dá pra confirmar isso
    de verdade mandando um e-mail de confirmação com link e esperando
    a pessoa clicar nele, o que é um passo bem maior.
    """
    if not email or "@" not in email:
        return False

    dominio = email.split("@")[-1].strip()

    if not dominio:
        return False

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        registros = resolver.resolve(dominio, "MX")
        return len(registros) > 0

    except Exception as e:
        print(f"[e-mail] Domínio '{dominio}' não tem servidor de e-mail configurado: {e}")
        return False
