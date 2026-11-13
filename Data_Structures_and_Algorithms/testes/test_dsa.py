"""Testes automáticos: lista encadeada, busca, ordenação, análise, arquivo, texto e leitura de entrada.

Executar (na pasta do projeto):  python -m unittest discover -s testes -v
"""
import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import armazenamento
import entrada
from analise import contar_por_categoria
from lista import IdDuplicadoError, ListaEncadeada
from ordenacao import ordenar
from servico import Servico
from texto import contem, normalizar


def fazer(id_, titulo="Título", categoria="Cat"):
    return Servico(id_, titulo, categoria, "descrição", "requisitos", "local", "fonte")


def ids(lista):
    """IDs na ordem da lista, percorrendo os nós; confere também o tamanho."""
    resultado = []
    no = lista.inicio
    while no is not None:
        resultado.append(no.dado.id)
        no = no.prox
    assert len(resultado) == lista.tamanho == len(lista), "tamanho inconsistente com o número de nós"
    return resultado


class TestListaVazia(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()

    def test_nova_lista(self):
        self.assertEqual((self.lista.inicio, self.lista.tamanho), (None, 0))

    def test_buscar_em_lista_vazia(self):
        self.assertIsNone(self.lista.buscar_id(1))

    def test_remover_em_lista_vazia(self):
        self.assertFalse(self.lista.remover(1))

    def test_atualizar_em_lista_vazia(self):
        self.assertFalse(self.lista.atualizar(1, fazer(1)))

    def test_percorrer_lista_vazia(self):
        self.assertEqual(list(self.lista), [])

    def test_pesquisar_em_lista_vazia(self):
        self.assertEqual(self.lista.pesquisar("titulo", "a"), [])

    def test_ordenar_lista_vazia(self):
        ordenar(self.lista, "titulo")
        self.assertEqual(ids(self.lista), [])

    def test_analise_lista_vazia(self):
        self.assertEqual(contar_por_categoria(self.lista), [])


class TestInsercao(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        self.lista.inserir_fim(fazer(3))
        self.lista.inserir_fim(fazer(1))
        self.lista.inserir_inicio(fazer(2))

    def test_ordem_apos_insercoes(self):
        self.assertEqual(ids(self.lista), [2, 3, 1])

    def test_duplicado_no_fim(self):
        with self.assertRaises(IdDuplicadoError):
            self.lista.inserir_fim(fazer(3))

    def test_duplicado_no_inicio(self):
        with self.assertRaises(IdDuplicadoError):
            self.lista.inserir_inicio(fazer(1))

    def test_tamanho_nao_muda_com_duplicado(self):
        with self.assertRaises(IdDuplicadoError):
            self.lista.inserir_fim(fazer(2))
        self.assertEqual(ids(self.lista), [2, 3, 1])


class TestBusca(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        for s in (fazer(3, "Água segura", "Saúde"), fazer(1, "alfa serviço", "Dinheiro"),
                  fazer(2, "Beta serviço", "Saúde")):
            self.lista.inserir_fim(s)

    def test_id_existente(self):
        self.assertEqual(self.lista.buscar_id(1).dado.id, 1)

    def test_id_inexistente(self):
        self.assertIsNone(self.lista.buscar_id(99))

    def test_titulo_ignora_maiusculas(self):
        self.assertEqual([s.id for s in self.lista.pesquisar("titulo", "BETA")], [2])

    def test_titulo_ignora_acentos(self):
        self.assertEqual([s.id for s in self.lista.pesquisar("titulo", "agua")], [3])
        self.assertEqual(len(self.lista.pesquisar("titulo", "servico")), 2)

    def test_categoria(self):
        self.assertEqual([s.id for s in self.lista.pesquisar("categoria", "saude")], [3, 2])

    def test_sem_resultado(self):
        self.assertEqual(self.lista.pesquisar("titulo", "inexistente"), [])


class TestAtualizacao(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        for i in (2, 3, 1):
            self.lista.inserir_fim(fazer(i, f"Serviço {i}"))

    def test_atualiza_titulo_e_preserva_id(self):
        self.assertTrue(self.lista.atualizar(3, fazer(777, "Novo título")))
        self.assertEqual(self.lista.buscar_id(3).dado.titulo, "Novo título")
        self.assertIsNone(self.lista.buscar_id(777))

    def test_inexistente(self):
        self.assertFalse(self.lista.atualizar(50, fazer(50)))

    def test_ordem_preservada(self):
        self.lista.atualizar(3, fazer(3, "Outro"))
        self.assertEqual(ids(self.lista), [2, 3, 1])


class TestOrdenacao(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        for s in (fazer(2, "Beta", "Saúde"), fazer(3, "Título novo", "Outra"),
                  fazer(1, "alfa", "Dinheiro"), fazer(4, "Delta", "Alertas")):
            self.lista.inserir_fim(s)

    def test_por_id(self):
        ordenar(self.lista, "id")
        self.assertEqual(ids(self.lista), [1, 2, 3, 4])

    def test_por_titulo_ignora_maiusculas(self):
        ordenar(self.lista, "titulo")
        self.assertEqual(ids(self.lista), [1, 2, 4, 3])

    def test_por_categoria(self):
        ordenar(self.lista, "categoria")
        self.assertEqual(ids(self.lista), [4, 1, 3, 2])

    def test_sequencia_de_ordenacoes(self):
        ordenar(self.lista, "titulo")
        ordenar(self.lista, "id")
        self.assertEqual(ids(self.lista), [1, 2, 3, 4])

    def test_um_unico_no(self):
        unica = ListaEncadeada()
        unica.inserir_fim(fazer(9))
        ordenar(unica, "titulo")
        self.assertEqual(ids(unica), [9])

    def test_lista_ja_ordenada_e_invertida(self):
        grande = ListaEncadeada()
        for i in range(50, 0, -1):
            grande.inserir_fim(fazer(i))
        ordenar(grande, "id")
        self.assertEqual(ids(grande), list(range(1, 51)))

    def test_desempate_por_id(self):
        iguais = ListaEncadeada()
        for i in (3, 1, 2):
            iguais.inserir_fim(fazer(i, "Mesmo título"))
        ordenar(iguais, "titulo")
        self.assertEqual(ids(iguais), [1, 2, 3])


class TestRemocao(unittest.TestCase):
    def setUp(self):
        self.lista = ListaEncadeada()
        for i in (1, 2, 3, 4):
            self.lista.inserir_fim(fazer(i))

    def test_meio(self):
        self.assertTrue(self.lista.remover(2))
        self.assertEqual(ids(self.lista), [1, 3, 4])

    def test_primeiro(self):
        self.assertTrue(self.lista.remover(1))
        self.assertEqual(ids(self.lista), [2, 3, 4])

    def test_ultimo(self):
        self.assertTrue(self.lista.remover(4))
        self.assertEqual(ids(self.lista), [1, 2, 3])

    def test_inexistente(self):
        self.assertFalse(self.lista.remover(99))
        self.assertEqual(ids(self.lista), [1, 2, 3, 4])

    def test_remover_ate_esvaziar_e_reinserir(self):
        for i in (1, 2, 3, 4):
            self.assertTrue(self.lista.remover(i))
        self.assertEqual((self.lista.inicio, self.lista.tamanho), (None, 0))
        self.lista.inserir_fim(fazer(5))
        self.assertEqual(ids(self.lista), [5])

    def test_remover_duas_vezes_o_mesmo_id(self):
        self.assertTrue(self.lista.remover(3))
        self.assertFalse(self.lista.remover(3))


class TestAnalise(unittest.TestCase):
    def test_contagem_por_categoria(self):
        lista = ListaEncadeada()
        for s in (fazer(3, categoria="Saúde"), fazer(1, categoria="Dinheiro"),
                  fazer(2, categoria="saude"), fazer(4, categoria="Alertas")):
            lista.inserir_fim(s)
        contagem = contar_por_categoria(lista)
        self.assertEqual(len(contagem), 3)
        self.assertEqual(dict(contagem)["Saúde"], 2)
        self.assertEqual(sum(q for _, q in contagem), len(lista))


class TestArquivo(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = os.path.join(self.pasta.name, "dados.json")

    def tearDown(self):
        self.pasta.cleanup()

    def test_salvar_e_carregar(self):
        lista = ListaEncadeada()
        for i in (4, 1, 2):
            lista.inserir_fim(fazer(i, f"Serviço {i} ação"))
        armazenamento.salvar(self.caminho, lista)
        outra = ListaEncadeada()
        self.assertEqual(armazenamento.carregar(self.caminho, outra), (3, 0))
        self.assertEqual(ids(outra), [4, 1, 2])
        self.assertEqual(outra.buscar_id(4).dado.titulo, "Serviço 4 ação")

    def test_arquivo_inexistente(self):
        with self.assertRaises(armazenamento.ArquivoAusente):
            armazenamento.carregar(self.caminho, ListaEncadeada())

    def test_json_corrompido(self):
        with open(self.caminho, "w", encoding="utf-8") as f:
            f.write("{ isso nao e json")
        with self.assertRaises(armazenamento.ArquivoCorrompido):
            armazenamento.carregar(self.caminho, ListaEncadeada())

    def test_json_que_nao_e_lista(self):
        with open(self.caminho, "w", encoding="utf-8") as f:
            f.write('{"id": 1}')
        with self.assertRaises(armazenamento.ArquivoCorrompido):
            armazenamento.carregar(self.caminho, ListaEncadeada())

    def test_registros_ruins_sao_ignorados(self):
        bom = fazer(5).para_dict()
        dados = [bom, dict(bom), {"id": 1}, "texto", {**bom, "id": "abc"}, {**bom, "id": 6, "titulo": ""}]
        with open(self.caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f)
        lista = ListaEncadeada()
        self.assertEqual(armazenamento.carregar(self.caminho, lista), (1, 5))
        self.assertEqual(ids(lista), [5])


class TestTexto(unittest.TestCase):
    def test_normalizar(self):
        self.assertEqual(normalizar("Água Çafé"), "agua cafe")

    def test_contem(self):
        self.assertTrue(contem("Saque Calamidade FGTS", "calamidade"))
        self.assertTrue(contem("Saúde", "SAUDE"))
        self.assertFalse(contem("Saque", "xyz"))


class TestValidacaoDeServico(unittest.TestCase):
    def test_id_invalido(self):
        base = fazer(1).para_dict()
        for ruim in (0, -3, 1000000, "7", None, True):
            with self.assertRaises(ValueError):
                Servico.de_dict({**base, "id": ruim})

    def test_campo_vazio_ou_grande_demais(self):
        base = fazer(1).para_dict()
        with self.assertRaises(ValueError):
            Servico.de_dict({**base, "titulo": "   "})
        with self.assertRaises(ValueError):
            Servico.de_dict({**base, "titulo": "A" * 101})


class TestEntrada(unittest.TestCase):
    def _com_teclado(self, respostas, funcao, *args):
        with mock.patch("builtins.input", side_effect=respostas), mock.patch("sys.stdout", new=StringIO()) as saida:
            return funcao(*args), saida.getvalue()

    def test_inteiro_repete_ate_valido(self):
        valor, saida = self._com_teclado(["abc", "", "1_0", "+5", "99", "-1", "7"], entrada.ler_inteiro, "?", 0, 9)
        self.assertEqual(valor, 7)
        self.assertEqual(saida.count("Entrada inválida"), 3)      # abc, 1_0, +5
        self.assertEqual(saida.count("Digite um número"), 1)      # vazio
        self.assertEqual(saida.count("fora do intervalo"), 2)     # 99, -1

    def test_inteiro_gigante(self):
        valor, saida = self._com_teclado(["9" * 40, "3"], entrada.ler_inteiro, "?", 1, 9)
        self.assertEqual(valor, 3)
        self.assertIn("fora do intervalo", saida)

    def test_texto_obrigatorio_e_limite(self):
        valor, saida = self._com_teclado(["", "   ", "x" * 11, " ok "], entrada.ler_texto, "?", 10)
        self.assertEqual(valor, "ok")
        self.assertIn("obrigatório", saida)
        self.assertIn("longo demais", saida)

    def test_texto_opcional_vazio(self):
        valor, _ = self._com_teclado([""], entrada.ler_texto, "?", 10, False)
        self.assertEqual(valor, "")

    def test_sim_nao(self):
        valor, saida = self._com_teclado(["talvez", "", "S"], entrada.ler_sim_nao, "?")
        self.assertTrue(valor)
        self.assertEqual(saida.count("inválida"), 2)

    def test_fim_da_entrada(self):
        with mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(entrada.EntradaEncerrada):
                entrada.ler_inteiro("?", 0, 9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
