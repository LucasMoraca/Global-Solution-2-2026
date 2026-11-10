# Resultados gerados por gerar_resultados.py

Todos os números são estimativas calculadas a partir de `dados/parametros.json`.

## 1. Necessidade (Wh)

| uso | nivel1_wh_dia | nivel2_wh_dia |
|---|---|---|
| celulares (tomada) | 96.25 | 96.25 |
| lâmpadas LED | 80.00 | 80.00 |
| geladeira | 0.00 | 840.00 |
| total por dia | 176.25 | 1016.25 |
| total em 48 h | 352.50 | 2032.50 |

## 2. Comparação - Nível 1 (4 celulares + 2 lâmpadas, 48 h)

| alternativa | renovavel | compra_r | operacao_48h_r | co2_kg_48h | cobertura_pct | custo_5_anos_r |
|---|---|---|---|---|---|---|
| Gerador a gasolina | não | 1819.90 | 32.51 | 8.98 | 100 | 1982.43 |
| Kit solar com bateria | sim | 6079.00 | 0.00 | 0.00 | 100 | 6079.00 |
| Power banks e lanternas | não | 730.00 | 0.00 | 0.00 | 100 | 730.00 |

## 2. Comparação - Nível 2 (nível 1 + geladeira, 48 h)

| alternativa | renovavel | compra_r | operacao_48h_r | co2_kg_48h | cobertura_pct | custo_5_anos_r |
|---|---|---|---|---|---|---|
| Gerador a gasolina | não | 1819.90 | 32.51 | 8.98 | 100 | 1982.43 |
| Kit solar com bateria | sim | 6079.00 | 0.00 | 0.00 | 39 | 6079.00 |
| Power banks e lanternas | não |  | 0.00 | 0.00 | 0 |  |

## 3. Sensibilidade: kit solar e o clima (nível 1, 48 h)

| clima | fator | painel_wh_dia | disponivel_48h_wh | cobertura_pct | dias_cobertos |
|---|---|---|---|---|---|
| dia médio do ano | 1.00 | 302.94 | 801.72 | 100 | sem limite |
| nublado sem chuva (-25%) | 0.75 | 227.21 | 650.25 | 100 | sem limite |
| nuvens densas (-60%) | 0.40 | 121.18 | 438.19 | 100 | 3.6 |
| tempestade forte (estresse) | 0.10 | 30.29 | 256.43 | 73 | 1.3 |

## 4. Sensibilidade: horas de gerador por dia (nível 1, 48 h)

| horas_por_dia | litros_48h | combustivel_r | co2_kg |
|---|---|---|---|
| 1 | 2.75 | 16.25 | 4.49 |
| 2 | 5.50 | 32.51 | 8.98 |
| 4 | 11.00 | 65.01 | 17.97 |
| 6 | 16.50 | 97.52 | 26.95 |

## 5. Cenários (custo total em 5 anos)

| cenario | gerador_5_anos_r | kit_solar_5_anos_r | power_banks_5_anos_r |
|---|---|---|---|
| base (Porto Alegre, 48 h) | 1982.43 | 6079.00 | 730.00 |
| gasolina média Brasil | 1998.38 | 6079.00 | 730.00 |
| kit solar -50% de preço | 1982.43 | 3039.50 | 730.00 |
| 7 dias sem luz | 2388.74 | 6079.00 | 2160.00 |
| 3 eventos por ano | 2307.48 | 6079.00 | 730.00 |

No cenário de 7 dias, o kit solar cobre 100% (clima médio).

Bateria sem sol para a geladeira por 48 h: 2.66 kWh (kit de 256 Wh).
