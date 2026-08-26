# importação da conexão do banco de dados

import os
import mysql.connector

# Importa a classe Error dessa mesma biblioteca, usada para capturar
# erros específicos de conexão.
from mysql.connector import Error


def get_connection():
    """
    Essa função tenta abrir uma conexão com o banco de dados.
    Toda vez que outra função precisar 'falar' com o MySQL,
    ela vai chamar essa função primeiro para conseguir a conexão.
    """
    try:
        conexao = mysql.connector.connect(
            # endereço do banco (localhost só funciona local/XAMPP)
            host=os.environ.get("DB_HOST", "localhost"),
            # usuário do MySQL
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get(
                "DB_PASSWORD", ""),          # senha do MySQL
            database=os.environ.get(
                "DB_NAME", "teste")          # nome do banco
        )
        # Se chegou até aqui sem erro, a conexão deu certo.
        return conexao

    except Error as e:
        # Se algo der errado, capturamos o erro aqui em vez de travar o programa.
        print(f"Erro ao conectar: {e}")
        return None


if __name__ == "__main__":
    conexao = get_connection()
    if conexao is not None and conexao.is_connected():
        print("Conexão realizada com sucesso!")
        conexao.close()
    else:
        print("Falha ao conectar.")
