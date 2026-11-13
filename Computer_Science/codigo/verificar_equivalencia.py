"""Confere as 8 combinações da tabela-verdade do grupo contra o programa teste.py.

Os valores da tabela-verdade foram copiados da página manuscrita do integrante
(colunas A, P, C, S). Este arquivo só COMPARA: não gera a tabela nem a simplificação.
Como rodar:  python verificar_equivalencia.py
"""
from teste import calcular_resultado, obter_orientacao_principal, obter_orientacao_documentos

# (A, P, C, S) copiados da tabela-verdade manuscrita
TABELA = [(1, 1, 1, 1), (0, 1, 1, 0), (1, 0, 1, 0), (0, 0, 1, 0),
          (1, 1, 0, 1), (0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 0)]


def forma_canonica(a, p, c):
    """S = (A.P.C) + (A.P.C')  (expressão canônica do grupo)"""
    nao_c = 1 - c
    return int((a and p and c) or (a and p and nao_c))


def simplificada(a, p):
    """S = A.P  (expressão simplificada do grupo)"""
    return int(a and p)


erros = 0
print("A P C | tabela | canônica | A.P | programa | resultado")
for a, p, c, s in TABELA:
    canonica, simples, programa = forma_canonica(a, p, c), simplificada(a, p), calcular_resultado(a, p)
    ok = s == canonica == simples == programa
    erros += 0 if ok else 1
    print(f"{a} {p} {c} |   {s}    |    {canonica}     |  {simples}  |    {programa}     | {'OK' if ok else 'DIVERGE'}")

# a orientação documental muda com C (e S não muda: S só olha A e P)
assert obter_orientacao_documentos(0) != obter_orientacao_documentos(1)
assert len({obter_orientacao_principal(a, p) for a in (0, 1) for p in (0, 1)}) == 4
print("\nCombinações com divergência:", erros)
