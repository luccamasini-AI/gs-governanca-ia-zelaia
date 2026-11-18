"""Medição de consultas novas e repetidas, sem confundir cache com inferência."""
import argparse
import hashlib
import json
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from .avaliacao import salvar
from .cache import CACHE
from .configuracao import Configuracao
from .corpus import RAIZ
from .fluxo import Assistente, validar_afirmacoes
from .revisao import cobertura


def resumir(casos):
    if any(c["resposta"]["status"] == "indisponivel" for c in casos):
        raise ValueError("Medição inválida: houve indisponibilidade de provedor.")
    resultado = {"variantes": {}}
    for nome in ("primeira_consulta", "repetida"):
        grupo = [c for c in casos if c["variante"] == nome]
        tempos = sorted(c["segundos"] for c in grupo)
        respondiveis = [c for c in grupo if c["respondivel"]]
        resultado["variantes"][nome] = {"execucoes": len(grupo), "media_s": statistics.mean(tempos),
            "mediana_s": statistics.median(tempos), "p95_s": tempos[math.ceil(len(tempos)*.95)-1],
            "media_respondiveis_s": statistics.mean(c["segundos"] for c in respondiveis),
            "estados_corretos": sum(c["status_correto"] for c in grupo),
            "citacoes_validas": sum(c["citacoes_validas"] for c in grupo),
            "acertos_cache": sum(c["registro"]["cache"]["acerto"] for c in grupo),
            "chamadas": sum(len(c["registro"]["chamadas"]) for c in grupo)}
    pares = [(next(c for c in casos if c["id"]==id_ and c["rodada"]==r and c["variante"]=="primeira_consulta"),
              next(c for c in casos if c["id"]==id_ and c["rodada"]==r and c["variante"]=="repetida"))
             for id_,r in sorted({(c["id"],c["rodada"]) for c in casos})]
    resultado["pares_resposta_identica"] = sum(a["resposta"]==b["resposta"] for a,b in pares)
    a,b = (resultado["variantes"][v] for v in ("primeira_consulta","repetida"))
    resultado["reducao_percentual_amostra_repetida"] = 100*(1-b["media_s"]/a["media_s"])
    resultado["reducao_percentual_respondiveis_repetidas"] = 100*(1-b["media_respondiveis_s"]/a["media_respondiveis_s"])
    return resultado


def executar(config, caso, variante, rodada):
    inicio=time.perf_counter()
    historico=[caso["preparacao"]] if caso.get("preparacao") else []
    resposta=Assistente(config).responder(caso["pergunta"],historico,registrar=True)
    segundos=time.perf_counter()-inicio
    registro=resposta.pop("registro")
    contexto=sorted([c for c in registro.get("selecao",[]) if c["relevancia"]>=config.parametros["limiar_relevancia"] and c["injecao"]<config.parametros["limiar_injecao"]],key=lambda c:(-c["relevancia"],c["id"]))[:config.parametros["top_k_contexto"]]
    fontes_validacao=registro.get("evidencias_reutilizadas",contexto)
    return {"id":caso["id"],"rodada":rodada,"variante":variante,"pergunta":caso["pergunta"],"historico":historico,
        "criterio":caso["criterio"],"status_esperados":caso["status"],"status_correto":resposta["status"] in caso["status"],
        "respondivel":bool(caso["evidencias"]),"segundos":segundos,"resposta":resposta,"registro":registro,
        "contexto_selecionado":contexto,"citacoes_validas":validar_afirmacoes(resposta["afirmacoes"],fontes_validacao) if resposta["status"]=="respondido" else not resposta["afirmacoes"],
        "cobertura_bm25":cobertura(registro["candidatos"],caso["evidencias"]) if not registro["cache"]["acerto"] else None,
        "cobertura_jev":cobertura(contexto,caso["evidencias"]) if not registro["cache"]["acerto"] else None}


def main():
    parser=argparse.ArgumentParser(description="Medição de cache de respostas aprovadas")
    parser.add_argument("--env")
    parser.add_argument("--saida",type=Path)
    parser.add_argument("--executar-api",action="store_true")
    parser.add_argument("--resumir",type=Path)
    args=parser.parse_args()
    if args.resumir:
        print(json.dumps(resumir(json.loads(args.resumir.read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
        return
    config=Configuracao.ler(args.env)
    if not args.executar_api or config.ausentes() or not args.saida:
        parser.error("São necessários credenciais, destino e --executar-api.")
    if (args.saida/"execucoes.json").exists():
        parser.error("O destino já contém resultados.")
    args.saida.mkdir(parents=True,exist_ok=True)
    config.parametros["cache_respostas"]=True
    arquivos=list((RAIZ/"descarte").glob("*.py"))+list((RAIZ/"dados").glob("*.json"))
    manifesto={"inicio_utc":datetime.now(timezone.utc).isoformat(),"parametros":config.parametros,
        "metodo":"Dez cenários, duas rodadas. Em cada par, cache vazio na primeira consulta e repetição imediata da mesma pergunta/histórico. Somente respostas aprovadas são armazenadas; abstenções continuam passando pelas APIs. Preparação separada. O ganho mede reutilização, não aceleração de inferência do Jev nem de perguntas inéditas.",
        "sha256":{str(p.relative_to(RAIZ)).replace(chr(92),"/"):hashlib.sha256(p.read_bytes()).hexdigest() for p in arquivos}}
    salvar(args.saida/"manifesto.json",manifesto)
    casos=json.loads((RAIZ/"dados/cenarios-revisao.json").read_text(encoding="utf-8"))["cenarios"]
    CACHE.limpar()
    preparacao=executar(config,casos[0],"preparacao",0)
    salvar(args.saida/"preparacao.json",preparacao)
    if preparacao["resposta"]["status"]=="indisponivel":
        parser.error("Provedor indisponível; medição não iniciada.")
    resultados=[]
    for rodada in (1,2):
        for caso in casos:
            CACHE.limpar()
            for variante in ("primeira_consulta","repetida"):
                item=executar(config,caso,variante,rodada)
                resultados.append(item)
                salvar(args.saida/"execucoes.json",resultados)
                print(f"{len(resultados)}/40 · {caso['id']} · {variante}: {item['resposta']['status']} · {item['segundos']:.4f} s",flush=True)
                if item["resposta"]["status"]=="indisponivel":
                    parser.error("Medição interrompida por indisponibilidade.")
    CACHE.limpar()
    salvar(args.saida/"resumo.json",resumir(resultados))
    manifesto["concluido_utc"]=datetime.now(timezone.utc).isoformat()
    manifesto["sha256_resultados"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.saida.glob("*.json") if p.name!="manifesto.json"}
    salvar(args.saida/"manifesto.json",manifesto)


if __name__=="__main__":
    main()
