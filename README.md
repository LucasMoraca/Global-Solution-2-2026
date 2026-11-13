# Plantão Enchente · Citizen Assist AI

**Quando a água sobe, a informação certa não pode esperar.**

Projeto da **Global Solution 2026.2 · FIAP** (tema **CitizenTech**), 1º ano de Ciência da Computação.

O Plantão Enchente combina um **sensor de nível de rio (Estação Sentinela)** com um **assistente digital** que avisa o morador e diz o que fazer: orientações de segurança, documentos perdidos e energia na falta de luz. Cada disciplina da GS construiu uma peça do mesmo sistema.

## Equipe

| Integrante | RM |
|---|---|
| Gabriel Barbosa Furin | 572941 |
| Lucas Kiodi Moraca | 571004 |
| Renan Fracalossi Mano da Silva | 569610 |

## O problema

Segundo o Atlas Digital de Desastres no Brasil (S2iD, MIDR), de 2013 a 2025 foram **6.750 registros de enchente** em municípios brasileiros, com **373 mortes** e **2.983.595 pessoas afetadas**. O **Sul concentra 42%** dos registros. A água sobe rápido, mas o aviso e a orientação certa costumam chegar tarde, e na hora do susto o morador não sabe o que fazer. (Análise estatística do grupo, em `Estatística`.)

## A solução

```
 Estação Sentinela ──► Lógica de decisão ──► Citizen Assist AI ──► Morador
 (nível, chuva,         (álgebra booleana:     ├─ Orientações oficiais (16, com fonte e data)
  velocidade da          área de risco,        ├─ Documentos perdidos (agente com IA, 7 fichas)
  subida, 4 níveis       alerta ativo,         └─ Energia na falta de luz (gerador x solar x power banks)
  de risco)              documentos)
                                  Base: estruturas de dados (lista encadeada, Merge Sort)
                                  Dados: estatística das enchentes no Brasil
```

## Repositórios por disciplina

