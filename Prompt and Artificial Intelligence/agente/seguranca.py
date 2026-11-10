"""seguranca.py - validação de entrada, dados pessoais e prompt injection (tudo por regras, sem IA)."""

import re

from agente.textos import contem, normalizar

TAMANHO_MAXIMO = 500

# --- dados pessoais: padrões que viram "[dado oculto]" antes de qualquer processamento ---------------------------
PADROES_PII = [
    ("e-mail", re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")),
    ("CPF", re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")),
    ("telefone", re.compile(r"(?<!\d)(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}(?!\d)")),
    ("CEP", re.compile(r"(?<!\d)\d{5}-\d{3}(?!\d)")),
    ("RG", re.compile(r"(?<!\d)\d{1,2}\.?\d{3}\.?\d{3}-?[0-9xX](?!\d)")),
    ("número longo", re.compile(r"(?<!\d)\d{7,}(?!\d)")),
]
OCULTO = "[dado oculto]"

# frases em que a pessoa anuncia que vai passar dados pessoais (sem ainda passar)
INTENCAO_DADOS = ["meu endereco", "meu telefone", "meu celular", "meu email", "meu e mail", "meu nome e",
                  "meu nome completo", "minha senha", "meu rg e", "meu cpf e", "meu cpf", "vou te passar",
                  "te passar meus", "te passar meu", "vou informar meu"]

# --- prompt injection ------------------------------------------------------------------------------------------
PADROES_INJECAO = ["ignore as instrucoes", "ignore todas as instrucoes", "ignore as regras", "ignore o que",
                   "desconsidere", "esqueca as instrucoes", "esqueca tudo", "prompt de sistema", "system prompt",
                   "suas instrucoes", "seu prompt", "mostre seu prompt", "revele", "nova regra", "novas regras",
                   "sistema", "agora voce e", "finja", "aja como", "modo desenvolvedor", "jailbreak", "dan"]
# "sistema" e "dan" sozinhos são fracos: só valem entre colchetes ou como palavra de comando
FORTES = [p for p in PADROES_INJECAO if p not in ("sistema", "dan")]


def mascarar(texto):
    """Troca dados pessoais por [dado oculto]. Devolve (texto_mascarado, tipos_encontrados)."""
    encontrados = []
    for nome, padrao in PADROES_PII:
        if padrao.search(texto):
            encontrados.append(nome)
            texto = padrao.sub(OCULTO, texto)
    return texto, encontrados


def anuncia_dados(texto):
    t = normalizar(texto)
    return any(contem(t, p) for p in INTENCAO_DADOS)


def detectar_injecao(texto):
    t = normalizar(texto)
    if any(contem(t, p) for p in FORTES):
        return True
    return bool(re.search(r"\[\s*(sistema|system|admin)\s*\]", texto.lower()))


def parece_sem_sentido(texto):
    """Texto sem palavras reconhecíveis: muito símbolo/número ou sequência de teclado."""
    sem_espaco = re.sub(r"\s", "", texto)
    if not sem_espaco:
        return True
    letras = sum(c.isalpha() for c in sem_espaco)
    if letras / len(sem_espaco) < 0.6:
        return True
    palavras = [p for p in normalizar(texto).split() if p.isalpha() and len(p) >= 2]
    if not palavras:
        return True
    def amassada(p):
        return not re.search(r"[aeiou]", p) or re.search(r"[^aeiou]{5,}", p) is not None
    return all(amassada(p) for p in palavras)


def validar(texto):
    """Devolve None se a entrada for aceitável, ou 'vazia' | 'longa' | 'sem_sentido'."""
    if texto is None or not str(texto).strip():
        return "vazia"
    if len(str(texto)) > TAMANHO_MAXIMO:
        return "longa"
    if parece_sem_sentido(str(texto)):
        return "sem_sentido"
    return None
