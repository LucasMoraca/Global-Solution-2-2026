"""main.py - Plantão Enchente / Energia: assistente de energia na falta de luz durante enchentes."""

import busca
import modelo as m
import orientacoes as o
from parametros import Parametros

MENU = """
=== Plantão Enchente - Energia na falta de luz ===
1) Perguntar ao assistente
2) Comparar as 3 alternativas (caso atual)
3) Mudar o caso (celulares, lâmpadas, dias)
4) Ver dados, fontes e o que é estimado
5) Sair
"""


def mostrar(linhas, fontes, p):
    for l in linhas:
        print("  " + l)
    if fontes:
        print("  Fontes: " + ", ".join(f"{s} ({p.fontes[s]['titulo']})" for s in fontes))
    print("  Aviso: " + o.LIMITACAO)


def perguntar(p, caso):
    pergunta = input("Pergunta: ")
    achada = busca.melhor(pergunta)
    if achada is None:
        print("  Não encontrei uma orientação para isso. Tente: gerador, quadro de luz, solar com chuva, power bank, "
              "geladeira, custo de combustível, CO2.")
        return caso
    caso = busca.ajustar_caso(pergunta, caso)
    print(f"\n[{achada['titulo']}]")
    linhas, fontes = o.responder(achada, caso, p)
    mostrar(linhas, fontes, p)
    return caso


def ler_inteiro(texto, padrao):
    bruto = input(f"{texto} [{padrao}]: ").strip()
    return int(bruto) if bruto.isdigit() else padrao


def mudar_caso(caso):
    novo = m.Caso(ler_inteiro("Celulares", caso.celulares), ler_inteiro("Lâmpadas", caso.lampadas),
                  ler_inteiro("Dias sem luz", caso.dias), caso.geladeira, caso.cidade_preco)
    try:
        m.validar(novo)
        return novo
    except ValueError as erro:
        print("  Valores inválidos:", erro)
        return caso


def ver_dados(p):
    print("\nParâmetros (tipo | valor | fonte):")
    for nome, item in p.itens.items():
        print(f"  {nome:34s} {item['tipo']:12s} {item['valor']} {item['unidade']}  [{item['fonte']}]")
    print("\nFontes:")
    for sid, f in p.fontes.items():
        print(f"  {sid}: {f['titulo']} - {f['url']}")


def main():
    p = Parametros()
    caso = m.Caso()
    while True:
        print(MENU)
        op = input("Opção: ").strip()
        if op == "1":
            caso = perguntar(p, caso)
        elif op == "2":
            linhas, fontes = o.calc_comparacao(caso, p)
            mostrar(linhas, fontes, p)
        elif op == "3":
            caso = mudar_caso(caso)
        elif op == "4":
            ver_dados(p)
        elif op == "5":
            print("Até logo. Se a área alagou, não religue a energia sem avaliação.")
            break
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    main()
