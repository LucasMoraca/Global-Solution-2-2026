# Citizen Assist AI - Plantão Enchente: Energia na falta de luz

Entrega de **Soluções em Energias Renováveis e Sustentáveis** (Global Solution FIAP 2026.2, CitizenTech).

## Integrantes
- Gabriel Barbosa Furin - RM 572941
- Lucas Kiodi Moraca - RM 571004
- Renan Fracalossi Mano da Silva - RM 569610

## Público e problema
Moradores de áreas de risco de enchente (referência: Porto Alegre) ficam sem energia por dias. Precisam carregar celulares e ter luz com segurança, e muitos recorrem a velas e geradores dentro de casa. O assistente responde com orientações de segurança e com cálculos de consumo, custo e CO2 de alternativas, uma delas renovável.

## Funções de energia do assistente
1. **Necessidade:** quanto de energia (Wh) para N celulares, N lâmpadas e N dias.
2. **Comparação de 3 alternativas** para a mesma necessidade e o mesmo período (48 h): gerador a gasolina, kit solar com bateria (renovável) e power banks + lanternas. Mostra compra, operação, CO2, cobertura e custo em 5 anos.
3. **Sensibilidade:** solar com nuvens e tempestade, horas de gerador, preço da gasolina, kit mais barato, 7 dias.
4. **Geladeira:** mostra o limite do kit solar e quando só o gerador atende (ao ar livre).
5. **Segurança** (fontes oficiais): gerador e monóxido de carbono, quadro de luz alagado, fio caído, vela.
6. Cada resposta mostra as fontes (S1 a S12) e o aviso de que são estimativas.

## Como rodar
Requer Python 3.9 ou mais novo. Sem bibliotecas externas.

```
python main.py                              # assistente (menu)
python gerar_resultados.py                  # recria as tabelas em resultados/
python -m unittest discover -s testes -v    # 36 testes
```
Exemplos de pergunta: "posso usar gerador na garagem?", "painel solar funciona com chuva?", "quanto custa a gasolina do gerador para 3 dias", "quantos power banks para 4 celulares e 3 dias".

## Estrutura
- `dados/parametros.json`: 35 parâmetros, cada um com valor, unidade, tipo (dado público ou estimado), fonte e nota.
- `dados/fontes.json`: 12 fontes com link.
- `modelo.py`: cálculos. `orientacoes.py`: respostas. `busca.py`: busca por palavras-chave. `main.py`: menu.
- `gerar_resultados.py` e `resultados/`: tabelas e cenários.
- `docs/ANALISE_ENERGETICA.md`: análise, comparação, custos, viabilidade, impactos, limitações e referências.
- `docs/TESTES_USUARIOS.md`: registro dos testes com usuários e ajustes.
- `testes/test_calculo.py`: testes com contas conferidas à mão.

## Resumo dos resultados (nível 1, 48 h)
| Alternativa | Compra | Operação | CO2 | Custo em 5 anos |
|---|---|---|---|---|
| Gerador a gasolina | R$ 1.819,90 | R$ 32,51 | 9,0 kg | R$ 1.982,43 |
| Kit solar (renovável) | R$ 6.079,00 | R$ 0 | 0 | R$ 6.079,00 |
| Power banks + lanternas | R$ 730,00 | R$ 0 | 0 | R$ 730,00 |

## Resultados dos testes
**Testes automatizados:** `python -m unittest discover -s testes -v` roda 36 testes, todos passando (contas conferidas à mão, busca, orientações e os três ajustes feitos depois dos testes com pessoas).

**Testes com usuários (07/11/2026):** 4 pessoas de fora do grupo, com 5 perguntas registradas. Duas foram respondidas direto e corretamente (gerador e vela); três mostraram lacunas ("o que é isso?", carregador portátil e a quem recorrer). Tempo por pessoa: 38 s, 1 min 01 s, 1 min 01 s e 36 s (média de 49 s). Um quinto teste (30 s) veio só com o tempo e não entra na contagem. Nota de facilidade não foi coletada.

| Pergunta | Resultado do teste | Ajuste feito |
|---|---|---|
| "o que é isso?" | Sem resposta | Orientação `ajuda` |
| Gerador em falta de energia | Correta | Nenhum |
| Carregador portátil na enchente | Respondeu outra coisa (quantos power banks) | Orientação `carregador_enchente` |
| A quem recorrer depois de perder tudo | Parcial (quadro de luz) | Orientação `recorrer` |
| Acender vela | Correta | Nenhum |

O reteste das mesmas perguntas no assistente atual (feito pela equipe) está em `docs/TESTES_USUARIOS.md`.

## Limitações
Valores são **estimativas, não garantias**. Parâmetros estimados estão marcados em `parametros.json`. Preços consultados em 05/11/2026. Não há medição em campo. Veja `docs/ANALISE_ENERGETICA.md`.

## Contribuição de energia em repositório compartilhado
Se este conteúdo for colocado no repositório do projeto das outras disciplinas, mantenha-o na pasta `energia/` e aponte esta pasta no README principal.

## IA generativa
Usada como apoio na construção; dados, contas e referências foram conferidos pela equipe.

## Links da entrega
- Repositório GitHub: COLE AQUI
- Vídeo no YouTube (não listado, até 3 min): COLE AQUI
