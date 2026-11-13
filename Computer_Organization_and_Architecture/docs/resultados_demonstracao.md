# Testes da demonstração (Estação Sentinela)

| Passo | Ação | Esperado | Obtido | Resultado |
|---|---|---|---|---|
| 1. Partida | Rio a 200 cm, sem chuva | NORMAL, LED verde | NORMAL, LEDs (1, 0, 0), LCD 'Rio:  0cm Ch:  0' | OK |
| 2. Rio sobe devagar (nível 50 cm) | Distance=150 cm (nível 50 cm), chuva=0 mm/h, 20 s | NORMAL, LEDs (1, 0, 0) | NORMAL, LEDs (1, 0, 0), LCD 'Rio: 50cm Ch:  0' / 'NORMAL      +0/m' | OK |
| 3. Limiar de ATENÇÃO (nível 80 cm) | Distance=120 cm (nível 80 cm), chuva=0 mm/h, 20 s | ATENCAO, LEDs (0, 1, 0) | ATENCAO, LEDs (0, 1, 0), LCD 'Rio: 80cm Ch:  0' / 'ATENCAO     +0/m' | OK |
| 4. Nível 90 cm | Distance=110 cm (nível 90 cm), chuva=0 mm/h, 20 s | ATENCAO, LEDs (0, 1, 0), LCD contém 'Rio: 90cm' | ATENCAO, LEDs (0, 1, 0), LCD 'Rio: 90cm Ch:  0' / 'ATENCAO     +0/m' | OK |
| 5. Chuva forte (40 mm/h) com o rio já alto | Distance=110 cm (nível 90 cm), chuva=40 mm/h, 5 s | ALERTA, LEDs (0, 0, 1), LCD contém 'Ch: 40' | ALERTA, LEDs (0, 0, 1), LCD 'Rio: 90cm Ch: 40' / 'ALERTA      +0/m' | OK |
| 6. Chuva volta a 0, rio em 130 cm | Distance=70 cm (nível 130 cm), chuva=0 mm/h, 25 s | ALERTA, LEDs (0, 0, 1) | ALERTA, LEDs (0, 0, 1), LCD 'Rio:130cm Ch:  0' / 'ALERTA      +0/m' | OK |
| 7. EMERGÊNCIA (nível 170 cm) | Distance=30 cm, 20 s | EMERGENCIA, LED vermelho pisca | EMERGENCIA, LED vermelho assumiu [0, 1] | OK |
| 8. Botão silencia o alarme | Apertar o botão azul | LCD 'Silenciado 60s' e buzzer mudo | LCD 'Silenciado 60s', mudo=True | OK |
| 9. Rio baixa para 90 cm (histerese) | Distance=110 cm (nível 90 cm), chuva=0 mm/h, 40 s | ATENCAO, LEDs (0, 1, 0) | ATENCAO, LEDs (0, 1, 0), LCD 'Rio: 90cm Ch:  0' / 'ATENCAO     +0/m' | OK |
| 10. Rio volta ao normal | Distance=200 cm (nível 0 cm), chuva=0 mm/h, 40 s | NORMAL, LEDs (1, 0, 0) | NORMAL, LEDs (1, 0, 0), LCD 'Rio:  0cm Ch:  0' / 'NORMAL      +0/m' | OK |
| 11. Subida rápida | Salto de 200 para 110 cm de uma vez (agora +5 s) | ALERTA (nível 90 seria ATENÇÃO; a velocidade ≥ 10 cm/min sobe um nível), taxa ≥ 10 cm/min | ALERTA, taxa 679 cm/min | OK |
| 12. Água estabiliza | Mais 20 s sem mudar | volta para ATENCAO | ATENCAO | OK |
| 13. Falha do sensor | Sensor sem leitura por 6 s | nunca NORMAL; LCD 'SEM SENSOR' | ATENCAO, LCD 'SEM SENSOR  +0/m' | OK |
| 14. Sensor volta | Leitura volta em 200 cm | NORMAL | NORMAL | OK |

**14 de 14 passos OK.**
