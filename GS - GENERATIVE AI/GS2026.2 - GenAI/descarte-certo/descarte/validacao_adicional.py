"""Dez perguntas adicionais em duas rodadas, sempre sem cache."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from .avaliacao import completo, salvar
from .configuracao import Configuracao
from .corpus import RAIZ


def main():
    parser = argparse.ArgumentParser(description="Validação adicional sem cache")
    parser.add_argument("--env", required=True)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--executar-api", action="store_true")
    args = parser.parse_args()
    config = Configuracao.ler(args.env)
    config.parametros["cache_respostas"] = False
    if config.ausentes() or not args.executar_api:
        parser.error("São necessários credenciais e --executar-api.")
    if (args.saida/"execucoes.json").exists():
        parser.error("O destino já contém resultados.")
    args.saida.mkdir(parents=True, exist_ok=True)
    origem = RAIZ/"dados/cenarios-adicionais.json"
    perguntas = json.loads(origem.read_text(encoding="utf-8"))["perguntas"]
    casos = [{**c, "id": f"{c['id']}-R{r}"} for r in (1,2) for c in perguntas]
    manifesto = {"inicio_utc": datetime.now(timezone.utc).isoformat(), "parametros": config.parametros,
        "sha256_perguntas": hashlib.sha256(origem.read_bytes()).hexdigest(),
        "sha256_codigo": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (RAIZ/"descarte").glob("*.py")}}
    salvar(args.saida/"manifesto.json", manifesto)
    completo(config, casos, args.saida/"execucoes.json")
    manifesto.update(concluido_utc=datetime.now(timezone.utc).isoformat(),
        sha256_resultado=hashlib.sha256((args.saida/"execucoes.json").read_bytes()).hexdigest())
    salvar(args.saida/"manifesto.json", manifesto)


if __name__ == "__main__":
    main()
