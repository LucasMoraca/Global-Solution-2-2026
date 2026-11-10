# Citizen Assist AI - Documentos pessoais

Entrega de **Prompt and Artificial Intelligence** (Global Solution FIAP 2026.2).

**Integrantes**
- Gabriel Barbosa Furin - RM 572941
- Lucas Kiodi Moraca - RM 571004
- Renan Fracalossi Mano da Silva - RM 569610

Assistente que responde sobre RG, CPF, título de eleitor, Carteira de Trabalho, certidões e CNH usando **somente** as 7 fichas da Central do Cidadão de Aurora (material fictício). Toda resposta cita a ficha e a data, avisa que não é canal oficial e não coleta dados pessoais.

## Como rodar
```
pip install -r requirements.txt
python main.py                                  # assistente no terminal (menu + pergunta livre)
python -m unittest discover -s testes -v        # 39 testes
jupyter notebook notebook_citizen_assist.ipynb  # golden dataset, juiz, antes x depois
```
**Com chave de API (OpenAI ou Groq)**, para ligar a reescrita por LLM e o **juiz LLM** no notebook. Defina a chave no terminal antes de rodar (nunca em arquivo, nunca no GitHub):
```
# Windows PowerShell
$env:OPENAI_API_KEY="sua-chave"
$env:OPENAI_MODELO="gpt-4o-mini"      # opcional: use o modelo liberado pelo professor
python verificar_chave.py             # teste rápido: deve dizer "Funcionou com ChatOpenAI"
jupyter notebook notebook_citizen_assist.ipynb
# Linux/Mac: export OPENAI_API_KEY=sua-chave
```
Groq também funciona (`GROQ_API_KEY`, `GROQ_MODELO`); se houver as duas chaves, `LLM_PROVEDOR=openai` ou `groq` escolhe. Com chave, a IA reescreve e **valida** cada resposta contra as fichas; sem chave, o assistente usa só a base (as fichas) e o juiz de regras funciona do mesmo jeito.

## Estrutura
- `fichas/`: as 7 fichas de referência (única fonte de verdade).
- `agente/`: `fichas.py` (carrega e divide em seções), `seguranca.py` (dados pessoais, injeção, validação), `recuperacao.py` (busca), `grafo.py` (agente LangGraph), `llm.py` (reescrita opcional, OpenAI ou Groq), `versao1.py` (linha de base do "antes"). `verificar_chave.py`: teste da chave.
- `avaliacao/`: `golden.json` (as 26 mensagens do enunciado), `golden_extra.json` (14 próprias), `juiz.py` (juiz LLM e juiz de regras).
- `notebook_citizen_assist.ipynb`: notebook do projeto. Para entregar executado, rode no Colab com a chave e baixe com as saídas. `resultados/`: CSVs.
- `docs/`: `RELATORIO_FINAL`, `JUSTIFICATIVAS.md`, `TESTES_USUARIOS.md`, `CONFERENCIA_MANUAL.md`, `grafo_agente.png`, `prints/`.

## Resultado da avaliação
| | Versão 1 (antes) | Versão 2 (depois) |
|---|---|---|
| Juiz de regras, 26 mensagens do golden dataset | 12 corretas | 26 corretas |
| Juiz de regras, 14 perguntas próprias | - | 14 corretas |
| Juiz LLM, 1ª execução (OpenAI, **juiz antigo**) | 3 de 26 | 8 de 26 |

O juiz LLM da primeira execução reprovou respostas corretas (ver `docs/CONFERENCIA_MANUAL.md`: em 4 das 8 amostras a razão estava com a conferência manual). Por isso ele foi **recalibrado** (checklist de pontos, veredito calculado pelo código). **Limitação declarada:** a execução com o juiz recalibrado não foi realizada nesta entrega, então os números do juiz LLM acima são os da primeira execução (juiz antigo) e **não devem ser lidos como a qualidade do agente**. O notebook está pronto para rodar a nova execução no Colab com a chave (variável de ambiente). Os CSVs da primeira execução estão em `docs/juiz_llm_execucao1/`.

## Testes com pessoas
5 pessoas de fora do grupo (uso livre): 11 acertos em 20 perguntas (55%) antes dos ajustes, 5 correções feitas e cobertas por testes. Detalhes e limites do protocolo em `docs/TESTES_USUARIOS.md`. Prints em `docs/prints/`.

## Relatório consolidado
`docs/RELATORIO_FINAL.md` (e `.pdf`) reúne arquitetura, justificativas, avaliação, testes e limitações, com os nomes dos integrantes no início.

## Limitações
Ver `docs/JUSTIFICATIVAS.md`. Não é canal oficial, não confirma serviços nem direitos e não guarda nenhum dado pessoal.
