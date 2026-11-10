# Testes com usuários — Citizen Assist AI (Plantão Enchente)

Data: 07/11/2026. Cinco pessoas de fora do grupo (P1, P2, P3, P4, P5), sem nome nem dados pessoais. Cada pessoa usou o programa e fez perguntas livres; ao sair, deu uma nota de facilidade de 1 a 5.

| Pessoa | Atendimentos | Tempo total | Nota de facilidade |
|---|---|---|---|
| P1 | 2 | 4 min | 3 |
| P2 | 3 | 3 min 37 s | 5 |
| P3 | 3 | 4 min 58 s | 2 |
| P4 | 3 | 3 min 45 s | 5 |
| P5 | 3 | 1,5 relatado (cerca de 1 min 10 s pelos horários do histórico) | 5 |

## Atendimentos
| # | Pessoa | Pergunta (como escrita) | Orientação | Encontrou | Ajudou | Tentativas | Tempo (s) |
|---|---|---|---|---|---|---|---|
| 1 | P1 | houve areas de enchente em são paulo em setembro de 2026? | 6 | sim | sim | 3 | 157,8 |
| 2 | P1 | no dia de hoej ocorreu algum alerta de enchente na cidade de são paulo? | 5 | sim | sim | 1 | 48,0 |
| 3 | P2 | Se eu estou em uma enchete eu devo sair do carro ? | 6 | sim | sim | 1 | 63,5 |
| 4 | P2 | O gpverno me da beneficios se eu sofrer alguma enchete? | nenhuma | não | - | 1 | 46,4 |
| 5 | P2 | Se eu estiver quase submersa dentro do carro na enchete, o que fazer? | 6 | sim | não | 1 | 41,4 |
| 6 | P3 | Qual p estadp brasil;eiro que mais sofre com enchentes e qual; seu volujme pluviométrico anual? | nenhuma | não | - | 1 | 55,5 |
| 7 | P3 | A partir da minha localização stusl, me informe o local mais próximo onde eu possa me proteger de uma enchente | 5 | sim | não | 1 | 127,8 |
| 8 | P3 | Em caso de contato com a água de uma enchente, o que devo fazer? Ademias, perdi todos os meus ben smateriais e náo tenho mais onde morar, a quem posso recorrer? | 5 | sim | não | 1 | 65,1 |
| 9 | P4 | se a minha residencia for atingida por uma enchente, tenho cobertura do seguro ou da prefeitura? | 5 | sim | não | 1 | 79,2 |
| 10 | P4 | qual a maior enchente da historia de sao paulo? | 5 | sim | não | 1 | 55,4 |
| 11 | P4 | como socorrer uma pessoa em uma enxurrada? | 5 | sim | não | 1 | 33,2 |
| 12 | P5 | Como me defender de e uma enchente? | 5 | sim | não | 1 | 32,7 |
| 13 | P5 | O que fazer se a enchente pegar você de carro | 6 | sim | sim | 1 | 18,2 |
| 14 | P5 | Como deixar a água segura para beber depois da enchente | 8 | sim | sim | 1 | 5,8 |

## Indicadores (opção 3 do programa)
- Atendimentos registrados: 14
- Resposta encontrada: 85,7% (12 de 14)
- Resposta que ajudou: 41,7% (5 de 12 avaliadas)
- Tempo médio por atendimento: 59,3 s
- Tentativas médias: 1,1
- Facilidade de uso: 4,0 (média de 3, 5, 2, 5 e 5)

## O que os testes mostraram
1. **P1** perguntou sobre dados do momento (enchente em setembro, alerta de hoje). O assistente só tem orientações fixas e deu a orientação geral. Limitação.
2. **P2** perguntou sobre benefícios do governo e não achou resposta. A base tem o Saque Calamidade do FGTS, mas a pergunta não usava as palavras-chave. **Ajuste feito.**
3. **P2** estava "quase submersa dentro do carro" e a orientação 6 trata de dirigir em alagamento, então não ajudou. A base não cobre carro submerso. Limitação; para risco imediato o programa já mostra 199 e 193.
4. **P3** fez perguntas fora da base (estado com mais enchentes, volume de chuva) e pediu o abrigo mais próximo; o programa não usa localização. Limitações.
5. **P3** juntou dois assuntos (contato com a água e perda de bens). O programa mostrou a orientação principal e alternativas, mas a de dinheiro não apareceu entre elas. Limitação (um assunto por pergunta).

6. **P4** fez três perguntas fora da base (seguro/prefeitura, maior enchente da história, socorrer uma pessoa na enxurrada). Todas receberam a orientação geral 5, porque a palavra "enchente" ou "enxurrada" pontua, e as três foram marcadas como não ajudou. O indicador "encontrou" (81,8%) mostra que a busca achou algo, e o "ajudou" (33,3%) mostra que nem sempre era a resposta. **Ajuste feito** (abaixo).

7. **P5** usou duas vezes o título de uma das "Outras orientações possíveis" como pergunta e achou a resposta certa em 18,2 s e 5,8 s. A pergunta aberta "Como me defender de uma enchente?" recebeu a orientação geral e foi marcada como não ajudou.

## Ajustes feitos
- Aviso de confiança MÉDIA (P4): o programa passa a dizer "esta é a orientação mais próxima da sua pergunta e pode não responder exatamente ao que você quer saber" e a apontar as outras opções. Não muda a busca; evita que a pessoa ache que a orientação responde ao que não responde.
- Orientação 14 (Saque Calamidade do FGTS): palavras-chave "benefício", "benefícios", "auxílio", "ajuda financeira", "perdi tudo", "perdi meus bens", "bens materiais", "perdi todos os meus bens". Reteste: a pergunta "O governo me dá benefícios se eu sofrer alguma enchente?" passou a achar a orientação 14 (3 pontos, confiança MÉDIA).

## Pendência
A meta de 10 atendimentos foi atingida (14). O aviso de confiança MÉDIA foi adicionado depois dos testes e ainda não foi testado com pessoas.
