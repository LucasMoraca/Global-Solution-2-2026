# Testes com usuários

**Integrantes:** Gabriel Barbosa Furin (RM 572941), Lucas Kiodi Moraca (RM 571004), Renan Fracalossi Mano da Silva (RM 569610).

Testes com 5 pessoas de fora do grupo, em 07/11/2026. Nenhum nome ou dado pessoal foi registrado (P1 a P5). **Limitação declarada:** o uso foi livre, sem as tarefas T1 a T3 cronometradas e sem o questionário de facilidade (ver "Indicadores").

## Fase 1 — uso livre (5 pessoas de fora, já realizada)
P1, P2, P3, P4 e P5 são pessoas de fora do grupo (sem nome nem dados pessoais). Cada uma usou o chat no Colab, com a chave OpenAI, fazendo perguntas livres. Esta fase **não seguiu as tarefas T1 a T3 nem o questionário**; serve para descobrir falhas e gerou os ajustes abaixo.

| Participante | Mensagens | Tempo total | Principais achados |
|---|---|---|---|
| P1 | 4 | 3 min 40 s | A IA respondeu "sim" por dedução (CNH para segunda via do RG), o que as fichas não dizem. Digitou "0" e o chat não entendeu. |
| P2 | 4 | 3 min 05 s | "Tirar a CNH" recebeu a ficha de renovação. Erros de digitação foram entendidos. |
| P3 | 6 | 6 min 32 s | Pergunta longa sobre RG respondida com a ficha FC-01 inteira. Pedido de prazo total e valor do exame respondido com honestidade ("não encontrei"). "Certidão" digitada errada caiu em fora do escopo. Pergunta de acompanhamento ("qual o órgão competente?") sem contexto. |
| P4 | 5 | 3 min 26 s | Documentos do RG e certidão de outra pessoa corretos. "Tirar a CNH" recebeu a ficha de renovação (esta execução usou a versão anterior ao ajuste da `primeira_cnh`; a versão atual avisa que só há renovação). "Qual a" caiu em fora do escopo. A pergunta sobre o valor médio do exame médico recebeu a ficha inteira, sem dizer com clareza que o valor não consta. |
| P5 | 5 | tempo não informado | Documentos do RG e certidão de outra pessoa corretos. "Quanto custa e qual é o tempo para renovar a CNH" respondeu só o custo, sem o prazo, e a validação aprovou: **falha de conteúdo (resposta incompleta), corrigida** (item 12). "Mas quanto tempo leva?" sem contexto caiu em fora do escopo (limitação). "0" ainda recebeu "não entendi", porque o Colab estava com o notebook antigo. |

Cada resposta foi conferida contra a ficha citada. Erros de conteúdo encontrados: 2 (P1 e P5, corrigidos). Falhas de busca: 2 (P2 e P3, corrigidas). Respostas pouco claras: 1 (P4, valor do exame: a ficha só diz que o exame é pago à parte, e o assistente mostrou a ficha inteira; fica como limitação). Limitação mantida: 1 (sem memória de conversa).

## Indicadores (calculados sobre a fase 1)
O protocolo previsto (tarefas T1 a T3 com cronômetro por tarefa e questionário de 5 perguntas) **não foi aplicado**. Os indicadores abaixo vêm do uso livre e têm essa limitação. Não há números inventados.

Conferência de cada pergunta feita (mensagens como "0", "." e "qual a" não contam): acerto = resposta correta e completa contra a ficha, vista antes de qualquer ajuste.

| Participante | Perguntas | Acertos | Erros | Tempo total |
|---|---|---|---|---|
| P1 | 3 | 2 | 1 (sim por dedução) | 3 min 40 s |
| P2 | 3 | 2 | 1 (tirar a CNH recebeu a renovação) | 3 min 05 s |
| P3 | 6 | 3 | 3 (pagamento não informado, certidão com erro de digitação, pergunta sem contexto) | 6 min 32 s |
| P4 | 4 | 2 | 2 (tirar a CNH com versão antiga, valor do exame sem clareza) | 3 min 26 s |
| P5 | 4 | 2 | 2 (prazo omitido, pergunta sem contexto) | não informado |
| **Total** | **20** | **11** | **9** | |

- **Acerto:** 11 de 20 = **55%** antes dos ajustes. Os erros de conteúdo (P1, P2, P4, P5) e de busca (P3) já foram corrigidos e cobertos por testes automatizados; os de contexto são limitação de projeto (sem memória, por privacidade). Os ajustes **não foram reaplicados com as mesmas pessoas**.
- **Tempo:** média de 4 min 11 s por pessoa (P1 a P4, que informaram) e de 52,8 s por mensagem (1.003 s em 19 mensagens de P1 a P4). Não é o tempo por tarefa pedido no protocolo.
- **Facilidade (1 a 5):** **não medida** para este assistente. O questionário não foi aplicado. (As notas de facilidade do projeto de Python são de outro assistente e não valem aqui.)

## Ajustes feitos depois dos testes (fase 1)
| Participante | O que aconteceu | Ajuste |
|---|---|---|
| P1 | Resposta "sim" por dedução, aprovada pela validação | Prompt de reescrita e validador proíbem concluir sim ou não quando as fichas não mencionam o assunto (JUSTIFICATIVAS, item 8) |
| P1 | "0" gerou "não entendi" | O chat explica que não há o que encerrar |
| P2 | "Tirar a CNH" recebeu a ficha de renovação | Rota `primeira_cnh`: avisa que as fichas só tratam de renovação (item 9) |
| P5 | Resposta só com o custo | Busca reconhece "tempo" como prazo e os prompts exigem responder todas as partes (item 12) |
| P3 | "cetrtidaò" não achou a FC-05 | Busca tolera uma troca de letras em palavras longas (item 10) |
| P3 | Pergunta sem contexto | Mantido por privacidade, registrado como limitação (item 11) |
