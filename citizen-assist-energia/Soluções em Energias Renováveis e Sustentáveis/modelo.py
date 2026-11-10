"""modelo.py - cálculo de energia, custo e CO2 para a falta de luz durante enchentes.

Necessidade comum às alternativas: carregar celulares e iluminar a casa, por um período de referência
(48 horas por padrão). As unidades estão nos nomes: wh (watt-hora), kwh, w (watt), l (litro), r (reais).
"""

import math
from dataclasses import dataclass

CLIMAS = {"media": "clima_media", "nublado": "clima_nublado", "denso": "clima_denso", "estresse": "clima_estresse"}
NOMES_CLIMA = {"media": "dia médio do ano", "nublado": "nublado sem chuva (-25%)",
               "denso": "nuvens densas (-60%)", "estresse": "tempestade forte (estresse)"}


@dataclass
class Caso:
    celulares: int = 4
    lampadas: int = 2
    dias: int = 2                 # 2 dias = 48 horas
    geladeira: bool = False
    cidade_preco: str = "poa"     # "poa" (Porto Alegre) ou "br" (média Brasil)


def validar(caso):
    """Levanta ValueError se o caso for impossível."""
    if not 0 <= caso.celulares <= 20:
        raise ValueError("celulares deve ficar entre 0 e 20")
    if not 0 <= caso.lampadas <= 10:
        raise ValueError("lampadas deve ficar entre 0 e 10")
    if not 1 <= caso.dias <= 14:
        raise ValueError("dias deve ficar entre 1 e 14")
    if caso.celulares == 0 and caso.lampadas == 0 and not caso.geladeira:
        raise ValueError("informe pelo menos um uso (celular, lâmpada ou geladeira)")
    if caso.cidade_preco not in ("poa", "br"):
        raise ValueError("cidade_preco deve ser 'poa' ou 'br'")


def fator_clima(p, clima):
    return 1.0 if clima == "media" else p.valor(CLIMAS[clima])


# ----------------------------------------------------------------------------- necessidade
def necessidade(caso, p):
    """Energia por dia (Wh) em cada uso, e o total que a tomada precisa entregar."""
    validar(caso)
    celulares_bateria = caso.celulares * p.valor("celular_wh")
    celulares_tomada = celulares_bateria / p.valor("celular_eficiencia_carga")
    luz = caso.lampadas * p.valor("lampada_led_w") * p.valor("horas_luz_noite")
    geladeira = p.valor("geladeira_kwh_mes") * 1000 / 30 if caso.geladeira else 0.0
    total_dia = celulares_tomada + luz + geladeira
    return {"celulares_bateria_wh_dia": celulares_bateria, "celulares_tomada_wh_dia": celulares_tomada,
            "luz_wh_dia": luz, "geladeira_wh_dia": geladeira,
            "total_wh_dia": total_dia, "total_wh_periodo": total_dia * caso.dias}


# ----------------------------------------------------------------------------- A) gerador a gasolina
def litros_por_kwh_gerador(p):
    """Consumo específico a 50% de carga, derivado da ficha do B4T-5000: tanque ÷ autonomia ÷ kW a 50%."""
    litros_hora = p.valor("gerador_ref_tanque_l") / p.valor("gerador_ref_autonomia_h")
    kw_50 = 0.5 * p.valor("gerador_ref_kva") * p.valor("gerador_fator_potencia")
    return litros_hora / kw_50


def fator_co2_fossil_kg_l(p):
    """kg de CO2 fóssil por litro de gasolina com etanol: densidade × carbono × 44/12 × fração fóssil."""
    puro = p.valor("gasolina_densidade") * p.valor("gasolina_fracao_carbono") * 44 / 12
    return puro * p.valor("gasolina_fracao_fossil")


def preco_gasolina(caso, p):
    return p.valor("gasolina_preco_poa" if caso.cidade_preco == "poa" else "gasolina_preco_br")


def gerador(caso, p, perfil="tipico"):
    """perfil 'tipico': liga X horas por dia a 50% da potência; 'minimo': liga só o tempo necessário (limite inferior)."""
    nec = necessidade(caso, p)
    kw_50 = 0.5 * p.valor("gerador_kva") * p.valor("gerador_fator_potencia")
    l_por_h = litros_por_kwh_gerador(p) * kw_50
    if perfil == "minimo":
        horas_dia = (nec["total_wh_dia"] / 1000) / kw_50
    else:
        horas_dia = p.valor("gerador_horas_dia")
    gerado_wh_dia = horas_dia * kw_50 * 1000
    cobertura = min(1.0, gerado_wh_dia / nec["total_wh_dia"])
    litros = horas_dia * l_por_h * caso.dias
    return {"nome": "Gerador a gasolina" + (" (uso mínimo)" if perfil == "minimo" else ""),
            "renovavel": False, "compra_r": p.valor("gerador_preco"),
            "operacao_r": litros * preco_gasolina(caso, p), "litros": litros,
            "co2_kg": litros * fator_co2_fossil_kg_l(p), "cobertura": cobertura,
            "horas_ligado": horas_dia * caso.dias}


