"""grafo.py - agente do Citizen Assist AI (LangGraph). Um agente, nós pequenos e explícitos.

proteger -> classificar -> montar -> reescrever (LLM opcional) -> validar (LLM opcional) -> finalizar
"""

from typing import List, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from agente import llm as modulo_llm
from agente import recuperacao, respostas, seguranca
from agente.fichas import carregar
from agente.textos import normalizar


class Estado(TypedDict, total=False):
    mensagem: str            # texto da pessoa (nunca é guardado)
    segura: str              # texto com dados pessoais ocultos
    pii: List[str]
    anuncia: bool
    invalida: Optional[str]
    injecao: bool
    busca: dict
    rota: str
    corpo: str
    codigos: List[str]
    resposta: str
    reescrito: bool          # True quando a IA reescreveu o texto e a conferência aprovou
    corpo_base: str          # texto vindo direto das fichas (sempre disponível como reserva)
    validacao: str           # nao_executada | aprovada | reprovada | ampliada | indisponivel


def criar_agente(fichas=None, llm=None):
    """llm=None: tudo determinístico. Passe um modelo (ex.: criar_llm_groq()) para reescrever as respostas."""
    fichas = fichas or carregar()

    def proteger(e: Estado) -> Estado:
        bruta = e.get("mensagem") or ""
        segura, pii = seguranca.mascarar(str(bruta))
        return {"segura": segura, "pii": pii, "anuncia": seguranca.anuncia_dados(str(bruta)),
                "invalida": seguranca.validar(segura), "injecao": seguranca.detectar_injecao(str(bruta))}

    def classificar(e: Estado) -> Estado:
        if e["invalida"]:
            return {"rota": e["invalida"]}
        busca = recuperacao.buscar(e["segura"], fichas)
        t = normalizar(e["segura"])
        if e["pii"] or e["anuncia"]:
            rota = "dados"
        elif e["injecao"]:
            rota = "injecao"
        elif recuperacao.eh_pergunta_meta(t):
            rota = "meta"
        elif recuperacao.eh_primeira_habilitacao(t):
            rota = "primeira_cnh"
        elif busca["empate"]:
            rota = "ambiguo"
        elif busca["assunto"]:
            rota = "escopo"
        else:
            rota = "fora_escopo"
        return {"busca": busca, "rota": rota}

    def montar(e: Estado) -> Estado:
        rota, busca = e["rota"], e.get("busca", {})
        secoes, codigos = [], []
        if rota == "vazia":
            corpo = respostas.VAZIA
        elif rota == "longa":
            corpo = respostas.LONGA
        elif rota == "sem_sentido":
            corpo = respostas.SEM_SENTIDO
        elif rota == "meta":
            corpo = respostas.META
        elif rota == "primeira_cnh":
            corpo = respostas.PRIMEIRA_CNH
        elif rota == "ambiguo":
            corpo = respostas.pergunta_assunto(busca["empate"], fichas)
        elif rota == "fora_escopo":
            corpo = respostas.FORA_ESCOPO
        elif rota == "injecao":
            corpo, secoes = respostas.INJECAO, busca.get("secoes", [])
            if secoes:
                corpo += "\nO que consta na ficha:\n" + respostas.texto_secoes(secoes)
        elif rota == "dados":
            assunto = busca.get("assunto")
            secoes = []
            if assunto and assunto != "FC-07":
                secoes += [(assunto, s) for s in fichas[assunto].secoes_do_tipo("atencao")]
                if "agendamento" in busca.get("intencoes", []):
                    secoes += [(assunto, s) for s in fichas[assunto].secoes_do_tipo("agendamento")]
            secoes += [("FC-07", s) for s in fichas["FC-07"].secoes_do_tipo("privacidade")]
            corpo = respostas.DADOS + "\n" + respostas.texto_secoes(secoes)
        else:  # escopo
            secoes = busca["secoes"]
            corpo = respostas.texto_secoes(secoes)
        codigos = sorted({c for c, _ in secoes})
        return {"corpo": corpo, "corpo_base": corpo, "codigos": codigos, "reescrito": False, "validacao": "nao_executada"}

    def reescrever(e: Estado) -> Estado:
        if llm is None or e["rota"] != "escopo":
            return {}
        trechos = e["corpo"]
        novo = modulo_llm.reescrever(llm, e["segura"], trechos, e["codigos"])
        return {"corpo": novo, "reescrito": True} if novo else {}

    def validar(e: Estado) -> Estado:
        """Com chave de API: a IA confere a resposta contra as fichas. Sem chave: nada muda (vale o texto das fichas)."""
        if llm is None or e["rota"] != "escopo":
            return {}
        veredito = modulo_llm.validar(llm, e["segura"], e["corpo_base"], e["corpo"])
        if veredito is None:  # IA indisponível ou resposta fora do formato: volta ao texto das fichas
            return {"corpo": e["corpo_base"], "reescrito": False, "validacao": "indisponivel"}
        if not veredito["fiel"]:
            return {"corpo": e["corpo_base"], "reescrito": False, "validacao": "reprovada"}
        if not veredito["responde"]:  # texto fiel, mas não responde: mostra a ficha inteira
            assunto = e["busca"]["assunto"]
            secoes = [(assunto, s) for s in fichas[assunto].secoes_visiveis()]
            return {"corpo": respostas.texto_secoes(secoes), "corpo_base": respostas.texto_secoes(secoes),
                    "codigos": sorted({c for c, _ in secoes}), "reescrito": False, "validacao": "ampliada"}
        return {"validacao": "aprovada"}

    def finalizar(e: Estado) -> Estado:
        texto = e["corpo"] + "\n" + respostas.rodape(e["codigos"], fichas)
        texto, _ = seguranca.mascarar(texto)  # última barreira: nada de dado pessoal na saída
        return {"resposta": texto}

    grafo = StateGraph(Estado)
    for nome, funcao in (("proteger", proteger), ("classificar", classificar), ("montar", montar),
                         ("reescrever", reescrever), ("validar", validar), ("finalizar", finalizar)):
        grafo.add_node(nome, funcao)
    grafo.add_edge(START, "proteger")
    grafo.add_edge("proteger", "classificar")
    grafo.add_edge("classificar", "montar")
    grafo.add_edge("montar", "reescrever")
    grafo.add_edge("reescrever", "validar")
    grafo.add_edge("validar", "finalizar")
    grafo.add_edge("finalizar", END)
    return grafo.compile()


def responder(agente, mensagem):
    """Executa o agente e devolve só o texto final (o estado interno não é guardado)."""
    return agente.invoke({"mensagem": mensagem})["resposta"]


def responder_completo(agente, mensagem):
    """Devolve dict: resposta, rota, reescrito (bool) e validacao (ver Estado). Nada é guardado."""
    estado = agente.invoke({"mensagem": mensagem})
    return {"resposta": estado["resposta"], "rota": estado.get("rota", ""), "reescrito": bool(estado.get("reescrito", False)),
            "validacao": estado.get("validacao", "nao_executada")}
