"""Aplica a revisão humana (planilhas de apoio preenchidas) aos corpus e grava o revisao.csv final.

Uso (na pasta com os arquivos baixados do Colab):
    python aplicar_revisao.py <pasta_com_os_arquivos>

Entradas na pasta: corpus_qa.jsonl, corpus_chat.jsonl, revisao_apoio_qa.csv, revisao_apoio_chat.csv
(preenchidas, separador ';'). Em cada linha da planilha, a coluna `decisao` aceita:
    ok       -> mantém o exemplo como está (alterado = não)
    corrigir -> troca pelo texto das colunas `nova_*` que estiverem preenchidas (alterado = sim)
    excluir  -> remove o exemplo do corpus (alterado = sim)
Saídas: corpus_qa.jsonl e corpus_chat.jsonl corrigidos (os originais ficam em *.original.jsonl) e revisao.csv
com as colunas arquivo, linha, alterado, comentário. A coluna `linha` sempre se refere ao arquivo ANTES das exclusões.
"""
import csv
import json
import shutil
import sys
from pathlib import Path

MIN_QA, MIN_CHAT = 100, 30
DECISIONS = {"ok", "corrigir", "excluir"}


def read_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_sheet(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def decision_of(sheet_row):
    value = next((v for k, v in sheet_row.items() if k.startswith("decisao")), "")
    decision = (value or "").strip().lower()
    if decision not in DECISIONS:
        raise SystemExit(f"Linha {sheet_row['linha']} de {sheet_row['arquivo']}: decisao '{decision}' inválida. "
                         f"Use ok, corrigir ou excluir.")
    return decision


def apply_qa(rows, sheet):
    removed, log = set(), []
    for item in sheet:
        index, decision = int(item["linha"]) - 1, decision_of(item)
        if decision == "corrigir":
            if item["nova_pergunta"].strip():
                rows[index]["instruction"] = item["nova_pergunta"].strip()
            if item["nova_resposta"].strip():
                rows[index]["output"] = item["nova_resposta"].strip()
        elif decision == "excluir":
            removed.add(index)
        log.append((item["arquivo"], item["linha"], "não" if decision == "ok" else "sim", item["comentario"].strip()))
    return [row for i, row in enumerate(rows) if i not in removed], log


def apply_chat(rows, sheet):
    removed, log = set(), []
    for item in sheet:
        index, decision = int(item["linha"]) - 1, decision_of(item)
        if decision == "corrigir":
            replies = [m for m in rows[index]["messages"] if m["role"] == "assistant"]
            for message, key in zip(replies, ("novo_atendente_1", "novo_atendente_2")):
                if item[key].strip():
                    message["content"] = item[key].strip()
        elif decision == "excluir":
            removed.add(index)
        log.append((item["arquivo"], item["linha"], "não" if decision == "ok" else "sim", item["comentario"].strip()))
    return [row for i, row in enumerate(rows) if i not in removed], log


def main(folder):
    folder = Path(folder)
    qa_rows, chat_rows = read_jsonl(folder / "corpus_qa.jsonl"), read_jsonl(folder / "corpus_chat.jsonl")
    qa_sheet, chat_sheet = read_sheet(folder / "revisao_apoio_qa.csv"), read_sheet(folder / "revisao_apoio_chat.csv")
    qa_new, qa_log = apply_qa(qa_rows, qa_sheet)
    chat_new, chat_log = apply_chat(chat_rows, chat_sheet)
    if len(qa_new) < MIN_QA or len(chat_new) < MIN_CHAT:
        raise SystemExit(f"Depois das exclusões ficariam {len(qa_new)} pares de QA (mínimo {MIN_QA}) e "
                         f"{len(chat_new)} diálogos (mínimo {MIN_CHAT}). Nada foi gravado: gere mais exemplos ou exclua menos.")
    for name, rows in (("corpus_qa", qa_new), ("corpus_chat", chat_new)):
        original = folder / f"{name}.original.jsonl"
        if not original.exists():
            shutil.copy(folder / f"{name}.jsonl", original)
        write_jsonl(folder / f"{name}.jsonl", rows)
    with open(folder / "revisao.csv", "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["arquivo", "linha", "alterado", "comentário"])
        writer.writerows(qa_log + chat_log)
    changed = sum(1 for entry in qa_log + chat_log if entry[2] == "sim")
    print(f"QA: {len(qa_rows)} -> {len(qa_new)} pares | chat: {len(chat_rows)} -> {len(chat_new)} diálogos")
    print(f"revisao.csv gravado: {len(qa_log) + len(chat_log)} linhas revisadas, {changed} alteradas.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
