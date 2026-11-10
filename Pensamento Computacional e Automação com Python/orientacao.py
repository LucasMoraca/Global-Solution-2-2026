# -*- coding: utf-8 -*-
"""Classe Orientacao: uma informação da base de conhecimento (um registro do JSON)."""


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    CAMPOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
              "documentos", "onde", "fonte", "verificado_em")

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dicionario(cls, dados):
        """Cria uma Orientacao a partir de um dicionário do JSON.

        Levanta ValueError se faltar algum campo ou se o tipo estiver errado.
        """
        faltando = [c for c in cls.CAMPOS if c not in dados]
        if faltando:
            raise ValueError("campos ausentes: " + ", ".join(faltando))
        if not isinstance(dados["id"], int):
            raise ValueError("id precisa ser número inteiro")
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(dados[campo], str) or not dados[campo].strip():
                raise ValueError(f"campo '{campo}' precisa ser um texto não vazio")
        if not isinstance(dados["palavras_chave"], list) or not dados["palavras_chave"]:
            raise ValueError("palavras_chave precisa ser uma lista não vazia")
        if not isinstance(dados["documentos"], list):
            raise ValueError("documentos precisa ser uma lista")
        return cls(**{campo: dados[campo] for campo in cls.CAMPOS})

    def exibir(self):
        """Mostra a orientação na tela."""
        print(f"\n>> {self.titulo} [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("Documentos necessários: a fonte não informa nenhum.")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente NÃO é um canal oficial.")
