import json
import threading
import unittest
import urllib.error
import urllib.request

from descarte.__main__ import criar_servidor
from descarte.configuracao import Configuracao


class ServidorTestes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = criar_servidor(Configuracao(), 0)
        cls.thread = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.thread.join()

    def test_arquivo_de_credenciais_nao_e_servido(self):
        with self.assertRaises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(self.url + "/.env.local")
        self.assertEqual(erro.exception.code, 404)

    def test_porta_em_uso_nao_aceita_segundo_servidor(self):
        with self.assertRaises(OSError):
            outro = criar_servidor(Configuracao(), self.servidor.server_port)
            outro.server_close()

    def test_estado_identifica_versao_sem_expor_configuracao_privada(self):
        with urllib.request.urlopen(self.url + "/api/estado") as resposta:
            estado = json.loads(resposta.read())
        self.assertEqual(estado["versao_prompt"], Configuracao().parametros["versao_prompt"])
        self.assertEqual(set(estado), {"pronto", "corpus", "versao_prompt"})

    def test_origem_externa_e_bloqueada_antes_das_apis(self):
        pedido = urllib.request.Request(self.url + "/api/conversar", b'{}',
                    {"Content-Type": "application/json", "Origin": "https://exemplo.invalid"})
        with self.assertRaises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(pedido)
        self.assertEqual(erro.exception.code, 403)

    def test_sem_configuracao_tem_503_e_mensagem_controlada(self):
        pedido = urllib.request.Request(self.url + "/api/conversar", json.dumps({"pergunta": "Onde levar sofá?"}).encode(),
                    {"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(pedido)
        self.assertEqual(erro.exception.code, 503)
        self.assertEqual(json.loads(erro.exception.read())["status"], "indisponivel")

    def test_pagina_tem_politica_de_conteudo(self):
        with urllib.request.urlopen(self.url) as resposta:
            self.assertIn("frame-ancestors 'none'", resposta.headers["Content-Security-Policy"])
            self.assertEqual(resposta.headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
