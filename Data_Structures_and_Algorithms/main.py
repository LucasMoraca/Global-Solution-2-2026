"""Citizen Assist AI - Plantão Enchente | Data Structures and Algorithms (GS 2026.2)

Gerenciador de serviços e orientações ao cidadão, com lista encadeada própria,
busca linear própria e Merge Sort próprio.

Integrantes: Gabriel Barbosa Furin (RM 572941), Lucas Kiodi Moraca (RM 571004),
             Renan Fracalossi Mano da Silva (RM 569610)

Como executar:  python main.py   (ou py main.py no Windows)
"""

import os
import sys

import armazenamento
from analise import exibir_analise
from entrada import EntradaEncerrada, ler_id, ler_inteiro, ler_sim_nao, ler_texto
from lista import IdDuplicadoError, ListaEncadeada
from ordenacao import ordenar
from servico import LIMITES, Servico

ARQUIVO_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "servicos.json")

MENU = """
===== CITIZEN ASSIST AI - SERVIÇOS AO CIDADÃO (Plantão Enchente) =====
 1. Cadastrar
 2. Consultar por ID
 3. Atualizar
 4. Excluir
 5. Pesquisar (título ou categoria)
 6. Ordenar
 7. Listar todos
 8. Análise (quantidade por categoria)
 9. Salvar em arquivo
 0. Encerrar"""


