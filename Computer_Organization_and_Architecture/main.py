# main.py
# PLANTAO ENCHENTE - Estacao Sentinela
# GS 2026.2 CitizenTech - Computer Organization and Architecture
# Raspberry Pi Pico + MicroPython (simulacao no Wokwi)
#
# Integrantes:
#   Gabriel Barbosa Furin - RM 572941
#   Lucas Kiodi Moraca - RM 571004
#   Renan Fracalossi Mano da Silva - RM 569610
#
# Problema: moradores de areas alagaveis recebem o aviso de enchente tarde demais.
# Solucao: uma estacao de baixo custo que mede o nivel do rio/corrego (sensor ultrassonico),
# a intensidade da chuva (pluviometro, simulado por um potenciometro) e a VELOCIDADE com que
# a agua sobe, classifica o risco em 4 niveis e avisa a comunidade com LEDs, buzzer e display.
#
# AVISO: prototipo educacional. Os limiares abaixo sao HIPOTETICOS e devem ser calibrados com
# dados reais e com a Defesa Civil. Nao substitui o alerta oficial (Defesa Civil: 199).

from machine import Pin, ADC, PWM, I2C, time_pulse_us
import time
import json

# ===================== DRIVER DO LCD I2C =====================
# Driver minimo para LCD 16x2 (controlador HD44780) com adaptador I2C PCF8574 (endereco 0x27).
#
# Mapeamento dos bits do PCF8574 (padrao dos adaptadores/backpacks):
#   P0 = RS | P1 = RW | P2 = E | P3 = luz de fundo | P4..P7 = D4..D7
# O LCD e usado em modo de 4 bits: cada byte e enviado em dois "nibbles" (4 bits),
# e cada nibble precisa de um pulso no pino E (enable) para ser lido pelo controlador.


class LcdI2C:
    RS = 0x01
    E = 0x04
    BL = 0x08

    def __init__(self, i2c, addr=0x27, cols=16, rows=2):
        self.i2c = i2c
        self.addr = addr
        self.cols = cols
        self.rows = rows
        self.bl = self.BL
        time.sleep_ms(50)
        # Sequencia de inicializacao do HD44780 para entrar em modo de 4 bits
        self._nibble(0x03)
        time.sleep_ms(5)
        self._nibble(0x03)
        time.sleep_us(150)
        self._nibble(0x03)
        time.sleep_us(150)
        self._nibble(0x02)
        time.sleep_us(150)
        self.cmd(0x28)  # 4 bits, 2 linhas, fonte 5x8
        self.cmd(0x0C)  # display ligado, cursor oculto
        self.cmd(0x06)  # cursor avanca para a direita ao escrever
        self.clear()

    def _write(self, valor):
        self.i2c.writeto(self.addr, bytes([(valor | self.bl) & 0xFF]))

    def _pulso(self, dado):
        self._write(dado | self.E)
        time.sleep_us(2)
        self._write(dado & ~self.E & 0xFF)
        time.sleep_us(60)

    def _nibble(self, nibble, rs=0):
        self._pulso(((nibble & 0x0F) << 4) | rs)

    def _byte(self, valor, rs=0):
        self._nibble(valor >> 4, rs)
        self._nibble(valor & 0x0F, rs)

    def cmd(self, comando):
        self._byte(comando, 0)
        if comando <= 0x03:  # clear e home levam ~1,5 ms
            time.sleep_ms(2)

    def clear(self):
        self.cmd(0x01)

    def escrever(self, linha, texto):
        """Escreve 'texto' na linha 0 ou 1, completando com espacos (apenas ASCII)."""
        self.cmd(0x80 | (0x40 if linha else 0x00))
        texto = ("%-" + str(self.cols) + "s") % texto
        for ch in texto[: self.cols]:
            o = ord(ch)
            self._byte(o if o < 128 else 0x3F, self.RS)  # fora do ASCII vira '?'


