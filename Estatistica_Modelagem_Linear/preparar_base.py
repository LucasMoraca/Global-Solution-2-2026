# -*- coding: utf-8 -*-
"""
GLOBAL SOLUTION 2026.2 - CitizenTech | Plantão Enchente
Preparação da base: painel estado x ano de desastres hidrológicos no Brasil (2013-2025).

Integrantes: Gabriel Barbosa Furin (RM 572941) | Lucas Kiodi Moraca (RM 571004)
             Renan Fracalossi Mano da Silva (RM 569610)

Fonte dos dados (REAIS):
  Atlas Digital de Desastres no Brasil (Sedec/MIDR), originado no S2iD, versão consolidada
  v1.1 de 06/08/2026 (https://atlasdigital.mdr.gov.br/). Cada linha é um registro municipal
  de desastre. Os registros foram lidos dos arquivos derivados publicados em
  https://github.com/Leoneldfernandes/desastres-no-brasil (arquivos data/events/*.json.gz).

O que este script faz:
  1) lê os 27 arquivos estaduais;
  2) mantém os registros com data de evento de 2013 a 2025;
  3) agrega por estado (UF) e ano: contagem de registros por tipologia e, para as enchentes
     (Alagamentos + Enxurradas + Inundações), os danos humanos e os prejuízos em R$;
  4) grava enchentes_brasil_uf_ano_2013_2025.csv (a base entregue: 27 UFs x 13 anos = 351 linhas).

Uso:  python preparar_base.py CAMINHO/desastres-no-brasil
Este passo é só para documentar a origem da base; a análise usa apenas o CSV gerado.
"""
import glob
import gzip
import json
import os
import sys

import pandas as pd

RAIZ = sys.argv[1] if len(sys.argv) > 1 else "desastres-no-brasil"
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "enchentes_brasil_uf_ano_2013_2025.csv")

# Ordem oficial das 16 tipologias (índice usado nos arquivos derivados)
TIPOS = ["Alagamentos", "Chuvas Intensas", "Doenças infecciosas", "Enxurradas", "Erosão",
         "Estiagem e Seca", "Granizo", "Incêndio Florestal", "Inundações", "Movimento de Massa",
         "Onda de Calor e Baixa Umidade", "Onda de Frio", "Outros",
         "Rompimento/Colapso de barragens", "Tornado", "Vendavais e Ciclones"]
ENCHENTES = {"Alagamentos", "Enxurradas", "Inundações"}
REGIAO = {**dict.fromkeys(["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "Norte"),
          **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
          **dict.fromkeys(["DF", "GO", "MS", "MT"], "Centro-Oeste"),
          **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"),
          **dict.fromkeys(["PR", "RS", "SC"], "Sul")}

bruto = pd.concat(
    [pd.DataFrame(json.load(gzip.open(a))["rows"], columns=json.load(gzip.open(a))["columns"]).assign(
        uf=os.path.basename(a)[:2]) for a in sorted(glob.glob(os.path.join(RAIZ, "data/events/*.json.gz")))],
    ignore_index=True)
bruto["tipologia"] = bruto["type"].map(dict(enumerate(TIPOS)))
bruto["ano"] = pd.to_datetime(bruto["eventDate"]).dt.year
bruto = bruto[(bruto.ano >= 2013) & (bruto.ano <= 2025)].copy()
bruto["prejuizo"] = bruto["publicLoss"] + bruto["privateLoss"]
enc = bruto[bruto.tipologia.isin(ENCHENTES)]

ufs = sorted(bruto.uf.unique())
base = pd.DataFrame(index=pd.MultiIndex.from_product([ufs, range(2013, 2026)], names=["uf", "ano"]))


def contar(mask):
    return bruto[mask].groupby(["uf", "ano"]).size()


def somar(col):
    return enc.groupby(["uf", "ano"])[col].sum()


base["registros_enchentes"] = contar(bruto.tipologia.isin(ENCHENTES))
base["alagamentos"] = contar(bruto.tipologia == "Alagamentos")
base["enxurradas"] = contar(bruto.tipologia == "Enxurradas")
base["inundacoes"] = contar(bruto.tipologia == "Inundações")
base["chuvas_intensas"] = contar(bruto.tipologia == "Chuvas Intensas")
base["movimento_massa"] = contar(bruto.tipologia == "Movimento de Massa")
base["vendavais_ciclones"] = contar(bruto.tipologia == "Vendavais e Ciclones")
base["estiagem_seca"] = contar(bruto.tipologia == "Estiagem e Seca")
base["mortos_enchentes"] = somar("deaths")
base["feridos_enchentes"] = somar("injured")
base["desabrigados_enchentes"] = somar("homeless")
base["desalojados_enchentes"] = somar("displaced")
base["pessoas_afetadas_enchentes"] = somar("humanTotal")
base["prejuizo_enchentes_rs"] = somar("prejuizo").round(2)
base = base.fillna(0)          # estado-ano sem registro = 0 registros
for c in base.columns:
    if c != "prejuizo_enchentes_rs":
        base[c] = base[c].astype(int)
base = base.reset_index()
base.insert(1, "regiao", base["uf"].map(REGIAO))
base.to_csv(SAIDA, index=False, encoding="utf-8")
print(f"{len(base)} linhas (estado x ano) gravadas em {SAIDA}")
print(f"registros de enchente usados: {int(base.registros_enchentes.sum())} | "
      f"todos os registros 2013-2025 lidos: {len(bruto)}")
