from test_conect import get_connection


def criar_tabela_usuarios():
    conexao = get_connection()

    if conexao is None:
        print("Não foi possível conectar ao banco.")
        return

    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            senha_hash VARCHAR(255) NOT NULL
        )
    """)

    conexao.commit()
    cursor.close()
    conexao.close()

    print("Tabela 'usuarios' criada com sucesso (ou já existia).")


if __name__ == "__main__":
    criar_tabela_usuarios()
