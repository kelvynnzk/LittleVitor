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
from usuarios import cadastro, login, buscar_usuario_por_id, confirmar_email
from eventos import criar_eventos, listar_eventos_usuario, listar_todos_eventos, buscar_evento_por_id, atualizar_evento, deletar_evento, listar_cidades_com_eventos
from compras import criar_tipo_ingresso, remover_tipos_ingresso_evento, listar_tipos_ingresso, registrar_compra, listar_compras_usuario, estatisticas_organizador, buscar_evento_destaque, listar_vendas_por_evento
from ingresso_pdf import gerar_pdf_ingresso
from email_service import enviar_email_confirmacao, enviar_email_boas_vindas, enviar_email_evento_criado
from validacao_email import dominio_aceita_email
# Cria a aplicação Flask. "__name__" aqui tem o mesmo papel que
# vimos antes — ajuda o Flask a saber onde ele está localizado
# no projeto, pra encontrar arquivos relacionados se precisar.
app = Flask(__name__)
CORS(app)
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

    # Só deixa cadastrar se o domínio do e-mail existir de verdade
    # (tiver servidor de e-mail configurado) — barra e-mails
    # inventados ou com erro de digitação antes mesmo de tentar salvar.
    if not dominio_aceita_email(email):
        return jsonify({"mensagem": "Esse e-mail não existe. Confira se digitou certo."}), 400

    # Chama a função que já construímos e testamos, passando
    # os dados que vieram do formulário do frontend. Agora ela
    # devolve o token de confirmação (ou False se der errado).
    token = cadastro(nome, email, senha)

    if token:
        # Manda o e-mail de confirmação com o link/token. Se der algum
        # problema aqui, a conta continua criada mesmo assim — só que
        # "presa" como pendente até reenviarmos o e-mail de algum jeito.
        try:
            enviar_email_boas_vindas(email, nome, token)
        except Exception as e:
            print(f"Erro ao enviar e-mail de confirmação: {e}")

        return jsonify({
            "mensagem": "Quase lá! Enviamos um e-mail de confirmação — clique no link pra ativar sua conta."
        })
    else:
        return jsonify({"mensagem":"Não foi possível cadastrar seu usuário"}),400


# Rota que confirma a conta a partir do token recebido por e-mail —
# chamada pela página confirmar-email.html quando a pessoa clica no
# link, não diretamente pelo link (assim a gente controla a tela que
# aparece depois, em vez de mostrar um JSON cru no navegador).
@app.route("/confirmar-email", methods=["POST"])
def rota_confirmar_email():

    dados = request.json
    token = dados.get("token")

    usuario = confirmar_email(token)

    if usuario:
        return jsonify({"mensagem": "E-mail confirmado com sucesso! Você já pode entrar.", "usuario": usuario})
    else:
        return jsonify({"mensagem": "Esse link de confirmação é inválido ou já foi usado."}), 400


@app.route("/login",methods=["POST"])
def rota_login():
    dados = request.json
    email= dados.get("email")
    senha= dados.get("senha")
    #guardamos as informaçõesdo usuário logado.

    resultado = login(email, senha)

    if resultado["sucesso"]:
        return jsonify({"mensagem": "Login realizado com sucesso!", "usuario": resultado["usuario"]})

    # Uma mensagem diferente pra cada motivo de falha — o "motivo"
    # também vai junto na resposta, pra o front-end saber em qual
    # campo (e-mail ou senha) mostrar o erro.
    mensagens_por_motivo = {
        "email_nao_encontrado": "Não existe nenhuma conta cadastrada com esse e-mail.",
        "senha_incorreta": "Senha incorreta.",
        "email_nao_verificado": "Confirme seu e-mail antes de entrar — verifique sua caixa de entrada.",
        "erro_servidor": "Não foi possível conectar ao banco de dados. Tente novamente em instantes."
    }
    mensagem = mensagens_por_motivo.get(resultado["motivo"], "Não foi possível fazer login.")

    return jsonify({"mensagem": mensagem, "motivo": resultado["motivo"]}), 401


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
    # Agora ela devolve o id do evento criado (ou False se der errado).
    evento_id = criar_eventos(titulo, categoria, descricao, data, horario, local, cidade, usuario_id)

    if evento_id:
        # Cadastra cada tipo de ingresso enviado junto com o formulário
        # (a lista de "Pista", "VIP", etc.), já vinculado a esse evento.
        ingressos = dados.get("ingressos", [])
        for ingresso in ingressos:
            criar_tipo_ingresso(evento_id, ingresso.get("nome"), ingresso.get("preco"), ingresso.get("quantidade"))

        # Manda um e-mail pro organizador confirmando a publicação, com
        # os dados do evento e um link pro painel. Assim como nos outros
        # e-mails, um problema aqui não invalida o evento já criado.
        try:
            organizador = buscar_usuario_por_id(usuario_id)
            if organizador:
                evento_para_email = {
                    "titulo": titulo, "categoria": categoria, "descricao": descricao,
                    "data": data, "horario": horario, "local": local, "cidade": cidade
                }
                enviar_email_evento_criado(organizador["email"], organizador["nome"], evento_para_email)
        except Exception as e:
            print(f"Erro ao enviar e-mail de evento criado: {e}")

        return jsonify({"mensagem": "Evento criado com sucesso!", "evento_id": evento_id})
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



