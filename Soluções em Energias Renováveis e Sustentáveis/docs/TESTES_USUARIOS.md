# Registro de testes com usuários

**Integrantes:** Gabriel Barbosa Furin (RM 572941), Lucas Kiodi Moraca (RM 571004), Renan Fracalossi Mano da Silva (RM 569610).

Testes reais feitos em 07/11/2026 com pessoas de fora do grupo. Nenhum nome, telefone ou endereço foi registrado (T1 a T4).

## Como testar
1. Rode `python main.py` e entregue o computador à pessoa.
2. Peça que faça uma pergunta sobre falta de luz em enchente (ex.: "Posso usar gerador na garagem?", "O painel solar funciona com chuva?", "Quantos power banks eu preciso?").
3. Anote o que ela perguntou, se entendeu a resposta e o que sugeriu.

## Registro
Quatro pessoas de fora do grupo (sem nome nem outros dados). Tempo = da primeira pergunta até terminar.

| Teste | Perfil | Situação / pergunta (como escrita) | A resposta foi entendida? | Comentário | Ajuste feito |
|---|---|---|---|---|---|
| T1 | Pessoa de fora (familiar de integrante), 38 s | "o que é isso?" | Não havia resposta: "Não encontrei uma orientação para isso" | Quem abre o programa não sabe o que perguntar | Nova orientação `ajuda` ("O que este assistente faz") com exemplos |
| T1 | (mesma pessoa) | "Durante a falta de energia e correto usar gerador?" | Resposta certa (gerador só ao ar livre, fonte S2) | Confirmação de que entendeu: não informada | Nenhum |
| T2 | Pessoa de fora (familiar de integrante), 1 min 01 s | "Se eu estiver em uma enchete eu posso utilizar um carregador portátil?" | Não: o assistente respondeu quantos power banks comprar, e ela queria saber se pode usar | Pergunta de sim ou não sobre segurança respondida com cálculo | Nova orientação `carregador_enchente`: não há fonte oficial sobre isso, repete o que a fonte S1 diz sobre equipamentos elétricos em área alagada |
| T3 | Pessoa de fora, 1 min 01 s | "Acabei de sofrer com uma enchente, perdi tudo e estou sem luz. A qual recurso público posso recorrer para solucionar o meu problema?" | Parcial: recebeu a orientação sobre quadro de luz, não sobre a quem recorrer | O assistente só trata de energia; não há fonte sobre benefícios | Nova orientação `recorrer`: 199 e 193, concessionária e Defesa Civil (fonte S1) e aviso de que não há informação sobre benefícios, sem inventar programas |
| T4 | Pessoa de fora (familiar de integrante), 36 s | "se duramte uma enchente faltar luz eu posso acender uma vela?" | Sim: a resposta (prefira lanterna a pilha ou LED, evite velas por risco de incêndio, fontes S1 e S5) responde direto | Confirmação de que entendeu: não informada | Nenhum |

Um quinto teste (30 s) foi relatado só com o tempo, sem as perguntas e respostas; por isso **não é contado** na tabela.

Observação: "entendeu" de T1 e T2 vem do relato de quem aplicou o teste; a avaliação de T3 foi feita pela equipe a partir do texto da resposta.

## Resumo dos resultados
| Item | Resultado |
|---|---|
| Pessoas de fora que testaram (com perguntas registradas) | 4 (T1 a T4), em 07/11/2026 |
| Perguntas registradas | 5 |
| Respondidas direto e corretamente | 2 de 5 (gerador e vela) |
| Lacunas encontradas | 3 de 5 ("o que é isso?", carregador portátil, a quem recorrer) |
| Tempo por pessoa | 38 s, 1 min 01 s, 1 min 01 s e 36 s (média de 49 s) |
| Quinto teste (30 s) | só o tempo; sem perguntas e respostas, por isso não entra na contagem |
| Nota de facilidade (1 a 5) | não foi coletada para Energia |
| Ajustes feitos | 3 novas orientações (`ajuda`, `carregador_enchente`, `recorrer`) |
| Testes automatizados depois dos ajustes | 36 testes, todos passando |

## Reteste das mesmas perguntas, depois dos ajustes
Feito pela equipe no assistente atual (não repetido com as mesmas pessoas). Mostra qual orientação o assistente passou a escolher.

| Teste | Pergunta (como escrita) | Antes | Depois dos ajustes |
|---|---|---|---|
| T1 | "o que é isso?" | Sem resposta | "O que este assistente faz" |
| T1 | "Durante a falta de energia e correto usar gerador?" | Resposta certa | "Gerador dentro de casa e monóxido de carbono" (igual) |
| T2 | "Se eu estiver em uma enchete eu posso utilizar um carregador portátil?" | Respondeu quantos power banks comprar | "Carregador portátil em enchente" |
| T3 | "Acabei de sofrer com uma enchente, perdi tudo e estou sem luz. A qual recurso público posso recorrer para solucionar o meu problema?" | Orientação sobre quadro de luz | "A quem recorrer sem energia e depois da enchente" |
| T4 | "se duramte uma enchente faltar luz eu posso acender uma vela?" | Resposta certa | "Vela ou lanterna" (igual) |

## Ajustes feitos depois dos testes
1. `orientacoes.py`: orientação `ajuda` (T1) — responde "o que é isso?", "como funciona", "ajuda".
2. `orientacoes.py`: orientação `carregador_enchente` (T2) — responde sim ou não sobre carregador portátil sem inventar fonte; mantém "quantos power banks para 4 celulares e 3 dias?" indo para o cálculo.
3. `orientacoes.py`: orientação `recorrer` (T3) — telefones de emergência, concessionária e Defesa Civil, e limite honesto do assistente.
4. `testes/test_calculo.py`: testes automatizados para os três ajustes (suíte com 36 testes, todos passando).

## Conclusão
4 pessoas testaram, com 5 perguntas. Duas foram respondidas direto (gerador e vela). Três mostraram lacunas ("o que é isso?", carregador portátil e a quem recorrer) e geraram os ajustes acima. Tempos de 36 s a 1 min 01 s. O assistente continua limitado a energia na falta de luz e não substitui a orientação da Defesa Civil. Os ajustes foram conferidos por testes automatizados, mas não foram repetidos com as mesmas pessoas. A meta de 4 a 5 testes foi atingida (4).
