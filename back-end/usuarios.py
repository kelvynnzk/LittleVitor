# Funções prontas para gerar e verificar hash de senha
# Fazem parte da biblioteca Werkzeug, que já instalamos antes.
from werkzeug.security import generate_password_hash, check_password_hash

# "secrets" é uma biblioteca do próprio Python pra gerar valores
# aleatórios seguros o bastante pra usar em senhas/tokens (diferente
# do módulo "random", que não é seguro pra esse tipo de coisa).
import secrets

# Importa a função que criamos no arquivo de conexão.
# Como seu arquivo se chama "test_conect.py" (sem a extensão .py no import),
# a importação fica assim:
from test_conect import get_connection

def cadastro (nome,email,senha):
 """
 Recebe os dados digitados pelo usuário e salva no banco de dados,
 já como uma conta "pendente" (email_verificado = 0), com um token
 aleatório de confirmação.

 Devolve o token gerado (uma string, portanto "truthy") se salvou
 com sucesso, ou False se deu errado — quem chamar essa função
 precisa desse token pra colocar no link do e-mail de confirmação.
 """
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

 # Gera um token aleatório e praticamente impossível de adivinhar
 # (43 caracteres) — é ele que vai no link do e-mail de confirmação,
 # provando que quem clicou tem acesso de verdade a essa caixa de entrada.
 token = secrets.token_urlsafe(32)

 "-------------  PERMITINDO QUE OS DADOS VÃO PARA O BANCO       ---------- ----"
    # try/except aqui também, porque o INSERT pode falhar
    # (ex: se o email já existir, já que é UNIQUE na tabela)
 try:
        # A query SQL que vamos executar.
        # %s são "espaços reservados" que serão substituídos pelos
        # valores reais na próxima linha, de forma segura.
        query = """
            INSERT INTO usuarios (nome, email, senha_hash, email_verificado, token_verificacao)
            VALUES (%s, %s, %s, 0, %s)
        """

        # Executa a query, passando os valores como uma tupla,
        # na MESMA ordem dos %s acima.
        cursor.execute(query, (nome, email, senha_hash, token))

        # Até aqui, a alteração só aconteceu na conexão atual.
        # commit() é o que realmente GRAVA a mudança no banco de dados.
        conexao.commit()

        print("Usuário cadastrado com sucesso! Aguardando confirmação do e-mail.")
        return token

 except Exception as e:
        # Se der erro (ex: email duplicado), mostramos qual foi.
        print(f"Erro ao cadastrar: {e}")
        return False
 finally:
        # finally roda sempre, tenha dado erro ou não.
        # Fechamos cursor e conexão para não deixar nada "pendurado".
        cursor.close()
        conexao.close()


def confirmar_email(token):
 """
 Confirma a conta associada a esse token — chamada quando a pessoa
 clica no link do e-mail de confirmação.

 Se o token existir e ainda não tiver sido usado, marca a conta como
 verificada e apaga o token (pra não poder ser reaproveitado), e
 devolve o usuário. Se o token não existir, devolve None.
 """
 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return None

 cursor = conexao.cursor(dictionary=True)

 try:
   # Busca alguém com esse token que AINDA não confirmou o e-mail —
   # um token só serve pra confirmar uma vez.
   query_busca = "SELECT id, nome, email FROM usuarios WHERE token_verificacao = %s AND email_verificado = 0"
   cursor.execute(query_busca, (token,))
   usuario = cursor.fetchone()

   if usuario is None:
     return None

   query_atualiza = "UPDATE usuarios SET email_verificado = 1, token_verificacao = NULL WHERE id = %s"
   cursor.execute(query_atualiza, (usuario["id"],))
   conexao.commit()

   print(f"E-mail confirmado para {usuario['email']}.")
   return usuario

 except Exception as e:
   print(f"Erro ao confirmar e-mail: {e}")
   return None

 finally:
   cursor.close()
   conexao.close()

def buscar_usuario_por_id(usuario_id):
 """
 Busca nome e e-mail de um usuário pelo id — usada quando precisamos
 mandar um e-mail pra ele (ex: avisando que o evento que ele criou
 foi publicado), mas só temos o usuario_id à mão, não o e-mail.
 Não devolve o hash da senha, só o necessário.
 """
 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return None

 cursor = conexao.cursor(dictionary=True)
 query = "SELECT id, nome, email FROM usuarios WHERE id = %s"
 cursor.execute(query, (usuario_id,))
 usuario = cursor.fetchone()
 cursor.close()
 conexao.close()

 return usuario


