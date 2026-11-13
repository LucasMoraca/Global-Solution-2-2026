"""Gera os testes da demonstração da gravação (Estação Sentinela, COA).

Roda, fora do Wokwi, a mesma sequência de ações do roteiro do vídeo (distância do sensor, chuva no
potenciômetro, botão) e confere, a cada passo, o risco, os LEDs e o texto do LCD. Mostra uma tabela
na tela e grava resultados_demonstracao.csv e resultados_demonstracao.md na pasta atual.

Uso (na pasta Computer_Organization):  python testes/demonstracao_gravacao.py
Os valores do Wokwi para repetir cada passo: Distance do HC-SR04 = distância (cm); chuva = Ch no LCD.
nível da água = 200 - distância.
"""
import contextlib
import csv
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulador import DIST, M, T, novo_sistema, rodar  # noqa: E402

NOMES = M.NOMES
LED_VERDE, LED_AMARELO, LED_VERMELHO = (1, 0, 0), (0, 1, 0), (0, 0, 1)
linhas = []        # resultado de cada verificação
falhas = []


def silencio():
    return contextlib.redirect_stdout(io.StringIO())     # esconde o log serial do sistema


def estado(s, bus):
    return {
        "risco": NOMES[s.risco],
        "leds": tuple(l.value() for l in s.leds),
        "lcd1": bus.linha(0).rstrip(),
        "lcd2": bus.linha(1).rstrip(),
        "taxa": s.taxa,
    }


def verifica(passo, acao, esperado, obtido, ok):
    linhas.append({"passo": passo, "acao": acao, "esperado": esperado, "obtido": obtido,
                   "resultado": "OK" if ok else "FALHA"})
    if not ok:
        falhas.append(passo)


def aplicar(s, adc, dist, chuva):
    DIST[0] = dist
    adc.raw = int(chuva / 100 * 65535)


def passo(s, bus, adc, titulo, dist, chuva, segundos, esperado_risco, esperado_leds=None,
          esperado_lcd=None, extra=None):
    """Aplica distância e chuva, deixa o sistema rodar e confere o resultado."""
    aplicar(s, adc, dist, chuva)
    with silencio():
        rodar(s, segundos)
    e = estado(s, bus)
    nivel = max(0, 200 - dist) if dist is not None else None
    acao = f"Distance={dist} cm (nível {nivel} cm), chuva={chuva} mm/h, {segundos} s"
    ok = e["risco"] == esperado_risco
    if esperado_leds is not None:
        ok = ok and e["leds"] == esperado_leds
    if esperado_lcd is not None:
        ok = ok and esperado_lcd in (e["lcd1"] + "|" + e["lcd2"])
    if extra is not None:
        ok = ok and extra(s, e)
    esp = esperado_risco + ("" if esperado_leds is None else f", LEDs {esperado_leds}")
    esp += "" if esperado_lcd is None else f", LCD contém '{esperado_lcd}'"
    verifica(titulo, acao, esp, f"{e['risco']}, LEDs {e['leds']}, LCD '{e['lcd1']}' / '{e['lcd2']}'", ok)
    return e


