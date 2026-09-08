from google import genai
from google.genai import types

from gemini_config import GEMINI_API_KEY
from eventos import listar_todos_eventos

# Modelo rápido e gratuito do Gemini — bom o suficiente pra conversar
# e recomendar eventos, dentro da camada gratuita da Google.
MODELO = "gemini-3.6-flash"


def _formatar_eventos_para_o_prompt(eventos):
    """
    Monta uma lista em texto simples com os eventos reais cadastrados
    no banco, pra colocar no prompt do Gemini. É a partir DESSA lista
    (e só dela) que o chatbot pode recomendar eventos — assim ele
    nunca inventa um evento que não existe de verdade no site.
    """
    if not eventos:
        return "Nenhum evento cadastrado no site no momento."

    linhas = []
    for evento in eventos:
        linhas.append(
            f"- ID {evento['id']}: \"{evento['titulo']}\" | categoria: {evento['categoria']} | "
            f"quando: {evento['data']} às {evento['horario']} | onde: {evento['local']}, {evento['cidade']} | "
            f"descrição: {evento.get('descricao') or 'sem descrição'}"
        )
    return "\n".join(linhas)


def _montar_prompt_sistema():
    eventos = listar_todos_eventos()
    lista_eventos = _formatar_eventos_para_o_prompt(eventos)

    return f"""Você é o assistente virtual do LittleVitor.com, um site de eventos.
Seu nome é "Vitinho". Fale sempre em português do Brasil, de forma curta, simpática e direta —
respostas de chat, não parágrafos longos.

Você ajuda de duas formas:

1) RECOMENDAR EVENTOS: pergunte sobre o gosto da pessoa (tipo de evento que curte — música,
gastronomia, arte, negócios, esporte, bem-estar —, cidade onde está, quando pode ir) e recomende
eventos com base nisso. IMPORTANTE: você só pode recomendar eventos que estão na lista real abaixo.
NUNCA invente um evento que não está nessa lista. Se não houver nenhum evento que combine com o
gosto da pessoa, diga isso com sinceridade, em vez de inventar algo.

Lista de eventos REAIS cadastrados agora no site:
{lista_eventos}

Quando recomendar um evento, cite o título dele e sugira que a pessoa veja mais detalhes na página
do evento (ela pode buscar pelo nome na aba "Eventos" do site).

2) AJUDAR A ORGANIZAR UM EVENTO: se a pessoa quiser criar/publicar um evento próprio, ajude com
dicas (categoria, descrição, tipos de ingresso) e oriente ela a usar a página "Criar evento" do
site pra publicar de verdade — você não cria o evento por ela diretamente, só orienta.

Não responda sobre assuntos fora desses dois temas (eventos do site). Se perguntarem algo não
relacionado, redirecione com simpatia de volta pro assunto de eventos."""


def _converter_historico_para_gemini(mensagens):
    """
    O front-end guarda o histórico no mesmo formato "genérico" que
    outras IAs de chat usam ({"role": "user"/"assistant", "content": "..."}).
    O Gemini espera um formato um pouco diferente: role "model" em vez
    de "assistant", e o texto dentro de uma lista "parts".
    """
    convertido = []
    for mensagem in mensagens:
        role = "model" if mensagem.get("role") == "assistant" else "user"
        convertido.append({"role": role, "parts": [{"text": mensagem.get("content", "")}]})
    return convertido


def responder_chat(mensagens):
    """
    Manda a conversa pro Gemini, junto com o prompt de sistema (que já
    inclui os eventos reais atualizados na hora), e devolve a resposta
    em texto.
    """
    if not GEMINI_API_KEY:
        return None

    cliente = genai.Client(api_key=GEMINI_API_KEY)

    resposta = cliente.models.generate_content(
        model=MODELO,
        contents=_converter_historico_para_gemini(mensagens),
        config=types.GenerateContentConfig(
            system_instruction=_montar_prompt_sistema(),
            # O gemini-3.6-flash "pensa" antes de responder, e esse
            # raciocínio consome tokens do mesmo limite da resposta —
            # por isso o número aqui é bem maior do que o texto final
            # costuma precisar (senão a resposta vem cortada no meio).
            max_output_tokens=2048,
        ),
    )

    return resposta.text
