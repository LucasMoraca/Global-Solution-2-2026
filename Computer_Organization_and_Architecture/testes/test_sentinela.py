"""Testes da logica da Estacao Sentinela fora do Wokwi.

Simula: relogio (ticks), HC-SR04 (largura de pulso), potenciometro, botao, LEDs, buzzer e um
emulador simplificado do controlador HD44780 atras do adaptador I2C PCF8574 (para validar o driver).
"""
import json
import os
import sys
import time
import types

PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, PROJ)

# ---------- relogio simulado (substitui as funcoes especificas do MicroPython) ----------
T = [0]
time.ticks_ms = lambda: T[0]
time.ticks_diff = lambda a, b: a - b
time.ticks_add = lambda a, b: a + b
time.sleep_ms = lambda ms: T.__setitem__(0, T[0] + ms)
time.sleep_us = lambda us: None

# ---------- modulo "machine" falso ----------
DIST = [200.0]          # distancia lida pelo sensor (None => sem eco)
machine = types.ModuleType("machine")


class _Stub:
    def __init__(self, *a, **k):
        pass


machine.Pin = machine.ADC = machine.PWM = machine.I2C = _Stub
machine.time_pulse_us = lambda pin, level, timeout: (-2 if DIST[0] is None
                                                    else int(DIST[0] * 2 / 0.0343))
sys.modules["machine"] = machine

import main as M          # noqa: E402
LcdI2C = M.LcdI2C

M.time_pulse_us = machine.time_pulse_us


# ---------- perifericos falsos ----------
class FakePin:
    def __init__(self, v=1):
        self.v = v

    def value(self, x=None):
        if x is None:
            return self.v
        self.v = x

    def low(self):
        self.v = 0

    def high(self):
        self.v = 1


class FakeADC:
    def __init__(self):
        self.raw = 0

    def read_u16(self):
        return self.raw


class FakeBuzzer:
    def __init__(self):
        self.duty = 0
        self.f = 0
        self.historico = []

    def duty_u16(self, d):
        self.duty = d

    def freq(self, f):
        self.f = f


class HD44780Bus:
    """Emula PCF8574 + HD44780 em modo 4 bits: trava o nibble na borda de descida de E."""

    def __init__(self):
        self.prev = 0
        self.mode4 = False
        self.hi = None
        self.ddram = [" "] * 128
        self.cursor = 0
        self.nibbles_init = []

    def writeto(self, addr, buf):
        assert addr == 0x27, "endereco I2C inesperado"
        b = buf[0]
        if (self.prev & 0x04) and not (b & 0x04):      # borda de descida de E
            self._latch((b >> 4) & 0x0F, b & 0x01)
        self.prev = b
        assert b & 0x08, "luz de fundo deveria estar ligada"

    def _latch(self, nib, rs):
        if not self.mode4:
            self.nibbles_init.append(nib)
            if nib == 0x02:
                self.mode4 = True
            return
        if self.hi is None:
            self.hi = nib
            return
        byte = (self.hi << 4) | nib
        self.hi = None
        if rs == 0:
            if byte == 0x01:
                self.ddram = [" "] * 128
                self.cursor = 0
            elif byte & 0x80:
                self.cursor = byte & 0x7F
        else:
            self.ddram[self.cursor] = chr(byte)
            self.cursor += 1

    def linha(self, n):
        base = 0x40 if n else 0x00
        return "".join(self.ddram[base:base + 16])


# ---------- montagem do sistema ----------
def novo_sistema():
    T[0] = 0
    DIST[0] = 200.0
    bus = HD44780Bus()
    lcd = LcdI2C(bus, 0x27)
    adc, buzzer, botao = FakeADC(), FakeBuzzer(), FakePin(1)
    leds = (FakePin(0), FakePin(0), FakePin(0))
    s = M.Sentinela(FakePin(0), FakePin(0), adc, leds, buzzer, botao, lcd)
    return s, bus, adc, buzzer, botao, leds


def rodar(s, segundos, passo_ms=50, antes=None):
    for _ in range(int(segundos * 1000 / passo_ms)):
        T[0] += passo_ms
        if antes:
            antes()
        s.tick()


def nivel_para_dist(nivel_cm):
    return M.ALTURA_SENSOR_CM - nivel_cm


falhas = []


def confere(nome, cond, detalhe=""):
    print(("OK   " if cond else "FALHA"), "|", nome, detalhe)
    if not cond:
        falhas.append(nome)


