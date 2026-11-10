"""Testes com contas feitas à mão. Rodar: python -m unittest discover -s testes -v (na pasta raiz)."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import busca  # noqa: E402
import modelo as m  # noqa: E402
import orientacoes as o  # noqa: E402
from parametros import Parametros  # noqa: E402


class TestNecessidade(unittest.TestCase):
    def setUp(self):
        self.p = Parametros()

    def test_celulares_bateria(self):
        self.assertAlmostEqual(m.necessidade(m.Caso(), self.p)["celulares_bateria_wh_dia"], 77.0)  # 4 × 19,25

    def test_celulares_tomada(self):
        self.assertAlmostEqual(m.necessidade(m.Caso(), self.p)["celulares_tomada_wh_dia"], 96.25)  # 77 / 0,8

    def test_total_dia_e_periodo(self):
        n = m.necessidade(m.Caso(), self.p)
        self.assertAlmostEqual(n["total_wh_dia"], 176.25)  # 96,25 + 2×8×5
        self.assertAlmostEqual(n["total_wh_periodo"], 352.5)

    def test_geladeira(self):
        self.assertAlmostEqual(m.necessidade(m.Caso(geladeira=True), self.p)["geladeira_wh_dia"], 840.0)  # 25,2 kWh/30

    def test_validacao(self):
        for caso in (m.Caso(celulares=-1), m.Caso(dias=0), m.Caso(celulares=0, lampadas=0), m.Caso(cidade_preco="x")):
            with self.assertRaises(ValueError):
                m.necessidade(caso, self.p)


class TestGerador(unittest.TestCase):
    def setUp(self):
        self.p = Parametros()

    def test_litros_por_kwh(self):
        self.assertAlmostEqual(m.litros_por_kwh_gerador(self.p), 1.25)  # 2,5 L/h ÷ 2 kW

    def test_litros_48h(self):
        self.assertAlmostEqual(m.gerador(m.Caso(), self.p)["litros"], 5.5)  # 1,375 L/h × 4 h

    def test_custo_combustivel(self):
        self.assertAlmostEqual(m.gerador(m.Caso(), self.p)["operacao_r"], 5.5 * 5.91)

    def test_preco_brasil_maior(self):
        self.assertGreater(m.gerador(m.Caso(cidade_preco="br"), self.p)["operacao_r"],
                           m.gerador(m.Caso(), self.p)["operacao_r"])

    def test_co2(self):
        fator = 0.74 * 0.86 * 44 / 12 * 0.70
        self.assertAlmostEqual(m.gerador(m.Caso(), self.p)["co2_kg"], 5.5 * fator)

    def test_mais_horas_mais_litros(self):
        a = m.gerador(m.Caso(), self.p.com(gerador_horas_dia=1))["litros"]
        b = m.gerador(m.Caso(), self.p.com(gerador_horas_dia=4))["litros"]
        self.assertAlmostEqual(b, 4 * a)


class TestSolar(unittest.TestCase):
    def setUp(self):
        self.p = Parametros()

    def test_bateria_util(self):
        self.assertAlmostEqual(m.kit_solar(m.Caso(), self.p)["bateria_util_wh"], 256 * 0.9 * 0.85)  # 195,84

    def test_painel_dia(self):
        esperado = 0.110 * 3.6 * 0.9 * 0.85 * 1000
        self.assertAlmostEqual(m.kit_solar(m.Caso(), self.p)["solar_wh_dia"], esperado)  # 302,94

    def test_clima_reduz(self):
        media = m.kit_solar(m.Caso(), self.p, "media")["solar_wh_dia"]
        denso = m.kit_solar(m.Caso(), self.p, "denso")["solar_wh_dia"]
        self.assertAlmostEqual(denso, 0.4 * media)

    def test_tempestade_cobre_parcial(self):
        self.assertAlmostEqual(m.kit_solar(m.Caso(), self.p, "estresse")["cobertura"], 256.43 / 352.5, places=2)

    def test_geladeira_nao_cabe(self):
        self.assertLess(m.kit_solar(m.Caso(geladeira=True), self.p)["cobertura"], 0.5)

    def test_dias_cobertos_infinito_com_superavit(self):
        self.assertTrue(math.isinf(m.kit_solar(m.Caso(), self.p)["dias_cobertos"]))


class TestBancos(unittest.TestCase):
    def setUp(self):
        self.p = Parametros()

    def test_unidades(self):
        b = m.power_banks(m.Caso(), self.p)
        self.assertAlmostEqual(b["wh_util_por_banco"], 48.1)  # 20 Ah × 3,7 V × 0,65
        self.assertEqual(b["unidades"], 5)  # ceil(214 / 48,1)
        self.assertAlmostEqual(b["compra_r"], 5 * 130 + 2 * 40)

    def test_geladeira_sem_cobertura(self):
        self.assertEqual(m.power_banks(m.Caso(geladeira=True), self.p)["cobertura"], 0.0)


class TestComparacao(unittest.TestCase):
    def test_tres_alternativas_uma_renovavel(self):
        linhas = m.comparar(m.Caso(), Parametros())
        self.assertEqual(len(linhas), 3)
        self.assertEqual(sum(1 for l in linhas if l["renovavel"]), 1)

    def test_custo_total_cinco_anos(self):
        g = m.comparar(m.Caso(), Parametros())[0]
        self.assertAlmostEqual(g["custo_total_r"], 1819.90 + 5 * 5.5 * 5.91)

    def test_parametros_estimados_identificados(self):
        p = Parametros()
        self.assertIn("celular_wh", p.estimados())
        self.assertNotIn("lampada_led_w", p.estimados())

    def test_recomendar_geladeira_cita_limite(self):
        texto = " ".join(m.recomendar(m.Caso(geladeira=True), Parametros()))
        self.assertIn("ao ar livre", texto)


class TestAssistente(unittest.TestCase):
    def setUp(self):
        self.p = Parametros()

    def test_busca_gerador_dentro(self):
        self.assertEqual(busca.melhor("posso usar o gerador dentro de casa?")["id"], "gerador_dentro")

    def test_busca_quadro(self):
        self.assertEqual(busca.melhor("a agua entrou no quadro de luz, posso religar o disjuntor?")["id"], "quadro_alagado")

    def test_busca_solar_chuva(self):
        self.assertEqual(busca.melhor("painel solar funciona com chuva?")["id"], "solar_chuva")

    def test_carregador_portatil_em_enchente(self):
        self.assertEqual(busca.melhor("Se eu estiver em uma enchete eu posso utilizar um carregador portátil?")["id"],
                         "carregador_enchente")

    def test_quantos_power_banks_continua_calculo(self):
        self.assertEqual(busca.melhor("quantos power banks para 4 celulares e 3 dias?")["id"], "power_banks")

    def test_busca_recorrer_nao_inventa_beneficio(self):
        r = busca.melhor("perdi tudo e estou sem luz, a qual recurso publico posso recorrer?")
        self.assertEqual(r["id"], "recorrer")
        self.assertIn("Não tenho informações sobre benefícios", " ".join(r["texto"]))
        self.assertEqual(busca.melhor("tem algum beneficio do governo?")["id"], "recorrer")

    def test_busca_ajuda(self):
        self.assertEqual(busca.melhor("o que é isso?")["id"], "ajuda")
        self.assertEqual(busca.melhor("como funciona esse assistente")["id"], "ajuda")

    def test_busca_gerador_nao_vira_ajuda(self):
        self.assertEqual(busca.melhor("Durante a falta de energia e correto usar gerador?")["id"], "gerador_dentro")

    def test_busca_vazia_e_sem_resultado(self):
        self.assertIsNone(busca.melhor(""))
        self.assertIsNone(busca.melhor("qual a capital da França"))

    def test_ajuste_caso_pela_pergunta(self):
        c = busca.ajustar_caso("quanto gasta para 3 celulares e 4 dias", m.Caso())
        self.assertEqual((c.celulares, c.dias), (3, 4))

    def test_ajuste_invalido_mantem_caso(self):
        c = busca.ajustar_caso("para 99 celulares", m.Caso())
        self.assertEqual(c.celulares, 4)

    def test_toda_orientacao_responde_com_fontes_validas(self):
        for x in o.todas():
            linhas, fontes = o.responder(x, m.Caso(), self.p)
            self.assertTrue(linhas, x["id"])
            for s in fontes:
                self.assertIn(s, self.p.fontes)

    def test_parametros_com_fonte_valida(self):
        for nome, item in self.p.itens.items():
            if item["fonte"]:
                for s in item["fonte"].replace(" ", "").split(","):
                    self.assertIn(s, self.p.fontes, nome)
            self.assertIn(item["tipo"], ("dado público", "estimado"), nome)


if __name__ == "__main__":
    unittest.main()
