"""analise.py - informacoes uteis a partir da lista."""

from texto import normalizar


def contar_por_categoria(lista):
    """Devolve [(categoria, quantidade), ...] na ordem em que cada categoria apareceu. O(n)."""
    nomes = {}
    contagem = {}
    for servico in lista:
        chave = normalizar(servico.categoria)
        if chave not in contagem:
            nomes[chave] = servico.categoria
            contagem[chave] = 0
        contagem[chave] += 1
    return [(nomes[c], contagem[c]) for c in contagem]


def exibir_analise(lista):
    print("\n=== ANÁLISE DOS SERVIÇOS CADASTRADOS ===")
    print(f"Total de registros: {len(lista)}")
    contagens = contar_por_categoria(lista)
    if not contagens:
        print("Não há registros para analisar.")
        return
    print(f"Categorias: {len(contagens)}\n")
    maior = menor = contagens[0]
    for nome, qtd in contagens:
        print(f"{nome:<28} {qtd:>3}  ({100 * qtd / len(lista):5.1f}%) {'#' * qtd}")
        if qtd > maior[1]:
            maior = (nome, qtd)
        if qtd < menor[1]:
            menor = (nome, qtd)
    print(f"\nCategoria com mais registros: {maior[0]} ({maior[1]})")
    print(f"Categoria com menos registros: {menor[0]} ({menor[1]})")