# ================= 1) funcoes puras =================
confere("nivel_base sem histerese: 79->0, 80->1, 120->2, 160->3",
        [M.nivel_base(n, 0) for n in (79, 80, 120, 160)] == [0, 1, 2, 3])
confere("histerese: em ALERTA, 118 continua ALERTA; 114 cai para ATENCAO",
        M.nivel_base(118, 2) == 2 and M.nivel_base(114, 2) == 1)
confere("risco_final: subida rapida sobe 1 nivel", M.risco_final(1, 12, 0) == 2)
confere("risco_final: chuva forte so conta se a agua ja esta alta",
        M.risco_final(0, 0, 35) == 0 and M.risco_final(1, 0, 35) == 2)
confere("risco_final: chuva extrema => minimo ATENCAO", M.risco_final(0, 0, 70) == 1)
confere("risco_final: teto em 3", M.risco_final(3, 50, 90) == 3)
confere("chuva_mmh: 0 -> 0, 65535 -> 100", M.chuva_mmh(0) == 0 and abs(M.chuva_mmh(65535) - 100) < 1e-9)
confere("distancia: pulso de 11662 us ~ 200 cm",
        abs(11662 * M.VEL_SOM_CM_US / 2 - 200) < 0.5)

# ================= 2) cenario normal + LCD =================
s, bus, adc, bz, btn, leds = novo_sistema()
confere("driver LCD: sequencia de init entrou em modo 4 bits (3,3,3,2)", bus.nibbles_init[:4] == [3, 3, 3, 2],
        str(bus.nibbles_init[:4]))
rodar(s, 5)
confere("normal: risco 0, LED verde ligado, outros desligados",
        s.risco == 0 and [l.v for l in leds] == [1, 0, 0])
confere("normal: buzzer mudo", bz.duty == 0)
confere("LCD linha 1 = 'Rio:  0cm Ch:  0'", bus.linha(0) == "Rio:  0cm Ch:  0", repr(bus.linha(0)))
confere("LCD linha 2 comeca com 'NORMAL'", bus.linha(1).startswith("NORMAL"), repr(bus.linha(1)))
confere("linhas do LCD tem 16 colunas", len(bus.linha(0)) == 16 and len(bus.linha(1)) == 16)

# ================= 3) degraus de nivel (esperando a janela de taxa passar) =================
for nivel, esperado, nome in ((90, 1, "ATENCAO"), (130, 2, "ALERTA"), (170, 3, "EMERGENCIA")):
    DIST[0] = nivel_para_dist(nivel)
    rodar(s, 30)
    confere("nivel %d cm => %s" % (nivel, nome), s.risco == esperado, "(risco=%d)" % s.risco)
confere("EMERGENCIA: LEDs vermelho pisca (verde/amarelo apagados)", leds[0].v == 0 and leds[1].v == 0)
confere("LCD mostra EMERGENCIA sem cortar o final da linha",
        bus.linha(1).startswith("EMERGENCIA") and bus.linha(1).endswith("/m"), repr(bus.linha(1)))
confere("LCD linha 1 com nivel de 3 digitos cabe em 16 colunas",
        bus.linha(0) == "Rio:170cm Ch:  0", repr(bus.linha(0)))

vistos = set()
for _ in range(80):
    T[0] += 50
    s.tick()
    vistos.add((leds[2].v, bz.duty > 0))
confere("EMERGENCIA: LED vermelho alterna e buzzer toca em pulsos",
        {(0, False), (1, True)} <= vistos or ({0, 1} <= {v[0] for v in vistos} and {True, False} <= {v[1] for v in vistos}),
        str(sorted(vistos)))

# histerese na descida
DIST[0] = nivel_para_dist(118)
rodar(s, 30)
confere("descendo de EMERGENCIA para 118 cm => ALERTA", s.risco == 2, "(risco=%d)" % s.risco)
DIST[0] = nivel_para_dist(116)
rodar(s, 30)
confere("histerese: 116 cm ainda ALERTA (limiar de saida = 115)", s.risco == 2, "(risco=%d)" % s.risco)
DIST[0] = nivel_para_dist(114)
rodar(s, 30)
confere("114 cm => ATENCAO", s.risco == 1, "(risco=%d)" % s.risco)
DIST[0] = nivel_para_dist(10)
rodar(s, 30)
confere("10 cm => NORMAL de novo", s.risco == 0 and leds[0].v == 1)