# ===================== PINAGEM (Raspberry Pi Pico) =====================
PIN_TRIG = 16          # HC-SR04 TRIG (saida digital)
PIN_ECHO = 17          # HC-SR04 ECHO (entrada digital, mede a largura do pulso)
PIN_CHUVA = 26         # potenciometro = pluviometro (ADC0)
PIN_LED_VERDE = 10
PIN_LED_AMARELO = 11
PIN_LED_VERMELHO = 12
PIN_BUZZER = 13        # saida PWM
PIN_BOTAO = 14         # botao "silenciar alarme" (entrada com pull-up)
PIN_SDA = 4            # I2C0 SDA -> LCD
PIN_SCL = 5            # I2C0 SCL -> LCD

# ===================== MODO DEMONSTRACAO (para gravar o video) =====================
# True  = a simulacao se joga sozinha, seguindo o roteiro do video (cerca de 75 s): o proprio codigo
#         "move" o sensor, a chuva e o botao. Basta clicar em Start Simulation e gravar a tela.
# False = Estacao normal: voce mexe no sensor ultrassonico, no potenciometro e no botao.
MODO_DEMO = True

# ===================== PARAMETROS (hipoteticos) =====================
ALTURA_SENSOR_CM = 200            # distancia do sensor ate o fundo do canal
LIMIAR_NIVEL_CM = (80, 120, 160)  # entra em ATENCAO / ALERTA / EMERGENCIA
HISTERESE_CM = 5                  # para descer de nivel, precisa cair 5 cm abaixo do limiar
CHUVA_MAX_MMH = 100               # fundo de escala do pluviometro simulado
CHUVA_FORTE_MMH = 30
CHUVA_EXTREMA_MMH = 60
TAXA_RAPIDA_CM_MIN = 10           # subida considerada rapida
JANELA_TAXA_MS = 10000            # janela para estimar a velocidade de subida
PERIODO_LEITURA_MS = 500          # periodo de amostragem dos sensores
PERIODO_LOG_MS = 2000             # periodo do log serial
SILENCIO_MS = 60000               # duracao do silenciamento do alarme
FALHAS_MAX = 5                    # leituras invalidas seguidas ate declarar falha do sensor
VEL_SOM_CM_US = 0.0343            # velocidade do som: ~343 m/s = 0,0343 cm/us

NOMES = ("NORMAL", "ATENCAO", "ALERTA", "EMERGENCIA")
ORIENTACAO = (
    "Sem risco no momento. Monitoramento ativo.",
    "Atencao: acompanhe os avisos da Defesa Civil.",
    "Alerta: evite areas alagaveis e prepare-se para sair.",
    "Emergencia: afaste-se do rio/corrego e ligue 199 (Defesa Civil) ou 193 (Bombeiros).",
)
# (tempo ligado em ms, periodo em ms, frequencia em Hz) por nivel de risco
PADRAO_BUZZER = (None, (150, 5000, 800), (300, 1000, 1200), (150, 300, 2000))


# ===================== SENSORES =====================
def distancia_cm(trig, echo):
    """Mede a distancia com o HC-SR04 pelo tempo de voo do pulso ultrassonico."""
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()
    duracao = time_pulse_us(echo, 1, 30000)   # largura do pulso em ECHO (us); <0 = timeout
    if duracao < 0:
        return None
    return duracao * VEL_SOM_CM_US / 2        # ida e volta -> divide por 2


