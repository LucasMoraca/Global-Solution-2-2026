# Roteiro da demonstração — Citizen Assist AI (DSA, Python)

Duração sugerida: 6 a 7 minutos. Os três falam. Grave numa **cópia da pasta**, para não alterar o `dados/servicos.json` original. Deixe abertos no VS Code: `servico.py`, `lista.py`, `ordenacao.py` e `DOCUMENTACAO.md`, além de um terminal na pasta do projeto, com fonte grande.

| Cena | Quem | O que falar | O que mostrar na tela nesse momento |
|---|---|---|---|
| 1. Abertura (0:00 a 0:40) | Renan | "Somos Gabriel (RM 572941), Lucas (RM 571004) e Renan (RM 569610). Fizemos em Python um gerenciador de serviços e orientações ao cidadão em situação de enchente, dentro do projeto Citizen Assist AI." | `DOCUMENTACAO.md`, seção 1 (recorte) |
| 2. O registro (0:40 a 1:30) | Gabriel | "Cada registro é um objeto da classe Servico: id, título, categoria, descrição, requisitos, local e fonte. O ID é único e cada campo é validado." | `servico.py` (classe e `de_dict`). Depois `dados/servicos.json` com os 16 registros |
| 3. A lista encadeada (1:30 a 2:50) | Lucas | "O No guarda um Servico e uma referência `prox` para o próximo nó. A lista guarda só o `inicio` e o `tamanho`. Não usamos list do Python. Na remoção eu guardo o nó anterior e religo; para inserir, antes eu confiro se o ID já existe." | `lista.py`: classes `No` e `ListaEncadeada`, `buscar_id`, `inserir_fim` e `remover` (destacar `anterior` e `anterior.prox = atual.prox`) |
| 4. Execução: cadastro, consulta e validação (2:50 a 4:20) | Gabriel | "Vou rodar." Cadastrar o ID 5 (duplicado: ele recusa), depois o ID 100. Consultar o 100. Digitar `abc` no menu e uma letra num ID. Consultar o ID 9999 (não existe). | Terminal: `python main.py`. Mostrar "Já existe um serviço com o ID 5", "Entrada inválida" e "Nenhum serviço encontrado" |
| 5. Atualizar, excluir e pesquisar (4:20 a 5:10) | Renan | "Atualizo só o título: o Enter mantém os outros campos e o ID não muda. Excluo pedindo confirmação. A pesquisa ignora maiúsculas e acentos; se não achar, avisa." | Opção 3 (ID 100), opção 4 (responder `n` e depois `s`), opção 5 com "agua" e depois com "zzzz" |
| 6. Ordenação e análise (5:10 a 6:20) | Lucas | "Implementamos o Merge Sort sem usar sorted nem sort: divide a lista ao meio com dois ponteiros, ordena cada metade e junta religando os nós. É O(n log n) em todos os casos." | `ordenacao.py` (`_dividir`, `_mesclar`, `_merge_sort`). Depois, no programa: opção 6 (por título) e opção 8 (análise por categoria) |
| 7. Testes e fechamento (6:20 a 7:00) | Todos | "Fizemos 50 testes automáticos e 8 cenários de menu, incluindo lista vazia, entradas inválidas e arquivo corrompido. A análise Big-O está na documentação." | Terminal: `python -m unittest discover -s testes -v` (termina em "OK"); depois `DOCUMENTACAO.md`, seção 6.3 (tabela Big-O) |

Antes de gravar, ensaie uma vez. Se você excluir o ID 100 e não salvar, o `dados/servicos.json` não muda.
