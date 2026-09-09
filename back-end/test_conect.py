#importação da conexão do banco de dados

import os
import mysql.connector

# Importa a classe Error dessa mesma biblioteca, usada para capturar
# erros específicos de conexão.
from mysql.connector import Error

# Importa a "flag" que controla o que cursor.rowcount significa depois
# de um UPDATE. Por padrão, o mysql-connector conta só as linhas que
# TIVERAM algum valor realmente alterado — se você salvar um formulário
# de edição sem mudar nada, rowcount vem 0 mesmo a linha existindo.
# Com FOUND_ROWS, rowcount passa a contar as linhas que bateram no
# WHERE (encontradas), que é o que atualizar_evento()/deletar_evento()
# usam pra checar se o evento existe e pertence a esse usuário.
from mysql.connector.constants import ClientFlag

def get_connection():
    """
    Essa função tenta abrir uma conexão com o banco de dados.
    Toda vez que outra função precisar 'falar' com o MySQL,
    ela vai chamar essa função primeiro para conseguir a conexão.
    """
    try:
        # os.environ.get("NOME", "valor_padrao") lê a variável de
        # ambiente se ela existir (é assim que o Railway — e qualquer
        # hospedagem de verdade — entrega as credenciais do banco,
        # sem precisar escrever senha nenhuma no código) e, se não
        # existir (rodando na sua própria máquina), usa o valor padrão
        # do XAMPP local, exatamente como já era antes.
        conexao = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "teste"),
            port=int(os.environ.get("DB_PORT", "3306")),
            client_flags=[ClientFlag.FOUND_ROWS]
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
