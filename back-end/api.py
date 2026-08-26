#importando as bibliotecas necessárias
# Flask é o framework que vai criar nosso servidor web e as rotas.
# "request" permite acessar os dados que o frontend vai enviar.
# "jsonify" transforma dados Python em formato JSON, que é o que
# o JavaScript do frontend consegue entender.
from flask import Flask, request, jsonify

# CORS libera a comunicação entre o frontend (rodando num endereço)
# e esse backend (rodando em outro endereço/porta).

from flask_cors import CORS

# Importa as funções que já construímos e testamos.
from usuarios import cadastro, login
from eventos import criar_eventos,listar_eventos_usuario,listar_todos_eventos
# Cria a aplicação Flask. "__name__" aqui tem o mesmo papel que
# vimos antes — ajuda o Flask a saber onde ele está localizado
# no projeto, pra encontrar arquivos relacionados se precisar.
app = Flask(__name__)
CORS(app)

from criar_tabela import criar_tabela_usuarios
criar_tabela_usuarios()
# Ativa o CORS pra essa aplicação inteira, liberando requisições
# vindas de outros endereços (como o frontend).


# @app.route define um "endereço" (rota) que o Flask vai responder.
# "/cadastro" é o caminho (ex: http://localhost:5000/cadastro).
# methods=["POST"] significa que essa rota só aceita requisições
# do tipo POST (usadas para ENVIAR dados, diferente do GET que
# é usado para apenas BUSCAR/ler informações).

@app.route("/cadastro", methods=["POST"])
def rota_cadastro():
    # request.json pega os dados enviados pelo frontend no formato
    # JSON, e transforma automaticamente num dicionário Python.
    dados = request.json

    # Extrai cada campo específico do dicionário recebido.
    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    # Chama a função que já construímos e testamos, passando
    # os dados que vieram do formulário do frontend.
    sucesso = cadastro(nome, email, senha)

    if sucesso:
        return jsonify({"mensagem":"Usuário cadastrado com sucesso"})# Devolve uma resposta em JSON para o frontend saber que  a requisição foi processada.
    else:
        return jsonify({"mensagem":"Não foi possível cadastrar seu usuário"}),400


@app.route("/login",methods=["POST"])
def rota_login():
    dados = request.json
    email= dados.get("email")
    senha= dados.get("senha")
    #guardamos as informaçõesdo usuário logado.

    usuario = login(email,senha)

    if usuario:
        return jsonify({"mensagem":"login realizado com sucesso ", "usuario":  usuario})
    else :
        return jsonify({"mensagem":"Email ou senha incorretos"}), 401


# Define a rota "/criar-evento", que só aceita requisições POST
# (porque estamos ENVIANDO dados para serem salvos, não buscando).
@app.route("/criar-evento", methods=["POST"])
def rota_criar_evento():

    # Pega o corpo da requisição (que vem em JSON do frontend)
    # e transforma automaticamente num dicionário Python.
    dados = request.json

    # Extrai cada campo específico do dicionário recebido.
    # Usamos .get() em vez de dados["titulo"] porque, se o campo
    # não vier por algum motivo, .get() retorna None em vez de
    # quebrar o programa com erro.
    titulo = dados.get("titulo")
    categoria = dados.get("categoria")
    descricao = dados.get("descricao")
    data = dados.get("data")
    horario = dados.get("horario")
    local = dados.get("local")
    cidade = dados.get("cidade")

    # Esse campo é diferente dos outros: ele não vem de um campo
    # de formulário digitado pelo usuário, e sim do usuário que
    # está logado no momento (vamos configurar isso no frontend
    # daqui a pouco, pegando do localStorage).
    usuario_id = dados.get("usuario_id")



     # Chama a função que já testamos e validamos, passando todos
    # os dados extraídos acima, na mesma ordem que a função espera.
    sucesso = criar_eventos(titulo, categoria, descricao, data, horario, local, cidade, usuario_id)

    # Verifica o que a função devolveu (True ou False) e responde
    # pro frontend de acordo, com o código de status apropriado.
    if sucesso:
        return jsonify({"mensagem": "Evento criado com sucesso!"})
    else:
        return jsonify({"mensagem": "Não foi possível criar o evento."}), 400




# Define a rota "/meus-eventos". Repare que agora usamos GET,
# não POST — porque estamos BUSCANDO dados, não enviando.
@app.route("/meus-eventos", methods=["GET"])
def rota_meus_eventos():

    # Em requisições GET, os dados costumam vir como parâmetros
    # na própria URL (ex: /meus-eventos?usuario_id=6), não no
    # corpo da requisição. Por isso usamos request.args em vez
    # de request.json.
    usuario_id = request.args.get("usuario_id")

    # Chama a função que já testamos, passando o id recebido.
    eventos = listar_eventos_usuario(usuario_id)

    # Devolve a lista de eventos encontrados, em formato JSON.
    return jsonify({"eventos": eventos})

# Rota pública — não depende de usuário logado, devolve
# todos os eventos cadastrados no sistema.
@app.route("/eventos", methods=["GET"])
def rota_eventos():

    # Chama a função que acabamos de criar e testar.
    eventos = listar_todos_eventos()

    # Devolve a lista completa em formato JSON.
    return jsonify({"eventos": eventos})



#Garante que o servidor só inicia se executar este aruquivo diretamente
if __name__ =="__main__":
     
   # app.run() inicia o servidor Flask de verdade.
    # debug=True faz o servidor reiniciar automaticamente
    # sempre que você salvar alterações no código, e mostra
    # mensagens de erro mais detalhadas no navegador (útil
    # durante o desenvolvimento, mas deve ser desligado em produção).
    app.run(debug=True)
