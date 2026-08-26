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

#Garante que o servidor só inicia se executar este aruquivo diretamente
if __name__ =="__main__":
     
   # app.run() inicia o servidor Flask de verdade.
    # debug=True faz o servidor reiniciar automaticamente
    # sempre que você salvar alterações no código, e mostra
    # mensagens de erro mais detalhadas no navegador (útil
    # durante o desenvolvimento, mas deve ser desligado em produção).
    app.run(debug=True)

    