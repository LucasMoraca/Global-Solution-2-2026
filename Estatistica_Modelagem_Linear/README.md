# Estatística: modelagem linear das enchentes no Brasil

Entrega de **Modelagem Linear para Aprendizado de Máquina** (Global Solution FIAP 2026.2, CitizenTech).

## Integrantes
- Gabriel Barbosa Furin - RM 572941
- Lucas Kiodi Moraca - RM 571004
- Renan Fracalossi Mano da Silva - RM 569610

FIAP, 1º ano de Ciência da Computação. Global Solution 2026.2 (tema CitizenTech), projeto **Plantão Enchente / Citizen Assist AI**.

## O que é
Análise estatística de uma base **real** de enchentes do Brasil (27 UFs x 13 anos, de 2013 a 2025, 351 linhas): estatística descritiva, distribuição normal, testes Z, correlação bivariada e multivariada, regressão linear simples e múltipla (com diagnóstico de resíduos e VIF) e regressão logística com validação cruzada. Resultados e figuras alimentam a seção de dados do projeto Plantão Enchente (por exemplo, o Sul concentra 42% dos registros).

**Fonte dos dados:** Atlas Digital de Desastres no Brasil (Sedec/MIDR), originado no S2iD, versão consolidada v1.1 (06/08/2026). Enchente = alagamentos + enxurradas + inundações. A base derivada foi montada com `preparar_base.py` a partir do repositório público <https://github.com/Leoneldfernandes/desastres-no-brasil>.

## Estrutura
| Arquivo | Conteúdo |
|---|---|
| `Relatorio_Estatistico_Plantao_Enchente.pdf` | relatório com métodos, resultados e interpretação |
| `analise_enchentes.py` | toda a análise (tabelas no terminal, figuras e `resultados.json`) |
| `preparar_base.py` | como a base foi construída a partir dos dados originais |
| `enchentes_brasil_uf_ano_2013_2025.csv` | base usada (351 linhas) |
| `resultados.json` | números calculados |
| `figuras/` | 10 figuras do relatório |

## Como executar
```bash
pip install -r requirements.txt
python analise_enchentes.py
```
O CSV precisa estar na mesma pasta do script. A execução regera `figuras/` e `resultados.json` (resultado determinístico: números idênticos aos entregues).