# Rota que busca um único evento pelo id — usada para preencher
# o formulário de edição com os dados já existentes do evento.
@app.route("/evento/<int:evento_id>", methods=["GET"])
def rota_buscar_evento(evento_id):

    evento = buscar_evento_por_id(evento_id)

    if evento:
        return jsonify({"evento": evento})
    else:
        return jsonify({"mensagem": "Evento não encontrado."}), 404


# Rota que atualiza um evento existente. Usa PUT (e não POST) porque
# estamos SUBSTITUINDO os dados de um recurso que já existe.
@app.route("/evento/<int:evento_id>", methods=["PUT"])
def rota_atualizar_evento(evento_id):

    dados = request.json

    titulo = dados.get("titulo")
    categoria = dados.get("categoria")
    descricao = dados.get("descricao")
    data = dados.get("data")
    horario = dados.get("horario")
    local = dados.get("local")
    cidade = dados.get("cidade")

    # O usuario_id vem do localStorage no frontend (usuário logado),
    # igual ao que já fazemos em "/criar-evento". É ele que garante,
    # junto com a query em atualizar_evento(), que só o dono do
    # evento consegue editá-lo.
    usuario_id = dados.get("usuario_id")

    sucesso = atualizar_evento(evento_id, titulo, categoria, descricao, data, horario, local, cidade, usuario_id)

    if sucesso:
        # Assim como em "/criar-evento", recriamos os tipos de ingresso
        # a partir da lista enviada: apaga os antigos e insere os novos.
        # É mais simples do que tentar descobrir quais linhas mudaram.
        #
        # Se algum tipo de ingresso já tiver ingressos vendidos, o banco
        # impede a exclusão (por causa da chave estrangeira em "compras")
        # e remover_tipos_ingresso_evento() devolve False. Nesse caso,
        # não mexemos nos tipos de ingresso — mais seguro do que apagar
        # e recriar pela metade, o que duplicaria os tipos.
        conseguiu_remover = remover_tipos_ingresso_evento(evento_id)

        if conseguiu_remover:
            ingressos = dados.get("ingressos", [])
            for ingresso in ingressos:
                criar_tipo_ingresso(evento_id, ingresso.get("nome"), ingresso.get("preco"), ingresso.get("quantidade"))
            return jsonify({"mensagem": "Evento atualizado com sucesso!"})
        else:
            return jsonify({
                "mensagem": "Evento atualizado, mas os tipos de ingresso não puderam ser alterados (já existem ingressos vendidos)."
            })
    else:
        return jsonify({"mensagem": "Não foi possível atualizar o evento."}), 400


# Rota que exclui um evento. Usa DELETE, o método adequado pra
# remover um recurso existente.
@app.route("/evento/<int:evento_id>", methods=["DELETE"])
def rota_deletar_evento(evento_id):

    # Em requisições DELETE também não costuma vir corpo JSON,
    # então pegamos o usuario_id da query string, como já fazemos
    # em "/meus-eventos".
    usuario_id = request.args.get("usuario_id")

    sucesso = deletar_evento(evento_id, usuario_id)

    if sucesso:
        return jsonify({"mensagem": "Evento excluído com sucesso!"})
    else:
        return jsonify({"mensagem": "Não foi possível excluir o evento."}), 400


