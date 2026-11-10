"""busca.py - encontra a orientação mais próxima da pergunta (palavras-chave, sem IA externa)."""

import re
import unicodedata

import orientacoes as o
import modelo as m

PALAVRAS_VAZIAS = {"qual", "quais", "como", "quanto", "quanta", "quantos", "para", "sobre", "dentro", "preciso"}


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", texto)


def pontuar(pergunta, orientacao):
    palavras = set(normalizar(pergunta).split())
    pontos = 3 * sum(1 for k in orientacao["palavras"] if k in palavras)
    pontos += sum(1 for w in normalizar(orientacao["titulo"]).split() if len(w) >= 4 and w not in PALAVRAS_VAZIAS and w in palavras)
    return pontos


def melhor(pergunta):
    """Orientação com mais pontos, ou None se nenhuma pontuar."""
    if not pergunta.strip():
        return None
    ranking = sorted(((pontuar(pergunta, x), x) for x in o.todas()), key=lambda t: -t[0])
    return ranking[0][1] if ranking and ranking[0][0] > 0 else None


def ajustar_caso(pergunta, caso):
    """Lê números da pergunta ('3 celulares', '4 dias', '2 lampadas') e devolve um Caso novo."""
    t = normalizar(pergunta)
    def achar(regex, padrao):
        r = re.search(regex, t)
        return int(r.group(1)) if r else padrao
    novo = m.Caso(achar(r"(\d+) celular", caso.celulares), achar(r"(\d+) (?:lampada|luz|luzes)", caso.lampadas),
                  achar(r"(\d+) dia", caso.dias), caso.geladeira, caso.cidade_preco)
    try:
        m.validar(novo)
        return novo
    except ValueError:
        return caso
