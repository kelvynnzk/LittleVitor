import os
import psycopg2
from psycopg2 import Error


def get_connection():
    try:
        database_url = os.environ.get("DATABASE_URL")

        if database_url:
            conexao = psycopg2.connect(database_url)
        else:
            conexao = psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", ""),
                dbname=os.environ.get("DB_NAME", "teste")
            )
        return conexao

    except Error as e:
        print(f"Erro ao conectar: {e}")
        return None


if __name__ == "__main__":
    conexao = get_connection()
    if conexao is not None:
        print("Conexão realizada com sucesso!")
        conexao.close()
    else:
        print("Falha ao conectar.")