def distancia_mediana(trig, echo):
    """Mediana de 3 medidas: filtra picos de ruido. Devolve None se nao houver leitura valida."""
    valores = []
    for _ in range(3):
        d = distancia_cm(trig, echo)
        if d is not None:
            valores.append(d)
        time.sleep_ms(10)
    if len(valores) < 2:
        return None
    valores.sort()
    return valores[len(valores) // 2]


def nivel_da_agua_cm(distancia):
    """Nivel da agua = altura do sensor - distancia ate a superficie."""
    return max(0.0, ALTURA_SENSOR_CM - distancia)


def chuva_mmh(leitura_u16):
    """Converte a leitura do ADC (0..65535 no MicroPython) em mm/h (0..CHUVA_MAX_MMH)."""
    return leitura_u16 * CHUVA_MAX_MMH / 65535


# ===================== LOGICA DE RISCO =====================
def nivel_base(nivel_cm, anterior):
    """Nivel de risco pela altura da agua, com histerese para nao ficar 'piscando' no limiar."""
    base = anterior
    while base < 3 and nivel_cm >= LIMIAR_NIVEL_CM[base]:
        base += 1
    while base > 0 and nivel_cm < LIMIAR_NIVEL_CM[base - 1] - HISTERESE_CM:
        base -= 1
    return base


def risco_final(base, taxa_cm_min, chuva):
    """Combina altura, velocidade de subida e chuva em um nivel de risco de 0 a 3."""
    r = base
    if taxa_cm_min >= TAXA_RAPIDA_CM_MIN:           # agua subindo rapido
        r += 1
    if chuva >= CHUVA_FORTE_MMH and base >= 1:      # chuva forte com a agua ja alta
        r += 1
    if chuva >= CHUVA_EXTREMA_MMH:                  # chuva extrema: no minimo ATENCAO
        r = max(r, 1)
    return min(r, 3)


class TaxaDeSubida:
    """Estima a velocidade de subida da agua (cm/min) numa janela deslizante."""

    def __init__(self):
        self.hist = []

    def atualizar(self, agora, nivel):
        self.hist.append((agora, nivel))
        while len(self.hist) > 1 and time.ticks_diff(agora, self.hist[1][0]) >= JANELA_TAXA_MS:
            self.hist.pop(0)
        t0, n0 = self.hist[0]
        dt = time.ticks_diff(agora, t0)
        if dt < JANELA_TAXA_MS // 2:                 # ainda sem dados suficientes
            return 0.0
        return (nivel - n0) * 60000 / dt


# ===================== SISTEMA =====================
class Sentinela:
    def __init__(self, trig, echo, adc, leds, buzzer, botao, lcd):
        self.trig, self.echo, self.adc = trig, echo, adc
        self.leds = leds            # (verde, amarelo, vermelho)
        self.buzzer, self.botao, self.lcd = buzzer, botao, lcd
        self.taxas = TaxaDeSubida()
        self.nivel = 0.0
        self.taxa = 0.0
        self.chuva = 0.0
        self.base = 0
        self.risco = 0
        self.falhas = 0
        self.falha = False
        self.mudo_ate = None
        self.risco_ao_silenciar = 0
        self.msg_ate = 0
        self.btn_anterior = 1
        self.t_btn = -1000
        self.t_leitura = None
        self.t_log = None
        self.linhas = (None, None)

    # ---- laco principal: chamado a cada ~20 ms ----
    def tick(self):
        agora = time.ticks_ms()
        self._botao(agora)
        if self.t_leitura is None or time.ticks_diff(agora, self.t_leitura) >= PERIODO_LEITURA_MS:
            self.t_leitura = agora
            self._ler_e_decidir(agora)
        self._atuar(agora)

    def _mudo(self, agora):
        return self.mudo_ate is not None and time.ticks_diff(self.mudo_ate, agora) > 0

    def _botao(self, agora):
        lido = self.botao.value()                    # pull-up: solto = 1, apertado = 0
        if lido == 0 and self.btn_anterior == 1 and time.ticks_diff(agora, self.t_btn) > 300:
            self.t_btn = agora
            if self.risco >= 1:
                self.mudo_ate = time.ticks_add(agora, SILENCIO_MS)
                self.risco_ao_silenciar = self.risco
                self.msg_ate = time.ticks_add(agora, 2000)
                self._atualizar_lcd(agora)
        self.btn_anterior = lido

    def _ler_e_decidir(self, agora):
        dist = distancia_mediana(self.trig, self.echo)
        self.chuva = chuva_mmh(self.adc.read_u16())
        if dist is None:
            self.falhas += 1
        else:
            self.falhas = 0
            self.nivel = nivel_da_agua_cm(dist)
            self.taxa = self.taxas.atualizar(agora, self.nivel)
            self.base = nivel_base(self.nivel, self.base)
        self.falha = self.falhas >= FALHAS_MAX

        novo = risco_final(self.base, self.taxa, self.chuva)
        if self.falha:
            novo = max(novo, 1)                      # sem enxergar o rio, nunca declara "NORMAL"
        if novo == 0 or (self.mudo_ate is not None and novo > self.risco_ao_silenciar):
            self.mudo_ate = None                     # risco subiu (ou acabou): volta a avisar
        mudou = novo != self.risco
        self.risco = novo

        self._atualizar_lcd(agora)
        if mudou:
            print("[%s] %s" % (NOMES[novo], ORIENTACAO[novo]))
        if mudou or self.t_log is None or time.ticks_diff(agora, self.t_log) >= PERIODO_LOG_MS:
            self.t_log = agora
            self._log(agora)

    def _atualizar_lcd(self, agora):
        t = max(-999, min(999, int(round(self.taxa))))
        taxa_txt = ("+" if t >= 0 else "-") + str(abs(t))
        l1 = "Rio:%3dcm Ch:%3d" % (int(round(self.nivel)), int(round(self.chuva)))
        if time.ticks_diff(self.msg_ate, agora) > 0:
            l2 = "Silenciado 60s"
        else:
            nome = "SEM SENSOR" if self.falha else NOMES[self.risco]   # max. 10 caracteres
            l2 = "%-10s%4s/m" % (nome, taxa_txt)
        if l1 != self.linhas[0]:
            self.lcd.escrever(0, l1)
        if l2 != self.linhas[1]:
            self.lcd.escrever(1, l2)
        self.linhas = (l1, l2)

    def _atuar(self, agora):
        r = self.risco
        pisca = (agora // 250) % 2 == 0
        verde = (r == 0) and not self.falha
        amarelo = ((r == 1) and not self.falha) or (self.falha and pisca)
        vermelho = (r == 2) or (r == 3 and pisca)
        self.leds[0].value(1 if verde else 0)
        self.leds[1].value(1 if amarelo else 0)
        self.leds[2].value(1 if vermelho else 0)

        padrao = PADRAO_BUZZER[r]
        if padrao is None or self._mudo(agora):
            self.buzzer.duty_u16(0)
        else:
            ligado, periodo, freq = padrao
            if agora % periodo < ligado:
                self.buzzer.freq(freq)
                self.buzzer.duty_u16(20000)
            else:
                self.buzzer.duty_u16(0)

    def _log(self, agora):
        print(json.dumps({
            "t_s": agora // 1000,
            "nivel_cm": round(self.nivel, 1),
            "taxa_cm_min": round(self.taxa, 1),
            "chuva_mmh": round(self.chuva, 1),
            "risco": NOMES[self.risco],
            "mudo": self._mudo(agora),
            "falha_sensor": self.falha,
        }))


def autoteste(leds, buzzer, lcd):
    """Teste de hardware na partida: acende cada LED, toca o buzzer e informa no LCD e na serial."""
    nomes = ("LED verde", "LED amarelo", "LED vermelho")
    for i in range(3):
        for k in range(3):
            leds[k].value(1 if k == i else 0)
        lcd.escrever(1, nomes[i])
        print("Autoteste:", nomes[i])
        time.sleep_ms(700)
    for k in range(3):
        leds[k].value(0)
    lcd.escrever(1, "Buzzer")
    print("Autoteste: buzzer")
    buzzer.freq(1000)
    buzzer.duty_u16(20000)
    time.sleep_ms(400)
    buzzer.duty_u16(0)
    lcd.escrever(1, "Autoteste OK")
    print("Autoteste concluido")
    time.sleep_ms(700)


# ===================== SIMULACAO DO ROTEIRO (MODO_DEMO) =====================
# Em MODO_DEMO, as leituras do sensor, da chuva e do botao vem desta tabela, e nao dos componentes.
# A logica de risco, os LEDs, o buzzer e o LCD sao os mesmos da Estacao real.
SIM = {"dist": 200, "chuva": 0}


class AdcSimulado:
    """Faz o papel do potenciometro (pluviometro): devolve a chuva simulada em 16 bits."""

    def read_u16(self):
        return int(SIM["chuva"] * 65535 / CHUVA_MAX_MMH)


class BotaoSimulado:
    """Faz o papel do botao 'silenciar' (pull-up: solto = 1, apertado = 0)."""

    def __init__(self):
        self.v = 1

    def value(self):
        return self.v


def distancia_simulada(trig, echo):
    return SIM["dist"]


# (segundo da cena, legenda, distancia do sensor em cm, chuva em mm/h, aperta o botao?)
# distancia/chuva = None mantem o valor anterior. Nivel da agua = 200 - distancia.
ROTEIRO = (
    (0, "CENA 1 - Estacao em operacao normal: rio baixo, LED verde", 200, 0, False),
    (6, "CENA 2 - O rio sobe de uma vez: o sensor passa a medir 110 cm (nivel da agua 90 cm). "
        "Pelo nivel seria ATENCAO, mas a subida e muito rapida (acima de 10 cm/min) e o sistema sobe "
        "um nivel -> ALERTA, LED vermelho", 110, None, False),
    (18, "          A agua se estabilizou: a velocidade de subida volta a zero e o risco cai para "
         "ATENCAO, LED amarelo", None, None, False),
    (25, "CENA 3 - Chuva forte: o pluviometro marca 40 mm/h com o rio ja alto -> ALERTA, LED vermelho",
     None, 40, False),
    (42, "CENA 4 - O rio chega a 170 cm (sensor a 30 cm) -> EMERGENCIA, LED vermelho piscando e buzzer agudo",
     30, 0, False),
    (52, "CENA 5 - Alguem aperta o botao azul: alarme silenciado por 60 s", None, None, True),
    (57, "CENA 6 - Monitor serial: a estacao registra nivel, taxa, chuva e risco em JSON a cada 2 s",
     None, None, False),
    (73, "FIM DA DEMONSTRACAO - Estacao Sentinela (prototipo educacional; nao substitui o alerta oficial, 199)",
     None, None, False),
)


def roteiro_demo(sistema, botao):
    """Executa o ROTEIRO em tempo real e continua rodando a estacao com os ultimos valores."""
    inicio = time.ticks_ms()
    proximo = 0
    soltar_em = None
    while True:
        seg = time.ticks_diff(time.ticks_ms(), inicio) / 1000
        while proximo < len(ROTEIRO) and seg >= ROTEIRO[proximo][0]:
            t, legenda, dist, chuva, aperta = ROTEIRO[proximo]
            if dist is not None:
                SIM["dist"] = dist
            if chuva is not None:
                SIM["chuva"] = chuva
            print("")
            print("[%02d:%02d] %s" % (t // 60, t % 60, legenda))
            if dist is not None or chuva is not None:
                print("        entradas simuladas -> sensor ultrassonico: %d cm (nivel da agua %d cm) | chuva: %d mm/h"
                      % (SIM["dist"], max(0, ALTURA_SENSOR_CM - SIM["dist"]), SIM["chuva"]))
            if aperta:
                botao.v = 0
                soltar_em = seg + 0.2
            proximo += 1
        if soltar_em is not None and seg >= soltar_em:
            botao.v = 1
            soltar_em = None
        sistema.tick()
        time.sleep_ms(20)


def main():
    global distancia_mediana
    leds = (Pin(PIN_LED_VERDE, Pin.OUT), Pin(PIN_LED_AMARELO, Pin.OUT), Pin(PIN_LED_VERMELHO, Pin.OUT))
    buzzer = PWM(Pin(PIN_BUZZER))
    buzzer.duty_u16(0)
    i2c = I2C(0, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=400000)
    lcd = LcdI2C(i2c, 0x27)
    if MODO_DEMO:
        trig = echo = None
        adc = AdcSimulado()
        botao = BotaoSimulado()
        distancia_mediana = distancia_simulada      # o "sensor" passa a ler a tabela do roteiro
    else:
        trig = Pin(PIN_TRIG, Pin.OUT)
        echo = Pin(PIN_ECHO, Pin.IN)
        adc = ADC(Pin(PIN_CHUVA))
        botao = Pin(PIN_BOTAO, Pin.IN, Pin.PULL_UP)

    lcd.escrever(0, "Plantao Enchente")
    print("Plantao Enchente - Estacao Sentinela iniciada" + (" (MODO DEMONSTRACAO)" if MODO_DEMO else ""))
    autoteste(leds, buzzer, lcd)

    sistema = Sentinela(trig, echo, adc, leds, buzzer, botao, lcd)
    if MODO_DEMO:
        roteiro_demo(sistema, botao)
    while True:
        sistema.tick()
        time.sleep_ms(20)


if __name__ == "__main__":
    main()
