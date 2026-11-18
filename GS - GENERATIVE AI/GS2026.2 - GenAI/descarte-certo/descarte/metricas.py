"""Recalcula as métricas finais a partir dos JSONs, sem chamar APIs."""
import json
import math
import statistics
from .corpus import RAIZ


def calcular():
    pasta = RAIZ / "relatorios"
    casos = json.loads((pasta / "teste-completo.json").read_text(encoding="utf-8"))
    geracao = json.loads((pasta / "teste-geracao.json").read_text(encoding="utf-8"))
    respondidas = [c for c in casos if c["resposta"]["status"] == "respondido"]
    respondiveis = [c for c in casos if "busca" in c and "apos_jev" in c]
    tempos = sorted(c["registro"]["segundos"] for c in casos)
    chamadas = [ch for c in casos for ch in c["registro"]["chamadas"]]
    m = {"perguntas": len(casos), "status_corretos": sum(c["status_correto"] for c in casos),
         "respondidas": len(respondidas), "afirmacoes": sum(len(c["resposta"]["afirmacoes"]) for c in respondidas),
         "media_segundos": statistics.mean(tempos), "mediana_segundos": statistics.median(tempos),
         "p95_segundos": tempos[math.ceil(len(tempos) * .95) - 1],
         "latencia_respondidas": statistics.mean(c["registro"]["segundos"] for c in respondidas) if respondidas else None,
         "candidatos_media": statistics.mean(len(c["registro"]["candidatos"]) for c in respondiveis),
         "contextos_media": statistics.mean(len(c["contexto_enviado"]) for c in respondiveis),
         "total_chamadas": len(chamadas),
         "geracao_citacoes": sum(c["citacoes_validas"] for c in geracao),
         "geracao_sustentada": sum(bool(c["verificacao_jev"]) and all(v >= .8 for v in c["verificacao_jev"].values()) for c in geracao),
         "geracao_afirmacoes": sum(len(c["resposta"]["afirmacoes"]) for c in geracao)}
    for sufixo, campo in [("antes", "busca"), ("depois", "apos_jev")]:
        m["cobertura_" + sufixo] = statistics.mean(c[campo]["cobertura_fontes"] for c in respondiveis)
        m["mrr_" + sufixo] = statistics.mean(c[campo]["reciproco_primeira_fonte"] for c in respondiveis)
    m["palavras_antes"] = sum(len(t["texto"].split()) for c in respondiveis for t in c["registro"]["candidatos"])
    m["palavras_depois"] = sum(len(t["texto"].split()) for c in respondiveis for t in c["contexto_enviado"])
    for provedor in ["openai", "jev"]:
        for direcao in ["input", "output"]:
            m[f"{direcao}_{provedor}"] = sum(ch.get("uso", {}).get(direcao + "_tokens", 0) for ch in chamadas
                                             if (ch["etapa"] == "geracao") == (provedor == "openai"))
    return m


if __name__ == "__main__":
    print(json.dumps(calcular(), ensure_ascii=False, indent=2))
