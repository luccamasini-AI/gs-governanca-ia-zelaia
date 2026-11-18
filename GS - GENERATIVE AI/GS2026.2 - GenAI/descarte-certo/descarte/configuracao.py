"""Configuração pública e leitura local de credenciais sem exposição."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .corpus import RAIZ


@dataclass
class Configuracao:
    parametros: dict = field(default_factory=lambda: json.loads((RAIZ / "dados/configuracao.json").read_text(encoding="utf-8")))
    chave_openai: str = field(default="", repr=False)
    chave_jev: str = field(default="", repr=False)

    @classmethod
    def ler(cls, arquivo: str | None = None):
        valores = {}
        caminho = Path(arquivo) if arquivo else RAIZ / ".env.local"
        if caminho.is_file():
            for linha in caminho.read_text(encoding="utf-8-sig").splitlines():
                if "=" in linha and not linha.lstrip().startswith("#"):
                    nome, valor = linha.split("=", 1)
                    valores[nome.strip()] = valor.strip().strip("\"'")
        config = cls(chave_openai=os.getenv("OPENAI_API_KEY") or valores.get("OPENAI_API_KEY", ""),
                     chave_jev=os.getenv("TYPESAFE_API_KEY") or valores.get("TYPESAFE_API_KEY", ""))
        for variavel, campo in [("OPENAI_MODEL", "modelo_openai"), ("JEV_MODEL", "modelo_jev")]:
            if os.getenv(variavel) or valores.get(variavel):
                config.parametros[campo] = os.getenv(variavel) or valores[variavel]
        return config

    def ausentes(self) -> list[str]:
        return [nome for nome, valor in [("OpenAI", self.chave_openai), ("Jev", self.chave_jev)] if not valor]
