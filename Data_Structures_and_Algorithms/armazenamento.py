"""armazenamento.py - persistencia em arquivo JSON."""

import json
import os

from lista import IdDuplicadoError
from servico import Servico


class ArquivoAusente(Exception):
    pass


class ArquivoCorrompido(Exception):
    pass


def carregar(caminho, lista):
    """Le o JSON e insere cada registro valido na lista. Devolve (lidos, ignorados).

    Registros invalidos ou com id repetido sao ignorados.
    """
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        raise ArquivoAusente(caminho)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ArquivoCorrompido(caminho)
    if not isinstance(dados, list):
        raise ArquivoCorrompido(caminho)

    lidos = ignorados = 0
    for item in dados:
        try:
            lista.inserir_fim(Servico.de_dict(item))
            lidos += 1
        except (ValueError, IdDuplicadoError):
            ignorados += 1
    return lidos, ignorados


def salvar(caminho, lista):
    """Grava a lista inteira (escreve num arquivo temporario e troca, para nao corromper)."""
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arquivo:
        json.dump([s.para_dict() for s in lista], arquivo, ensure_ascii=False, indent=2)
    os.replace(temporario, caminho)
