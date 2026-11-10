"""recuperacao.py - escolhe a ficha (assunto) e as seções (intenção) por palavras-chave. Sem IA: é busca + regras."""

from agente.textos import contem, normalizar

# intenção -> palavras/frases que a revelam (normalizadas)
INTENCOES = {
    "custo": ["custo", "custa", "quanto custa", "quanto pago", "valor", "preco", "taxa", "pago", "paga", "gratuito",
              "gratuita", "gratis"],
    "prazo": ["prazo", "demora", "demorar", "pronto", "pronta", "em quanto tempo", "quanto tempo demora",
              "quando fica", "ate quando", "quanto tempo leva", "tempo leva", "qual e o tempo", "qual o tempo",
              "o tempo para", "tempo estimado", "tempo total", "tempo de espera"],
    "agendamento": ["agendar", "agendamento", "marcar", "marcacao", "preciso marcar"],
    "documentos": ["documento", "documentos", "levar", "boletim", "comprovante", "papeis", "o que preciso", "exigido"],
    "passo": ["passo a passo", "etapas"],
    "geral": ["como faco", "como fazer", "como tirar", "como me inscrever", "inscrever", "inscricao", "como solicitar"],
    "quem": ["quem pode", "sozinho", "sozinha", "filho", "filha", "menor", "crianca", "obrigatorio", "obrigatoria",
             "idade"],
    "onde": ["onde", "local", "endereco do posto"],
    "quando_renovar": ["antecedencia", "venceu", "vencida", "vencido", "vencimento", "dirigir", "quando renovar",
                       "posso renovar"],
    "validade": ["validade", "por quanto tempo vale", "vale a", "valida"],
    "horario": ["sabado", "sabados", "domingo", "feriado", "feriados", "horario de atendimento", "que horas",
                "funcionamento", "atendem", "abre", "fecha"],
    "terceiros": ["outra pessoa", "terceiro", "terceiros", "procuracao", "alguem por mim", "representante"],
    "pagamento": ["pagar", "pagamento", "pix", "boleto", "guia"],
    "libras": ["libras", "interprete", "surdo", "surda", "acessibilidade", "prioritario", "prioridade", "gestante"],
    "privacidade": ["privacidade", "senha", "dados pessoais"],
}
# intenção -> tipos de seção que respondem
SECOES = {"custo": ["custo"], "prazo": ["prazo"], "agendamento": ["agendamento"], "documentos": ["documentos"],
          "passo": ["passo"], "quem": ["quem"], "onde": ["onde"], "quando_renovar": ["quando_renovar"],
          "validade": ["validade"], "horario": ["horario"], "terceiros": ["quem", "terceiros"],
          "pagamento": ["pagamento"], "libras": ["libras"], "privacidade": ["privacidade"],
          "geral": ["custo", "prazo", "agendamento", "passo"]}
# intenções cujas regras gerais ficam na FC-07 e devem ser citadas junto da ficha do documento
COMPLEMENTA_FC07 = {"agendamento": ["agendamento"], "terceiros": ["terceiros"], "pagamento": ["pagamento"],
                    "libras": ["libras"], "horario": ["horario"], "privacidade": ["privacidade"]}
SO_FC07 = {"horario", "pagamento", "libras", "privacidade"}
PALAVRAS_MENOR = ["filho", "filha", "menor", "crianca", "sozinho", "sozinha", "anos de idade"]
PRIMEIRA_HABILITACAO = ["tirar minha cnh", "tirar a cnh", "tirar cnh", "primeira cnh", "primeira habilitacao", "habilitar", "fazer a cnh"]
PERGUNTA_META = ["canal oficial", "e oficial", "prefeitura", "voce e o", "voce e um", "governo", "orgao oficial"]


def pontuar_assuntos(texto_norm, fichas):
    """Pontos por ficha: cada palavra-chave achada vale o número de palavras dela."""
    pontos = {}
    for codigo, ficha in fichas.items():
        total = sum(len(k.split()) for k in ficha.palavras_chave if contem(texto_norm, k))
        if total:
            pontos[codigo] = total
    return pontos


def achar_intencoes(texto_norm):
    achadas = [i for i, termos in INTENCOES.items() if any(contem(texto_norm, t) for t in termos)]
    if "quando_renovar" in achadas and "antecedencia" in texto_norm:
        achadas = [i for i in achadas if i not in ("prazo", "custo")]
    if "geral" in achadas:
        if len(achadas) > 1:  # "como faço" junto de uma pergunta específica: vale só a específica
            achadas.remove("geral")
        else:
            pass
    if "pagamento" in achadas and "custo" in achadas:  # "pago?" e "paga" são custo, não forma de pagamento
        achadas.remove("pagamento")
    return achadas


def eh_pergunta_meta(texto_norm):
    return any(contem(texto_norm, t) for t in PERGUNTA_META)


def buscar(texto, fichas):
    """Devolve dict: assunto (código|None), empate (lista), intencoes, secoes [(codigo, Secao)]."""
    t = normalizar(texto)
    pontos = pontuar_assuntos(t, fichas)
    intencoes = achar_intencoes(t)
    assunto, empate = None, []
    # FC-07 só vale como assunto próprio quando a intenção é geral de atendimento
    pontos_doc = {c: p for c, p in pontos.items() if c != "FC-07"}
    if pontos_doc:
        melhor = max(pontos_doc.values())
        topo = [c for c, p in pontos_doc.items() if p == melhor]
        if len(topo) == 1:
            assunto = topo[0]
        else:
            empate = sorted(topo)
    elif any(i in SO_FC07 or i in ("terceiros", "agendamento") for i in intencoes) or "FC-07" in pontos:
        assunto = "FC-07"
    if assunto is None and not empate:
        return {"assunto": None, "empate": [], "intencoes": intencoes, "secoes": []}
    secoes = []
    if assunto:
        ficha = fichas[assunto]
        if not intencoes:
            secoes = [(assunto, s) for s in ficha.secoes_visiveis()]
        for i in intencoes:
            if i in SO_FC07 and assunto != "FC-07":
                fonte = fichas["FC-07"]
                alvo = [(("FC-07"), s) for tp in SECOES[i] for s in fonte.secoes_do_tipo(tp)]
                secoes += alvo
                continue
            for tp in SECOES[i]:
                secoes += [(assunto, s) for s in ficha.secoes_do_tipo(tp)]
            if assunto != "FC-07" and i in COMPLEMENTA_FC07:
                for tp in COMPLEMENTA_FC07[i]:
                    secoes += [("FC-07", s) for s in fichas["FC-07"].secoes_do_tipo(tp)]
        if "quem" in intencoes and assunto != "FC-07" and any(contem(t, p) for p in PALAVRAS_MENOR):
            secoes += [("FC-07", s) for s in fichas["FC-07"].secoes_do_tipo("terceiros")]
        vistos, unicas = set(), []
        for cod, s in secoes:
            if (cod, s.rotulo) not in vistos:
                vistos.add((cod, s.rotulo))
                unicas.append((cod, s))
        secoes = unicas
        if not secoes:  # intenção pedida que a ficha não tem: mostra a ficha inteira
            secoes = [(assunto, s) for s in ficha.secoes_visiveis()]
    return {"assunto": assunto, "empate": empate, "intencoes": intencoes, "secoes": secoes}


def eh_primeira_habilitacao(texto_norm):
    """Pergunta sobre TIRAR a CNH (as fichas só tratam da renovação)."""
    return any(contem(texto_norm, t) for t in PRIMEIRA_HABILITACAO) and not any(
        contem(texto_norm, t) for t in ("renovar", "renovacao", "renovada"))