# ================= 4) subida rapida (nivel baixo, mas subindo) =================
s, bus, adc, bz, btn, leds = novo_sistema()
rodar(s, 3)
inicio = T[0]


def sobe_1cm_por_s():
    DIST[0] = nivel_para_dist(min(40, (T[0] - inicio) / 1000.0))


rodar(s, 20, antes=sobe_1cm_por_s)
confere("subida de ~60 cm/min (nivel < 40 cm) => ATENCAO por velocidade", s.risco == 1 and s.base == 0,
        "(risco=%d base=%d taxa=%.1f)" % (s.risco, s.base, s.taxa))

# ================= 5) chuva =================
s, bus, adc, bz, btn, leds = novo_sistema()
adc.raw = int(70 / 100 * 65535)
rodar(s, 3)
confere("chuva extrema (70 mm/h) com rio baixo => ATENCAO", s.risco == 1, "(risco=%d)" % s.risco)
confere("LCD mostra a chuva (Ch: 70)", "Ch: 70" in bus.linha(0), repr(bus.linha(0)))
s, bus, adc, bz, btn, leds = novo_sistema()
DIST[0] = nivel_para_dist(90)
rodar(s, 30)
adc.raw = int(35 / 100 * 65535)
rodar(s, 3)
confere("chuva forte (35 mm/h) + rio em ATENCAO => ALERTA", s.risco == 2, "(risco=%d)" % s.risco)

# ================= 6) falha do sensor =================
s, bus, adc, bz, btn, leds = novo_sistema()
rodar(s, 3)
DIST[0] = None
rodar(s, 1)
confere("1-2 leituras ruins ainda nao declaram falha", not s.falha)
rodar(s, 4)
confere("5 leituras invalidas seguidas => falha e risco >= ATENCAO (fail-safe)", s.falha and s.risco >= 1)
confere("LCD mostra 'SEM SENSOR' sem cortar o final da linha",
        bus.linha(1).startswith("SEM SENSOR") and bus.linha(1).endswith("/m"), repr(bus.linha(1)))
DIST[0] = 200.0
rodar(s, 3)
confere("sensor volta => falha limpa e NORMAL", (not s.falha) and s.risco == 0)

# ================= 7) botao de silenciar =================
s, bus, adc, bz, btn, leds = novo_sistema()
DIST[0] = nivel_para_dist(130)
rodar(s, 30)
assert s.risco == 2


def toca():
    toca.n += 1 if bz.duty > 0 else 0


toca.n = 0
rodar(s, 3, antes=toca)
confere("ALERTA: buzzer toca antes de silenciar", toca.n > 0)
btn.v = 0
rodar(s, 0.2)
btn.v = 1
rodar(s, 0.2)
confere("botao: LCD mostra 'Silenciado 60s'", bus.linha(1).startswith("Silenciado 60s"), repr(bus.linha(1)))
toca.n = 0
rodar(s, 10, antes=toca)
confere("silenciado: buzzer em silencio por 10 s", toca.n == 0)
confere("silenciado: LED vermelho continua aceso", leds[2].v == 1)
DIST[0] = nivel_para_dist(170)
rodar(s, 30)
toca.n = 0
rodar(s, 3, antes=toca)
confere("risco piorou (EMERGENCIA) => silencio cancelado, buzzer volta", s.risco == 3 and toca.n > 0)

s, bus, adc, bz, btn, leds = novo_sistema()
DIST[0] = nivel_para_dist(130)
rodar(s, 30)
btn.v = 0
rodar(s, 0.2)
btn.v = 1
rodar(s, 61)
toca.n = 0
rodar(s, 3, antes=toca)
confere("apos 60 s o silencio expira e o buzzer volta", toca.n > 0)

s, bus, adc, bz, btn, leds = novo_sistema()
rodar(s, 3)
btn.v = 0
rodar(s, 0.2)
confere("botao com risco NORMAL nao silencia nada", s.mudo_ate is None)

# ================= 8) log serial em JSON =================
import io
import contextlib

s, bus, adc, bz, btn, leds = novo_sistema()
DIST[0] = nivel_para_dist(130)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rodar(s, 35)
linhas = [l for l in buf.getvalue().splitlines() if l.startswith("{")]
ult = json.loads(linhas[-1])
confere("log serial em JSON valido com os campos esperados",
        set(ult) == {"t_s", "nivel_cm", "taxa_cm_min", "chuva_mmh", "risco", "mudo", "falha_sensor"}, str(ult))
