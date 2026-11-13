"""entrada.py - leitura segura do teclado. Repete a pergunta ate a entrada ser valida."""

import re

from servico import ID_MAXIMO


class EntradaEncerrada(Exception):
    """A entrada acabou (Ctrl+D / Ctrl+Z) ou o usuario interrompeu (Ctrl+C)."""


def _ler(pergunta):
    try:
        return input(pergunta).strip()
    except (EOFError, KeyboardInterrupt):
        raise EntradaEncerrada()


def ler_inteiro(pergunta, minimo, maximo):
    while True:
        texto = _ler(pergunta)
        if texto == "":
            print("Digite um número.")
        elif not re.fullmatch(r"-?[0-9]+", texto):
            print("Entrada inválida: digite apenas números inteiros.")
        elif not minimo <= int(texto) <= maximo:
            print(f"Valor fora do intervalo permitido ({minimo} a {maximo}).")
        else:
            return int(texto)


def ler_id(pergunta, minimo=1):
    return ler_inteiro(pergunta, minimo, ID_MAXIMO)


def ler_texto(pergunta, limite, obrigatorio=True):
    while True:
        texto = _ler(pergunta)
        if texto == "":
            if not obrigatorio:
                return ""
            print("Campo obrigatório: não pode ficar vazio.")
        elif len(texto) > limite:
            print(f"Texto longo demais (máximo {limite} caracteres).")
        else:
            return texto


def ler_sim_nao(pergunta):
    while True:
        texto = _ler(pergunta).lower()
        if texto == "s":
            return True
        if texto == "n":
            return False
        print("Resposta inválida: digite s para sim ou n para não.")
