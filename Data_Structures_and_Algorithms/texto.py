"""texto.py - normalizacao de texto para comparar e pesquisar sem diferenciar maiusculas e acentos."""

import unicodedata


def normalizar(texto):
    """Minusculas e sem acentos: 'Água' -> 'agua'."""
    decomposto = unicodedata.normalize("NFD", texto.casefold())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def contem(texto, trecho):
    """True se 'trecho' aparece em 'texto' (sem diferenciar maiusculas e acentos)."""
    return normalizar(trecho) in normalizar(texto)
