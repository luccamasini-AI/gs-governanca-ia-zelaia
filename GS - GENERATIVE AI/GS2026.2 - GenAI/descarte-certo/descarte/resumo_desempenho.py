"""Estatísticas pareadas; a reamostragem preserva as duas rodadas de cada pergunta."""
import argparse
import json
import math
import random
import statistics
from pathlib import Path
from .desempenho import VARIANTES


def resumir(casos):
    linhas = {}
    for variante in VARIANTES:
        grupo = [c for c in casos if c["variante"] == variante and "segundos" in c]
        tempos = sorted(c["segundos"] for c in grupo)
        etapas = {}
        for c in grupo:
            for chamada in c["registro"]["chamadas"]:
                etapa = chamada["etapa"]
                etapas[etapa] = etapas.get(etapa, 0) + chamada.get("segundos", 0)
        respondiveis = [c for c in grupo if c["cobertura_jev"] is not None]
        linhas[variante] = {"execucoes": len(grupo), "media_s": statistics.mean(tempos), "mediana_s": statistics.median(tempos),
            "p95_s": tempos[math.ceil(len(tempos)*.95)-1], "estados_corretos": sum(c["status_correto"] for c in grupo),
            "citacoes_validas": sum(c["citacoes_validas"] for c in grupo),
            "media_respondiveis_s": statistics.mean(c["segundos"] for c in respondiveis),
            "media_nao_respondiveis_s": statistics.mean(c["segundos"] for c in grupo if c not in respondiveis),
            "media_trechos": statistics.mean(len(c["contexto_selecionado"]) for c in grupo),
            "media_palavras": statistics.mean(c["palavras_contexto"] for c in grupo),
            "cobertura_literal": statistics.mean(c["cobertura_jev"]["proporcao"] for c in respondiveis),
            "etapas_media_s": {k: v/len(grupo) for k, v in etapas.items()},
            "chamadas": sum(len(c["registro"]["chamadas"]) for c in grupo),
            "tentativas_http_adicionais": sum(max(c.get("tentativas", 1)-1, 0) for item in grupo for c in item["registro"]["chamadas"])}
    comparacoes = []
    for referencia, alvo in [("bm25", "selecao_jev"), ("bm25", "completo_jev"), ("vetorial", "completo_jev"), ("hibrido", "completo_jev"), ("completo_llm", "completo_jev")]:
        for apenas_respondiveis in [False, True]:
            pares = {}
            for c in casos:
                if c["variante"] not in (referencia, alvo) or "segundos" not in c or (apenas_respondiveis and c["cobertura_jev"] is None):
                    continue
                pares.setdefault(c["id"], {}).setdefault(c["variante"], []).append(c["segundos"])
            grupos = [p for p in pares.values() if all(len(p.get(v, [])) == 2 for v in (referencia, alvo))]
            def ganho(amostra):
                base = sum(sum(p[referencia]) for p in amostra)
                novo = sum(sum(p[alvo]) for p in amostra)
                return 100*(1-novo/base)
            rng = random.Random(20261110)
            amostras = sorted(ganho(rng.choices(grupos, k=len(grupos))) for _ in range(5000))
            comparacoes.append({"referencia": referencia, "alvo": alvo, "recorte": "respondiveis" if apenas_respondiveis else "todos",
                "perguntas_pareadas": len(grupos), "reducao_percentual_media": ganho(grupos),
                "intervalo_bootstrap_95": [amostras[124], amostras[4874]],
                "nota": "Valor negativo indica aumento de latência. Intervalo descritivo por pergunta; não mede variação entre dias, regiões ou cargas."})
    return {"variantes": linhas, "comparacoes": comparacoes}


def main():
    parser = argparse.ArgumentParser(description="Resumo do comparativo RAG")
    parser.add_argument("--arquivo", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(resumir(json.loads(args.arquivo.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
