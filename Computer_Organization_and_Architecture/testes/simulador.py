"""Simulador da Estacao Sentinela fora do Wokwi (relogio, HC-SR04, potenciometro, botao, LEDs, buzzer e LCD).

Usado por demonstracao_gravacao.py. Mesmo codigo de montagem do test_sentinela.py."""
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


