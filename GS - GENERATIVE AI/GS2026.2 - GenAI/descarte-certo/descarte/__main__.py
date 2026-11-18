"""Servidor local do protótipo; não destinado à exposição pública."""

import argparse
import json
import socket
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, BoundedSemaphore
from urllib.parse import urlparse

from .configuracao import Configuracao
from .corpus import RAIZ, carregar
from .fluxo import Assistente


class ServidorLocal(ThreadingHTTPServer):
    # SO_REUSEADDR permite dois listeners na mesma porta no Windows.
    allow_reuse_address = not hasattr(socket, "SO_EXCLUSIVEADDRUSE")

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def criar_servidor(config, porta=8765):
    chegadas = deque()
    trava = Lock()
    vagas = BoundedSemaphore(2)

    class Atendimento(BaseHTTPRequestHandler):
        def log_message(self, formato, *args):
            pass  # Não registrar perguntas, cabeçalhos ou dados do cidadão.

        def entregar(self, codigo, corpo, tipo="application/json; charset=utf-8"):
            if isinstance(corpo, dict):
                corpo = json.dumps(corpo, ensure_ascii=False).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            try:
                self.wfile.write(corpo)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def host_valido(self):
            return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

        def do_GET(self):
            if not self.host_valido():
                return self.entregar(403, {"erro": "Origem não permitida."})
            rota = urlparse(self.path).path
            if rota == "/api/fontes":
                corpus = carregar()
                return self.entregar(200, {"versao": corpus["versao"], "metodo": corpus["metodo"], "fontes": corpus["documentos"]})
            if rota == "/api/estado":
                return self.entregar(200, {"pronto": not config.ausentes(), "corpus": carregar()["versao"],
                                          "versao_prompt": config.parametros["versao_prompt"]})
            arquivos = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/estilo.css": ("estilo.css", "text/css; charset=utf-8")}
            if rota not in arquivos:
                return self.entregar(404, {"erro": "Página não encontrada."})
            nome, tipo = arquivos[rota]
            self.entregar(200, (RAIZ / "web" / nome).read_bytes(), tipo)

        def do_POST(self):
            origem = self.headers.get("Origin")
            origens = {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}
            if not self.host_valido() or (origem is not None and origem not in origens):
                return self.entregar(403, {"erro": "Origem não permitida."})
            if self.path != "/api/conversar":
                return self.entregar(404, {"erro": "Rota não encontrada."})
            if self.headers.get_content_type() != "application/json":
                return self.entregar(415, {"erro": "Envie dados JSON."})
            try:
                tamanho = int(self.headers.get("Content-Length", "0"))
                if not 0 < tamanho <= 16000:
                    return self.entregar(413, {"erro": "Mensagem muito extensa."})
                dados = json.loads(self.rfile.read(tamanho))
                if not isinstance(dados, dict):
                    raise ValueError()
            except (ValueError, UnicodeDecodeError):
                return self.entregar(400, {"erro": "Mensagem inválida."})
            with trava:
                agora = time.monotonic()
                while chegadas and agora - chegadas[0] > 60:
                    chegadas.popleft()
                if len(chegadas) >= 12:
                    return self.entregar(429, {"erro": "Aguarde um minuto antes de enviar outra pergunta."})
                chegadas.append(agora)
            if not vagas.acquire(blocking=False):
                return self.entregar(429, {"erro": "Há consultas em andamento. Tente novamente em instantes."})
            try:
                resultado = Assistente(config).responder(dados.get("pergunta"), dados.get("historico", []))
                self.entregar(503 if resultado["status"] == "indisponivel" else 200, resultado)
            except Exception:
                self.entregar(500, {"erro": "Não foi possível concluir a consulta. Tente novamente."})
            finally:
                vagas.release()

    return ServidorLocal(("127.0.0.1", porta), Atendimento)


def main():
    parser = argparse.ArgumentParser(description="Descarte Certo — protótipo local")
    parser.add_argument("--env", help="Arquivo local de credenciais")
    parser.add_argument("--porta", type=int, default=8765)
    args = parser.parse_args()
    config = Configuracao.ler(args.env)
    try:
        servidor = criar_servidor(config, args.porta)
    except OSError:
        parser.error("Não foi possível abrir a porta local. Encerre o servidor anterior ou escolha outra porta com --porta.")
    print(f"Descarte Certo em http://127.0.0.1:{args.porta}", flush=True)
    if config.ausentes():
        print("Configuração pendente: " + ", ".join(config.ausentes()), flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
