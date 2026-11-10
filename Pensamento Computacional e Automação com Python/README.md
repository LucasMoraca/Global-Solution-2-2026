# Citizen Assist AI — Plantão Enchente

Assistente de terminal em Python que orienta moradores de áreas de risco de enchente (alertas, o que fazer durante, saúde depois e dinheiro/documentos), usando só fontes oficiais.
Global Solution 2026.2 — FIAP, CitizenTech — Pensamento Computacional e Automação com Python.

> **Este assistente NÃO é um canal oficial.** Em risco imediato, ligue 199 (Defesa Civil) ou 193 (Bombeiros).

## Integrantes

| Nome | RM |
|---|---|
| Gabriel Barbosa Furin | 572941 |
| Lucas Kiodi Moraca | 571004 |
| Renan Fracalossi Mano da Silva | 569610 |

## Público e problema

**Público:** moradores de áreas de risco de enchente (e suas famílias).
**Problema:** na hora da chuva forte e nos dias seguintes, a informação oficial está espalhada em vários sites (Defesa Civil, Ministério da Saúde, FGTS, gov.br). O assistente reúne 16 orientações curtas em um só lugar, sempre com a fonte e a data de verificação.

## ODS relacionados

- **ODS 11** — Cidades e comunidades sustentáveis (reduzir o impacto de desastres sobre a população).
- **ODS 13** — Ação contra a mudança global do clima (adaptação e resposta a eventos extremos).

## Como executar

Precisa apenas de Python 3.8 ou mais novo (nenhuma biblioteca externa).

```bash
git clone <link-do-repositorio>
cd citizen-assist-ai
python main.py
```

No Windows, se `python` não funcionar, use `py main.py`. Menu: `1` pergunta, `2` categorias, `3` indicadores, `4` exportar CSV, `0` sair. Em toda tela, `0` volta.

## Estrutura

```
citizen-assist-ai/
├── main.py                  # menu principal
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento + normalizar()
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # 16 orientações em 4 categorias
    ├── historico.json           # atendimentos registrados (JSON)
    └── atendimentos.csv         # exportação dos atendimentos
```

- `Orientacao`: guarda um registro da base e tem `exibir()`.
- `BaseConhecimento`: `carregar()`, `categorias()`, `por_categoria()`, `pontuar()` e `buscar()` (devolve lista de tuplas `(pontos, orientacao)` da maior para a menor).
- `Assistente`: **tem uma** `BaseConhecimento` (composição, não herança). Métodos `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`; atributos `nome`, `base`, `historico`.

## Regra de pontuação

A pergunta passa por `normalizar()`: minúsculas, sem acentos, sem pontuação, espaços repetidos removidos, com um espaço em cada ponta (para achar só palavras inteiras).

- **+3** por palavra-chave da orientação que aparece na pergunta;
- **+1** por palavra da pergunta com 4 letras ou mais que aparece no título (palavras muito comuns como *como, para, depois, fazer* são ignoradas nesse ponto extra);
- **6 ou mais** = confiança **ALTA**; **3 a 5** = **MÉDIA**; **menos de 3** = "Não encontrei" (sugere outras palavras e as categorias).
- Mostra a melhor orientação e até 2 alternativas. Empate: vence o menor `id`.

Exemplo real: *"Posso beber a água da torneira depois da enchente?"* → orientação 8 (água segura): palavra-chave "agua da torneira" (+3) e as palavras "agua", "beber", "enchente" no título (+3) = **6, ALTA**. A orientação 5 (durante a enchente) fica com 4 (MÉDIA) e aparece como alternativa.

## Regras de segurança

- Entradas inválidas (letras, número fora da faixa, vazio, s/n inválido) nunca encerram o programa.
- **Dados pessoais** (8 ou mais dígitos, ou "@") são bloqueados e **não são registrados**.
- Toda resposta mostra fonte, data de verificação e o aviso de que não é canal oficial.
- JSON da base ausente ou corrompido não derruba o programa (avisa e segue); registros inválidos são ignorados. Histórico corrompido é guardado como `historico.json.corrompido` e um novo é criado.

