# Análise energética: falta de luz durante enchentes

## 1. Necessidade energética (pública e real)

Moradores de áreas de risco de enchente ficam sem energia elétrica, às vezes por dias. No Rio Grande do Sul, em 31/05/2024, ainda havia cerca de 55 mil consumidores sem luz (S12, dados da ANEEL). Sem energia, a pessoa não carrega o celular (para pedir ajuda e receber alertas) e fica sem luz à noite. Muita gente improvisa com velas e geradores dentro de casa, o que causa incêndio e intoxicação por monóxido de carbono (S1, S2).

- **Recorte:** cidade de referência Porto Alegre; período de referência de **48 horas**.
- **Nível 1 (caso principal):** 4 celulares carregados uma vez por dia + 2 lâmpadas LED de 8 W por 5 h/noite.
- **Nível 2 (mostra o limite):** nível 1 + uma geladeira.

## 2. Consumo (origem, unidade, período, premissas)

| Uso | Conta | Resultado | Tipo |
|---|---|---|---|
| Celulares | 4 × 19,25 Wh ÷ 0,80 (eficiência de carga) | 96,25 Wh/dia | estimado (bateria típica 5.000 mAh × 3,85 V; 0,80 é premissa) |
| Lâmpadas LED | 2 × 8 W × 5 h | 80 Wh/dia | dado público (S5) |
| Geladeira (nível 2) | 25,2 kWh/mês ÷ 30 | 840 Wh/dia | dado público (S5) |
| **Nível 1** | 96,25 + 80 | **176,25 Wh/dia; 352,5 Wh em 48 h** | |
| **Nível 2** | 176,25 + 840 | **1.016,25 Wh/dia; 2.032,5 Wh em 48 h** | |

Os parâmetros ficam em `dados/parametros.json`, cada um marcado como "dado público" ou "estimado", com a fonte (`dados/fontes.json`).

## 3. Alternativas comparadas (mesma necessidade, mesmo período de 48 h)

**A) Gerador a gasolina (não renovável).** Modelo de referência B4T-2500, 2,2 kVA, R$ 1.819,90 (S7).
- Consumo: a ficha do B4T-5000 (S6) dá tanque de 25 L e autonomia de 10 h a 4 kVA. Isso indica 2,5 L/h para 2 kW, ou **1,25 L/kWh** (derivado; fator de potência 1 assumido). A 50% de 2,2 kVA, o gerador gasta 1,375 L/h.
- Perfil típico estimado: ligado 2 h/dia → 4 h em 48 h → **5,5 L**.
- Combustível: 5,5 L × R$ 5,91/L (média de Porto Alegre, ANP, S3) = **R$ 32,51**.
- CO2: 0,74 kg/L × 0,86 × 44/12 ≈ 2,33 kg por litro de gasolina pura (estimativa estequiométrica). Com 30% de etanol (S10), a parcela fóssil é 70%: ≈ 1,63 kg/L. Total: **≈ 9,0 kg de CO2 fóssil** (método do inventário, S11).

**B) Kit solar com bateria (renovável).** Referência: estação portátil de 256 Wh com painel de 110 W, R$ 6.079,00 (S8; o anúncio é inconsistente entre título e descrição, então o preço é só ordem de grandeza).
- Bateria útil: 256 × 0,90 (descarga) × 0,85 (saída AC) = **195,84 Wh**.
- Painel: 0,110 kW × 3,6 kWh/kWp/dia (produtividade anual em Porto Alegre, S4) × 0,90 × 0,85 = **302,94 Wh/dia** em dia médio.
- Em 48 h: 195,84 + 2 × 302,94 = 801,7 Wh, contra 352,5 Wh necessários: **cobertura 100%**.
- Clima: nublado (-25%) e nuvens densas (-60%) vêm de S9. O fator de tempestade forte (0,10) é estimativa nossa, para estresse. Com 0,10, a cobertura cai para **73%** e a bateria sozinha aguenta cerca de 1,3 dia.
- Emissão na operação: 0. Fabricação e descarte da bateria não foram quantificados.

**C) Power banks + lanternas LED (complemento de baixo custo).** 5 power banks de 20.000 mAh (48,1 Wh úteis cada, eficiência 0,65 estimada) + 2 lanternas de 3 W. Custo estimado **R$ 730** (preços estimados, sem fonte confirmada). Precisam ser carregados antes da chuva.

## 4. Resultados (arquivo `resultados/resultados.md`)

| Alternativa (nível 1, 48 h) | Compra | Operação 48 h | CO2 | Cobertura | Custo em 5 anos* |
|---|---|---|---|---|---|
| A) Gerador | R$ 1.819,90 | R$ 32,51 | 9,0 kg | 100% | R$ 1.982,43 |
| B) Kit solar | R$ 6.079,00 | R$ 0 | 0 | 100% (73% em tempestade) | R$ 6.079,00 |
| C) Power banks | R$ 730,00 | R$ 0 | 0 | 100% | R$ 730,00 |

\*1 evento de 48 h por ano, 5 anos (premissa).

**Nível 2 (geladeira):** são necessários 2,03 kWh em 48 h. O kit de 256 Wh cobre só 39%; sem sol, seriam precisos cerca de 2,66 kWh de bateria. Power banks não alimentam geladeira. Só o gerador entrega, e apenas ao ar livre.

## 5. Viabilidade, custos e impactos

- **Custo:** o kit solar não se paga com o combustível economizado (R$ 32,51 por evento contra R$ 4.259 de diferença de compra). Seu valor é não depender de combustível nem de posto aberto, e não gerar CO. Mesmo com preço pela metade, o custo em 5 anos continua maior que o do gerador.
- **Viabilidade:** para o nível 1, power banks resolvem com menor custo. O kit solar vale se a falta de luz pode durar muitos dias. Em 7 dias, os power banks precisariam de mais unidades (R$ 2.160 em 5 anos); o kit solar cobre com sol médio.
- **Ambiental:** o gerador emite CO2 e também CO, ruído e risco de intoxicação. O kit solar e os power banks emitem 0 na operação, mas têm impacto de fabricação e descarte de baterias, não calculado aqui.
- **Segurança:** não é só custo. Gerador exige uso ao ar livre; religar a energia após alagamento exige avaliação profissional (S1, S2).

## 6. Recomendação do assistente

1. Base: power banks carregados + lanternas LED (barato, seguro, sem emissão).
2. Kit solar: se o orçamento permite e a falta de luz pode passar de 2 dias com sol.
3. Gerador: só para cargas pesadas (geladeira), ao ar livre, com alarme de CO.

## 7. Limitações

- Todos os números são **estimativas**, não resultados garantidos.
- Estimados (marcados no JSON): bateria do celular, eficiência de carga, horas de gerador por dia, fator de potência, densidade e carbono da gasolina, fator de tempestade, lanterna, power bank (potência e preço), eventos por ano.
- Preço do kit: anúncio inconsistente (S8). Preços de gerador e kit foram consultados em 05/11/2026 e mudam.
- A produtividade solar é anual (S4), não de dias de enchente. Consumo real do gerador varia com a carga.
- Não há medição em campo; os testes com usuários (docs/TESTES_USUARIOS.md) avaliam clareza, não energia.

## 8. Referências

Ver `dados/fontes.json` (S1 a S12, com link). A resposta de cada orientação do assistente mostra os códigos das fontes usadas.

## 9. Uso de IA generativa

O código e os textos foram elaborados com apoio de IA. A equipe deve conferir os dados nas fontes, refazer as contas (`python -m unittest discover -s testes`) e validar as premissas.
