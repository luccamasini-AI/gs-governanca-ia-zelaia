import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from descarte import avaliacao, metricas
from descarte.configuracao import Configuracao
from descarte.corpus import RAIZ
from descarte.fluxo import Assistente
from descarte.provedores import Provedores, ErroProvedor, noul
from test_fluxo import ProvedoresControlados


class RevisaoTestes(unittest.TestCase):
    def test_parte_confirmada_pode_sair_com_ressalva_validada_sem_negar_as_demais(self):
        p = ProvedoresControlados()
        a = Assistente(Configuracao(chave_openai="teste", chave_jev="teste"), p)
        def gerar(pergunta, historico, evidencias, correcao=None):
            return {"status": "respondido", "mensagem": "", "afirmacoes": [
                {"texto": "A unidade A recebe o material.", "evidencias": [evidencias[0]["id"]]},
                {"texto": "Outras unidades não recebem.", "evidencias": [evidencias[0]["id"]]}]}
        for aceita in [True, False]:
            with self.subTest(aceita=aceita), patch.object(p, "gerar", side_effect=gerar), patch.object(a, "verificar", return_value={"sustenta_0": .95, "sustenta_1": .1, "desvio_0": .01, "desvio_1": .01}), patch.object(a, "verificar_cobertura", return_value={"completa": .1, "com_ressalva": .95 if aceita else .1}):
                r = a.responder("Qualquer unidade recebe móveis? A unidade A é opção?")
            self.assertEqual(r["status"], "respondido" if aceita else "sem_evidencia")
            if aceita:
                self.assertEqual(len(r["afirmacoes"]), 1)
                self.assertIn("Não é possível estender", r["mensagem"])
                self.assertNotIn("Outras unidades não recebem", str(r))

    def test_limite_do_conhecimento_considera_contexto_completo_sem_ampliar_citacoes(self):
        a = Assistente(Configuracao())
        fontes = [{"id": "geral", "texto": "Algumas unidades recebem."},
                  {"id": "local", "texto": "A publicação confirma a unidade A na região."}]
        afirmacoes = [{"texto": "A base não confirma todas as unidades da região.", "evidencias": ["geral"]}]
        with patch.object(a.provedores, "decidir", return_value={"sustenta_0": .95}) as chamada:
            a.verificar(afirmacoes, fontes)
        estado = chamada.call_args.args[0]
        self.assertEqual(estado["contexto_disponivel"], {f["id"]: f for f in fontes})
        self.assertEqual(estado["itens"]["item_0"]["evidencias_citadas"], [fontes[0]])

    def test_resposta_parcial_so_sai_quando_ainda_cobre_a_pergunta(self):
        for completa in [True, False]:
            provedor = ProvedoresControlados()
            a = Assistente(Configuracao(chave_openai="teste", chave_jev="teste"), provedor)
            def gerar(pergunta, historico, evidencias, correcao=None):
                return {"status": "respondido", "mensagem": "", "afirmacoes": [
                    {"texto": "O atendimento é gratuito.", "evidencias": [evidencias[0]["id"]]},
                    {"texto": "Informação adicional inválida.", "evidencias": [evidencias[0]["id"]]}]}
            original = provedor.decidir
            def decidir(estado, perguntas, etapa):
                if etapa == "cobertura_resposta":
                    return {"completa": .95 if completa else .05}
                return original(estado, perguntas, etapa)
            with self.subTest(completa=completa), patch.object(provedor, "gerar", side_effect=gerar), patch.object(provedor, "decidir", side_effect=decidir), patch.object(a, "verificar", return_value={"sustenta_0": .95, "sustenta_1": .05, "desvio_0": .01, "desvio_1": .9}):
                resposta = a.responder("O ecoponto é gratuito?", registrar=True)
            self.assertEqual(resposta["status"], "respondido" if completa else "sem_evidencia")
            if completa:
                self.assertEqual([p["texto"] for p in resposta["afirmacoes"]], ["O atendimento é gratuito."])

    def test_cada_decisao_jev_referencia_somente_seu_objeto(self):
        a = Assistente(Configuracao())
        fontes = [{"id": "fonte-a", "texto": "Fato A"}, {"id": "fonte-b", "texto": "Fato B"}]
        afirmacoes = [{"texto": "A", "evidencias": ["fonte-a"]}, {"texto": "B", "evidencias": ["fonte-b"]}]
        with patch.object(a.provedores, "decidir", return_value={"sustenta_0": .9, "sustenta_1": .1}) as chamada:
            a.verificar(afirmacoes, fontes)
        estado, perguntas, _ = chamada.call_args.args
        self.assertEqual(estado["itens"]["item_0"]["evidencias_citadas"], [fontes[0]])
        self.assertEqual(estado["itens"]["item_1"]["evidencias_citadas"], [fontes[1]])
        self.assertIn("'item_0'", perguntas["sustenta_0"]["instructions"])
        self.assertIn("'item_1'", perguntas["sustenta_1"]["instructions"])

    def test_correcao_recebe_rascunho_e_pontuacoes_anteriores(self):
        provedor = ProvedoresControlados(sustenta=False)
        a = Assistente(Configuracao(chave_openai="teste", chave_jev="teste"), provedor)
        with patch.object(provedor, "gerar", wraps=provedor.gerar) as gerar:
            a.responder("Onde levar sofá?")
        correcao = gerar.call_args_list[1].args[3]
        self.assertIsInstance(correcao, dict)
        self.assertIn("rascunho_anterior", correcao)
        self.assertIn("verificacao", correcao)

    def test_jev_resposta_malformada_vira_erro_controlado(self):
        cliente = Provedores(Configuracao())
        for resposta in [None, [], {"answers": None}, {"answers": {"a": None}}, {"answers": {"a": .9}}]:
            with self.subTest(resposta=resposta), patch.object(cliente, "_post", return_value=resposta):
                with self.assertRaises(ErroProvedor):
                    cliente.decidir({}, {"a": noul("Teste")}, "teste")

    def test_openai_resposta_malformada_vira_erro_controlado(self):
        cliente = Provedores(Configuracao())
        for resposta in [None, [], {"status": "completed", "output": None},
                         {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text"}]}]},
                         {"status": "completed", "output": [{"type": "message", "content": None}]}]:
            with self.subTest(resposta=resposta), patch.object(cliente, "_post", return_value=resposta):
                with self.assertRaises(ErroProvedor):
                    cliente.gerar("Pergunta", [], [])

    def test_abstencao_registra_rascunho_sem_expor_promessa(self):
        config = Configuracao(chave_openai="teste", chave_jev="teste")
        provedor = ProvedoresControlados()
        rascunho = {"status": "esclarecimento", "mensagem": "Envie seu endereço e eu agendarei a coleta.", "afirmacoes": []}
        with patch.object(provedor, "gerar", return_value=rascunho):
            r = Assistente(config, provedor).responder("Onde levar sofá?", registrar=True)
        self.assertEqual(r["registro"]["tentativas"][0]["rascunho"], rascunho)
        self.assertNotIn("agendarei", r["mensagem"])

    def test_verificacao_vazia_nao_libera_afirmacao(self):
        a = Assistente(Configuracao(chave_openai="teste", chave_jev="teste"), ProvedoresControlados())
        with patch.object(a, "verificar", return_value={}):
            self.assertEqual(a.responder("Onde levar sofá?")["status"], "sem_evidencia")

    def test_metricas_incluem_perda_de_fonte_em_abstencao(self):
        # Dados artificiais locais: o teste não depende de relatórios antigos da entrega.
        casos = [{"resposta": {"status": "respondido", "afirmacoes": [{"texto": "Fato"}]},
                  "status_correto": True, "registro": {"segundos": 1, "chamadas": [], "candidatos": [{"texto": "Fato"}]},
                  "contexto_enviado": [{"texto": "Fato"}],
                  "busca": {"cobertura_fontes": 1, "reciproco_primeira_fonte": 1},
                  "apos_jev": {"cobertura_fontes": 1, "reciproco_primeira_fonte": 1}}
                 for _ in range(2)]
        geracao = []
        respondiveis = [c for c in casos if "apos_jev" in c]
        afetado = respondiveis[0]
        afetado["resposta"]["status"] = "sem_evidencia"
        afetado["apos_jev"] = {"cobertura_fontes": 0, "reciproco_primeira_fonte": 0, "acerto": 0}
        afetado["contexto_enviado"] = []
        def leitura(caminho, **opcoes):
            return json.dumps(casos if caminho.name == "teste-completo.json" else geracao)
        with patch.object(Path, "read_text", leitura):
            calculo = metricas.calcular()
        self.assertAlmostEqual(calculo["cobertura_depois"], (len(respondiveis) - 1) / len(respondiveis))

    def test_recuperacao_respeita_parametros_e_janela_do_fluxo(self):
        config = Configuracao()
        config.parametros.update(bm25_k1=.6, bm25_b=.1)
        caso = {"id": "teste", "pergunta": "sofá", "fontes": ["ecopontos"], "historico": ["óleo", "gesso", "móveis"]}
        with patch.object(avaliacao, "buscar", wraps=avaliacao.buscar) as busca:
            avaliacao.recuperacao(config, [caso])
        self.assertEqual(busca.call_args.args[0], "gesso\nmóveis\nsofá")
        self.assertEqual(busca.call_args.args[3:], (.6, .1))

    def test_manifesto_por_artefato_identifica_codigo_e_resultado(self):
        with tempfile.TemporaryDirectory() as pasta:
            with patch("sys.argv", ["avaliacao", "--etapa", "recuperacao", "--saida", pasta]):
                avaliacao.main()
            manifesto = json.loads((Path(pasta) / "teste-recuperacao-manifesto.json").read_text(encoding="utf-8"))
        self.assertIn("sha256_codigo", manifesto)
        self.assertIn("sha256_resultado", manifesto)
        self.assertEqual(manifesto["artefato"], "teste-recuperacao.json")


if __name__ == "__main__":
    unittest.main()
