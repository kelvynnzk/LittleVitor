from test_conect import get_connection


def criar_tipo_ingresso(evento_id, nome, preco, quantidade_total):
    """
    Cadastra um tipo de ingresso (ex: "Pista", "VIP") vinculado a um evento.
    Chamada uma vez para cada linha da seção "Tipos de ingresso" do
    formulário de criar/editar evento.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return False

    cursor = conexao.cursor()

    try:
        query = """
            INSERT INTO tipos_ingresso (evento_id, nome, preco, quantidade_total)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (evento_id, nome, preco, quantidade_total))
        conexao.commit()
        return True

    except Exception as e:
        print(f"Erro ao criar tipo de ingresso: {e}")
        return False

    finally:
        cursor.close()
        conexao.close()


def remover_tipos_ingresso_evento(evento_id):
    """
    Remove todos os tipos de ingresso de um evento. Usado no fluxo de
    edição: em vez de tentar descobrir quais linhas mudaram, adicionaram
    ou sumiram, é mais simples apagar tudo e recriar do zero a partir
    da lista que veio do formulário.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return False

    cursor = conexao.cursor()

    try:
        cursor.execute("DELETE FROM tipos_ingresso WHERE evento_id = %s", (evento_id,))
        conexao.commit()
        return True

    except Exception as e:
        print(f"Erro ao remover tipos de ingresso: {e}")
        return False

    finally:
        cursor.close()
        conexao.close()


def listar_tipos_ingresso(evento_id):
    """
    Lista os tipos de ingresso de um evento, já calculando quantos
    ainda estão disponíveis (quantidade_total - quantidade_vendida).
    Usado tanto na tela de compra (evento.html) quanto na tela de
    edição de evento (pra pré-preencher as linhas de ingresso).
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return []

    cursor = conexao.cursor(dictionary=True)

    try:
        query = """
            SELECT id, evento_id, nome, preco, quantidade_total, quantidade_vendida,
                   (quantidade_total - quantidade_vendida) AS disponivel
            FROM tipos_ingresso
            WHERE evento_id = %s
            ORDER BY id ASC
        """
        cursor.execute(query, (evento_id,))
        tipos = cursor.fetchall()

        # "preco" vem do banco como Decimal — convertendo pra float aqui
        # (em vez de deixar pro jsonify) porque já fizemos essa mesma
        # conversão de tipos "estranhos" em todas as outras funções
        # deste projeto (eventos.py faz o mesmo com horario/data).
        for tipo in tipos:
            tipo["preco"] = float(tipo["preco"])

        return tipos

    except Exception as e:
        print(f"Erro ao listar tipos de ingresso: {e}")
        return []

    finally:
        cursor.close()
        conexao.close()


def buscar_tipo_ingresso_por_id(tipo_ingresso_id):
    """
    Busca um único tipo de ingresso pelo id — usado em registrar_compra()
    para conferir preço e disponibilidade antes de fechar a compra.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        query = """
            SELECT id, evento_id, nome, preco, quantidade_total, quantidade_vendida,
                   (quantidade_total - quantidade_vendida) AS disponivel
            FROM tipos_ingresso
            WHERE id = %s
        """
        cursor.execute(query, (tipo_ingresso_id,))
        tipo = cursor.fetchone()

        if tipo:
            tipo["preco"] = float(tipo["preco"])

        return tipo

    except Exception as e:
        print(f"Erro ao buscar tipo de ingresso: {e}")
        return None

    finally:
        cursor.close()
        conexao.close()


def buscar_compra_por_mp_payment_id(mp_payment_id):
    """
    Busca uma compra já registrada a partir do id do pagamento no
    Mercado Pago. Usada como trava de segurança contra registro
    duplicado: um pagamento Pix é consultado várias vezes (polling)
    até ser aprovado, e não podemos gravar a mesma compra de novo a
    cada consulta depois da aprovação.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM compras WHERE mp_payment_id = %s", (mp_payment_id,))
        return cursor.fetchone()

    except Exception as e:
        print(f"Erro ao buscar compra pelo payment_id do Mercado Pago: {e}")
        return None

    finally:
        cursor.close()
        conexao.close()


