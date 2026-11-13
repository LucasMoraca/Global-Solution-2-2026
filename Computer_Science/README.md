# Computer Science: lógica booleana no Plantão Enchente

Entrega de **Computer Science** (Global Solution FIAP 2026.2, CitizenTech).

## Integrantes
- Gabriel Barbosa Furin - RM 572941
- Lucas Kiodi Moraca - RM 571004
- Renan Fracalossi Mano da Silva - RM 569610

FIAP, 1º ano de Ciência da Computação. Global Solution 2026.2 (tema CitizenTech), projeto **Plantão Enchente / Citizen Assist AI**.

## O que é
Modelagem por lógica booleana de uma decisão do assistente: **S = A AND P**, em que A = o morador está em área de risco, P = há alerta oficial ativo e C = o morador tem acesso aos documentos (a variável C só escolhe a mensagem sobre documentos). O trabalho cobre tabela-verdade, expressão canônica, simplificação, mapa de Karnaugh, circuito lógico original e simplificado, e um programa em Python que implementa a lógica.

O relatório completo está em [`GS2026_CS_Relatorio_Tecnico_Plantao_Enchente.pdf`](GS2026_CS_Relatorio_Tecnico_Plantao_Enchente.pdf).

## Estrutura
| Pasta/arquivo | Conteúdo |
|---|---|
| `GS2026_CS_Relatorio_Tecnico_Plantao_Enchente.pdf` | relatório técnico (tabela-verdade, Karnaugh, circuitos, testes) |
| `codigo/teste.py` | programa interativo em Python (pede A, P e C e mostra a orientação) |
| `codigo/verificar_equivalencia.py` | confere as 8 combinações: tabela x expressão canônica x forma simplificada x programa |
| `codigo/verificacao_saida.txt` | saída da verificação (0 divergências) |
| `prints/` | capturas dos circuitos e das execuções do programa, usadas no relatório |

## Como executar
Só precisa de Python 3, sem instalar nada:

```bash
cd codigo
python teste.py                    # no Windows, se não funcionar: py teste.py
python verificar_equivalencia.py   # compara as 8 combinações
```

## Declaração de uso de IA
Conforme o relatório: a tabela-verdade, a simplificação, o mapa de Karnaugh e os circuitos foram feitos pelos integrantes, sem IA. A IA foi usada apenas para redigir o relatório, conferir as representações e corrigir um erro de digitação no texto de uma mensagem do programa.