def buscar_perfil_usuario(usuario_id):
 """
 Busca os dados completos de perfil de um usuário (nome, e-mail,
 telefone, cidade e desde quando a conta existe) — usada pela tela
 "Meu perfil", pra preencher o formulário com os dados reais salvos
 no banco, em vez de valores fixos/inventados.
 """
 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return None

 cursor = conexao.cursor(dictionary=True)
 query = "SELECT id, nome, email, telefone, cidade, criado_em FROM usuarios WHERE id = %s"
 cursor.execute(query, (usuario_id,))
 usuario = cursor.fetchone()
 cursor.close()
 conexao.close()

 if usuario and usuario.get("criado_em"):
   usuario["criado_em"] = str(usuario["criado_em"])

 return usuario


def atualizar_perfil(usuario_id, nome, email, telefone, cidade):
 """
 Atualiza os dados de perfil de um usuário — chamada quando a
 pessoa clica em "Salvar alterações" na tela "Meu perfil".
 Devolve True se atualizou, False se deu algum problema (ex: e-mail
 já usado por outra conta, já que a coluna é UNIQUE).
 """
 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return False

 cursor = conexao.cursor()

 try:
   query = """
     UPDATE usuarios
     SET nome = %s, email = %s, telefone = %s, cidade = %s
     WHERE id = %s
   """
   cursor.execute(query, (nome, email, telefone, cidade, usuario_id))
   conexao.commit()
   return True

 except Exception as e:
   print(f"Erro ao atualizar perfil: {e}")
   return False

 finally:
   cursor.close()
   conexao.close()

# ============================================================
# BLOCO DE TESTE (temporário, só para verificar se o cadastro funciona)
# ============================================================


#if __name__ == "__main__":
 #cadastro("Teste da Silva", "teste@email.com", "senha123")
 # ============================================================

def login(email,senha):
 """
 Verifica se existe um usuário com esse email, e se a senha digitada
 bate com o hash salvo no banco.

 Em vez de só devolver o usuário ou None, devolve um dicionário
 {"sucesso": bool, "motivo": str|None, "usuario": dict|None} — o
 "motivo" diz exatamente o que deu errado ("email_nao_encontrado",
 "senha_incorreta" ou "erro_servidor"), pra quem chamar essa função
 conseguir mostrar uma mensagem de erro específica pra cada caso, em
 vez de um "e-mail ou senha incorretos" genérico pros dois.
 """
 conexao = get_connection() #abre uma nova conxão, como feito no cadastro
 if conexao is None:
   print("Não foi possível conectar ao banco") #mesma coisa feita com a conexão do cadastro.
   return {"sucesso": False, "motivo": "erro_servidor", "usuario": None}

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

 # Primeiro caso: não existe ninguém cadastrado com esse e-mail.
 if usuario is None:
   print("Nenhum usuário encontrado com esse e-mail.")
   return {"sucesso": False, "motivo": "email_nao_encontrado", "usuario": None}

 # Segundo caso: o e-mail existe, mas a senha digitada não bate com
 # o hash salvo.
 if not check_password_hash(usuario["senha_hash"], senha):
   print("Senha incorreta.")
   return {"sucesso": False, "motivo": "senha_incorreta", "usuario": None}

 # Terceiro caso: e-mail e senha corretos, mas a conta ainda não foi
 # confirmada (a pessoa nunca clicou no link do e-mail de cadastro).
 if not usuario["email_verificado"]:
   print("E-mail ainda não confirmado.")
   return {"sucesso": False, "motivo": "email_nao_verificado", "usuario": None}

 # Deu tudo certo — mas antes de devolver o usuário, tiramos o hash
 # da senha e os tokens internos (verificação de e-mail, redefinição
 # de senha) do dicionário. O front-end não precisa (e não deveria)
 # receber isso: ele só vai guardar esse dicionário no localStorage,
 # e não faz sentido guardar segredos internos lá.
 print(f"Bem-vindo, {usuario['nome']}!")
 campos_internos = {"senha_hash", "token_verificacao", "token_redefinicao_senha", "token_redefinicao_expira"}
 usuario_sem_senha = {chave: valor for chave, valor in usuario.items() if chave not in campos_internos}
 return {"sucesso": True, "motivo": None, "usuario": usuario_sem_senha}

