# Estação Sentinela - Plantão Enchente

Entrega de **Computer Organization and Architecture** (Global Solution FIAP 2026.2, CitizenTech).

## Integrantes
- Gabriel Barbosa Furin - RM 572941
- Lucas Kiodi Moraca - RM 571004
- Renan Fracalossi Mano da Silva - RM 569610

## Links da entrega
- Vídeo (YouTube): https://youtu.be/GP1SGBqTki4
- Projeto no Wokwi: COLE AQUI

## Problema e solução
Moradores de áreas alagáveis recebem o aviso de enchente tarde demais. A **Estação Sentinela** é um protótipo de baixo custo, simulado no Wokwi com Raspberry Pi Pico e MicroPython. Ela mede o **nível do rio ou córrego** (sensor ultrassônico), a **intensidade da chuva** (pluviômetro, simulado por um potenciômetro) e a **velocidade com que a água sobe**. Classifica o risco em 4 níveis (NORMAL, ATENÇÃO, ALERTA, EMERGÊNCIA) e avisa a comunidade com LEDs, buzzer e display LCD. Um botão silencia o alarme por 60 segundos.

> **Aviso:** protótipo educacional. Os limiares são **hipotéticos** e precisam ser calibrados com dados reais e com a Defesa Civil. Não substitui o alerta oficial (Defesa Civil: 199; Bombeiros: 193).

## Componentes e pinagem (Raspberry Pi Pico)
| Componente | Pino | Função |
|---|---|---|
| Sensor ultrassônico HC-SR04 | GP16 (TRIG), GP17 (ECHO) | mede a distância até a água pelo tempo de voo do som |
| Potenciômetro | GP26 (ADC0) | simula o pluviômetro (0 a 100 mm/h) |
| Display LCD 16x2 com I2C (0x27) | GP4 (SDA), GP5 (SCL) | mostra nível, chuva, risco e velocidade de subida |
| LED verde / amarelo / vermelho | GP10 / GP11 / GP12 (resistor de 330 ohms) | indicam o risco |
| Buzzer | GP13 (PWM) | alarme sonoro, com tom e ritmo por nível |
| Botão | GP14 (pull-up interno) | silencia o alarme por 60 s |

## Conceitos de arquitetura de computadores aplicados
- **GPIO** de entrada e saída (LEDs, botão, TRIG e ECHO) e **pull-up** no botão (solto = 1, apertado = 0).
- **ADC de 16 bits** (0 a 65535) para o potenciômetro, convertido em mm/h.
- **Barramento I2C** com o LCD, usando o adaptador PCF8574 e um driver mínimo escrito por nós (modo de 4 bits do controlador HD44780).
- **PWM** no buzzer para variar o tom (800, 1200 e 2000 Hz).
- **Medida de tempo** com `ticks_ms`/`ticks_diff` e pulso de ECHO medido com `time_pulse_us`; distância = tempo x 0,0343 cm/us / 2.
- **Laço de controle por polling**: o laço principal roda a cada ~20 ms (botão, LEDs, buzzer); os sensores são lidos a cada 500 ms; o log serial sai a cada 2 s.

## Lógica de risco
- **Nível da água** = 200 cm (altura do sensor) - distância medida. Mediana de 3 leituras para filtrar ruído.
- **Limiares** de nível: 80 cm (ATENÇÃO), 120 cm (ALERTA) e 160 cm (EMERGÊNCIA), com **histerese** de 5 cm para o risco não ficar "piscando" no limite.
- **Velocidade de subida** estimada em janela de 10 s: se for **10 cm/min ou mais**, o risco sobe um nível.
- **Chuva**: 30 mm/h ou mais com a água já alta (ATENÇÃO ou pior) sobe um nível; 60 mm/h ou mais garante no mínimo ATENÇÃO.
- **Falha do sensor**: após 5 leituras inválidas seguidas, o sistema mostra "SEM SENSOR" e nunca declara NORMAL.
- **Alarme**: LED verde (NORMAL), amarelo (ATENÇÃO), vermelho fixo (ALERTA) e vermelho piscando (EMERGÊNCIA); buzzer com 800 Hz (bip curto a cada 5 s), 1200 Hz (a cada 1 s) e 2000 Hz (a cada 0,3 s). O botão silencia por 60 s, mas o alarme volta se o risco subir.
- Cada mudança de risco imprime a orientação na serial (por exemplo, "Emergencia: afaste-se do rio/corrego e ligue 199 ...") e há um log JSON a cada 2 s.

## Como executar no Wokwi
1. Em wokwi.com, crie um projeto **Raspberry Pi Pico** com **MicroPython**.
2. Cole o conteúdo de `main.py` na aba `main.py` e o de `diagram.json` na aba `diagram.json`.
3. Clique em **Start Simulation** e abra o Serial Monitor.

O `main.py` tem uma chave no início, `MODO_DEMO`:
- `MODO_DEMO = True` (padrão da entrega): a **demonstração roda sozinha** por cerca de 75 s. O próprio código simula as leituras do sensor, da chuva e do botão (normal, subida rápida, alerta, chuva forte, emergência, botão de silenciar e log), com uma legenda no Serial Monitor a cada cena. A lógica de risco, os LEDs, o buzzer e o LCD são os mesmos da estação real.
- `MODO_DEMO = False`: estação com controle manual. Clique no HC-SR04 e altere **Distance** (nível da água = 200 - distância), gire o potenciômetro (chuva) e clique no botão azul.

## Testes
Rodam fora do Wokwi, com Python 3 e sem bibliotecas externas, simulando relógio, sensor, potenciômetro, botão, LEDs, buzzer e até o controlador do LCD:

```
python testes/test_sentinela.py          # testes da lógica e do driver do LCD (deve terminar em "RESULTADO: TUDO OK")
python testes/demonstracao_gravacao.py   # 14 passos da demonstração; grava resultados_demonstracao.csv e .md
```
O resultado dos 14 passos (14 de 14 OK) está em `docs/resultados_demonstracao.md`. Ao quebrar de propósito um limiar de risco, os testes acusam falha, o que mostra que eles detectam erros.

## Limitações
- Os limiares (nível, velocidade e chuva) são **hipotéticos**; sem calibração em campo.
- Tudo foi **simulado** no Wokwi e em testes de software; não houve medição com o hardware real nem em um rio.
- O potenciômetro apenas representa um pluviômetro real.
- Em hardware real, o ECHO do HC-SR04 é de 5 V e o Pico trabalha com 3,3 V: seria preciso um divisor de tensão (no Wokwi, a ligação é direta).
- A leitura de distância assume ar parado e superfície lisa; vento, espuma e lixo na água afetam o sensor ultrassônico.
- Não envia alertas pela internet nem substitui a Defesa Civil.

## IA generativa
Usada como apoio na construção do código, dos testes e da documentação. A equipe deve conferir os limiares, rodar os testes e validar o projeto no Wokwi.