| Disciplina | O que entrega | Repositório | Vídeo |
|---|---|---|---|
| Pensamento Computacional e Automação com Python | Assistente de orientações em Python: dicionários e tuplas, OO, busca por regras com nível de confiança (ALTA/MÉDIA), proteção de dados e indicadores em arquivo | [link](COLE_AQUI) | [link](COLE_AQUI) |
| Soluções em Energias Renováveis e Sustentáveis | Comparação de gerador, kit solar e power banks para 4 celulares e 2 lâmpadas por 48 h (352 Wh), com custos, CO₂, limitações e aviso de monóxido de carbono | [link](COLE_AQUI) | [link](COLE_AQUI) |
| Prompt and Artificial Intelligence | Agente de documentos perdidos (LangGraph) com 7 fichas verificadas, guardrails (LGPD, escopo, prompt injection) e avaliação | [link](COLE_AQUI) | n/a |
| Computer Organization and Architecture | Estação Sentinela: Raspberry Pi Pico, sensor ultrassônico, LEDs, buzzer, LCD I2C, MicroPython (simulada no Wokwi) | [link](COLE_AQUI) | [YouTube](https://youtu.be/GP1SGBqTki4) |
| Data Structures and Algorithms | Gerenciador de serviços com lista encadeada própria, busca linear e Merge Sort, em Python (50 testes) | [link](COLE_AQUI) | n/a |
| Computer Science | Lógica booleana `S = A AND P`: tabela-verdade, Karnaugh, circuitos e programa em Python | [link](COLE_AQUI) | n/a |
| Modelagem Linear para Aprendizado de Máquina (Estatística) | Análise de 351 linhas (27 UFs x 13 anos): descritiva, testes Z, correlação, regressões linear e logística | [link](COLE_AQUI) | n/a |
| Modelagem Matemática e Computacional | Gestão da frota de ônibus: sistema linear 4x4 e redistribuição como transformação linear | [link](COLE_AQUI) | n/a |

## Como as peças se encaixam

1. **Sentinela** (COA) mede o nível do rio (200 cm menos a distância até a água), a chuva e a velocidade da subida. Classifica o risco em **NORMAL, ATENÇÃO, ALERTA e EMERGÊNCIA** (limiares hipotéticos de 80, 120 e 160 cm, com histerese de 5 cm). Subida de 10 cm/min ou mais, ou chuva forte com o rio já alto, elevam o risco um nível. Acende LEDs, toca o buzzer e mostra tudo no LCD; um botão silencia o alarme por 60 s.
2. **Lógica de decisão** (CS): `S = A AND P` (A = morador em área de risco, P = alerta oficial ativo) aciona a orientação reforçada: acompanhar os alertas oficiais e seguir a Defesa Civil, inclusive evacuação. A variável C define a mensagem sobre documentos pessoais.
3. **Assistente de orientações** (Python): o morador pergunta com as próprias palavras; a busca por regras responde com nível de confiança, **fonte oficial e data de verificação**.
4. **Documentos perdidos** (Prompt and AI): agente que responde **somente** com fichas verificadas, cita a fonte, bloqueia dados pessoais e recusa tentativas de manipulação. A IA só reescreve e confere; a busca é feita por código.
5. **Energia** (Energias Renováveis): compara alternativas para a falta de luz. Em resumo: gerador a gasolina R$ 1.819,90 de compra, R$ 32,51 de combustível em 48 h e 9,0 kg de CO₂; kit solar R$ 6.079,00; power banks com lanternas R$ 730,00, ambos com cobertura de 100% da demanda de 352 Wh em condições normais (o kit solar cai para 73% em tempestade).
6. **Base e dados** (DSA, Estatística, Modelagem): estruturas de dados próprias para o catálogo de serviços, estatística dos registros oficiais para mostrar onde priorizar, e um modelo de frota para evacuação.

## Como executar

Cada repositório tem o próprio README com instruções. De forma geral:

- **Python (PCP, DSA, CS):** só precisa de Python 3. `python main.py` (ou `python teste.py` no CS).
- **Sentinela:** abra um projeto Raspberry Pi Pico com MicroPython no [Wokwi](https://wokwi.com), cole `main.py` e `diagram.json` e clique em *Start Simulation*. Com `MODO_DEMO = True`, a demonstração roda sozinha por cerca de 75 s.
- **Prompt and AI:** notebook no Google Colab. A chave da OpenAI é lida **somente** de variável de ambiente ou do *Secrets* do Colab, nunca de arquivo.
- **Estatística e Modelagem:** `pip install -r requirements.txt` e depois `python analise_enchentes.py` ou o notebook.

## Testes e validação

- Mais de **120 testes automatizados** somados nos projetos (lógica da Sentinela, assistente, agente, estruturas de dados).
- Testes com **pessoas de fora do grupo**, com falhas encontradas e corrigidas (registros em cada repositório de disciplina).
- Nenhum teste usa dados pessoais reais.

## Limitações e avisos

- É um **protótipo educacional**. **Não é canal oficial** e não substitui a Defesa Civil (199) nem os Bombeiros (193).
- Os limiares da Sentinela são **hipotéticos** e precisam de calibração com dados reais e com a Defesa Civil. Tudo foi simulado no Wokwi e em testes de software, sem medição em campo.
- As fichas de documentos são **fictícias** (Central do Cidadão de Aurora). Preços de energia são estimativas, com fontes e premissas documentadas no repositório de Energia.
- Ainda não existe um aplicativo de celular: as telas do vídeo de apresentação são mockups do conceito.

## Próximos passos

- Integrar alertas em tempo real da Defesa Civil, do Cemaden e do INMET.
- Calibrar os limiares do sensor com dados reais.
- Ampliar a base de orientações e fichas e levar o app às comunidades mais afetadas.

## ODS

**ODS 11** (Cidades e comunidades sustentáveis) e **ODS 13** (Ação contra a mudança global do clima).

## Uso de IA generativa

A IA foi usada como apoio na construção do código, dos testes e da documentação. Em cada disciplina, as regras do enunciado sobre uso de IA foram seguidas (em Computer Science, por exemplo, tabela-verdade, Karnaugh e circuitos foram feitos sem IA). A equipe revisou e validou as entregas. O vídeo de apresentação tem narração humana.

## Fontes principais

- Atlas Digital de Desastres no Brasil (Sedec/MIDR, S2iD), versão consolidada v1.1.
- Defesa Civil (Prefeitura de São Paulo), FEMA e demais fontes citadas nos repositórios de cada disciplina.

---
FIAP · Global Solution 2026.2 · Gabriel Barbosa Furin, Lucas Kiodi Moraca e Renan Fracalossi Mano da Silva
