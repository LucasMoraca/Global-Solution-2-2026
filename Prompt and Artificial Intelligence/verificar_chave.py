"""verificar_chave.py - testa se a chave de API funciona, com uma chamada mínima. Não imprime a chave."""

from agente.llm import criar_llm, nome_provedor

llm = criar_llm()
if llm is None:
    print("Nenhuma chave encontrada. Defina OPENAI_API_KEY (ou GROQ_API_KEY) no terminal e rode de novo.")
else:
    try:
        resposta = llm.invoke("Responda apenas: ok")
        print(f"Funcionou com {nome_provedor(llm)}. Resposta do modelo: {resposta.content.strip()[:40]}")
    except Exception as erro:  # noqa: BLE001
        print(f"A chave foi lida, mas a chamada falhou ({type(erro).__name__}). Confira a chave, o nome do modelo e a rede.")
