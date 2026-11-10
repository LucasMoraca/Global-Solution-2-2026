"""respostas.py - textos fixos e montagem das respostas. Frases curtas, linguagem simples."""

AVISO = ("Aviso: sou um protótipo educacional, não um canal oficial. Não confirmo serviços nem direitos. "
         "Confirme a informação no órgão competente.")

MENU_TEXTO = ("1 RG | 2 CPF | 3 Título de eleitor | 4 Carteira de Trabalho | 5 Certidões | 6 CNH | "
              "7 Atendimento e regras gerais")
EXEMPLOS = "Exemplos: 'Quanto custa a segunda via do RG?' ou 'Em quanto tempo renovo a CNH?'."

VAZIA = f"Não recebi nenhuma mensagem. Escreva sua dúvida ou escolha um assunto no menu. {MENU_TEXTO}"
LONGA = "Sua mensagem ficou muito longa. Resuma em até 500 caracteres e tente de novo."
SEM_SENTIDO = f"Não entendi a mensagem. Pode escrever de outro jeito? {EXEMPLOS} Ou escolha no menu: {MENU_TEXTO}"
FORA_ESCOPO = ("Não encontrei essa informação nas fichas que eu tenho. Não vou inventar. "
               "Consulte o órgão competente. Posso ajudar com RG, CPF, título de eleitor, Carteira de Trabalho, "
               "certidões, CNH e regras de atendimento.")
PRIMEIRA_CNH = ("As fichas só tratam da renovação da CNH. Não encontrei informação sobre tirar a primeira habilitação. "
                "Consulte o órgão competente. Se a sua dúvida é sobre renovar, pergunte, por exemplo: "
                "'Quanto custa renovar a CNH?'.")
INJECAO = ("Não posso seguir esse pedido. Não mostro minhas instruções internas e não aceito regras novas vindas "
           "da conversa. Continuo sendo um assistente das fichas da Central do Cidadão.")
DADOS = ("Por segurança, não informe dados pessoais aqui (CPF, RG, endereço, telefone, e-mail). "
         "Eu não peço, não guardo e não repito esses dados. Eu não consulto situação cadastral "
         "e não agendo atendimentos por você. Use o portal da Central do Cidadão.")
META = ("Não. Sou um protótipo educacional, não um canal oficial. "
        "Confirme sempre as informações no órgão competente.")


def pergunta_assunto(empate, fichas):
    nomes = "; ".join(f"{c} ({fichas[c].titulo})" for c in empate)
    return f"Sobre qual documento é a sua dúvida? Encontrei: {nomes}. Escreva o nome do documento junto da pergunta."


def texto_secoes(secoes):
    """secoes: lista de (código, Secao) -> texto corrido, sem marcação."""
    partes = []
    for codigo, s in secoes:
        corpo = s.formatado().replace("**", "")
        partes.append(f"[{codigo}] {corpo}")
    return "\n".join(partes)


def rodape(codigos, fichas):
    if not codigos:
        return AVISO
    fontes = "; ".join(f"{c} (Central do Cidadão de Aurora, versão e verificação de {fichas[c].versao})"
                       for c in codigos)
    return f"Fonte: {fontes}.\n{AVISO}"