def main():
    # ---------- cenário A: sequência do vídeo, com mudanças graduais ----------
    s, bus, adc, bz, btn, leds = novo_sistema()
    with silencio():
        rodar(s, 3)
    e = estado(s, bus)
    verifica("1. Partida", "Rio a 200 cm, sem chuva", "NORMAL, LED verde",
             f"{e['risco']}, LEDs {e['leds']}, LCD '{e['lcd1']}'",
             e["risco"] == "NORMAL" and e["leds"] == LED_VERDE and e["lcd1"].startswith("Rio:  0cm"))
    passo(s, bus, adc, "2. Rio sobe devagar (nível 50 cm)", 150, 0, 20, "NORMAL", LED_VERDE)
    passo(s, bus, adc, "3. Limiar de ATENÇÃO (nível 80 cm)", 120, 0, 20, "ATENCAO", LED_AMARELO)
    passo(s, bus, adc, "4. Nível 90 cm", 110, 0, 20, "ATENCAO", LED_AMARELO, "Rio: 90cm")
    passo(s, bus, adc, "5. Chuva forte (40 mm/h) com o rio já alto", 110, 40, 5, "ALERTA", LED_VERMELHO,
          "Ch: 40")
    passo(s, bus, adc, "6. Chuva volta a 0, rio em 130 cm", 70, 0, 25, "ALERTA", LED_VERMELHO)
    # emergência: LED vermelho deve piscar (aceso e apagado dentro de 1 s)
    aplicar(s, adc, 30, 0)
    with silencio():
        rodar(s, 20)
        vistos = set()
        for _ in range(20):                         # 20 passos de 50 ms = 1 s
            rodar(s, 0.05)
            vistos.add(s.leds[2].value())
    e = estado(s, bus)
    verifica("7. EMERGÊNCIA (nível 170 cm)", "Distance=30 cm, 20 s", "EMERGENCIA, LED vermelho pisca",
             f"{e['risco']}, LED vermelho assumiu {sorted(vistos)}",
             e["risco"] == "EMERGENCIA" and vistos == {0, 1})
    # botão de silenciar
    btn.v = 0
    with silencio():
        rodar(s, 0.1)
        btn.v = 1
        rodar(s, 0.5)
    e = estado(s, bus)
    verifica("8. Botão silencia o alarme", "Apertar o botão azul", "LCD 'Silenciado 60s' e buzzer mudo",
             f"LCD '{e['lcd2']}', mudo={s._mudo(T[0])}",
             "Silenciado 60s" in e["lcd2"] and s._mudo(T[0]) and e["risco"] == "EMERGENCIA")
    passo(s, bus, adc, "9. Rio baixa para 90 cm (histerese)", 110, 0, 40, "ATENCAO", LED_AMARELO)
    passo(s, bus, adc, "10. Rio volta ao normal", 200, 0, 40, "NORMAL", LED_VERDE)

    # ---------- cenário B: subida rápida (um salto de 200 para 110 cm) ----------
    s, bus, adc, bz, btn, leds = novo_sistema()
    with silencio():
        rodar(s, 3)
    aplicar(s, adc, 110, 0)
    with silencio():
        rodar(s, 5)
    e = estado(s, bus)
    verifica("11. Subida rápida", "Salto de 200 para 110 cm de uma vez (agora +5 s)",
             "ALERTA (nível 90 seria ATENÇÃO; a velocidade ≥ 10 cm/min sobe um nível), taxa ≥ 10 cm/min",
             f"{e['risco']}, taxa {e['taxa']:.0f} cm/min", e["risco"] == "ALERTA" and e["taxa"] >= 10)
    with silencio():
        rodar(s, 20)
    e = estado(s, bus)
    verifica("12. Água estabiliza", "Mais 20 s sem mudar", "volta para ATENCAO",
             f"{e['risco']}", e["risco"] == "ATENCAO")

    # ---------- cenário C: falha do sensor ----------
    s, bus, adc, bz, btn, leds = novo_sistema()
    with silencio():
        rodar(s, 3)
    DIST[0] = None                                    # sem eco
    with silencio():
        rodar(s, 6)
    e = estado(s, bus)
    verifica("13. Falha do sensor", "Sensor sem leitura por 6 s", "nunca NORMAL; LCD 'SEM SENSOR'",
             f"{e['risco']}, LCD '{e['lcd2']}'", e["risco"] != "NORMAL" and "SEM SENSOR" in e["lcd2"])
    DIST[0] = 200.0
    with silencio():
        rodar(s, 3)
    e = estado(s, bus)
    verifica("14. Sensor volta", "Leitura volta em 200 cm", "NORMAL", e["risco"], e["risco"] == "NORMAL")

    # ---------- saída ----------
    print("\nTESTES DA DEMONSTRAÇÃO (Estação Sentinela)\n")
    for r in linhas:
        print(f"[{r['resultado']:5s}] {r['passo']}")
        print(f"        ação:     {r['acao']}")
        print(f"        esperado: {r['esperado']}")
        print(f"        obtido:   {r['obtido']}")
    total = len(linhas)
    print(f"\nRESULTADO: {total - len(falhas)} de {total} passos OK" + ("" if not falhas else "  | FALHAS: " + ", ".join(falhas)))

    pasta = os.getcwd()
    with open(os.path.join(pasta, "resultados_demonstracao.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["passo", "acao", "esperado", "obtido", "resultado"], delimiter=";")
        w.writeheader()
        w.writerows(linhas)
    with open(os.path.join(pasta, "resultados_demonstracao.md"), "w", encoding="utf-8") as f:
        f.write("# Testes da demonstração (Estação Sentinela)\n\n| Passo | Ação | Esperado | Obtido | Resultado |\n|---|---|---|---|---|\n")
        for r in linhas:
            f.write("| {passo} | {acao} | {esperado} | {obtido} | {resultado} |\n".format(**{k: v.replace("|", "/") for k, v in r.items()}))
        f.write(f"\n**{total - len(falhas)} de {total} passos OK.**\n")
    print("Arquivos gravados: resultados_demonstracao.csv e resultados_demonstracao.md")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
