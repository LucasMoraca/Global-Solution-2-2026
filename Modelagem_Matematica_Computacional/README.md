# Modelagem Matemática e Computacional: mobilidade urbana

Entrega de **Modelagem Matemática e Computacional** (Global Solution FIAP 2026.2, CitizenTech).

## Integrantes
- Gabriel Barbosa Furin - RM 572941
- Lucas Kiodi Moraca - RM 571004
- Renan Fracalossi Mano da Silva - RM 569610

FIAP, 1º ano de Ciência da Computação. Global Solution 2026.2 (tema CitizenTech), projeto **Plantão Enchente / Citizen Assist AI**.

## O que é
Notebook sobre a **gestão da frota de ônibus** (modelo-base reaproveitável no Plantão Enchente para evacuação e retorno). Etapa 1: sistema linear 4x4 a partir dos registros operacionais, com representação matricial, Teorema de Rouché-Capelli (determinante, posto, núcleo), resolução à mão e em Python e verificação. Etapa 2: política de redistribuição da frota como **transformação linear**, com demonstração de que preserva o total, não gera alocações negativas e mantém valores inteiros. Termina com indicadores e conclusões. O notebook já está executado, com as saídas visíveis.

## Estrutura
| Arquivo | Conteúdo |
|---|---|
| `GS_Modelagem_Matematica_Computacional.ipynb` | notebook com texto, código e resultados |
| `GS_Modelagem_Matematica_Computacional.html` | mesma versão para leitura no navegador, sem instalar nada |
| `requirements.txt` | bibliotecas usadas |

## Como executar
```bash
pip install -r requirements.txt jupyter
jupyter notebook GS_Modelagem_Matematica_Computacional.ipynb
```
Ou abra no Google Colab (File > Upload notebook) e execute com *Run all*.
