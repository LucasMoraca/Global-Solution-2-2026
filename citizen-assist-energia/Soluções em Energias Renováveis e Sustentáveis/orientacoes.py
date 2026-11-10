"""orientacoes.py - respostas do assistente. Segurança vem de fontes oficiais; números vêm do modelo."""

import modelo as m

SEGURANCA = [
    {"id": "gerador_dentro", "titulo": "Gerador dentro de casa e monóxido de carbono",
     "palavras": ["gerador", "dentro", "garagem", "monoxido", "co", "fumaca", "ventilador", "janela", "varanda"],
     "texto": ["Nunca use gerador dentro de casa, garagem ou em local parcialmente fechado. Mantenha-o ao ar livre, "
               "inclusive ao reabastecer. Ventilador ou janela aberta não evitam o acúmulo de monóxido de carbono, "
               "que não tem cor nem cheiro. Instale alarme de CO a pilha."],
     "fontes": ["S2"]},
    {"id": "quadro_alagado", "titulo": "Quadro de luz e religação após alagamento",
     "palavras": ["quadro", "disjuntor", "religar", "ligar", "luz", "voltou", "alagado", "agua", "tomada", "cheiro"],
     "texto": ["Se a área está alagada, não toque em equipamentos elétricos nem no quadro. Aguarde a concessionária ou "
               "a Defesa Civil. Antes de religar, peça que um profissional avalie a instalação e verifique infiltração "
               "ou cheiro de queimado."],
     "fontes": ["S1"]},
    {"id": "fio_caido", "titulo": "Fio caído ou rede danificada",
     "palavras": ["fio", "cabo", "poste", "caido", "rede", "faisca", "choque"],
     "texto": ["Trate qualquer fio caído como energizado. Mantenha distância, avise a concessionária e a Defesa Civil "
               "e não tente mover o fio nem a água ao redor."],
     "fontes": ["S1"]},
    {"id": "vela", "titulo": "Vela ou lanterna",
     "palavras": ["vela", "velas", "lanterna", "luz", "iluminar", "lamparina", "fogo"],
     "texto": ["Prefira lanternas a pilha ou LED. Evite velas por causa do risco de incêndio. "
               "Lanternas LED de 3 W gastam pouco: duas por 5 h/noite somam cerca de 30 Wh por dia."],
     "fontes": ["S1", "S5"]},
]


def _caso_texto(caso):
    return f"{caso.celulares} celular(es), {caso.lampadas} lâmpada(s), {caso.dias} dia(s)"


def calc_necessidade(caso, p):
    n = m.necessidade(caso, p)
    return [f"Caso: {_caso_texto(caso)}.",
            f"Celulares: {n['celulares_tomada_wh_dia']:.1f} Wh/dia na tomada (bateria {n['celulares_bateria_wh_dia']:.1f} Wh, "
            f"eficiência de carga {p.valor('celular_eficiencia_carga') * 100:.0f}%, estimada).",
            f"Lâmpadas LED: {n['luz_wh_dia']:.1f} Wh/dia ({p.valor('lampada_led_w'):.0f} W × {p.valor('horas_luz_noite'):.0f} h).",
            f"Total: {n['total_wh_dia']:.1f} Wh/dia, {n['total_wh_periodo']:.1f} Wh em {caso.dias} dia(s)."], ["S5"]


def calc_combustivel(caso, p):
    g = m.gerador(caso, p)
    return [f"Gerador B4T-2500 a 50% de carga, {p.valor('gerador_horas_dia'):.0f} h/dia (perfil típico, estimado): "
            f"{g['litros']:.1f} L em {caso.dias} dia(s).",
            f"Custo de combustível: R$ {g['operacao_r']:.2f} (gasolina a R$ {m.preco_gasolina(caso, p):.2f}/L).",
            f"Compra do gerador: R$ {g['compra_r']:.2f}.",
            "Se ligar menos horas, gasta menos; o consumo real varia com a carga."], ["S3", "S6", "S7"]


def calc_emissoes(caso, p):
    g = m.gerador(caso, p)
    return [f"O gerador emite cerca de {g['co2_kg']:.1f} kg de CO2 fóssil em {caso.dias} dia(s) "
            f"({m.fator_co2_fossil_kg_l(p):.2f} kg por litro, estimativa para gasolina com 30% de etanol).",
            "O kit solar e os power banks não emitem na operação. Fabricação e descarte das baterias "
            "não foram quantificados aqui."], ["S10", "S11"]


