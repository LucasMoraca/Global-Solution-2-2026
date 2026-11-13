def obter_entrada_valida(nome_variavel, descricao):
    while True:
        entrada = input(f"\n{descricao}\nDigite 1 para SIM ou 0 para NÃO: ").strip()
        if entrada in ("0", "1"):
            return int(entrada)
        print("Entrada inválida! Por favor, digite apenas 0 ou 1.")

def calcular_resultado(a, p):
    return int(a and p)

def obter_orientacao_principal(a, p):
    orientacoes = {
        (0, 0): "Prevenção básica e consulta aos canais oficiais.",
        (0, 1): "Monitore as condições do local, fique atento aos possíveis sinais de risco e acompanhe as orientações da Defesa Civil.",
        (1, 0): "Mantenha as medidas preventivas, acompanhe as condições da região e prepare-se para uma possível situação de emergência.",
        (1, 1): "Orientação reforçada! Acompanhe os alertas oficiais e siga as instruções da Defesa Civil, inclusive quanto à necessidade de evacuação."
    }
    return orientacoes[(a, p)]

def obter_orientacao_documentos(c):
    if c == 0:
        return "Priorize sua segurança! Não coloque sua vida em risco para recuperar documentos. Em um momento seguro, procure os órgãos responsáveis para solicitar segundas vias."
    return "Mantenha seus documentos pessoais protegidos e, se possível, tenha acesso às versões digitais oficiais."

def exibir_aviso_legal():
    print("\n" + "=" * 65)
    print("ATENÇÃO: PLANTÃO ENCHENTE")
    print("Esta ferramenta oferece orientação preliminar.")
    print("Não substitui os alertas e instruções dos órgãos oficiais,")
    print("como Defesa Civil e Corpo de Bombeiros.")
    print("=" * 65)

def exibir_resultado(a, p, c, resultado):
    orientacao = obter_orientacao_principal(a, p)
    documentos = obter_orientacao_documentos(c)
    print("\n" + "=" * 55)
    print("              RESULTADO DA ANÁLISE")
    print("=" * 55)
    print(f"\nEntradas: A={a} | P={p} | C={c}")
    print(f"Classificação lógica (S = A AND P): {resultado}")
    print("\nORIENTAÇÃO PRINCIPAL:")
    print(orientacao)
    print("\nDOCUMENTOS PESSOAIS:")
    print(documentos)
    exibir_aviso_legal()

def main():
    print("=" * 55)
    print("             SISTEMA PLANTÃO ENCHENTE")
    print("=" * 55)
    print("\nOlá! Vamos verificar algumas informações")
    print("para apresentar orientações preventivas.")
    print("Responda às perguntas abaixo utilizando 1 para SIM")
    print("ou 0 para NÃO.\n")
    a = obter_entrada_valida("A", "Você está em uma área oficialmente identificada como área de risco pela Defesa Civil?")
    p = obter_entrada_valida("P", "Existe um alerta oficial ativo da Defesa Civil para a região onde você está?")
    c = obter_entrada_valida("C", "Você tem acesso aos seus documentos pessoais importantes (RG/CIN, CNH, certidões), em formato físico ou digital oficial?")
    resultado = calcular_resultado(a, p)
    exibir_resultado(a, p, c, resultado)

if __name__ == "__main__":
    main()