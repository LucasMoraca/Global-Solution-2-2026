# -*- coding: utf-8 -*-
"""Citizen Assist AI - assistente de terminal do Plantão Enchente.

Global Solution 2026.2 FIAP (CitizenTech)
Integrantes: Gabriel Barbosa Furin (RM 572941), Lucas Kiodi Moraca (RM 571004),
             Renan Fracalossi Mano da Silva (RM 569610)

Como executar:  python main.py
"""

import os

from assistente import Assistente, AVISO_NAO_OFICIAL
from base_conhecimento import BaseConhecimento

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA, "data")


def main():
    base = BaseConhecimento(os.path.join(PASTA_DADOS, "base_conhecimento.json"))
    base.carregar()
    assistente = Assistente(
        "Citizen Assist AI - Plantão Enchente",
        base,
        os.path.join(PASTA_DADOS, "historico.json"),
        os.path.join(PASTA_DADOS, "atendimentos.csv"),
    )

    print(f"\n=== {assistente.nome} ===")
    print("Orientações para quem mora em área de risco de enchente.")
    print(AVISO_NAO_OFICIAL)
    for aviso in base.avisos:
        print(f"Atenção: {aviso}")

    try:
        while True:
            print("\nMENU PRINCIPAL")
            print("  1. Fazer uma pergunta")
            print("  2. Navegar por categorias")
            print("  3. Ver indicadores")
            print("  4. Exportar atendimentos para CSV")
            print("  0. Sair")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                assistente.perguntar()
            elif opcao == "2":
                assistente.navegar()
            elif opcao == "3":
                assistente.indicadores()
            elif opcao == "4":
                assistente.exportar_csv()
            elif opcao == "0":
                assistente.avaliar_facilidade()
                break
            else:
                print("Opção inválida. Digite 1, 2, 3, 4 ou 0.")
    except (EOFError, KeyboardInterrupt):
        print("\nEncerrando.")
    print("Até logo! Em emergência, ligue 199 (Defesa Civil) ou 193 (Bombeiros).")


if __name__ == "__main__":
    main()