def login_com_google(email, nome):
 """
 Login (ou cadastro automático) usando uma conta do Google já
 verificada pelo próprio Google — por isso não passa pelo fluxo de
 "token de confirmação por e-mail" que o cadastro normal usa: o
 Google já provou que esse e-mail é de verdade.

 Se já existe uma conta com esse e-mail, entra nela (e marca como
 verificada, caso ainda não estivesse — por exemplo, se a pessoa
 tinha cadastrado com senha antes e nunca confirmou o e-mail).
 Se não existe, cria uma conta nova na hora, já verificada.

 Devolve o mesmo formato de usuário que login() devolve (sem o hash
 da senha).
 """
 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return None

 cursor = conexao.cursor(dictionary=True)

 try:
   cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
   usuario = cursor.fetchone()

   if usuario is None:
     # Conta nova: como quem faz login é sempre o Google (nunca com
     # senha), a senha salva é só um valor aleatório que ninguém
     # sabe — a coluna exige um hash, mas ele nunca será usado.
     senha_aleatoria_hash = generate_password_hash(secrets.token_urlsafe(24))
     cursor.execute(
       "INSERT INTO usuarios (nome, email, senha_hash, email_verificado) VALUES (%s, %s, %s, 1)",
       (nome, email, senha_aleatoria_hash)
     )
     conexao.commit()
     usuario_id = cursor.lastrowid
     print(f"Conta criada automaticamente via Google para {email}.")

   else:
     usuario_id = usuario["id"]
     if not usuario["email_verificado"]:
       cursor.execute("UPDATE usuarios SET email_verificado = 1 WHERE id = %s", (usuario_id,))
       conexao.commit()
     print(f"Login via Google: bem-vindo de volta, {usuario['nome']}!")

   cursor.execute("SELECT id, nome, email, email_verificado, criado_em FROM usuarios WHERE id = %s", (usuario_id,))
   return cursor.fetchone()

 except Exception as e:
   print(f"Erro no login com Google: {e}")
   return None

 finally:
   cursor.close()
   conexao.close()


def solicitar_redefinicao_senha(email):
 """
 Gera um token de redefinição de senha (válido por 30 minutos) para
 a conta com esse e-mail — chamada pela tela "Esqueci minha senha".

 Devolve (token, nome) se existir uma conta com esse e-mail, ou None
 se não existir. Quem chama essa função decide o que fazer com isso:
 por segurança, a rota da API sempre mostra a mesma mensagem de
 sucesso pro front-end, pra não revelar quais e-mails têm conta
 cadastrada — só manda o e-mail de verdade se o token vier preenchido.
 """
 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return None

 cursor = conexao.cursor(dictionary=True)

 try:
   cursor.execute("SELECT id, nome FROM usuarios WHERE email = %s", (email,))
   usuario = cursor.fetchone()

   if usuario is None:
     return None

   token = secrets.token_urlsafe(32)

   query = """
     UPDATE usuarios
     SET token_redefinicao_senha = %s,
         token_redefinicao_expira = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
     WHERE id = %s
   """
   cursor.execute(query, (token, usuario["id"]))
   conexao.commit()

   return token, usuario["nome"]

 except Exception as e:
   print(f"Erro ao solicitar redefinição de senha: {e}")
   return None

 finally:
   cursor.close()
   conexao.close()


def verificar_token_redefinicao(token):
 """
 Confere se um token de redefinição de senha existe e ainda não
 expirou — usada assim que a página redefinir-senha.html carrega,
 pra decidir se mostra o formulário de nova senha ou um aviso de
 link inválido/expirado, e de novo na hora de salvar a nova senha.
 """
 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return None

 cursor = conexao.cursor(dictionary=True)

 try:
   query = """
     SELECT id, nome FROM usuarios
     WHERE token_redefinicao_senha = %s AND token_redefinicao_expira > NOW()
   """
   cursor.execute(query, (token,))
   return cursor.fetchone()

 finally:
   cursor.close()
   conexao.close()


def redefinir_senha(token, nova_senha):
 """
 Troca a senha da conta dona desse token de redefinição, desde que
 ele ainda seja válido (existente e não expirado). Apaga o token
 depois de usado, pra não poder ser reaproveitado num link antigo.

 Devolve True se trocou a senha, False se o token era
 inválido/expirado ou se algo deu errado.
 """
 usuario = verificar_token_redefinicao(token)
 if usuario is None:
   return False

 conexao = get_connection()
 if conexao is None:
   print("Não foi possível conectar ao banco.")
   return False

 cursor = conexao.cursor()

 try:
   senha_hash = generate_password_hash(nova_senha)
   query = """
     UPDATE usuarios
     SET senha_hash = %s, token_redefinicao_senha = NULL, token_redefinicao_expira = NULL
     WHERE id = %s
   """
   cursor.execute(query, (senha_hash, usuario["id"]))
   conexao.commit()
   return True

 except Exception as e:
   print(f"Erro ao redefinir senha: {e}")
   return False

 finally:
   cursor.close()
   conexao.close()


#==========bloco de teste temporario=============
'''if __name__ == "__main__":
    # Testando com a senha CERTA (deve dar "Bem-vindo...")
    login("teste@email.com", "senha123")

    # Testando com a senha ERRADA (deve dar "Email ou senha incorretos")
    login("teste@email.com", "senhaerrada")'''
#=======================================================================


