"""gerar_resultados.py - gera as tabelas de resultados (CSV e Markdown) em resultados/."""

import csv
import math
import os

import modelo as m
from parametros import Parametros

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


def r2(x):
    return "" if x is None else f"{x:.2f}"


def salvar_csv(nome, cabecalho, linhas):
    with open(os.path.join(PASTA, nome), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)


def tabela_md(cabecalho, linhas):
    out = ["| " + " | ".join(cabecalho) + " |", "|" + "---|" * len(cabecalho)]
    out += ["| " + " | ".join(str(c) for c in l) + " |" for l in linhas]
    return "\n".join(out)


def main():
    os.makedirs(PASTA, exist_ok=True)
    p = Parametros()
    md = ["# Resultados gerados por gerar_resultados.py", "",
          "Todos os números são estimativas calculadas a partir de `dados/parametros.json`.", ""]

    # 1. necessidade
    c1, c2 = m.Caso(), m.Caso(geladeira=True)
    n1, n2 = m.necessidade(c1, p), m.necessidade(c2, p)
    cab = ["uso", "nivel1_wh_dia", "nivel2_wh_dia"]
    linhas = [["celulares (tomada)", r2(n1["celulares_tomada_wh_dia"]), r2(n2["celulares_tomada_wh_dia"])],
              ["lâmpadas LED", r2(n1["luz_wh_dia"]), r2(n2["luz_wh_dia"])],
              ["geladeira", r2(n1["geladeira_wh_dia"]), r2(n2["geladeira_wh_dia"])],
              ["total por dia", r2(n1["total_wh_dia"]), r2(n2["total_wh_dia"])],
              ["total em 48 h", r2(n1["total_wh_periodo"]), r2(n2["total_wh_periodo"])]]
    salvar_csv("necessidade.csv", cab, linhas)
    md += ["## 1. Necessidade (Wh)", "", tabela_md(cab, linhas), ""]

    # 2. comparação nível 1 e 2
    for nome, caso in (("nivel1", c1), ("nivel2", c2)):
        cab = ["alternativa", "renovavel", "compra_r", "operacao_48h_r", "co2_kg_48h", "cobertura_pct", "custo_5_anos_r"]
        linhas = [[l["nome"], "sim" if l["renovavel"] else "não", r2(l["compra_r"]), r2(l["operacao_r"]),
                   r2(l["co2_kg"]), f"{l['cobertura'] * 100:.0f}", r2(l["custo_total_r"])]
                  for l in m.comparar(caso, p)]
        salvar_csv(f"comparacao_{nome}.csv", cab, linhas)
        titulo = "Nível 1 (4 celulares + 2 lâmpadas, 48 h)" if nome == "nivel1" else "Nível 2 (nível 1 + geladeira, 48 h)"
        md += [f"## 2. Comparação - {titulo}", "", tabela_md(cab, linhas), ""]

    # 3. sensibilidade solar
    cab = ["clima", "fator", "painel_wh_dia", "disponivel_48h_wh", "cobertura_pct", "dias_cobertos"]
    linhas = []
    for clima, fator, k in m.sensibilidade_clima(c1, p):
        dias = "sem limite" if math.isinf(k["dias_cobertos"]) else f"{k['dias_cobertos']:.1f}"
        linhas.append([m.NOMES_CLIMA[clima], f"{fator:.2f}", r2(k["solar_wh_dia"]), r2(k["disponivel_wh"]),
                       f"{k['cobertura'] * 100:.0f}", dias])
    salvar_csv("sensibilidade_solar.csv", cab, linhas)
    md += ["## 3. Sensibilidade: kit solar e o clima (nível 1, 48 h)", "", tabela_md(cab, linhas), ""]

    # 4. sensibilidade gerador
    cab = ["horas_por_dia", "litros_48h", "combustivel_r", "co2_kg"]
    linhas = [[h, r2(l), r2(r), r2(c)] for h, l, r, c in m.sensibilidade_horas_gerador(c1, p)]
    salvar_csv("sensibilidade_gerador.csv", cab, linhas)
    md += ["## 4. Sensibilidade: horas de gerador por dia (nível 1, 48 h)", "", tabela_md(cab, linhas), ""]

    # 5. cenários de preço e horizonte
    cab = ["cenario", "gerador_5_anos_r", "kit_solar_5_anos_r", "power_banks_5_anos_r"]
    cenarios = [("base (Porto Alegre, 48 h)", p, c1),
                ("gasolina média Brasil", p, m.Caso(cidade_preco="br")),
                ("kit solar -50% de preço", p.com(kit_preco=p.valor("kit_preco") / 2), c1),
                ("7 dias sem luz", p, m.Caso(dias=7)),
                ("3 eventos por ano", p.com(eventos_por_ano=3), c1)]
    linhas = []
    for nome, pp, caso in cenarios:
        a = m.comparar(caso, pp)
        linhas.append([nome] + [r2(x["custo_total_r"]) for x in a])
    salvar_csv("cenarios.csv", cab, linhas)
    md += ["## 5. Cenários (custo total em 5 anos)", "", tabela_md(cab, linhas), ""]
    k7 = m.kit_solar(m.Caso(dias=7), p)
    md += [f"No cenário de 7 dias, o kit solar cobre {k7['cobertura'] * 100:.0f}% (clima médio).", ""]

    # 6. bateria necessária para a geladeira
    md += [f"Bateria sem sol para a geladeira por 48 h: {m.bateria_necessaria_wh(c2, p) / 1000:.2f} kWh "
           f"(kit de {p.valor('kit_bateria_wh'):.0f} Wh).", ""]

    with open(os.path.join(PASTA, "resultados.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