confere("log: ALERTA com nivel ~130 cm", ult["risco"] == "ALERTA" and abs(ult["nivel_cm"] - 130) < 1)
confere("mensagem de orientacao impressa ao mudar de nivel",
        any(l.startswith("[ALERTA]") for l in buf.getvalue().splitlines()))

# ================= 9) consistencia do diagram.json =================
d = json.load(open(os.path.join(PROJ, "diagram.json")))
ids = {p["id"]: p["type"] for p in d["parts"]}
confere("diagram.json: ids de pecas unicos", len(ids) == len(d["parts"]))
pinos_usados = []
ok_ids = True
for a, b, *_ in d["connections"]:
    for ponta in (a, b):
        pid = ponta.split(":")[0]
        ok_ids &= pid in ids
        pinos_usados.append(ponta)
confere("diagram.json: toda conexao aponta para uma peca existente", ok_ids)
conex = {(a, b) for a, b, *_ in d["connections"]}
precisa = {
    ("pico:GP16", "ultra:TRIG"), ("pico:GP17", "ultra:ECHO"), ("pico:GP26", "pot:SIG"),
    ("pico:GP4", "lcd:SDA"), ("pico:GP5", "lcd:SCL"), ("pico:GP10", "rv:1"), ("pico:GP11", "ra:1"),
    ("pico:GP12", "rr:1"), ("pico:GP13", "bz:2"), ("pico:GP14", "btn:1.l"),
}
achados = {tuple(sorted(p)) for p in conex}
confere("diagram.json: pinagem bate com as constantes de main.py",
        all(tuple(sorted(p)) in achados for p in precisa))
pins_main = {M.PIN_TRIG: "GP16", M.PIN_ECHO: "GP17", M.PIN_CHUVA: "GP26", M.PIN_LED_VERDE: "GP10",
             M.PIN_LED_AMARELO: "GP11", M.PIN_LED_VERMELHO: "GP12", M.PIN_BUZZER: "GP13",
             M.PIN_BOTAO: "GP14", M.PIN_SDA: "GP4", M.PIN_SCL: "GP5"}
confere("constantes de pino em main.py = GPxx do diagrama", all("GP%d" % k == v for k, v in pins_main.items()))
gp = [p for p in pinos_usados if p.startswith("pico:GP")]
confere("nenhum GPIO ligado a duas coisas (exceto I/O dedicados)", len(gp) == len(set(gp)), str(sorted(gp)))


# ================= 10) autoteste de hardware na partida =================
s, bus, adc, bz, btn, leds = novo_sistema()
estados, sons = [], []
_orig_valor = FakePin.value


class LedEspia(FakePin):
    def __init__(self, nome):
        super().__init__(0)
        self.nome = nome

    def value(self, x=None):
        if x is not None:
            estados.append((self.nome, x))
        return super().value(x)


class BuzzerEspia(FakeBuzzer):
    def duty_u16(self, d):
        sons.append(d)
        super().duty_u16(d)


leds_e = (LedEspia("verde"), LedEspia("amarelo"), LedEspia("vermelho"))
buz_e = BuzzerEspia()
bus2 = HD44780Bus()
M.autoteste(leds_e, buz_e, LcdI2C(bus2, 0x27))
acendeu = [n for n, v in estados if v == 1]
confere("autoteste: acende verde, amarelo e vermelho nessa ordem", acendeu == ["verde", "amarelo", "vermelho"], str(acendeu))
confere("autoteste: um LED por vez (nunca dois acesos juntos)",
        all(sum(1 for l in leds_e if l.v) <= 1 for _ in [0]))
confere("autoteste: buzzer toca e termina em silencio", max(sons) > 0 and sons[-1] == 0, str(sons))
confere("autoteste: todos os LEDs terminam apagados", all(l.v == 0 for l in leds_e))
confere("autoteste: LCD termina em 'Autoteste OK'", bus2.linha(1).startswith("Autoteste OK"), repr(bus2.linha(1)))

print()
print("RESULTADO:", "TUDO OK" if not falhas else "%d FALHA(S): %s" % (len(falhas), falhas))
sys.exit(1 if falhas else 0)