## Indicadores e histórico

Cada atendimento é gravado em `data/historico.json` (data, sessão, origem, pergunta, id, encontrou, ajudou, tentativas, tempo). Ao sair, a pessoa dá uma nota de 1 a 5 para a facilidade de uso. A opção 3 mostra: % de resposta encontrada, % que ajudou, tempo médio, tentativas médias, facilidade média e dúvidas sem solução. A opção 4 exporta tudo para `data/atendimentos.csv` (UTF-8, abre direto no Excel).

## Integrações

O assistente funciona offline com a base local. Integração prevista (não implementada): consulta a alertas em tempo real da Defesa Civil em vez de só orientar a se cadastrar.

## Fontes (verificadas em 04/11/2026)

1. https://www.gov.br/pt-br/servicos/solicitar-cadastro-para-recebimento-de-avisos-e-alertas-de-desastres
2. https://www.gov.br/mdr/pt-br/assuntos/protecao-e-defesa-civil/defesa-civil-alerta
3. https://www.gov.br/mcom/pt-br/noticias/2026/setembro/emergencia-voce-sabe-para-quem-ligar-quando-precisa-de-ajuda
4. https://estado.rs.gov.br/saiba-como-agir-em-caso-de-inundacoes
5. https://prefeitura.sp.gov.br/web/defesa_civil/w/cuidados_importantes/179951
6. https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/e/enchentes
7. https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/e/enchentes/cuidados-com-a-agua
8. https://www.gov.br/saude/pt-br/assuntos/noticias/2024/maio/ministerio-da-saude-orienta-sobre-cuidados-essenciais-a-populacao-no-pos-enchente
9. https://www.fgts.gov.br/Paginas/trabalhador/saque-calamidade.aspx
10. https://www.gov.br/pt-br/servicos/obter-cartao-de-cpf

## Resultado do teste com usuários

Testes feitos em 07/11/2026 com 5 pessoas de fora do grupo (sem nomes nem dados pessoais). Dados completos em `data/historico.json` e `data/atendimentos.csv`; detalhes em `docs/TESTES_USUARIOS.md`.

- Pessoas que testaram: 5
- Atendimentos realizados: 14
- Resposta encontrada: 85,7% | Resposta ajudou: 41,7% (5 de 12 avaliadas)
- Tempo médio por atendimento: 59,3 s | Tentativas médias: 1,1 | Facilidade média (1-5): 4,0 (notas 3, 5, 2, 5 e 5)
- Principais problemas: (1) perguntas fora da base (seguro, maior enchente da história, socorrer alguém, abrigo próximo, benefícios) recebiam a orientação geral "durante a enchente", que contém a palavra "enchente" mas não responde; "encontrou" ficou alto e "ajudou" ficou baixo; (2) perguntas sobre dados do momento; (3) pergunta com dois assuntos recebe uma orientação só.
- O que mudamos por causa do teste: (a) palavras-chave de benefício e perda de bens na orientação 14 (FGTS); (b) quando a confiança é MÉDIA, o programa avisa que a orientação é a mais próxima e pode não responder exatamente à pergunta, e aponta as outras opções.

## Limitações

- Base pequena (16 orientações): perguntas fora desses temas retornam "Não encontrei" ou a orientação geral mais próxima (com aviso). Não cobre seguro, indenização, histórico de enchentes nem socorro a terceiros.
- A busca é por palavras: não entende sinônimos que não estejam nas palavras-chave, nem erros de digitação.
- Valores e prazos (ex.: FGTS) mudam; confira sempre na fonte indicada. Cada orientação mostra a data em que foi verificada.
- Não substitui a Defesa Civil: não envia alertas nem acompanha a situação em tempo real. Não sabe se houve alerta hoje nem dá o abrigo mais próximo (não usa localização).
- Pergunta com mais de um assunto recebe uma orientação principal e alternativas, não todas as respostas.

## Vídeo técnico

Link (YouTube, não listado): `COLE AQUI`
