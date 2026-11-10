"""textos.py - normalização de texto usada por todo o agente."""

import re
import unicodedata
from difflib import SequenceMatcher


def normalizar(texto):
    """minúsculas, sem acento, só letras e números separados por espaço."""
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]", " ", texto)).strip()


def contem(texto_normalizado, termo_normalizado):
    """True se o termo (palavra ou frase) aparece com limites de palavra.

    Para termos de UMA palavra com 7+ letras, aceita também um erro de digitação
    (mesma letra inicial, tamanho parecido e semelhança de 88% ou mais).
    """
    if f" {termo_normalizado} " in f" {texto_normalizado} ":
        return True
    if " " in termo_normalizado or len(termo_normalizado) < 7:
        return False
    for palavra in texto_normalizado.split():
        if (palavra[:1] == termo_normalizado[:1] and abs(len(palavra) - len(termo_normalizado)) <= 1
                and SequenceMatcher(None, palavra, termo_normalizado).ratio() >= 0.88):
            return True
    return False
