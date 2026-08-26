# Funções prontas para gerar e verificar hash de senha
# Fazem parte da biblioteca Werkzeug, que já instalamos antes.
from werkzeug.security import generate_password_hash, check_password_hash

# Importa a função que criamos no arquivo de conexão.
# Como seu arquivo se chama "test_conect.py" (sem a extensão .py no import),
# a importação fica assim:
from test_conect import get_connection

def cadastro (nome,email,senha):
 """Recebe os dados digitados pelo usuário e salva no banco de dados."""
 # Chama a função que já testamos, tentando abrir uma conexão com o banco.
 conexao = get_connection()

    # Se a conexão falhou (get_connection retornou None),
    # não faz sentido continuar tentando usar essa conexão inexistente.
    # Por isso, paramos a função aqui com "return" (sem valor nenhum).
 if conexao is None:
    print("Não foi possível conectar ao banco.")
    return False
    # O cursor é o "objeto" responsável por executar comandos SQL
    # usando a conexão que acabamos de abrir.
 cursor = conexao.cursor()
     # Transforma a senha digitada em um hash (texto embaralhado e
     # irreversível), como conversamos antes. NUNCA guardamos a
      # senha original no banco.
 senha_hash = generate_password_hash(senha)
 "-------------  PERMITINDO QUE OS DADOS VÃO PARA O BANCO       ---------- ----"
    # try/except aqui também, porque o INSERT pode falhar
    # (ex: se o email já existir, já que é UNIQUE na tabela)
 try:
        # A query SQL que vamos executar.
        # %s são "espaços reservados" que serão substituídos pelos
        # valores reais na próxima linha, de forma segura.
        query = "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)"

        # Executa a query, passando os valores como uma tupla,
        # na MESMA ordem dos %s acima.
        cursor.execute(query, (nome, email, senha_hash))

        # Até aqui, a alteração só aconteceu na conexão atual.
        # commit() é o que realmente GRAVA a mudança no banco de dados.
        conexao.commit()

        print("Usuário cadastrado com sucesso!")
        return True
 
 except Exception as e:
        # Se der erro (ex: email duplicado), mostramos qual foi.
        print(f"Erro ao cadastrar: {e}")
        return False
 finally:
        # finally roda sempre, tenha dado erro ou não.
        # Fechamos cursor e conexão para não deixar nada "pendurado".
        cursor.close()
        conexao.close()

# ============================================================
# BLOCO DE TESTE (temporário, só para verificar se o cadastro funciona)
# ============================================================


#if __name__ == "__main__":
 #cadastro("Teste da Silva", "teste@email.com", "senha123")
 # ============================================================

def login(email,senha):
 """Verifica se existe um usuário com esse email, e se a senhadigitada bate com o hash salvo no banco."""
 conexao = get_connection() #abre uma nova conxão, como feito no cadastro
 if conexao is None:
   print("Não foi possível conectar ao banco") #mesma coisa feita com a conexão do cadastro.
   return None

 # dictionary=True faz o cursor devolver os resultados como um
 # dicionário (ex: {"nome": "...", "email": "..."}), em vez de
 # uma tupla sem nome (ex: ("João", "joao@email.com")).
 # Isso deixa mais fácil acessar cada campo pelo nome depois.
 cursor = conexao.cursor(dictionary=True)

 # Query que busca, na tabela usuarios, a linha onde o email seja igual ao que foi digitado.
 query = "SELECT * FROM usuarios WHERE email = %s"
 #Essa linha é o que de fato manda o comando SQL para o MySQL executar. Até aqui, na linha anterior, você só tinha escrito a query como texto:
 cursor.execute(query, (email,))

 # Executa de fato a busca no banco, substituindo o %s pelo valor
 # de "email". Sem essa linha, a query nunca é enviada ao MySQL,
 # e o fetchone() abaixo não teria nenhum resultado para buscar.
 usuario = cursor.fetchone()

  # Já podemos fechar cursor e conexão aqui, porque não vamos mais fazer nenhuma outra operação no banco dentro dessa função.
 cursor.close()
 conexao.close()

   # Verifica duas coisas ao mesmo tempo, usando "and":
    # 1) se "usuario" não é None (ou seja, achou alguém com esse email)
    # 2) se a senha digitada, quando comparada, bate com o hash salvo
 if usuario and check_password_hash(usuario["senha_hash"], senha):
  print(f"Bem-vindo, {usuario['nome']}!")
  return usuario
    # casi não encontre usuario com essas credenciais digitadas.
 else:
   print("Email ou senha incorretos.")
   return None

#==========bloco de teste temporario=============
'''if __name__ == "__main__":
    # Testando com a senha CERTA (deve dar "Bem-vindo...")
    login("teste@email.com", "senha123")

    # Testando com a senha ERRADA (deve dar "Email ou senha incorretos")
    login("teste@email.com", "senhaerrada")'''
#=======================================================================


