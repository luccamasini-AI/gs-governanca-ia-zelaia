import unittest
from unittest.mock import patch

from descarte.configuracao import Configuracao
from descarte.fluxo import Assistente
from descarte.provedores import Provedores, ErroProvedor, noul


class ContratosTestes(unittest.TestCase):
    def test_decisao_invalida_nao_e_tratada_como_confianca(self):
        cliente = Provedores(Configuracao())
        for valor in [None, True, float("nan"), 1.1, -0.1, "0.9"]:
            with self.subTest(valor=valor), patch.object(cliente, "_post", return_value={"answers": {"a": {"noul": valor}}}):
                with self.assertRaises(ErroProvedor):
                    cliente.decidir({}, {"a": noul("Teste")}, "teste")

    def test_falha_externa_nao_vira_falta_de_evidencia(self):
        config = Configuracao(chave_openai="teste", chave_jev="teste")
        with patch.object(Provedores, "decidir", side_effect=ErroProvedor("selecao: serviço indisponível.")):
            resposta = Assistente(config).responder("Onde levar sofá?", registrar=True)
        self.assertEqual(resposta["status"], "indisponivel")
        self.assertEqual(resposta["afirmacoes"], [])

    def test_resposta_incompleta_nao_e_exibida(self):
        cliente = Provedores(Configuracao())
        with patch.object(cliente, "_post", return_value={"status": "incomplete", "output": []}):
            with self.assertRaises(ErroProvedor):
                cliente.gerar("Pergunta", [], [])


if __name__ == "__main__":
    unittest.main()
