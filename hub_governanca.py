"""Servidor Web do Hub Executivo de Governança em IA e Business Analytics (CitizenTech / ZelaIA)."""

import json
import mimetypes
import threading
import webbrowser
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import unquote, urlparse

from governanca_hub.governance_simulation_engine import (
    compare_greedy_vs_optimal_dispatch,
    get_default_zelaia_dispatch_tasks,
    sanitize_citizen_input_lgpd,
    simulate_ispd_cluster_scaling,
)
from governanca_hub.repository_data_loader import (
    build_complete_hub_api_payload,
    get_workspace_root,
)

WEB_ASSETS_DIR = Path(__file__).resolve().parent / "governanca_hub" / "web"
DEFAULT_PORT = 8505


def resolve_safe_media_path(category: str, raw_filename: str) -> Path | None:
    """Resolve com segurança o caminho de uma imagem de evidência das pastas do repositório."""
    safe_name = Path(unquote(raw_filename)).name
    if not safe_name or ".." in raw_filename:
        return None

    root_path = get_workspace_root()
    if category == "cv_fig":
        target = (
            root_path
            / "GS - VISÃO COMPUTACIONAL"
            / "GS 4 VISÃO"
            / "artifacts"
            / "figures"
            / safe_name
        )
    elif category == "cv_sample":
        target = (
            root_path
            / "GS - VISÃO COMPUTACIONAL"
            / "GS 4 VISÃO"
            / "artifacts"
            / "sample_media"
            / "test_images"
            / safe_name
        )
    elif category == "iot_fig":
        target = (
            root_path
            / "GS - IOT"
            / "GS2026.2 - IoT"
            / "evidencias"
            / safe_name
        )
    else:
        return None

    return target if target.exists() and target.is_file() else None


class GovernanceHubRequestHandler(BaseHTTPRequestHandler):
    """Controlador HTTP das rotas da SPA e da API de Governança e Simulação."""

    def log_message(self, format_str: str, *args: Any) -> None:
        """Mantém o console limpo registrando apenas erros críticos."""
        return

    def _send_json(self, payload: Dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Recurso nao encontrado")
            return
        mime_type, _ = mimetypes.guess_type(str(file_path))
        content_type = mime_type or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path).path

        if parsed_path in ("/", "/index.html"):
            self._send_file(WEB_ASSETS_DIR / "index.html")
            return

        if parsed_path == "/web/styles.css":
            self._send_file(WEB_ASSETS_DIR / "styles.css")
            return

        if parsed_path == "/web/app.js":
            self._send_file(WEB_ASSETS_DIR / "app.js")
            return

        if parsed_path == "/api/telemetry":
            payload = build_complete_hub_api_payload()
            self._send_json(payload)
            return

        if parsed_path.startswith("/media/"):
            parts = parsed_path.strip("/").split("/", 2)
            if len(parts) == 3:
                _, category, filename = parts
                media_path = resolve_safe_media_path(category, filename)
                if media_path:
                    self._send_file(media_path)
                    return
            self.send_error(HTTPStatus.NOT_FOUND, "Midia nao encontrada")
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Rota nao encontrada")

    def do_POST(self) -> None:
        parsed_path = urlparse(self.path).path
        if parsed_path != "/api/simulate":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint invalido")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            request_data = json.loads(raw_body)
        except json.JSONDecodeError:
            request_data = {}

        raw_text = str(request_data.get("raw_text", ""))
        task_count = int(request_data.get("task_count", 1000))
        budget_hours = int(request_data.get("budget_hours", 8))

        lgpd_audit = sanitize_citizen_input_lgpd(raw_text)
        cluster_metrics = simulate_ispd_cluster_scaling(task_count)
        opt_result = compare_greedy_vs_optimal_dispatch(
            get_default_zelaia_dispatch_tasks(), budget_hours
        )

        response_payload = {
            "sanitized_text": lgpd_audit.sanitized_text,
            "masked_counts": lgpd_audit.masked_items_count,
            "cluster": cluster_metrics,
            "optimization": asdict(opt_result),
        }
        self._send_json(response_payload)


def start_hub_server(port: int = DEFAULT_PORT, open_browser: bool = True) -> None:
    """Inicia o servidor local do Hub Web (com fallback automático de porta) e abre o navegador."""
    httpd = None
    selected_port = port
    for candidate_port in range(port, port + 15):
        try:
            httpd = ThreadingHTTPServer(
                ("127.0.0.1", candidate_port), GovernanceHubRequestHandler
            )
            selected_port = candidate_port
            break
        except OSError:
            continue

    if httpd is None:
        raise RuntimeError("Não foi possível alocar uma porta local entre 8505 e 8519.")

    url = f"http://127.0.0.1:{selected_port}"
    print("=" * 76)
    print("  FIAP • GLOBAL SOLUTION 2026.2 • GOVERNANÇA EM IA E BUSINESS ANALYTICS")
    print(f"  Hub Web Moderno (Bento Grid SaaS) ativo em: {url}")
    print("  Pressione Ctrl+C nesta janela para encerrar o servidor.")
    print("=" * 76)

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando o servidor do Hub...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    start_hub_server()