def calc_comparacao(caso, p):
    linhas = m.comparar(caso, p)
    saida = [f"Comparação para {_caso_texto(caso)}:"]
    for l in linhas:
        compra = "-" if l["compra_r"] is None else f"R$ {l['compra_r']:.2f}"
        saida.append(f"- {l['nome']}: compra {compra}, operação R$ {l['operacao_r']:.2f}, "
                     f"CO2 {l['co2_kg']:.1f} kg, cobertura {l['cobertura'] * 100:.0f}%.")
    saida += m.recomendar(caso, p)
    return saida, ["S3", "S4", "S6", "S7", "S8"]


def calc_solar_chuva(caso, p):
    saida = [f"Kit solar de {p.valor('kit_painel_w'):.0f} W e {p.valor('kit_bateria_wh'):.0f} Wh, caso {_caso_texto(caso)}:"]
    for clima, fator, k in m.sensibilidade_clima(caso, p):
        saida.append(f"- {m.NOMES_CLIMA[clima]} (fator {fator:.2f}): painel {k['solar_wh_dia']:.0f} Wh/dia, "
                     f"cobertura {k['cobertura'] * 100:.0f}%.")
    saida.append("O fator de tempestade forte (0,10) é estimativa; só a produção anual vem de dado público.")
    return saida, ["S4", "S9"]


def calc_power_banks(caso, p):
    b = m.power_banks(caso, p)
    if b["compra_r"] is None:
        return [b["observacao"]], []
    return [f"Para {_caso_texto(caso)}: {b['unidades']} power bank(s) de 20.000 mAh "
            f"({b['wh_util_por_banco']:.1f} Wh úteis cada) + {caso.lampadas} lanterna(s) LED.",
            f"Custo estimado: R$ {b['compra_r']:.2f} (preços estimados). {b['observacao']}"], []


def calc_geladeira(caso, p):
    c = m.Caso(caso.celulares, caso.lampadas, caso.dias, True, caso.cidade_preco)
    return m.recomendar(c, p), ["S5", "S6", "S8"]


CALCULOS = [
    {"id": "necessidade", "titulo": "Quanta energia eu preciso",
     "palavras": ["quanta", "energia", "preciso", "consumo", "wh", "kwh", "necessidade", "gasta"], "funcao": calc_necessidade},
    {"id": "combustivel", "titulo": "Custo de combustível do gerador",
     "palavras": ["combustivel", "gasolina", "litros", "custo", "gerador", "gasta", "quanto"], "funcao": calc_combustivel},
    {"id": "emissoes", "titulo": "Emissões de CO2",
     "palavras": ["co2", "emissao", "emissoes", "poluicao", "carbono", "ambiente", "polui", "meio"], "funcao": calc_emissoes},
    {"id": "comparacao", "titulo": "Gerador, solar ou power bank: qual escolher",
     "palavras": ["comparar", "melhor", "escolher", "solar", "gerador", "alternativa", "vale", "compensa", "recomenda"],
     "funcao": calc_comparacao},
    {"id": "solar_chuva", "titulo": "Painel solar com chuva e nuvens",
     "palavras": ["solar", "chuva", "nublado", "nuvem", "painel", "sol", "tempestade", "chovendo"], "funcao": calc_solar_chuva},
    {"id": "power_banks", "titulo": "Quantos power banks eu preciso",
     "palavras": ["power", "bank", "powerbank", "bateria", "portatil", "carregador", "quantos", "carregar"], "funcao": calc_power_banks},
    {"id": "geladeira", "titulo": "Geladeira no kit solar",
     "palavras": ["geladeira", "freezer", "refrigerador", "comida", "alimentos", "congelador"], "funcao": calc_geladeira},
]


def todas():
    return SEGURANCA + CALCULOS


def responder(orientacao, caso, p):
    """Devolve (linhas, fontes). Toda resposta termina com limitações."""
    if "funcao" in orientacao:
        linhas, fontes = orientacao["funcao"](caso, p)
    else:
        linhas, fontes = orientacao["texto"], orientacao["fontes"]
    return list(linhas), list(fontes)


LIMITACAO = ("Estimativas, não garantias: consumo real, preços e clima variam. "
             "Em emergência, ligue 199 (Defesa Civil) ou 193 (Bombeiros).")