def registrar_compra(tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular, mp_payment_id=None, forma_pagamento=None):
    """
    Registra a compra de ingressos: confere se ainda há disponibilidade
    suficiente, grava a compra e soma a quantidade vendida no tipo de
    ingresso correspondente.

    "mp_payment_id" e "forma_pagamento" só vêm preenchidos quando a
    compra passou por um pagamento de verdade no Mercado Pago (ver
    pagamentos.py) — servem de registro e, no caso do Pix, evitam
    gravar a mesma compra duas vezes (ver buscar_compra_por_mp_payment_id).

    Retorna um dicionário {"sucesso": bool, "mensagem": str, "valor_total": float}.

    Observação: a conferência de disponibilidade aqui é "olha e depois
    grava" (não usa transação com lock). Em um sistema com muito mais
    tráfego, com várias pessoas comprando o mesmo ingresso ao mesmo
    tempo, seria preciso um SELECT ... FOR UPDATE dentro de uma
    transação pra evitar vender o mesmo ingresso duas vezes.
    """
    if not tipo_ingresso_id or not usuario_id or not quantidade or quantidade < 1:
        return {"sucesso": False, "mensagem": "Dados da compra incompletos.", "valor_total": 0}

    if mp_payment_id:
        compra_existente = buscar_compra_por_mp_payment_id(mp_payment_id)
        if compra_existente:
            compra_existente["valor_total"] = float(compra_existente["valor_total"])
            return {
                "sucesso": True,
                "mensagem": "Compra realizada com sucesso!",
                "valor_total": compra_existente["valor_total"],
                "compra_id": compra_existente["id"],
                "tipo": buscar_tipo_ingresso_por_id(tipo_ingresso_id),
                "ja_registrada": True
            }

    tipo = buscar_tipo_ingresso_por_id(tipo_ingresso_id)

    if tipo is None:
        return {"sucesso": False, "mensagem": "Tipo de ingresso não encontrado.", "valor_total": 0}

    if tipo["disponivel"] < quantidade:
        return {
            "sucesso": False,
            "mensagem": f"Restam apenas {tipo['disponivel']} ingresso(s) desse tipo.",
            "valor_total": 0
        }

    valor_total = round(tipo["preco"] * quantidade, 2)

    conexao = get_connection()

    if conexao is None:
        return {"sucesso": False, "mensagem": "Não foi possível conectar ao banco.", "valor_total": 0}

    cursor = conexao.cursor()

    try:
        query_compra = """
            INSERT INTO compras (tipo_ingresso_id, usuario_id, quantidade, valor_total, nome_titular, email_titular, mp_payment_id, forma_pagamento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_compra, (tipo_ingresso_id, usuario_id, quantidade, valor_total, nome_titular, email_titular, mp_payment_id, forma_pagamento))

        query_atualizar = """
            UPDATE tipos_ingresso
            SET quantidade_vendida = quantidade_vendida + %s
            WHERE id = %s
        """
        cursor.execute(query_atualizar, (quantidade, tipo_ingresso_id))

        conexao.commit()

        # lastrowid aqui é o id da linha que acabamos de inserir em
        # "compras" — vai virar o código impresso no PDF do ingresso
        # (ex: LV-000042) e é único pra cada compra.
        compra_id = cursor.lastrowid

        return {
            "sucesso": True,
            "mensagem": "Compra realizada com sucesso!",
            "valor_total": valor_total,
            "compra_id": compra_id,
            "tipo": tipo
        }

    except Exception as e:
        print(f"Erro ao registrar compra: {e}")
        return {"sucesso": False, "mensagem": "Não foi possível concluir a compra.", "valor_total": 0}

    finally:
        cursor.close()
        conexao.close()


def estatisticas_organizador(usuario_id):
    """
    Calcula os números reais do painel de quem organiza eventos
    (painel.html): quantos eventos essa pessoa tem, quantos ingressos
    já venderam no total, e quanto isso já rendeu em reais.

    Faz duas consultas separadas em vez de uma só com todos os JOINs
    juntos: se juntássemos "compras" na mesma consulta que soma
    "quantidade_vendida" (que já é um total por tipo de ingresso), cada
    compra multiplicaria essa soma de novo — dando um número inflado.
    Mantendo as duas contagens em consultas separadas, cada uma soma
    exatamente o que deveria.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return {"eventos_ativos": 0, "ingressos_vendidos": 0, "total_arrecadado": 0}

    cursor = conexao.cursor(dictionary=True)

    try:
        # Quantos eventos essa pessoa tem, e quantos ingressos (somando
        # todos os tipos, de todos os eventos dela) já foram vendidos.
        query_eventos = """
            SELECT
                COUNT(DISTINCT eventos.id) AS eventos_ativos,
                COALESCE(SUM(tipos_ingresso.quantidade_vendida), 0) AS ingressos_vendidos
            FROM eventos
            LEFT JOIN tipos_ingresso ON tipos_ingresso.evento_id = eventos.id
            WHERE eventos.usuario_id = %s
        """
        cursor.execute(query_eventos, (usuario_id,))
        linha_eventos = cursor.fetchone()

        # Quanto já foi arrecadado, somando o valor de todas as compras
        # feitas em ingressos dos eventos dessa pessoa.
        query_arrecadado = """
            SELECT COALESCE(SUM(compras.valor_total), 0) AS total_arrecadado
            FROM compras
            JOIN tipos_ingresso ON tipos_ingresso.id = compras.tipo_ingresso_id
            JOIN eventos ON eventos.id = tipos_ingresso.evento_id
            WHERE eventos.usuario_id = %s
        """
        cursor.execute(query_arrecadado, (usuario_id,))
        linha_arrecadado = cursor.fetchone()

        return {
            "eventos_ativos": linha_eventos["eventos_ativos"],
            # SUM() de uma coluna inteira devolve Decimal no MySQL, não
            # int — convertendo aqui pra não devolver um número "estranho"
            # (tipo Decimal) no JSON.
            "ingressos_vendidos": int(linha_eventos["ingressos_vendidos"]),
            "total_arrecadado": float(linha_arrecadado["total_arrecadado"])
        }

    except Exception as e:
        print(f"Erro ao calcular estatísticas do organizador: {e}")
        return {"eventos_ativos": 0, "ingressos_vendidos": 0, "total_arrecadado": 0}

    finally:
        cursor.close()
        conexao.close()


