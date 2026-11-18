"""Converte as planilhas de revisão em arquivos Markdown legíveis (para preencher à mão) e de volta para CSV.

Uso:
    python revisao_md.py para-md  <pasta>   # CSV -> REVISAO_QA.md, REVISAO_CHAT.md, REVISAO_FIDELIDADE.md
    python revisao_md.py para-csv <pasta>   # os .md preenchidos -> CSV (sobrescreve os da pasta)

No .md, preencha apenas o valor depois de "Decisão:", "Nova ...:", "Comentário:" (ou "Fiel:", "Observação:").
Cada valor fica em uma única linha. Depois do para-csv, rode aplicar_revisao.py.
"""
import csv
import re
import sys
from pathlib import Path

QA_FIELDS = [("pergunta", "Pergunta"), ("resposta", "Resposta"), ("trecho", "Trecho"), ("fonte", "Fonte"),
             ("decisao", "Decisão (ok / corrigir / excluir)"), ("nova_pergunta", "Nova pergunta"),
             ("nova_resposta", "Nova resposta"), ("comentario", "Comentário")]
CHAT_FIELDS = [("usuario_1", "Usuário 1"), ("atendente_1", "Atendente 1"), ("usuario_2", "Usuário 2"),
               ("atendente_2", "Atendente 2"), ("decisao", "Decisão (ok / corrigir / excluir)"),
               ("novo_atendente_1", "Novo atendente 1"), ("novo_atendente_2", "Novo atendente 2"),
               ("comentario", "Comentário")]
FID_FIELDS = [("pergunta", "Pergunta"), ("resposta", "Resposta"), ("trecho", "Trecho"), ("fonte", "Fonte"),
              ("fiel_humano", "Fiel (sim / não)"), ("observacao", "Observação")]
EDITABLE = {"decisao", "nova_pergunta", "nova_resposta", "novo_atendente_1", "novo_atendente_2", "comentario",
            "fiel_humano", "observacao"}

HEADERS = {
    "qa": ("corpus_qa.jsonl", ["arquivo", "linha", "pergunta", "resposta", "trecho", "fonte",
                               "decisao (ok/corrigir/excluir)", "nova_pergunta", "nova_resposta", "comentario"]),
    "chat": ("corpus_chat.jsonl", ["arquivo", "linha", "usuario_1", "atendente_1", "usuario_2", "atendente_2",
                                   "decisao (ok/corrigir/excluir)", "novo_atendente_1", "novo_atendente_2", "comentario"]),
}


def one_line(text):
    return " ".join((text or "").split())


def read_csv(path, delimiter):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def key_of(row, name):
    return next((k for k in row if k.startswith(name)), name)


def write_md(path, title, intro, label, rows, fields, id_key="linha"):
    parts = [f"# {title}\n", intro + "\n"]
    for row in rows:
        parts.append(f"\n## {label} {row[id_key]}\n")
        for key, text in fields:
            parts.append(f"- **{text}:** {one_line(row.get(key_of(row, key), ''))}")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def read_md(path):
    items, current = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^## \D+ (\d+)\s*$", line)
        if heading:
            current = int(heading.group(1))
            items[current] = {}
            continue
        field = re.match(r"^- \*\*(.+?):\*\*\s?(.*)$", line)
        if field and current is not None:
            items[current][field.group(1)] = field.group(2).strip()
    return items


def to_md(folder):
    qa = read_csv(folder / "revisao_apoio_qa.csv", ";")
    chat = read_csv(folder / "revisao_apoio_chat.csv", ";")
    fid = read_csv(folder / "amostra_fidelidade.csv", ",")
    rule = "Preencha só o valor depois de cada rótulo editável; mantenha cada valor em uma linha."
    write_md(folder / "REVISAO_QA.md", "Revisão do QA",
             f"Para cada par: a resposta está sustentada pelo trecho e responde à pergunta? {rule} "
             "Decisão: ok, corrigir (escreva nova pergunta e/ou nova resposta) ou excluir. Mantenha 100 pares ou mais.",
             "QA", qa, QA_FIELDS)
    write_md(folder / "REVISAO_CHAT.md", "Revisão do chat",
             f"Para cada diálogo: a resposta é correta, simples, sem parecer jurídico e sem inventar órgão ou prazo? "
             f"A 2ª pergunta depende da 1ª? {rule} Mantenha 30 diálogos ou mais.",
             "Chat", chat, CHAT_FIELDS)
    write_md(folder / "REVISAO_FIDELIDADE.md", "Amostra de fidelidade",
             f"Para cada item: o trecho sozinho confirma toda a resposta? Responda sim ou não em 'Fiel'. {rule}",
             "Item", fid, FID_FIELDS)
    print("Gerados: REVISAO_QA.md, REVISAO_CHAT.md, REVISAO_FIDELIDADE.md")


def to_csv(folder):
    for kind, md_name, fields in (("qa", "REVISAO_QA.md", QA_FIELDS), ("chat", "REVISAO_CHAT.md", CHAT_FIELDS)):
        source, header = HEADERS[kind]
        items = read_md(folder / md_name)
        with open(folder / f"revisao_apoio_{kind}.csv", "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(header)
            for number, values in items.items():
                data = {key: values.get(text, "") for key, text in fields}
                writer.writerow([source, number] + [data[h.split(" ")[0]] for h in header[2:]])
    fid_items = read_md(folder / "REVISAO_FIDELIDADE.md")
    original = {int(r["linha"]): r for r in read_csv(folder / "amostra_fidelidade.csv", ",")}
    with open(folder / "amostra_fidelidade.csv", "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["linha", "pergunta", "resposta", "trecho", "fonte", "sobreposicao", "fiel_humano", "observacao"])
        for number, values in fid_items.items():
            row = original[number]
            writer.writerow([number, row["pergunta"], row["resposta"], row["trecho"], row["fonte"], row["sobreposicao"],
                             values.get("Fiel (sim / não)", ""), values.get("Observação", "")])
    print("CSV atualizados: revisao_apoio_qa.csv, revisao_apoio_chat.csv, amostra_fidelidade.csv")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("para-md", "para-csv"):
        raise SystemExit(__doc__)
    folder_arg = Path(sys.argv[2])
    to_md(folder_arg) if sys.argv[1] == "para-md" else to_csv(folder_arg)
