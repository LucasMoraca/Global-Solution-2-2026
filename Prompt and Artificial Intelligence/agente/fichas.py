"""fichas.py - carrega as fichas .md e as divide em seções (custo, prazo, documentos...)."""

import os
import re

from agente.textos import normalizar

PASTA_FICHAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fichas")

# Palavras-chave que as fichas não trazem (FC-07 não tem linha "Palavras-chave"); definidas pelo grupo.
CHAVES_EXTRAS = {"FC-07": ["atendimento", "horario de atendimento", "sabado", "domingo", "feriado", "agendamento",
                           "procuracao", "terceiros", "pagamento", "pix", "libras", "interprete", "acessibilidade",
                           "prioritario", "privacidade"]}

# rótulo da ficha (normalizado, começo) -> tipos de seção
TIPOS = [("custo e prazo", ["custo", "prazo"]), ("custo", ["custo"]), ("prazo", ["prazo"]),
         ("agendamento", ["agendamento"]), ("documentos", ["documentos"]), ("passo a passo", ["passo"]),
         ("quem", ["quem"]), ("onde", ["onde"]), ("quando renovar", ["quando_renovar"]),
         ("validade", ["validade"]), ("atencao", ["atencao"]), ("isencao", ["isencao"]),
         ("horario", ["horario"]), ("atendimento por terceiros", ["terceiros"]), ("pagamento", ["pagamento"]),
         ("atendimento prioritario", ["libras"]), ("perda", ["perda"]), ("privacidade", ["privacidade"]),
         ("fonte", ["fonte"]), ("palavras chave", ["chaves"])]


class Secao:
    def __init__(self, rotulo, texto):
        self.rotulo = rotulo
        self.texto = texto
        norm = normalizar(rotulo)
        self.tipos = []
        for inicio, tipos in TIPOS:
            if norm.startswith(inicio):
                self.tipos = tipos
                break

    def formatado(self):
        return f"{self.rotulo}: {self.texto}".strip()


class Ficha:
    def __init__(self, codigo, titulo, secoes, versao):
        self.codigo, self.titulo, self.secoes, self.versao = codigo, titulo, secoes, versao
        chaves = [s for s in secoes if "chaves" in s.tipos]
        lista = [c.strip() for c in chaves[0].texto.split(",")] if chaves else []
        lista += CHAVES_EXTRAS.get(codigo, [])
        self.palavras_chave = sorted({normalizar(c) for c in lista if normalizar(c)})

    def secoes_do_tipo(self, tipo):
        return [s for s in self.secoes if tipo in s.tipos]

    def secoes_visiveis(self):
        return [s for s in self.secoes if not ({"chaves", "fonte"} & set(s.tipos))]


def _ler_ficha(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.read().splitlines()
    cabecalho = re.match(r"#\s*(FC-\d+)\s*—\s*(.+)", linhas[0])
    codigo, titulo = cabecalho.group(1), cabecalho.group(2).strip()
    secoes, rotulo, corpo = [], None, []

    def fechar():
        if rotulo is not None:
            secoes.append(Secao(rotulo, "\n".join(l for l in corpo if l.strip()).strip()))

    for linha in linhas[1:]:
        m = re.match(r"\*\*(.+?):\*\*\s*(.*)$", linha)
        if m:
            fechar()
            rotulo, corpo = m.group(1), [m.group(2)]
        elif rotulo is not None:
            corpo.append(linha)
    fechar()
    fonte = next((s.texto for s in secoes if "fonte" in s.tipos), "")
    versao = re.search(r"(\d{2}/\d{2}/\d{4})", fonte)
    return Ficha(codigo, titulo, secoes, versao.group(1) if versao else "data não informada")


def carregar(pasta=PASTA_FICHAS):
    fichas = {}
    for nome in sorted(os.listdir(pasta)):
        if nome.startswith("FC-") and nome.endswith(".md"):
            f = _ler_ficha(os.path.join(pasta, nome))
            fichas[f.codigo] = f
    return fichas
