"""Cache limitado de respostas aprovadas, sem persistência de perguntas."""
import copy
import time
import threading
from collections import OrderedDict


class CacheRespostas:
    def __init__(self, capacidade=128, validade=300):
        self.capacidade = capacidade
        self.validade = validade
        self._itens = OrderedDict()
        self._trava = threading.Lock()

    def obter(self, chave):
        with self._trava:
            item = self._itens.get(chave)
            if item is None:
                return None
            instante, resposta = item
            if time.monotonic() - instante >= self.validade:
                del self._itens[chave]
                return None
            self._itens.move_to_end(chave)
            return copy.deepcopy(resposta)

    def guardar(self, chave, resposta):
        if resposta.get("status") != "respondido" or not resposta.get("afirmacoes") or not resposta.get("fontes"):
            return
        with self._trava:
            self._itens[chave] = (time.monotonic(), copy.deepcopy(resposta))
            self._itens.move_to_end(chave)
            while len(self._itens) > self.capacidade:
                self._itens.popitem(last=False)

    def limpar(self):
        with self._trava:
            self._itens.clear()


CACHE = CacheRespostas()
