# -*- coding: utf-8 -*-
"""Classe Assistente: conversa com a pessoa, registra o histórico e calcula indicadores.

O Assistente USA uma BaseConhecimento (composição): ele tem uma base dentro dele,
mas não herda dela.
"""

import csv
import json
import os
import re
import time
from datetime import datetime

from base_conhecimento import confianca

AVISO_NAO_OFICIAL = "Aviso: este assistente NÃO é um canal oficial. Em risco imediato, ligue 199 (Defesa Civil) ou 193 (Bombeiros)."
COLUNAS_CSV = ["data", "sessao", "origem", "pergunta", "id", "encontrou",
               "ajudou", "tentativas", "tempo", "nota_facilidade"]
MAX_DIGITOS = 8           # 8 dígitos ou mais seguidos ou não: bloqueia (CPF, telefone, RG...)
TAMANHO_MAX_PERGUNTA = 200


class Assistente:
    """Assistente de terminal: perguntar, navegar, registrar, indicadores e exportar_csv."""

    def __init__(self, nome, base, caminho_historico, caminho_csv):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.historico = []
        self.sessao = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.atendimentos_na_sessao = 0
        self._carregar_historico()

    # ------------------------------------------------------------------ histórico
    def _carregar_historico(self):
        """Lê data/historico.json. Se faltar ou estiver corrompido, começa vazio sem travar."""
        self.historico = []
        if not os.path.exists(self.caminho_historico):
            return
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list):
                raise ValueError("o histórico não é uma lista")
            self.historico = [item for item in dados if isinstance(item, dict)]
        except (OSError, ValueError, UnicodeDecodeError):
            # ValueError cobre JSONDecodeError. Guarda uma cópia do arquivo ruim e recomeça.
            copia = self.caminho_historico + ".corrompido"
            try:
                os.replace(self.caminho_historico, copia)
                print(f"Aviso: o histórico estava ilegível. Guardei uma cópia em {os.path.basename(copia)} e comecei um novo.")
            except OSError:
                print("Aviso: o histórico estava ilegível. Comecei um novo em memória.")
            self.historico = []

    def _salvar_historico(self):
        """Grava o histórico no disco (escreve em arquivo temporário e troca, para não corromper)."""
        temporario = self.caminho_historico + ".tmp"
        try:
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho_historico)
            return True
        except OSError:
            print("Aviso: não consegui salvar o histórico no disco. Os dados ficam só nesta execução.")
            return False

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        """Guarda um atendimento no histórico. Dados pessoais nunca chegam aqui."""
        registro = {
            "tipo": "atendimento",
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,
            "pergunta": pergunta[:TAMANHO_MAX_PERGUNTA],
            "id": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo": round(tempo, 1),
        }
        self.historico.append(registro)
        self.atendimentos_na_sessao += 1
        self._salvar_historico()

    def avaliar_facilidade(self):
        """Pergunta a nota de 1 a 5 ao sair e guarda no histórico."""
        if self.atendimentos_na_sessao == 0:
            return
        while True:
            texto = self._ler("De 1 a 5, quão fácil foi usar o assistente? (0 para pular): ")
            if texto == "0":
                return
            if texto in ("1", "2", "3", "4", "5"):
                self.historico.append({"tipo": "avaliacao", "sessao": self.sessao,
                                       "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       "nota_facilidade": int(texto)})
                self._salvar_historico()
                print("Obrigado pela nota!")
                return
            print("Opção inválida. Digite um número de 1 a 5, ou 0 para pular.")

    # ------------------------------------------------------------------ entrada
    @staticmethod
    def _ler(mensagem):
        """Lê uma linha do teclado, sem espaços nas pontas."""
        return input(mensagem).strip()

    def _ler_sim_nao(self, mensagem):
        """Repete até receber 's', 'n' ou '0'. Devolve 's', 'n' ou '0'."""
        while True:
            texto = self._ler(mensagem).lower()
            if texto in ("s", "n", "0"):
                return texto
            print("Opção inválida. Digite s para sim, n para não ou 0 para voltar.")

    @staticmethod
    def tem_dados_pessoais(texto):
        """True se o texto parece conter dado pessoal: '@' ou 8+ dígitos (CPF, telefone, RG...)."""
        if "@" in texto:
            return True
        return len(re.sub(r"\D", "", texto)) >= MAX_DIGITOS

    # ------------------------------------------------------------------ perguntar
    def perguntar(self):
        """Fluxo de pergunta livre: busca na base e mostra a melhor orientação e alternativas."""
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível, então não consigo responder agora.")
            return
        inicio = time.time()
        tentativas = 0
        ultima = ""
        while True:
            texto = self._ler("\nDigite sua dúvida (0 para voltar): ")
            if texto == "0":
                if tentativas > 0:
                    self.registrar("pergunta", ultima, None, False, None, tentativas, time.time() - inicio)
                return
            if not texto:
                print("Você não digitou nada. Escreva sua dúvida com algumas palavras.")
                continue
            if self.tem_dados_pessoais(texto):
                print("Por segurança, NÃO digite dados pessoais (CPF, telefone, e-mail, endereço).")
                print("Essa mensagem não foi registrada. Escreva sua dúvida sem esses dados.")
                continue

            tentativas += 1
            ultima = texto
            resultados = [(p, o) for p, o in self.base.buscar(texto) if confianca(p)]
            if not resultados:
                print("\nNão encontrei uma orientação para essa pergunta.")
                print("Tente outras palavras (ex.: 'enchente', 'água', 'FGTS', 'alerta') ou use a opção de categorias:")
                for categoria in self.base.categorias():
                    print(f"  - {categoria}")
                print(AVISO_NAO_OFICIAL)
                escolha = self._ler_sim_nao("Quer tentar de novo com outras palavras? (s/n, 0 para voltar): ")
                if escolha == "s":
                    continue
                self.registrar("pergunta", texto, None, False, None, tentativas, time.time() - inicio)
                return

            pontos, melhor = resultados[0]
            print(f"\nConfiança: {confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()
            if confianca(pontos) == "MÉDIA":
                print("Atenção: esta é a orientação mais próxima da sua pergunta e pode não responder exatamente "
                      "ao que você quer saber. Veja as outras opções abaixo.")
            alternativas = [o for _, o in self.base.buscar(texto)[1:3]]
            if alternativas:
                print("\nOutras orientações possíveis:")
                for numero, alternativa in enumerate(alternativas, start=1):
                    print(f"  {numero}. {alternativa.titulo}")
            mostrada = melhor
            escolha = self._ler_sim_nao("\nA resposta ajudou? (s/n, 0 para voltar): ")
            if escolha == "n" and alternativas:
                mostrada, escolha = self._oferecer_alternativa(alternativas, mostrada)
                tentativas += 1 if mostrada is not melhor else 0
            ajudou = True if escolha == "s" else False if escolha == "n" else None
            self.registrar("pergunta", texto, mostrada.id, True, ajudou, tentativas, time.time() - inicio)
            return

    def _oferecer_alternativa(self, alternativas, atual):
        """Deixa a pessoa abrir uma alternativa. Devolve (orientação mostrada, resposta s/n/0)."""
        while True:
            texto = self._ler("Quer abrir uma alternativa? Digite o número dela (0 para não): ")
            if texto == "0":
                return atual, "n"
            if texto.isdigit() and 1 <= int(texto) <= len(alternativas):
                escolhida = alternativas[int(texto) - 1]
                escolhida.exibir()
                return escolhida, self._ler_sim_nao("\nEssa resposta ajudou? (s/n, 0 para voltar): ")
            print(f"Opção inválida. Digite um número de 1 a {len(alternativas)} ou 0.")

    # ------------------------------------------------------------------ navegar
    def navegar(self):
        """Navegação por categorias: categoria -> lista de orientações -> orientação."""
        categorias = self.base.categorias()
        if not categorias:
            print("A base de conhecimento não está disponível, então não há categorias para mostrar.")
            return
        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"  {numero}. {categoria}")
            texto = self._ler("Escolha uma categoria (0 para voltar): ")
            if texto == "0":
                return
            if not (texto.isdigit() and 1 <= int(texto) <= len(categorias)):
                print(f"Opção inválida. Digite um número de 1 a {len(categorias)} ou 0.")
                continue
            self._navegar_categoria(categorias[int(texto) - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\n{categoria}:")
            for numero, orientacao in enumerate(orientacoes, start=1):
                print(f"  {numero}. {orientacao.titulo}")
            texto = self._ler("Escolha uma orientação (0 para voltar): ")
            if texto == "0":
                return
            if not (texto.isdigit() and 1 <= int(texto) <= len(orientacoes)):
                print(f"Opção inválida. Digite um número de 1 a {len(orientacoes)} ou 0.")
                continue
            inicio = time.time()
            escolhida = orientacoes[int(texto) - 1]
            escolhida.exibir()
            resposta = self._ler_sim_nao("\nA resposta ajudou? (s/n, 0 para voltar): ")
            ajudou = True if resposta == "s" else False if resposta == "n" else None
            self.registrar("categoria", escolhida.titulo, escolhida.id, True, ajudou, 1, time.time() - inicio)

    # ------------------------------------------------------------------ indicadores
    def _atendimentos(self):
        return [r for r in self.historico if r.get("tipo", "atendimento") == "atendimento"]

    def _notas(self):
        return [r["nota_facilidade"] for r in self.historico
                if r.get("tipo") == "avaliacao" and isinstance(r.get("nota_facilidade"), int)]

    def indicadores(self):
        """Calcula e mostra os indicadores. Devolve um dicionário com os valores."""
        atendimentos = self._atendimentos()
        total = len(atendimentos)
        if total == 0:
            print("\nAinda não há atendimentos registrados para calcular indicadores.")
            return {"total": 0}

        encontrados = [r for r in atendimentos if r.get("encontrou")]
        avaliados = [r for r in encontrados if r.get("ajudou") is not None]
        ajudaram = [r for r in avaliados if r.get("ajudou")]
        tempos = [r["tempo"] for r in atendimentos if isinstance(r.get("tempo"), (int, float))]
        tentativas = [r["tentativas"] for r in atendimentos if isinstance(r.get("tentativas"), int)]
        notas = self._notas()
        sem_solucao = [r for r in atendimentos if not r.get("encontrou") or r.get("ajudou") is False]

        resultado = {
            "total": total,
            "pct_encontrada": 100 * len(encontrados) / total,
            "pct_ajudou": (100 * len(ajudaram) / len(avaliados)) if avaliados else None,
            "tempo_medio": (sum(tempos) / len(tempos)) if tempos else None,
            "tentativas_medias": (sum(tentativas) / len(tentativas)) if tentativas else None,
            "facilidade_media": (sum(notas) / len(notas)) if notas else None,
            "sem_solucao": len(sem_solucao),
        }

        def formatar(valor, sufixo=""):
            return "sem dados" if valor is None else f"{valor:.1f}{sufixo}"

        print("\n===== INDICADORES =====")
        print(f"Atendimentos registrados: {total}")
        print(f"Resposta encontrada: {formatar(resultado['pct_encontrada'], '%')}")
        print(f"Resposta que ajudou: {formatar(resultado['pct_ajudou'], '%')} (entre as avaliadas)")
        print(f"Tempo médio por atendimento: {formatar(resultado['tempo_medio'], ' s')}")
        print(f"Tentativas médias por atendimento: {formatar(resultado['tentativas_medias'])}")
        print(f"Facilidade de uso (nota média 1-5): {formatar(resultado['facilidade_media'])}")
        print(f"Dúvidas sem solução: {len(sem_solucao)}")
        for r in sem_solucao[-5:]:
            motivo = "não encontrada" if not r.get("encontrou") else "não ajudou"
            print(f"  - \"{r.get('pergunta', '')}\" ({motivo})")
        return resultado

    # ------------------------------------------------------------------ CSV
    def exportar_csv(self):
        """Exporta os atendimentos para data/atendimentos.csv. Devolve True se deu certo."""
        atendimentos = self._atendimentos()
        nota_por_sessao = {r.get("sessao"): r["nota_facilidade"] for r in self.historico
                           if r.get("tipo") == "avaliacao" and isinstance(r.get("nota_facilidade"), int)}
        try:
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for r in atendimentos:
                    linha = dict(r)
                    linha["nota_facilidade"] = nota_por_sessao.get(r.get("sessao"), "")
                    escritor.writerow(linha)
        except OSError as erro:
            print(f"Não consegui gravar o CSV ({erro.strerror}). Se ele estiver aberto em outro programa, feche-o e tente de novo.")
            return False
        print(f"CSV exportado com {len(atendimentos)} atendimento(s): {self.caminho_csv}")
        return True
