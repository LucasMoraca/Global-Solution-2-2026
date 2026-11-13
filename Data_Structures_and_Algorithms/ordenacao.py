"""ordenacao.py - Merge Sort implementado pela equipe, religando os nos da lista (sem sorted/sort)."""

from lista import No
from texto import normalizar


def chave_id(s):
    return (s.id,)


def chave_titulo(s):
    return (normalizar(s.titulo), s.id)


def chave_categoria(s):
    return (normalizar(s.categoria), normalizar(s.titulo), s.id)


CRITERIOS = {"id": chave_id, "titulo": chave_titulo, "categoria": chave_categoria}


def _dividir(inicio):
    """Divide em duas metades usando dois ponteiros (um anda 1 no, o outro anda 2)."""
    lento, rapido = inicio, inicio.prox
    while rapido is not None:
        rapido = rapido.prox
        if rapido is not None:
            lento = lento.prox
            rapido = rapido.prox
    segunda = lento.prox
    lento.prox = None
    return inicio, segunda


def _mesclar(a, b, chave):
    """Junta duas listas ja ordenadas ligando sempre o menor no primeiro."""
    cabeca = No(None)
    cauda = cabeca
    while a is not None and b is not None:
        if chave(a.dado) <= chave(b.dado):
            cauda.prox = a
            a = a.prox
        else:
            cauda.prox = b
            b = b.prox
        cauda = cauda.prox
    cauda.prox = a if a is not None else b
    return cabeca.prox


def _merge_sort(inicio, chave):
    if inicio is None or inicio.prox is None:
        return inicio
    primeira, segunda = _dividir(inicio)
    return _mesclar(_merge_sort(primeira, chave), _merge_sort(segunda, chave), chave)


def ordenar(lista, criterio):
    """Ordena a lista in-place por 'id', 'titulo' ou 'categoria'. O(n log n)."""
    lista.inicio = _merge_sort(lista.inicio, CRITERIOS[criterio])
