# importação da conexão do banco de dados

import os
import psycopg2
from psycopg2 import Error


def get_connection():
    """
    Essa função tenta abrir uma conexão com o banco de dados.
    Toda vez que outra função precisar 'falar' com o Postgres,
    ela vai chamar essa função primeiro para conseguir a conexão.
    """
    try:
        # No Render, a variável DATABASE_URL é criada automaticamente
        # quando você conecta o banco Postgres ao seu Web Service.
        # Local (na sua máquina), você define essa mesma variável
        # manualmente, apontando pro seu Postgres local.
        database_url = os.environ.get("DATABASE_URL")

        if database_url:
            conexao = psycopg2.connect(database_url)
        else:
            # Fallback para desenvolvimento local, caso você não tenha
            # configurado a DATABASE_URL ainda.
            conexao = psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                user=os.environ.get("DB_USER", "postgres"),
                password=os.environ.get("DB_PASSWORD", ""),
                dbname=os.environ.get("DB_NAME", "teste")
            )