# ----------------------------------------------------------------------------- B) kit solar com bateria
def kit_solar(caso, p, clima="media"):
    nec = necessidade(caso, p)
    util_bateria = (p.valor("kit_bateria_wh") * p.valor("kit_profundidade_descarga")
                    * p.valor("kit_eficiencia_saida_ac"))
    solar_dia = (p.valor("kit_painel_w") / 1000 * p.valor("solar_produtividade_poa") * fator_clima(p, clima)
                 * p.valor("kit_eficiencia_painel_bateria") * p.valor("kit_eficiencia_saida_ac") * 1000)
    disponivel = util_bateria + solar_dia * caso.dias
    cobertura = min(1.0, disponivel / nec["total_wh_periodo"])
    saldo_dia = solar_dia - nec["total_wh_dia"]
    if saldo_dia >= 0:
        dias_cobertos = math.inf
    else:
        dias_cobertos = util_bateria / -saldo_dia
    return {"nome": "Kit solar com bateria", "renovavel": True, "compra_r": p.valor("kit_preco"),
            "operacao_r": 0.0, "litros": 0.0, "co2_kg": 0.0, "cobertura": cobertura,
            "bateria_util_wh": util_bateria, "solar_wh_dia": solar_dia, "disponivel_wh": disponivel,
            "dias_cobertos": dias_cobertos, "clima": clima}


def bateria_necessaria_wh(caso, p):
    """Capacidade nominal de bateria (sem painel) para cobrir todo o período."""
    nec = necessidade(caso, p)
    return nec["total_wh_periodo"] / (p.valor("kit_profundidade_descarga") * p.valor("kit_eficiencia_saida_ac"))


# ----------------------------------------------------------------------------- C) power banks + lanternas
def power_banks(caso, p):
    nec = necessidade(caso, p)
    if caso.geladeira:
        return {"nome": "Power banks e lanternas", "renovavel": False, "compra_r": None, "operacao_r": 0.0,
                "litros": 0.0, "co2_kg": 0.0, "cobertura": 0.0, "unidades": None,
                "observacao": "Não alimenta geladeira."}
    wh_banco = p.valor("banco_mah") / 1000 * p.valor("banco_tensao_v") * p.valor("banco_eficiencia")
    luz_wh_dia = caso.lampadas * p.valor("lanterna_led_w") * p.valor("horas_luz_noite")
    total_wh = (nec["celulares_bateria_wh_dia"] + luz_wh_dia) * caso.dias
    unidades = math.ceil(total_wh / wh_banco) if total_wh > 0 else 0
    compra = unidades * p.valor("banco_preco") + caso.lampadas * p.valor("lanterna_preco")
    return {"nome": "Power banks e lanternas", "renovavel": False, "compra_r": compra, "operacao_r": 0.0,
            "litros": 0.0, "co2_kg": 0.0, "cobertura": 1.0, "unidades": unidades,
            "wh_util_por_banco": wh_banco, "energia_wh": total_wh,
            "observacao": "Pré-carregue antes da chuva. As lanternas iluminam menos que lâmpadas de 8 W."}


# ----------------------------------------------------------------------------- comparação
def custo_total(alternativa, p):
    """Compra + operação de todos os eventos no horizonte (eventos por ano × anos)."""
    if alternativa["compra_r"] is None:
        return None
    eventos = p.valor("eventos_por_ano") * p.valor("anos_horizonte")
    return alternativa["compra_r"] + alternativa["operacao_r"] * eventos


def comparar(caso, p, clima="media"):
    """Lista de alternativas para o mesmo caso e o mesmo período, com custo total no horizonte."""
    linhas = [gerador(caso, p), kit_solar(caso, p, clima), power_banks(caso, p)]
    for linha in linhas:
        linha["custo_total_r"] = custo_total(linha, p)
    return linhas


def sensibilidade_clima(caso, p):
    return [(clima, fator_clima(p, clima), kit_solar(caso, p, clima)) for clima in CLIMAS]


def sensibilidade_horas_gerador(caso, p, horas=(1, 2, 4, 6)):
    resultado = []
    for h in horas:
        g = gerador(caso, p.com(gerador_horas_dia=h))
        resultado.append((h, g["litros"], g["operacao_r"], g["co2_kg"]))
    return resultado


def recomendar(caso, p):
    """Recomendação em texto simples, coerente com os números calculados."""
    linhas = comparar(caso, p)
    gerador_, kit, banco = linhas
    nec = necessidade(caso, p)
    if caso.geladeira:
        bateria = bateria_necessaria_wh(caso, p)
        return [
            f"Para manter uma geladeira ligada por {caso.dias} dia(s) são necessários cerca de "
            f"{nec['total_wh_periodo'] / 1000:.1f} kWh. O kit de {p.valor('kit_bateria_wh'):.0f} Wh cobre só "
            f"{kit['cobertura'] * 100:.0f}% disso; seriam precisos uns {bateria / 1000:.1f} kWh de bateria.",
            "Nesse caso o gerador é a opção que entrega a energia, mas só funciona com segurança ao ar livre, "
            f"com custo de combustível de cerca de R$ {gerador_['operacao_r']:.2f} no período e "
            f"{gerador_['co2_kg']:.1f} kg de CO2.",
            "Power banks não alimentam geladeira.",
        ]
    texto = [
        f"Para {caso.celulares} celular(es) e {caso.lampadas} lâmpada(s) por {caso.dias} dia(s), a tomada precisa "
        f"entregar cerca de {nec['total_wh_periodo']:.0f} Wh.",
        f"Opção mais barata e segura: {banco['unidades']} power bank(s) de 20.000 mAh e lanternas, "
        f"cerca de R$ {banco['compra_r']:.2f}, carregados antes da chuva.",
    ]
    if kit["cobertura"] >= 1.0:
        texto.append(f"Kit solar: cobre o caso (R$ {kit['compra_r']:.2f} de compra). Vale se você quer recarregar "
                     "por vários dias, mas o preço é muito maior e o painel rende menos com chuva.")
    else:
        texto.append(f"Kit solar: cobre {kit['cobertura'] * 100:.0f}% do caso; precisaria de bateria maior.")
    texto.append(f"Gerador: custo de compra R$ {gerador_['compra_r']:.2f} + combustível, e emite "
                 f"{gerador_['co2_kg']:.1f} kg de CO2 no período. Só use ao ar livre, nunca dentro de casa.")
    return texto
