"""parametros.py - lê dados/parametros.json e dados/fontes.json (cada número tem origem e tipo)."""

import json
import os

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")


def _ler(nome):
    with open(os.path.join(PASTA_DADOS, nome), "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


class Parametros:
    """Acesso aos parâmetros do cálculo. p.valor('lampada_led_w') devolve o número."""

    def __init__(self, parametros=None, fontes=None):
        self.itens = parametros if parametros is not None else _ler("parametros.json")
        self.fontes = fontes if fontes is not None else _ler("fontes.json")

    def valor(self, nome):
        return self.itens[nome]["valor"]

    def item(self, nome):
        return self.itens[nome]

    def com(self, **alteracoes):
        """Cópia com valores trocados (para análise de sensibilidade)."""
        novos = {k: dict(v) for k, v in self.itens.items()}
        for nome, valor in alteracoes.items():
            novos[nome]["valor"] = valor
        return Parametros(novos, self.fontes)

    def estimados(self):
        return [n for n, i in self.itens.items() if i["tipo"] == "estimado"]
