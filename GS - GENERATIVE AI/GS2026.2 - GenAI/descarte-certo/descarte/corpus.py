"""Segmentação rastreável e recuperação lexical BM25."""

import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PARADAS = set("a o as os e de da do das dos um uma uns umas em no na nos nas para por com que qual quais como onde posso pode ser ao aos se eu meu minha isso isto voce voces sao".split())


def normalizar(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))


def termos(texto: str) -> list[str]:
    palavras = [p for p in re.findall(r"[a-z0-9]+", normalizar(texto)) if p not in PARADAS and len(p) > 1]
    # Normalização leve de plural; não equivale a análise morfológica completa.
    return [p[:-3] + "vel" if p.endswith("veis") else p[:-1] if p.endswith("s") and len(p) > 3 else p for p in palavras]


def carregar() -> dict:
    return json.loads((RAIZ / "dados/corpus.json").read_text(encoding="utf-8"))


def preparar_consulta(pergunta: str, historico=None) -> str:
    return "\n".join((historico or [])[-2:] + [pergunta])


def dividir(documentos: list[dict], tamanho: int = 90, sobreposicao: int = 15) -> list[dict]:
    if tamanho < 10 or not 0 <= sobreposicao < tamanho:
        raise ValueError("Tamanho e sobreposição de chunks inválidos.")
    resultado = []
    for documento in documentos:
        blocos = []
        atual: list[str] = []
        for paragrafo in documento["texto"].split("\n\n"):
            palavras = paragrafo.split()
            if atual and len(atual) + len(palavras) > tamanho:
                blocos.append(" ".join(atual))
                atual = atual[-sobreposicao:] if sobreposicao else []
            atual.extend(palavras)
            while len(atual) > tamanho:
                blocos.append(" ".join(atual[:tamanho]))
                atual = atual[tamanho - sobreposicao:]
        if atual:
            blocos.append(" ".join(atual))
        for indice, texto in enumerate(blocos):
            resultado.append({**documento, "id": f"{documento['id']}-{indice + 1}",
                              "fonte_id": documento["id"], "texto": texto,
                              "hash": hashlib.sha256(texto.encode()).hexdigest()})
    return resultado


def buscar(pergunta: str, chunks: list[dict], top_k: int = 12, k1: float = 1.5, b: float = 0.75) -> list[dict]:
    consulta = set(termos(pergunta))
    if not consulta or not chunks:
        return []
    contagens = [Counter(termos(c["titulo"] + " " + c["texto"])) for c in chunks]
    tamanhos = [sum(c.values()) for c in contagens]
    media = sum(tamanhos) / len(tamanhos) or 1
    frequencias = Counter(t for c in contagens for t in c)
    resultados = []
    for chunk, contagem, tamanho in zip(chunks, contagens, tamanhos):
        score = 0.0
        for termo in consulta:
            tf = contagem[termo]
            if tf:
                idf = math.log(1 + (len(chunks) - frequencias[termo] + .5) / (frequencias[termo] + .5))
                score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * tamanho / media))
        if score > 0:
            resultados.append({**chunk, "bm25": round(score, 6)})
    return sorted(resultados, key=lambda c: (-c["bm25"], c["id"]))[:top_k]
