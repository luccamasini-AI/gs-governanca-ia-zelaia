"""Verificações matemáticas do comparativo, sem consumo de API."""
import unittest
from descarte.desempenho import cosseno, fundir
from descarte.otimizacao import resumir


class TesteComparativo(unittest.TestCase):
    def test_indisponibilidade_nao_e_interpretada_como_aceleracao(self):
        with self.assertRaisesRegex(ValueError, "indisponibilidade"):
            resumir([{"resposta": {"status": "indisponivel"}}])

    def test_cosseno_preserva_direcao_e_trata_nulo(self):
        self.assertAlmostEqual(cosseno([1, 2], [10, 20]), 1)
        self.assertAlmostEqual(cosseno([1, 0], [0, 2]), 0)
        self.assertEqual(cosseno([0, 0], [1, 2]), 0)
        with self.assertRaises(ValueError):
            cosseno([1], [1, 2])

    def test_rrf_favorece_concordancia_sem_duplicar_documento(self):
        a, b, c = ({"id": i} for i in "abc")
        resultado = fundir([[a, b], [c, b]], limite=2)
        self.assertEqual([x["id"] for x in resultado], ["b", "a"])
        self.assertAlmostEqual(resultado[0]["rrf"], 2/62)


if __name__ == "__main__":
    unittest.main()
