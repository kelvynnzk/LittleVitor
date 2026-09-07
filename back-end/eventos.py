from test_conect import get_connection

def criar_eventos(titulo, categoria, descricao, data, horario, local, cidade, usuario_id):
    """ Recebe os dados do evento (vindos do formulário) e salva no banco,
    associando o evento ao usuário que o criou.

    Retorna o id do evento recém-criado (um número, portanto "truthy")
    em caso de sucesso, ou False se der errado — quem chamar essa
    função precisa do id pra poder cadastrar os tipos de ingresso
    vinculados a esse evento logo em seguida.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco de dados.")
        return False

    cursor = conexao.cursor()

    try:
        query = """
            INSERT INTO eventos (titulo, categoria, descricao, data, horario, local, cidade, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (titulo, categoria, descricao, data, horario, local, cidade, usuario_id))
        conexao.commit()

        # lastrowid é o id que o MySQL acabou de gerar pro AUTO_INCREMENT
        # dessa linha — é assim que sabemos o id do evento sem precisar
        # fazer um SELECT extra depois do INSERT.
        novo_id = cursor.lastrowid

        print("Evento criado com sucesso!")
        return novo_id

    except Exception as e:
        print(f"Erro ao criar evento: {e}")
        return False

    finally:
        cursor.close()
        conexao.close()


def listar_eventos_usuario(usuario_id):
    """
    Busca no banco todos os eventos criados por um usuário específico.
    """

    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return []

    cursor = conexao.cursor(dictionary=True)

    try:
        query = "SELECT * FROM eventos WHERE usuario_id = %s ORDER BY criado_em DESC"
        cursor.execute(query, (usuario_id,))

        eventos = cursor.fetchall()

        # Converte o campo "horario" de cada evento para texto,
        # porque o MySQL devolve esse tipo de coluna como um objeto
        # "timedelta" do Python, que o jsonify não consegue converter
        # para JSON diretamente.
        for evento in eventos:
            if evento.get("horario"):
                evento["horario"] = str(evento["horario"])

            if evento.get("data"):
                evento["data"] = str(evento["data"])

            if evento.get("criado_em"):
                evento["criado_em"] = str(evento["criado_em"])

        return eventos

       

    except Exception as e:
        print(f"Erro ao buscar eventos: {e}")
        return []

    finally:
        cursor.close()
        conexao.close()

def listar_todos_eventos():
    """
    Busca no banco TODOS os eventos cadastrados, de todos os
    usuários — usado para exibir a agenda pública no index.html.
    """

    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return []

    cursor = conexao.cursor(dictionary=True)

    try:
        # Repare que aqui NÃO tem "WHERE usuario_id = %s" — buscamos
        # todos os eventos, sem filtrar por quem criou.
        # Ordenamos pela data do EVENTO (não da criação), do mais
        # próximo pro mais distante, para mostrar primeiro o que
        # vai acontecer em breve.
        query = "SELECT * FROM eventos ORDER BY data ASC"
        cursor.execute(query)

        eventos = cursor.fetchall()

        # Mesma conversão de tipos que já fizemos antes, necessária
        # para o jsonify conseguir devolver esses dados como JSON.
        for evento in eventos:
            if evento.get("horario"):
                evento["horario"] = str(evento["horario"])

            if evento.get("data"):
                evento["data"] = str(evento["data"])

            if evento.get("criado_em"):
                evento["criado_em"] = str(evento["criado_em"])

        return eventos

    except Exception as e:
        print(f"Erro ao buscar eventos: {e}")
        return []

    finally:
        cursor.close()
        conexao.close()


def listar_cidades_com_eventos():
    """
    Lista as cidades que têm pelo menos um evento cadastrado, com a
    contagem real de eventos em cada uma — usado na seção "Explore
    por cidade" do index.html, que antes mostrava cidades e números
    fixos (inventados), sem nenhuma relação com os eventos reais.
    """
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return []

    cursor = conexao.cursor(dictionary=True)

    try:
        query = """
            SELECT cidade, COUNT(*) AS total
            FROM eventos
            WHERE cidade IS NOT NULL AND cidade != ''
            GROUP BY cidade
            ORDER BY total DESC
        """
        cursor.execute(query)
        cidades = cursor.fetchall()

        for cidade in cidades:
            cidade["total"] = int(cidade["total"])

        return cidades

    except Exception as e:
        print(f"Erro ao listar cidades com eventos: {e}")
        return []

    finally:
        cursor.close()
        conexao.close()

def buscar_evento_por_id(evento_id):
    """
    Busca um único evento específico pelo seu id.
    Usado para carregar os dados na tela de edição.
    """

    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return None

    cursor = conexao.cursor(dictionary=True)

    try:
        query = "SELECT * FROM eventos WHERE id = %s"
        cursor.execute(query, (evento_id,))

        evento = cursor.fetchone()

        if evento:
            if evento.get("horario"):
                evento["horario"] = str(evento["horario"])
            if evento.get("data"):
                evento["data"] = str(evento["data"])
            if evento.get("criado_em"):
                evento["criado_em"] = str(evento["criado_em"])

        return evento

    except Exception as e:
        print(f"Erro ao buscar evento: {e}")
        return None

    finally:
        cursor.close()
        conexao.close()


def atualizar_evento(evento_id, titulo, categoria, descricao, data, horario, local, cidade, usuario_id):
    """
    Atualiza os dados de um evento já existente.
    O "usuario_id" entra também no WHERE, não só o "evento_id" —
    isso garante que um usuário só consiga editar eventos que ele
    mesmo criou, mesmo que tente forjar o id de um evento de outra pessoa.
    """

    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return False

    cursor = conexao.cursor()

    try:
        query = """
            UPDATE eventos
            SET titulo = %s, categoria = %s, descricao = %s, data = %s,
                horario = %s, local = %s, cidade = %s
            WHERE id = %s AND usuario_id = %s
        """
        cursor.execute(query, (titulo, categoria, descricao, data, horario, local, cidade, evento_id, usuario_id))
        conexao.commit()

        # rowcount é 0 quando o id não existe ou não pertence a esse usuário.
        if cursor.rowcount == 0:
            print("Nenhum evento encontrado para atualizar (id inválido ou não pertence a esse usuário).")
            return False

        print("Evento atualizado com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao atualizar evento: {e}")
        return False

    finally:
        cursor.close()
        conexao.close()


def deletar_evento(evento_id, usuario_id):
    """
    Remove um evento do banco. Assim como em atualizar_evento, o
    "usuario_id" entra no WHERE para impedir que um usuário exclua
    eventos que não são dele.
    """

    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return False

    cursor = conexao.cursor()

    try:
        query = "DELETE FROM eventos WHERE id = %s AND usuario_id = %s"
        cursor.execute(query, (evento_id, usuario_id))
        conexao.commit()

        if cursor.rowcount == 0:
            print("Nenhum evento encontrado para excluir (id inválido ou não pertence a esse usuário).")
            return False

        print("Evento excluído com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao excluir evento: {e}")
        return False

    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    eventos = listar_eventos_usuario(17)
    print("Eventos encontrados:", eventos)








    