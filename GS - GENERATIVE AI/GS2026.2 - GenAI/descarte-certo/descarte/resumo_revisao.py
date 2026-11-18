"""Recalcula a avaliação repetida, mantendo os casos que terminaram em abstenção."""
import json
import math
import statistics
from .corpus import RAIZ


def calcular():
    pasta = RAIZ / "relatorios/revisao/final"
    def ler(nome):
        return json.loads((pasta / nome).read_text(encoding="utf-8"))
    casos, controles, julgamentos = ler("fluxo-repetido.json"), ler("jev-controles.json"), ler("julgamentos.json")
    respondiveis = [c for c in casos if c["cobertura_bm25"] is not None]
    respondidas = [c for c in casos if c["resposta"]["status"] == "respondido"]
    tempos = sorted(c["registro"]["segundos"] for c in casos)
    pares = []
    for id_ in sorted({c["id"] for c in casos}):
        par = [c for c in casos if c["id"] == id_]
        textos = {(json.dumps(c["resposta"]["afirmacoes"], ensure_ascii=False), c["resposta"]["mensagem"]) for c in par}
        pares.append({"id": id_, "estados_iguais": len({c["resposta"]["status"] for c in par}) == 1,
                      "texto_identico": len(textos) == 1})
    return {
        "cenarios": len(pares), "execucoes": len(casos), "estados_corretos": sum(c["status_correto"] for c in casos),
        "criterios_editoriais_atendidos": sum(j["atende_criterio"] for j in julgamentos),
        "respondiveis": len(respondiveis), "respostas": len(respondidas),
        "afirmacoes": sum(len(c["resposta"]["afirmacoes"]) for c in respondidas),
        "afirmacoes_com_inferencia_nao_sustentada": sum(len(j["afirmacoes_nao_sustentadas"]) for j in julgamentos),
        "cobertura_bm25": statistics.mean(c["cobertura_bm25"]["proporcao"] for c in respondiveis),
        "cobertura_jev": statistics.mean(c["cobertura_jev"]["proporcao"] for c in respondiveis),
        "media_segundos": statistics.mean(tempos), "mediana_segundos": statistics.median(tempos),
        "p95_segundos": tempos[math.ceil(len(tempos) * .95) - 1], "media_candidatos": statistics.mean(len(c["registro"]["candidatos"]) for c in respondiveis),
        "media_contexto": statistics.mean(len(c["contexto_selecionado"]) for c in respondiveis),
        "pares_estaveis_estado": sum(p["estados_iguais"] for p in pares),
        "pares_texto_identico": sum(p["texto_identico"] for p in pares),
        "controles_jev_corretos": sum(a["aprovado"] == a["esperado_sustentado"] for r in controles for a in r["afirmacoes"]),
        "controles_jev_total": sum(len(r["afirmacoes"]) for r in controles),
        "controles_material_corretos": sum(a["detectado"] == a["esperado_desvio"] for r in controles for a in r.get("desvios_material", [])),
        "controles_material_total": sum(len(r.get("desvios_material", [])) for r in controles),
        "controles_cobertura_corretos": sum(a["aprovado"] == a["esperado_completa"] for r in controles for a in r.get("cobertura_resposta", [])),
        "controles_cobertura_total": sum(len(r.get("cobertura_resposta", [])) for r in controles),
        "controles_ressalva_corretos": sum(a["aprovado_com_ressalva"] == a["esperado_com_ressalva"] for r in controles for a in r.get("cobertura_resposta", []) if a.get("esperado_com_ressalva") is not None),
        "controles_ressalva_total": sum(a.get("esperado_com_ressalva") is not None for r in controles for a in r.get("cobertura_resposta", [])),
        "injecoes_indiretas_bloqueadas": sum(a["bloqueado"] for r in controles for a in r["injecoes_indiretas"]),
        "injecoes_diretas_bloqueadas": sum(r["injecao_direta"]["status"] == "bloqueado" for r in controles),
        "chamadas_fluxo": sum(len(c["registro"]["chamadas"]) for c in casos), "comparacoes": pares,
    }


if __name__ == "__main__":
    print(json.dumps(calcular(), ensure_ascii=False, indent=2))
