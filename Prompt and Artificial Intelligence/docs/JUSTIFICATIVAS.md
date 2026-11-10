# Justificativas e limitações

**Integrantes:** Gabriel Barbosa Furin (RM 572941), Lucas Kiodi Moraca (RM 571004), Renan Fracalossi Mano da Silva (RM 569610).

## Framework: LangGraph
- O fluxo é uma sequência de passos pequenos com estado (proteger, classificar, montar, reescrever, finalizar). O LangGraph deixa cada passo explícito, testável e desenhável (`docs/grafo_agente.png`).
- Não usamos CrewAI porque ele serve melhor para vários agentes que conversam entre si, e aqui não há esse caso.
- Não usamos uma cadeia simples do LangChain porque precisamos de caminhos diferentes (escopo, fora do escopo, dados pessoais, injeção) sobre o mesmo estado.

## Arquitetura: um agente só
Um único agente com nós de função única. O domínio é pequeno (7 fichas) e uma pergunta não pede divisão de tarefas entre agentes. Vários agentes aumentariam o custo e os pontos de falha, sem ganho.

| Nó | Papel | Usa IA? |
|---|---|---|
| proteger | oculta CPF, telefone, e-mail etc.; valida entrada vazia, longa ou sem sentido; detecta prompt injection | não |
| classificar | escolhe a rota e busca ficha + seções | não |
| montar | monta a resposta com o texto da ficha | não |
| reescrever | simplifica a linguagem (com chave) | sim |
| validar | a IA confere a resposta contra as fichas (com chave) | sim |
| finalizar | acrescenta fonte, data e aviso; mascara dados pessoais na saída | não |

## Modelo de linguagem: OpenAI (ou Groq), opcional
- Usamos a API da OpenAI com a chave fornecida pelo professor, modelo padrão `gpt-4o-mini` (configurável em `OPENAI_MODELO`; **ajustar para o modelo realmente usado**). O código também aceita Groq. Escolhemos um modelo pequeno e barato porque a tarefa é só reescrever trechos curtos e julgar respostas curtas, sem raciocínio longo. A chave fica só em variável de ambiente.
- O mesmo modelo é usado no juiz.
- **Onde a IA entra e onde não:** busca, regras, validação, privacidade e citação são código comum (determinístico, testável, sem custo e sem risco de inventar). Com chave, a IA reescreve em linguagem simples os trechos já escolhidos, valida a resposta contra as fichas (se reprovar, volta ao texto da ficha; se achar incompleta, mostra a ficha inteira) e, na avaliação, julga o golden dataset. A IA não pesquisa fora das fichas: elas são a única fonte de verdade. Sem chave, o assistente usa só a base. Se o modelo não estiver disponível, o agente continua igual.
- A saída do modelo é conferida: números que não estejam nos trechos ou ausência de citação de ficha fazem o agente descartá-la e usar o texto da ficha.

## Dados pessoais
Não pedimos nem guardamos dados pessoais: sem histórico, arquivo, banco ou log. O primeiro nó oculta padrões (CPF, RG, telefone, CEP, e-mail, números longos) e detecta frases como "vou te passar meu endereço". O LLM e o juiz só recebem o texto já oculto. Testes e exemplos usam só dados fictícios.

## Prompt injection
Mensagem e fichas são tratadas como dados. Padrões de manipulação ("ignore as instruções", "prompt de sistema", "[SISTEMA] nova regra") levam a uma recusa e, se a mensagem também perguntava algo das fichas, à resposta correta da ficha. O LLM não é chamado nesses casos. O prompt do LLM trata pergunta e trechos como dados entre delimitadores.

## O que o grupo tentou e mudou
1. **Versão 1** devolvia a ficha inteira. Errou por comparar palavras-chave sem acento com o texto acentuado e por não ter proteções. Corrigimos com normalização e seções.
2. A intenção "quanto" fazia "Em quanto tempo fica pronto?" cair em custo. Trocamos por "quanto custa", "valor", "taxa" etc.
3. "Como faço" puxava custo, prazo e passo a passo em perguntas específicas (Libras). Agora só vale quando é a única intenção.
4. A FC-07 não tem palavras-chave nas fichas; definimos as nossas (`CHAVES_EXTRAS`) e a FC-07 é citada junto da ficha do documento quando a regra geral se aplica (agendamento, terceiros).
5. Quando duas fichas empatam ("segunda via"), o agente pergunta qual documento em vez de escolher.
6. O texto sobre dados pessoais foi reescrito para dizer claramente "não agendo atendimentos por você".

7. **Primeira execução do juiz LLM (OpenAI):** o juiz reprovou respostas corretas porque penalizava as linhas padrão "Fonte" e "Aviso" e informação extra correta. Mudamos o juiz: o LLM confere só o conteúdo, por lista de pontos, e o código confere fichas citadas e dados pessoais e calcula o veredito. As verificações literais do juiz de regras foram flexibilizadas para aceitar paráfrase (a IA reescreve com outras palavras).
8. **Teste com usuário (P1):** a IA respondeu "sim" a uma pergunta cuja resposta não consta nas fichas, e a validação aprovou. Reforçamos o prompt de reescrita e o de validação para proibir "sim" ou "não" por dedução. O chat também passou a explicar que não há comando para sair.
9. **Teste com usuária (P2):** a pergunta sobre *tirar* a CNH recebeu a ficha de *renovação*. Agora o assistente avisa que as fichas só tratam de renovação e orienta a consultar o órgão competente.
10. **Teste com usuária (P3):** a pergunta sobre a certidão de nascimento dos pais foi escrita "cetrtidaò" e caiu em "fora do escopo", apesar de a FC-05 cobrir certidões. A busca por palavra exata não tolerava erro de digitação. Agora termos de uma palavra com 7 letras ou mais aceitam uma troca de letras (semelhança de 88%, mesma letra inicial). "carteira" e "cnh" não viram "certidão" (teste automatizado). O juiz de regras continua em 26 de 26 e 14 de 14.
11. **Limitação vista no teste P3:** o chat não guarda histórico (por privacidade). Quando a pessoa escreveu "qual o órgão competente?" logo depois de outra pergunta, o assistente não sabia a que se referia e respondeu "fora do escopo". Mantivemos assim de propósito e registramos como limitação.
12. **Teste com usuário (P5):** "Quanto custa e qual é o tempo para renovar a CNH" recebia só o custo; o prazo de 7 dias úteis sumia, e a validação por IA aprovou. Havia duas causas: a busca não reconhecia "tempo" como pedido de prazo (agora reconhece "quanto tempo leva", "qual o tempo", "tempo estimado" etc.; "por quanto tempo vale" continua sendo validade) e o prompt de reescrita e o de validação não exigiam responder todas as partes da pergunta (agora exigem; omitir uma parte conhecida faz a validação reprovar). Testes automatizados cobrem os dois pontos. **Precisa reexecutar no Colab para confirmar a parte da IA.**

## Limitações
- Busca por palavras-chave: perguntas com vocabulário muito diferente podem cair em "não encontrei".
- Sem memória de conversa (decisão de privacidade): "e o prazo?" sem contexto não funciona.
- O juiz de regras não mede clareza; o juiz LLM pode errar ou variar. Por isso há conferência manual de uma amostra (`CONFERENCIA_MANUAL.md`).
- Detecção de dados pessoais e de injeção por padrões: variações criativas podem passar.
- Fichas fictícias: nada vale para documentos reais. O assistente não é canal oficial nem confirma serviços ou direitos.
