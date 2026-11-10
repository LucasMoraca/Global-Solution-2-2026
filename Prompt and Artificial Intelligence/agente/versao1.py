"""versao1.py - PRIMEIRA versão do assistente (linha de base do 'antes').

Só busca a ficha por palavra-chave e devolve a ficha inteira. Tratava apenas mensagem vazia ou longa.
Não tinha proteção de dados pessoais, de prompt injection nem tratamento de texto sem sentido.
"""

from agente.fichas import carregar


class AgenteV1:
    def __init__(self, fichas=None):
        self.fichas = fichas or carregar()

    def responder(self, mensagem):
        if not mensagem or not mensagem.strip():
            return "Digite sua pergunta."
        if len(mensagem) > 500:
            return "Mensagem muito longa."
        texto = mensagem.lower()
        melhor, pontos = None, 0
        for codigo, ficha in self.fichas.items():
            p = sum(1 for k in ficha.palavras_chave if k in texto)  # busca simples por trecho
            if p > pontos:
                melhor, pontos = codigo, p
        if melhor is None:
            return "Não encontrei essa informação nas fichas."
        ficha = self.fichas[melhor]
        corpo = "\n".join(s.formatado() for s in ficha.secoes_visiveis())
        return f"{ficha.titulo}\n{corpo}\nFonte: {melhor}, versão de {ficha.versao}.\nAviso: protótipo educacional."