class App:
    def __init__(self, caminho):
        self.caminho = caminho
        self.lista = ListaEncadeada()
        self.alterado = False

    # ------------------------------------------------------------ arquivo
    def carregar(self):
        try:
            lidos, ignorados = armazenamento.carregar(self.caminho, self.lista)
            extra = f" ({ignorados} registro(s) inválido(s) ignorado(s))" if ignorados else ""
            print(f"Carregados {lidos} registro(s) de {self.caminho}{extra}.")
        except armazenamento.ArquivoAusente:
            print(f"Arquivo {self.caminho} não encontrado. Iniciando com a lista vazia.")
        except armazenamento.ArquivoCorrompido:
            print(f"O arquivo {self.caminho} está corrompido. Iniciando com a lista vazia.")
        except OSError as erro:
            print(f"Não foi possível abrir o arquivo ({erro.strerror}). Iniciando com a lista vazia.")

    def salvar(self):
        try:
            armazenamento.salvar(self.caminho, self.lista)
        except OSError as erro:
            print(f"Não foi possível salvar em {self.caminho} ({erro.strerror}).")
            return
        print(f"{len(self.lista)} registro(s) salvo(s) em {self.caminho}.")
        self.alterado = False

    # ------------------------------------------------------------ operacoes
    def listar(self):
        if len(self.lista) == 0:
            print("\nA lista está vazia. Cadastre um serviço (opção 1).")
            return
        print(f"\n  {'ID':<4} {'CATEGORIA':<27} TÍTULO")
        for servico in self.lista:
            print(servico.linha())
        print(f"Total: {len(self.lista)} registro(s).")

    def cadastrar(self):
        print("\n--- Cadastrar serviço (digite 0 no ID para cancelar) ---")
        while True:
            id_ = ler_id("ID (número inteiro positivo): ", minimo=0)
            if id_ == 0:
                print("Cadastro cancelado.")
                return
            if self.lista.buscar_id(id_) is not None:
                print(f"Já existe um serviço com o ID {id_}. Escolha outro ID.")
                continue
            break
        campos = [ler_texto(f"{nome}: ", LIMITES[campo]) for campo, nome in (
            ("titulo", "Título"), ("categoria", "Categoria"), ("descricao", "Descrição"),
            ("requisitos", "Requisitos/documentos"), ("local", "Local de atendimento"), ("fonte", "Fonte"))]
        try:
            self.lista.inserir_fim(Servico(id_, *campos))
        except IdDuplicadoError:
            print(f"Erro: o ID {id_} já existe.")
            return
        print(f"Serviço {id_} cadastrado.")
        self.alterado = True

    def consultar(self):
        print("\n--- Consultar por ID ---")
        if len(self.lista) == 0:
            print("A lista está vazia. Nada para consultar.")
            return
        id_ = ler_id("ID: ")
        no = self.lista.buscar_id(id_)
        if no is None:
            print(f"Nenhum serviço encontrado com o ID {id_}.")
        else:
            print(no.dado.detalhes())

    def atualizar(self):
        print("\n--- Atualizar serviço ---")
        if len(self.lista) == 0:
            print("A lista está vazia. Nada para atualizar.")
            return
        id_ = ler_id("ID do serviço a atualizar: ")
        no = self.lista.buscar_id(id_)
        if no is None:
            print(f"Nenhum serviço encontrado com o ID {id_}.")
            return
        print(no.dado.detalhes())
        print("\nDigite o novo valor ou apenas Enter para manter o atual (o ID não muda).")
        novo = no.dado.copiar()
        for campo, nome in (("titulo", "Novo título"), ("categoria", "Nova categoria"),
                            ("descricao", "Nova descrição"), ("requisitos", "Novos requisitos"),
                            ("local", "Novo local"), ("fonte", "Nova fonte")):
            valor = ler_texto(f"{nome}: ", LIMITES[campo], obrigatorio=False)
            if valor:
                setattr(novo, campo, valor)
        self.lista.atualizar(id_, novo)
        print(f"Serviço {id_} atualizado.")
        self.alterado = True

    def excluir(self):
        print("\n--- Excluir serviço ---")
        if len(self.lista) == 0:
            print("A lista está vazia. Nada para excluir.")
            return
        id_ = ler_id("ID do serviço a excluir: ")
        no = self.lista.buscar_id(id_)
        if no is None:
            print(f"Nenhum serviço encontrado com o ID {id_}.")
            return
        print(f"Serviço encontrado: [{no.dado.id}] {no.dado.titulo}")
        if not ler_sim_nao("Confirma a exclusão? (s/n): "):
            print("Exclusão cancelada.")
            return
        self.lista.remover(id_)
        print(f"Serviço {id_} excluído.")
        self.alterado = True

    def pesquisar(self):
        print("\n--- Pesquisar ---")
        if len(self.lista) == 0:
            print("A lista está vazia. Nada para pesquisar.")
            return
        print("1. Por título (contém o texto)\n2. Por categoria (contém o texto)")
        campo = "titulo" if ler_inteiro("Escolha (1 ou 2): ", 1, 2) == 1 else "categoria"
        termo = ler_texto("Texto a procurar: ", LIMITES["titulo"])
        achados = self.lista.pesquisar(campo, termo)
        print(f"\n  {'ID':<4} {'CATEGORIA':<27} TÍTULO")
        if not achados:
            print("  (nenhum resultado)")
            print(f'Nenhum serviço encontrado para "{termo}". Tente outra palavra ou use a opção 7 para ver todos.')
            return
        for servico in achados:
            print(servico.linha())
        print(f"{len(achados)} resultado(s). Use a opção 2 com o ID para ver os detalhes.")

    def ordenar(self):
        print("\n--- Ordenar (Merge Sort) ---")
        if len(self.lista) == 0:
            print("A lista está vazia. Nada para ordenar.")
            return
        print("1. Por ID\n2. Por título\n3. Por categoria")
        opcao = ler_inteiro("Escolha (1 a 3): ", 1, 3)
        ordenar(self.lista, ("id", "titulo", "categoria")[opcao - 1])
        self.alterado = True
        print("Lista ordenada.")
        self.listar()

    # ------------------------------------------------------------ laco principal
    def executar(self):
        self.carregar()
        acoes = {1: self.cadastrar, 2: self.consultar, 3: self.atualizar, 4: self.excluir,
                 5: self.pesquisar, 6: self.ordenar, 7: self.listar,
                 8: lambda: exibir_analise(self.lista), 9: self.salvar}
        try:
            while True:
                print(MENU)
                opcao = ler_inteiro("Opção: ", 0, 9)
                if opcao == 0:
                    if self.alterado and ler_sim_nao("Há alterações não salvas. Salvar antes de sair? (s/n): "):
                        self.salvar()
                    break
                acoes[opcao]()
        except EntradaEncerrada:
            print("\nEntrada encerrada.")
            if self.alterado:
                print("Aviso: as alterações não foram salvas.")
        print("Até logo!")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    App(sys.argv[1] if len(sys.argv) > 1 else ARQUIVO_PADRAO).executar()
