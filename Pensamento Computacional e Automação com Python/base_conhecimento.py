# -*- coding: utf-8 -*-
"""Classe BaseConhecimento: o conjunto de todas as orientações e a busca por pontuação."""

import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ü": "u", "ç": "c"}

# Palavras comuns que aparecem em muitos títulos e não dizem nada sobre o assunto.
# Elas não ganham o ponto extra do título (regra explicada no README).
PALAVRAS_VAZIAS = {"como", "para", "onde", "qual", "quais", "quando", "fazer", "faco",
                   "posso", "preciso", "sobre", "depois", "antes", "durante", "pode",
                   "esta", "esse", "essa", "isso", "mais", "muito", "tenho", "quem"}

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
LIMITE_ALTA = 6      # 6 pontos ou mais: confiança ALTA
LIMITE_MEDIA = 3     # de 3 a 5 pontos: confiança MÉDIA; abaixo disso: "não encontrei"


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação, com um espaço em cada ponta.

    O espaço nas pontas permite procurar palavras inteiras com ' palavra '.
    """
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()\"'-/":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def confianca(pontos):
    """Devolve 'ALTA', 'MEDIA' ou None, conforme a pontuação."""
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    """Lê o JSON, lista as categorias e busca a melhor orientação."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []       # lista de objetos Orientacao
        self.avisos = []            # mensagens sobre problemas ao carregar

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava o programa.

        Devolve True se carregou pelo menos uma orientação.
        """
        self.orientacoes = []
        self.avisos = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.avisos.append(f"Arquivo da base não encontrado: {self.caminho}")
            return False
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.avisos.append(f"O arquivo da base está corrompido: {self.caminho}")
            return False
        except OSError as erro:
            self.avisos.append(f"Não consegui abrir a base ({erro.strerror}).")
            return False

        if not isinstance(dados, list):
            self.avisos.append("A base precisa ser uma lista de orientações.")
            return False

        ids_usados = set()
        for posicao, item in enumerate(dados, start=1):
            try:
                if not isinstance(item, dict):
                    raise ValueError("o registro não é um dicionário")
                orientacao = Orientacao.de_dicionario(item)
                if orientacao.id in ids_usados:
                    raise ValueError(f"id {orientacao.id} repetido")
            except ValueError as erro:
                self.avisos.append(f"Registro {posicao} ignorado: {erro}")
                continue
            ids_usados.add(orientacao.id)
            self.orientacoes.append(orientacao)

        if not self.orientacoes:
            self.avisos.append("Nenhuma orientação válida foi encontrada na base.")
        return bool(self.orientacoes)

    def categorias(self):
        """Lista as categorias, sem repetir, em ordem alfabética."""
        return sorted({o.categoria for o in self.orientacoes})

    def por_categoria(self, categoria):
        """Lista as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, orientacao, pergunta_normalizada):
        """Calcula os pontos de uma orientação para uma pergunta já normalizada.

        +3 por palavra-chave que aparece na pergunta;
        +1 por palavra da pergunta (4 letras ou mais) que aparece no título.
        """
        pontos = 0
        for chave in orientacao.palavras_chave:
            if normalizar(chave) in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE
        titulo = normalizar(orientacao.titulo)
        for palavra in sorted(set(pergunta_normalizada.split())):
            if len(palavra) >= 4 and palavra not in PALAVRAS_VAZIAS and f" {palavra} " in titulo:
                pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a menor pontuação."""
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(orientacao, pergunta_normalizada)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        # maior pontuação primeiro; em empate, o menor id (ordem estável e previsível)
        resultados.sort(key=lambda tupla: (-tupla[0], tupla[1].id))
        return resultados
