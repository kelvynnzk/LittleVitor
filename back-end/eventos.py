from test_conect import get_connection

def criar_eventos(titulo, categoria, descricao, data, horario, local, cidade, usuario_id):
    """ Recebe os dados do evento (vindos do formulário) e salva no banco,
    associando o evento ao usuário que o criou.
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
        print("Evento criado com sucesso!")
        return True

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

if __name__ == "__main__":
    eventos = listar_eventos_usuario(17)
    print("Eventos encontrados:", eventos)