# Rota que lista os tipos de ingresso de um evento (ex: Pista, VIP),
# já com a quantidade disponível calculada. Usada tanto na tela de
# compra (evento.html) quanto pra pré-preencher a edição do evento.
@app.route("/tipos-ingresso/<int:evento_id>", methods=["GET"])
def rota_listar_tipos_ingresso(evento_id):

    tipos = listar_tipos_ingresso(evento_id)
    return jsonify({"tipos_ingresso": tipos})


# Rota que registra a compra de ingressos (a "simulação de compra").
@app.route("/comprar", methods=["POST"])
def rota_comprar():

    dados = request.json

    tipo_ingresso_id = dados.get("tipo_ingresso_id")
    usuario_id = dados.get("usuario_id")
    quantidade = dados.get("quantidade")
    nome_titular = dados.get("nome_titular")
    email_titular = dados.get("email_titular")

    resultado = registrar_compra(tipo_ingresso_id, usuario_id, quantidade, nome_titular, email_titular)

    if resultado["sucesso"]:
        # A compra já está gravada no banco nesse ponto — o que vem
        # a seguir (gerar o PDF e mandar o e-mail) é só a confirmação
        # por e-mail. Se der algum problema aqui, a compra continua
        # válida mesmo assim; só avisamos no console do servidor.
        try:
            evento = buscar_evento_por_id(resultado["tipo"]["evento_id"])
            codigo_ingresso = f"LV-{resultado['compra_id']:06d}"

            pdf_bytes = gerar_pdf_ingresso(
                resultado["compra_id"], evento, resultado["tipo"],
                quantidade, nome_titular, resultado["valor_total"]
            )

            enviar_email_confirmacao(
                email_titular, nome_titular, evento, resultado["tipo"],
                quantidade, resultado["valor_total"], pdf_bytes, codigo_ingresso
            )
        except Exception as e:
            print(f"Erro ao gerar/enviar o ingresso por e-mail: {e}")

        return jsonify({"mensagem": resultado["mensagem"], "valor_total": resultado["valor_total"]})
    else:
        return jsonify({"mensagem": resultado["mensagem"]}), 400


# Rota que lista as compras já feitas por um usuário (histórico de
# ingressos comprados). Ainda não tem uma tela própria no frontend,
# mas já fica pronta pra ser usada (ex: numa futura página "Meus ingressos").
@app.route("/minhas-compras", methods=["GET"])
def rota_minhas_compras():

    usuario_id = request.args.get("usuario_id")
    compras = listar_compras_usuario(usuario_id)
    return jsonify({"compras": compras})


# Rota que calcula os números reais do painel do organizador
# (eventos ativos, ingressos vendidos, total arrecadado), usada pra
# substituir os números fixos que existiam antes em painel.html.
@app.route("/painel-stats", methods=["GET"])
def rota_painel_stats():

    usuario_id = request.args.get("usuario_id")
    stats = estatisticas_organizador(usuario_id)
    return jsonify(stats)


# Rota pública que devolve o evento "em destaque" da página inicial —
# o que já vendeu mais ingressos no total.
@app.route("/evento-destaque", methods=["GET"])
def rota_evento_destaque():

    evento = buscar_evento_destaque()
    return jsonify({"evento": evento})


# Rota que lista, para cada evento de um usuário, quantos ingressos
# já foram vendidos e quantos existem no total — usada pra mostrar a
# barra de progresso de vendas de cada evento em painel.html.
@app.route("/vendas-por-evento", methods=["GET"])
def rota_vendas_por_evento():

    usuario_id = request.args.get("usuario_id")
    vendas = listar_vendas_por_evento(usuario_id)
    return jsonify({"vendas": vendas})


# Rota pública que lista as cidades com eventos reais cadastrados,
# com a contagem de cada uma — usada na seção "Explore por cidade"
# do index.html.
@app.route("/cidades-com-eventos", methods=["GET"])
def rota_cidades_com_eventos():

    cidades = listar_cidades_com_eventos()
    return jsonify({"cidades": cidades})


#Garante que o servidor só inicia se executar este aruquivo diretamente
if __name__ =="__main__":
     
   # app.run() inicia o servidor Flask de verdade.
    # debug=True faz o servidor reiniciar automaticamente
    # sempre que você salvar alterações no código, e mostra
    # mensagens de erro mais detalhadas no navegador (útil
    # durante o desenvolvimento, mas deve ser desligado em produção).
    app.run(debug=True)
