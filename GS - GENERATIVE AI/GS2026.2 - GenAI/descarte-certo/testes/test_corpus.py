import unittest

from descarte.corpus import dividir, buscar


class CorpusTestes(unittest.TestCase):
    def setUp(self):
        self.documentos = [
            {"id": "sofa", "titulo": "Móveis", "url": "https://prefeitura.sp.gov.br/a", "texto": "Sofás e colchões são móveis volumosos.\n\nEcopontos recebem móveis gratuitamente.", "consultado_em": "2026-11-10"},
            {"id": "oleo", "titulo": "Óleo", "url": "https://prefeitura.sp.gov.br/b", "texto": "Óleo de cozinha usado deve ser armazenado em garrafas para entrega em pontos de coleta.", "consultado_em": "2026-11-10"},
        ]

    def test_busca_preserva_fonte_e_ordena_evidencia(self):
        resultados = buscar("Onde entregar óleo de cozinha?", dividir(self.documentos))
        self.assertEqual(resultados[0]["fonte_id"], "oleo")
        self.assertEqual(resultados[0]["consultado_em"], "2026-11-10")

    def test_chunks_cobrem_todas_as_palavras_e_respeitam_limite(self):
        documento = dict(self.documentos[0], texto=" ".join(f"palavra{i}" for i in range(100)))
        chunks = dividir([documento], tamanho=30, sobreposicao=5)
        self.assertTrue(all(len(c["texto"].split()) <= 30 for c in chunks))
        palavras = {p for c in chunks for p in c["texto"].split()}
        self.assertEqual(len(palavras), 100)

    def test_consulta_sem_termos_nao_recupera_tudo(self):
        self.assertEqual(buscar("e de a", dividir(self.documentos)), [])

    def test_sobreposicao_invalida_e_rejeitada(self):
        with self.assertRaises(ValueError):
            dividir(self.documentos, tamanho=20, sobreposicao=20)

    def test_singular_recupera_plural_acentuado(self):
        self.assertEqual(buscar("sofá", dividir(self.documentos))[0]["fonte_id"], "sofa")


if __name__ == "__main__":
    unittest.main()
