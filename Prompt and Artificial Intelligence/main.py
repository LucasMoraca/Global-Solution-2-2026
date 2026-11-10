"""main.py - Citizen Assist AI (documentos pessoais). Uso só com teclado. Nada é gravado em disco."""

from agente.fichas import carregar
from agente.grafo import criar_agente, responder
from agente.llm import criar_llm, nome_provedor
from agente.respostas import MENU_TEXTO

CATEGORIAS = {"1": "FC-01", "2": "FC-02", "3": "FC-03", "4": "FC-04", "5": "FC-05", "6": "FC-06", "7": "FC-07"}

ABERTURA = """Citizen Assist AI - Central do Cidadão de Aurora (material didático fictício)
Sou um protótipo educacional, não um canal oficial. Não digite CPF, RG, telefone, endereço ou e-mail.
Digite o número de um assunto ou escreva sua pergunta. Digite 0 para sair.
"""


def main():
    fichas = carregar()
    llm = criar_llm()  # None sem chave: o agente funciona do mesmo jeito, sem reescrita por IA
    agente = criar_agente(fichas, llm)
    print(ABERTURA)
    print(f"Reescrita por IA: {nome_provedor(llm)}")
    print(MENU_TEXTO)
    while True:
        try:
            texto = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo.")
            break
        if texto == "0":
            print("Até logo.")
            break
        if texto in CATEGORIAS:
            ficha = fichas[CATEGORIAS[texto]]
            print(f"\n{ficha.titulo}")
            codigo = ficha.codigo
            print("\n".join(f"[{codigo}] {s.formatado().replace('**', '')}" for s in ficha.secoes_visiveis()))
            print(f"Fonte: {codigo} (versão e verificação de {ficha.versao}).")
            print("Aviso: sou um protótipo educacional, não um canal oficial. Confirme a informação no órgão competente.")
            continue
        print("\n" + responder(agente, texto))


if __name__ == "__main__":
    main()
