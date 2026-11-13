# Repositórios da Global Solution 2026.2 (CitizenTech) · Plantão Enchente

Cada pasta abaixo é **um repositório independente**, pronto para subir no GitHub. Pensamento Computacional (Python), Energias Renováveis e Prompt and AI já foram publicados à parte.

| Pasta | Matéria |
|---|---|
| `1_Computer_Organization_and_Architecture` | Estação Sentinela (Wokwi, Raspberry Pi Pico, MicroPython) |
| `2_Data_Structures_and_Algorithms` | lista encadeada e Merge Sort em Python (50 testes) |
| `3_Computer_Science` | lógica booleana (tabela-verdade, Karnaugh, circuitos, Python) |
| `4_Estatistica_Modelagem_Linear` | análise estatística das enchentes no Brasil |
| `5_Modelagem_Matematica_Computacional` | notebook de frota de ônibus e álgebra linear |

## Como publicar (para cada pasta)
Pelo site: crie um repositório novo no GitHub (sem README, sem .gitignore), clique em *uploading an existing file* e arraste **o conteúdo** da pasta (não a pasta em si).

Ou pelo terminal, dentro da pasta da matéria:
```bash
git init
git add .
git commit -m "Entrega Global Solution 2026.2"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
git push -u origin main
```
Nomes sugeridos: `gs2026-coa-sentinela`, `gs2026-dsa-citizen-assist`, `gs2026-cs-logica-booleana`, `gs2026-estatistica-enchentes`, `gs2026-modelagem-matematica`.

## Antes de publicar
- **COA:** cole o link do projeto no Wokwi no `README.md` (linha "Projeto no Wokwi: COLE AQUI").
- **CS:** confirmem a "Declaração de uso de IA" e a divisão de tarefas no README, que seguem o relatório.
- Nenhuma pasta contém chave de API, senha ou dados pessoais.
