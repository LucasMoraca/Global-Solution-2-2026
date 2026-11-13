"""lista.py - lista simplesmente encadeada implementada pela equipe (sem usar list/deque do Python)."""

from texto import contem


class IdDuplicadoError(Exception):
    """Ja existe um servico com esse identificador."""


class No:
    """Um no da lista: guarda um Servico e uma referencia para o proximo no."""

    def __init__(self, dado):
        self.dado = dado
        self.prox = None


class ListaEncadeada:
    def __init__(self):
        self.inicio = None
        self.tamanho = 0

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        """Percurso: devolve os servicos na ordem da lista. O(n)."""
        atual = self.inicio
        while atual is not None:
            yield atual.dado
            atual = atual.prox

    def buscar_id(self, id_):
        """Busca linear pelo id. Devolve o No ou None. Melhor O(1), pior O(n)."""
        atual = self.inicio
        while atual is not None:
            if atual.dado.id == id_:
                return atual
            atual = atual.prox
        return None

    def inserir_inicio(self, servico):
        """O(n): a ligacao e O(1), mas e preciso checar se o id ja existe."""
        if self.buscar_id(servico.id) is not None:
            raise IdDuplicadoError(servico.id)
        novo = No(servico)
        novo.prox = self.inicio
        self.inicio = novo
        self.tamanho += 1

    def inserir_fim(self, servico):
        """O(n): percorre ate o ultimo no."""
        if self.buscar_id(servico.id) is not None:
            raise IdDuplicadoError(servico.id)
        novo = No(servico)
        if self.inicio is None:
            self.inicio = novo
        else:
            ultimo = self.inicio
            while ultimo.prox is not None:
                ultimo = ultimo.prox
            ultimo.prox = novo
        self.tamanho += 1

    def atualizar(self, id_, novo):
        """Troca os dados do servico. O id nao muda. Devolve False se nao existir. O(n)."""
        alvo = self.buscar_id(id_)
        if alvo is None:
            return False
        novo = novo.copiar()
        novo.id = id_
        alvo.dado = novo
        return True

    def remover(self, id_):
        """Remove o no com esse id (primeiro, meio, fim ou unico). Devolve False se nao existir. O(n)."""
        anterior = None
        atual = self.inicio
        while atual is not None and atual.dado.id != id_:
            anterior = atual
            atual = atual.prox
        if atual is None:
            return False
        if anterior is None:
            self.inicio = atual.prox
        else:
            anterior.prox = atual.prox
        atual.prox = None
        self.tamanho -= 1
        return True

    def pesquisar(self, campo, termo):
        """Servicos cujo 'titulo' ou 'categoria' contem o termo (sem diferenciar maiusculas/acentos). O(n)."""
        achados = []
        for servico in self:
            if contem(getattr(servico, campo), termo):
                achados.append(servico)
        return achados

    def limpar(self):
        self.inicio = None
        self.tamanho = 0