def buscar_evento_destaque():
    """
    Escolhe o evento "em destaque" da página inicial: o que já vendeu
    mais ingressos no total (somando todos os tipos de ingresso dele).
    Eventos sem nenhuma venda entram com 0 e ainda podem ser escolhidos
    se nenhum outro evento tiver vendas — o desempate, nesse caso, é o
    evento criado mais recentemente.

    Retorna um dicionário com os dados do evento + vendidos/disponivel/
    total_ingressos, ou None se não houver nenhum evento cadastrado.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        query = """
            SELECT
                eventos.id, eventos.titulo, eventos.categoria, eventos.data,
                eventos.horario, eventos.local, eventos.cidade,
                COALESCE(SUM(tipos_ingresso.quantidade_vendida), 0) AS vendidos,
                COALESCE(SUM(tipos_ingresso.quantidade_total), 0) AS total_ingressos
            FROM eventos
            LEFT JOIN tipos_ingresso ON tipos_ingresso.evento_id = eventos.id
            GROUP BY eventos.id
            ORDER BY vendidos DESC, eventos.criado_em DESC
            LIMIT 1
        """
        cursor.execute(query)
        evento = cursor.fetchone()

        if evento is None:
            return None

        evento["data"] = str(evento["data"])
        evento["horario"] = str(evento["horario"]) if evento["horario"] else ""

        # Mesma conversão de Decimal -> int que fizemos em
        # estatisticas_organizador(): SUM() devolve Decimal, não int.
        evento["vendidos"] = int(evento["vendidos"])
        evento["total_ingressos"] = int(evento["total_ingressos"])
        evento["disponivel"] = evento["total_ingressos"] - evento["vendidos"]

        return evento

    except Exception as e:
        print(f"Erro ao buscar evento em destaque: {e}")
        return None

    finally:
        cursor.close()
        conexao.close()


def listar_vendas_por_evento(usuario_id):
    """
    Lista, para cada evento desse usuário, quantos ingressos já foram
    vendidos e quantos existem no total (somando todos os tipos de
    ingresso do evento). Usado em painel.html pra mostrar a barra de
    progresso de vendas de cada evento — antes esse número era fixo
    (inventado), igual pra todo mundo.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return []

    cursor = conexao.cursor(dictionary=True)

    try:
        query = """
            SELECT
                eventos.id AS evento_id,
                COALESCE(SUM(tipos_ingresso.quantidade_vendida), 0) AS vendidos,
                COALESCE(SUM(tipos_ingresso.quantidade_total), 0) AS total_ingressos
            FROM eventos
            LEFT JOIN tipos_ingresso ON tipos_ingresso.evento_id = eventos.id
            WHERE eventos.usuario_id = %s
            GROUP BY eventos.id
        """
        cursor.execute(query, (usuario_id,))
        linhas = cursor.fetchall()

        for linha in linhas:
            linha["vendidos"] = int(linha["vendidos"])
            linha["total_ingressos"] = int(linha["total_ingressos"])

        return linhas

    except Exception as e:
        print(f"Erro ao listar vendas por evento: {e}")
        return []

    finally:
        cursor.close()
        conexao.close()


def listar_compras_usuario(usuario_id):
    """
    Lista as compras de um usuário, já trazendo o nome do tipo de
    ingresso e o título do evento (via JOIN), pra facilitar uma futura
    tela de "Meus ingressos".
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return []

    cursor = conexao.cursor(dictionary=True)

    try:
        query = """
            SELECT compras.id, compras.quantidade, compras.valor_total, compras.criado_em,
                   tipos_ingresso.nome AS tipo_ingresso_nome,
                   eventos.id AS evento_id, eventos.titulo AS evento_titulo,
                   eventos.data AS evento_data
            FROM compras
            JOIN tipos_ingresso ON tipos_ingresso.id = compras.tipo_ingresso_id
            JOIN eventos ON eventos.id = tipos_ingresso.evento_id
            WHERE compras.usuario_id = %s
            ORDER BY compras.criado_em DESC
        """
        cursor.execute(query, (usuario_id,))
        compras = cursor.fetchall()

        for compra in compras:
            compra["valor_total"] = float(compra["valor_total"])
            if compra.get("criado_em"):
                compra["criado_em"] = str(compra["criado_em"])
            if compra.get("evento_data"):
                compra["evento_data"] = str(compra["evento_data"])

        return compras

    except Exception as e:
        print(f"Erro ao listar compras: {e}")
        return []

    finally:
        cursor.close()
        conexao.close()
