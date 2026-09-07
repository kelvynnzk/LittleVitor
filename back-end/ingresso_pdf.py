from fpdf import FPDF


def _seguro(texto):
    """
    As fontes padrão do fpdf2 (Helvetica, Courier) só desenham
    caracteres Latin-1 — cobre acentos do português, mas não emoji
    nem símbolos mais exóticos. Em vez de a geração do PDF inteiro
    falhar por causa de um único caractere (ex: alguém colocou um
    emoji no título do evento), trocamos o que não é suportado por "?".
    """
    return str(texto).encode("latin-1", errors="replace").decode("latin-1")


def gerar_pdf_ingresso(compra_id, evento, tipo_ingresso, quantidade, nome_titular, valor_total):
    """
    Monta o PDF do ingresso (um "bilhete" simples de uma página) e
    devolve os bytes prontos pra anexar no e-mail — sem salvar nenhum
    arquivo temporário no disco.

    Recebe o "compra_id" (pra gerar um código de ingresso único, tipo
    "LV-000042"), o dicionário do evento (vindo de buscar_evento_por_id),
    o dicionário do tipo de ingresso (vindo de buscar_tipo_ingresso_por_id),
    a quantidade comprada, o nome de quem vai usar o ingresso, e o
    valor total já pago.
    """
    codigo_ingresso = f"LV-{compra_id:06d}"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margin(20)

    # ---------- CABEÇALHO ----------
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(90, 40, 180)
    pdf.cell(0, 14, "LittleVitor.com", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(110, 110, 110)
    pdf.cell(0, 8, "Confirmação de ingresso", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ---------- CAIXA DO INGRESSO ----------
    x_inicial = pdf.get_x()
    y_inicial = pdf.get_y()
    largura_caixa = pdf.w - 2 * pdf.l_margin

    pdf.set_draw_color(180, 160, 220)
    pdf.set_line_width(0.6)
    pdf.rect(x_inicial, y_inicial, largura_caixa, 92)

    pdf.set_xy(x_inicial + 8, y_inicial + 8)
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(largura_caixa - 16, 8, _seguro(evento["titulo"]), new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(x_inicial + 8)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 7, _seguro(f"{evento['data']}  ·  {evento['horario']}"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(x_inicial + 8)
    pdf.cell(0, 7, _seguro(f"{evento['local']}, {evento['cidade']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Linha divisória dentro da caixa
    pdf.set_x(x_inicial + 8)
    y_linha = pdf.get_y()
    pdf.set_draw_color(225, 220, 235)
    pdf.line(x_inicial + 8, y_linha, x_inicial + largura_caixa - 8, y_linha)
    pdf.ln(6)

    # ---------- DADOS DO INGRESSO (em duas colunas) ----------
    largura_coluna = (largura_caixa - 16) / 2

    def campo(rotulo, valor):
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(140, 140, 140)
        pdf.cell(largura_coluna, 5, rotulo, new_x="LEFT", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(largura_coluna, 7, _seguro(valor), new_x="LEFT", new_y="NEXT")

    y_campos = pdf.get_y()

    pdf.set_xy(x_inicial + 8, y_campos)
    campo("TITULAR", nome_titular)

    pdf.set_xy(x_inicial + 8 + largura_coluna, y_campos)
    campo("TIPO DE INGRESSO", tipo_ingresso["nome"])

    y_campos_2 = pdf.get_y() + 4
    pdf.set_xy(x_inicial + 8, y_campos_2)
    campo("QUANTIDADE", str(quantidade))

    pdf.set_xy(x_inicial + 8 + largura_coluna, y_campos_2)
    campo("VALOR PAGO", f"R$ {valor_total:.2f}".replace(".", ","))

    # ---------- CÓDIGO DO INGRESSO ----------
    pdf.set_xy(x_inicial + 8, y_inicial + 92 - 16)
    pdf.set_font("Courier", "B", 13)
    pdf.set_text_color(90, 40, 180)
    pdf.cell(0, 8, codigo_ingresso, new_x="LMARGIN", new_y="NEXT")

    # ---------- RODAPÉ ----------
    pdf.set_y(y_inicial + 92 + 12)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(140, 140, 140)
    pdf.multi_cell(
        0, 5,
        "Apresente este ingresso (impresso ou na tela do celular) na entrada do evento. "
        "Compra simulada - LittleVitor.com."
    )

    return bytes(pdf.output())
