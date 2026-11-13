"""Executa os cenários de menu (testes/entradas) e grava as saídas em testes/saidas.

Cada cenário roda numa pasta temporária, então dados/servicos.json nunca é alterado.
Uso (na pasta do projeto):  python testes/rodar_cenarios.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADAS = os.path.join(RAIZ, "testes", "entradas")
SAIDAS = os.path.join(RAIZ, "testes", "saidas")

BOM = {"id": 5, "titulo": "T", "categoria": "C", "descricao": "D", "requisitos": "R", "local": "L", "fonte": "F"}


def preparar(nome, pasta):
    """Cria o arquivo de dados do cenário e devolve o nome do arquivo (relativo à pasta)."""
    if nome == "t4_lista_vazia":
        return "nao_existe.json"
    if nome == "t7_arquivo_corrompido":
        with open(os.path.join(pasta, "ruim.json"), "w", encoding="utf-8") as f:
            f.write("{ isso nao e json")
        return "ruim.json"
    if nome == "t8_registros_invalidos":
        dados = [BOM, dict(BOM), {"id": 1}, "texto", {**BOM, "id": "abc"}, {**BOM, "id": 6, "titulo": ""}]
        with open(os.path.join(pasta, "mistura.json"), "w", encoding="utf-8") as f:
            json.dump(dados, f)
        return "mistura.json"
    shutil.copy(os.path.join(RAIZ, "dados", "servicos.json"), os.path.join(pasta, "servicos.json"))
    return "servicos.json"


def main():
    os.makedirs(SAIDAS, exist_ok=True)
    ambiente = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": RAIZ}
    falhas = 0
    for arquivo in sorted(os.listdir(ENTRADAS)):
        nome = arquivo[:-4]
        with tempfile.TemporaryDirectory() as pasta:
            dados = preparar(nome, pasta)
            with open(os.path.join(ENTRADAS, arquivo), "rb") as entrada:
                r = subprocess.run([sys.executable, os.path.join(RAIZ, "main.py"), dados], cwd=pasta,
                                   stdin=entrada, capture_output=True, env=ambiente)
        saida = r.stdout.decode("utf-8").replace("\r\n", "\n")
        with open(os.path.join(SAIDAS, arquivo), "w", encoding="utf-8", newline="\n") as f:
            f.write(saida)
        ok = r.returncode == 0 and not r.stderr and "Traceback" not in saida
        falhas += 0 if ok else 1
        print(f"{'OK  ' if ok else 'ERRO'} {nome}")
        if not ok:
            print(r.stderr.decode("utf-8"))
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
