"""servico.py - o registro (um servico/orientacao ao cidadao)."""

ID_MAXIMO = 999999
LIMITES = {"titulo": 100, "categoria": 40, "descricao": 800,
           "requisitos": 640, "local": 160, "fonte": 200}


class Servico:
    """Um servico ou orientacao ao cidadao, com identificador unico."""

    CAMPOS_TEXTO = ("titulo", "categoria", "descricao", "requisitos", "local", "fonte")

    def __init__(self, id, titulo, categoria, descricao, requisitos, local, fonte):
        self.id = id
        self.titulo = titulo
        self.categoria = categoria
        self.descricao = descricao
        self.requisitos = requisitos
        self.local = local
        self.fonte = fonte

    def copiar(self):
        return Servico(self.id, self.titulo, self.categoria, self.descricao,
                       self.requisitos, self.local, self.fonte)

    def para_dict(self):
        return {"id": self.id, **{campo: getattr(self, campo) for campo in self.CAMPOS_TEXTO}}

    @classmethod
    def de_dict(cls, dados):
        """Cria um Servico a partir de um dicionario. Levanta ValueError se for invalido."""
        if not isinstance(dados, dict):
            raise ValueError("o registro nao e um dicionario")
        faltando = [c for c in ("id",) + cls.CAMPOS_TEXTO if c not in dados]
        if faltando:
            raise ValueError("campos ausentes: " + ", ".join(faltando))
        id_ = dados["id"]
        if isinstance(id_, bool) or not isinstance(id_, int) or not 1 <= id_ <= ID_MAXIMO:
            raise ValueError(f"id invalido (use um inteiro de 1 a {ID_MAXIMO})")
        for campo in cls.CAMPOS_TEXTO:
            valor = dados[campo]
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"campo '{campo}' precisa ser um texto nao vazio")
            if len(valor) > LIMITES[campo]:
                raise ValueError(f"campo '{campo}' passa de {LIMITES[campo]} caracteres")
        return cls(id_, *(dados[c].strip() for c in cls.CAMPOS_TEXTO))

    def detalhes(self):
        return (f"\n[ID {self.id}] {self.titulo}\n"
                f"  Categoria : {self.categoria}\n"
                f"  Descrição : {self.descricao}\n"
                f"  Requisitos: {self.requisitos}\n"
                f"  Local     : {self.local}\n"
                f"  Fonte     : {self.fonte}")

    def linha(self):
        return f"  {self.id:<4} {self.categoria:<27} {self.titulo}"
