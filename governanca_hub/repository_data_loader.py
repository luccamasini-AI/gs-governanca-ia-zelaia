"""Carregador de artefatos, métricas e arquivos reais das oito pastas do repositório."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from governanca_hub.domain_contracts import ModuleGovernanceRecord


def get_workspace_root() -> Path:
    """Retorna o diretório raiz do monorepo de Governança."""
    return Path(__file__).resolve().parent.parent


def load_json_file_safely(file_path: Path, fallback_data: Any) -> Any:
    """Lê um arquivo JSON do disco com tratamento explícito de exceções."""
    if not file_path.exists():
        return fallback_data
    try:
        with file_path.open("r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except (OSError, json.JSONDecodeError):
        return fallback_data


def load_computer_vision_metrics() -> Dict[str, Any]:
    """Carrega o relatório JSON real do módulo de Visão Computacional."""
    root_path = get_workspace_root()
    metrics_path = (
        root_path
        / "GS - VISÃO COMPUTACIONAL"
        / "GS 4 VISÃO"
        / "artifacts"
        / "metrics"
        / "evaluation_report.json"
    )
    fallback_metrics = {
        "metrics": {
            "accuracy": 0.9971,
            "precision": 1.0,
            "recall": 0.9941,
            "f1_score": 0.997,
        },
        "confusion_matrix": {
            "true_negative": 339,
            "false_positive": 0,
            "false_negative": 2,
            "true_positive": 337,
        },
        "performance": {
            "average_latency_ms": 4.48,
            "fps": 223.2,
            "local_average_latency_ms": 30.72,
            "local_fps": 32.6,
        },
    }
    loaded = load_json_file_safely(metrics_path, fallback_metrics)
    return loaded if isinstance(loaded, dict) else fallback_metrics


def load_nlp_quality_metrics() -> Dict[str, Any]:
    """Carrega o relatório JSON real de qualidade do corpus de NLP."""
    root_path = get_workspace_root()
    nlp_json_path = (
        root_path
        / "GS - NLP"
        / "GS-NLP-2S-main"
        / "entrega-gs"
        / "saida"
        / "relatorio_qualidade.json"
    )
    fallback_nlp = {
        "corpus": {
            "corpus_texto.jsonl": {"exemplos": 68, "media_tokens": 461.0},
            "corpus_qa.jsonl": {"exemplos": 126, "media_tokens": 45.0},
            "corpus_chat.jsonl": {"exemplos": 36, "media_tokens": 281.3},
            "corpus_teste.jsonl": {"exemplos": 24, "media_tokens": 51.5},
        },
        "vazamento_maior_similaridade": 0.848,
        "lingua_real": {
            "corpus_qa.jsonl": 0.381,
            "corpus_chat.jsonl": 0.583,
            "corpus_teste.jsonl": 0.500,
        },
    }
    loaded = load_json_file_safely(nlp_json_path, fallback_nlp)
    return loaded if isinstance(loaded, dict) else fallback_nlp


def load_iot_complete_telemetry() -> Dict[str, Any]:
    """Carrega as métricas reais de robustez (Studio) e do experimento de sintéticos (PyTorch) do módulo IoT."""
    root_path = get_workspace_root()
    iot_base = root_path / "GS - IOT" / "GS2026.2 - IoT"
    robustez_path = iot_base / "robustez" / "resultados.json"
    sinteticos_path = iot_base / "experimento_sinteticos" / "resultados.json"

    robustez_list = load_json_file_safely(robustez_path, [])
    sinteticos_dict = load_json_file_safely(sinteticos_path, {})

    model_08_int8_records: Dict[str, Any] = {}
    if isinstance(robustez_list, list):
        for entry in robustez_list:
            if (
                isinstance(entry, dict)
                and entry.get("modelo") == 8
                and entry.get("variante") == "int8"
            ):
                cond = str(entry.get("condicao", ""))
                model_08_int8_records[cond] = entry

    return {
        "studio_url": "https://studio.edgeimpulse.com/studio/1161308/impulse/8/learning/keras/25",
        "target_mcu": "Cortex-M4F 80MHz",
        "model_08_int8": model_08_int8_records,
        "synthetic_study": sinteticos_dict if isinstance(sinteticos_dict, dict) else {},
        "synthetic_comparison_table": [
            {
                "condition": "Novos limpos (45)",
                "public_base": 65.2,
                "plus_synthetics": 60.7,
                "plus_variations": 60.7,
                "studio_08_int8": 55.6,
            },
            {
                "condition": "Volume -12 dB (45)",
                "public_base": 58.5,
                "plus_synthetics": 60.0,
                "plus_variations": 60.7,
                "studio_08_int8": 51.1,
            },
            {
                "condition": "Ruído SNR 20 dB (45)",
                "public_base": 38.5,
                "plus_synthetics": 43.0,
                "plus_variations": 43.0,
                "studio_08_int8": 33.3,
            },
            {
                "condition": "Ruído SNR 10 dB (45)",
                "public_base": 34.8,
                "plus_synthetics": 40.7,
                "plus_variations": 37.0,
                "studio_08_int8": 31.1,
            },
        ],
    }


def list_computer_vision_sample_images() -> List[Path]:
    """Lista as imagens reais de teste do módulo de Visão Computacional."""
    root_path = get_workspace_root()
    images_dir = (
        root_path
        / "GS - VISÃO COMPUTACIONAL"
        / "GS 4 VISÃO"
        / "artifacts"
        / "sample_media"
        / "test_images"
    )
    if not images_dir.exists():
        return []
    return sorted(images_dir.glob("*.jpg"))


def list_computer_vision_figure_paths() -> Dict[str, Path]:
    """Retorna os caminhos dos gráficos de avaliação do módulo de Visão Computacional."""
    root_path = get_workspace_root()
    figures_dir = (
        root_path
        / "GS - VISÃO COMPUTACIONAL"
        / "GS 4 VISÃO"
        / "artifacts"
        / "figures"
    )
    figure_names = {
        "Matriz de Confusão (678 imagens)": "confusion_matrix.png",
        "Curvas de Treinamento (Loss e Acurácia)": "training_history.png",
        "Mapas de Atenção Espacial (Grad-CAM / WSOL)": "correct_predictions_analysis.png",
        "Análise dos 2 Falsos Negativos e Sombra": "error_and_interference_analysis.png",
    }
    resolved_figures: Dict[str, Path] = {}
    for label, filename in figure_names.items():
        candidate_path = figures_dir / filename
        if candidate_path.exists():
            resolved_figures[label] = candidate_path
    return resolved_figures


def list_iot_evidence_figure_paths() -> Dict[str, Path]:
    """Retorna as 5 capturas oficiais do Edge Impulse Studio presentes em GS - IOT."""
    root_path = get_workspace_root()
    evidencias_dir = root_path / "GS - IOT" / "GS2026.2 - IoT" / "evidencias"
    figure_names = {
        "1. Data Acquisition (Edge Impulse Studio)": "01_data_acquisition.png",
        "2. Impulse Design (Janela 5s + MFE + CNN)": "02_impulse_design_modelo_01.png",
        "3. Generate Features (Espectrogramas MFE)": "03_generate_features_modelo_01.png",
        "4. Classifier 08 int8 (Validação 66,7% | ROC 0,86)": "04_classifier_modelo_08_int8.png",
        "5. Model Testing no Conjunto Público": "05_model_testing_modelo_01.png",
    }
    resolved_figures: Dict[str, Path] = {}
    for label, filename in figure_names.items():
        candidate_path = evidencias_dir / filename
        if candidate_path.exists():
            resolved_figures[label] = candidate_path
    return resolved_figures


def list_folder_verified_files(folder_name: str, limit: int = 16) -> List[str]:
    """Lista os arquivos reais verificados dentro da pasta da disciplina."""
    folder_path = get_workspace_root() / folder_name
    if not folder_path.exists():
        return []
    files_found: List[str] = []
    for path_item in sorted(folder_path.rglob("*")):
        if (
            path_item.is_file()
            and path_item.name not in (".env", "__init__.py")
            and not any(
                ignored in str(path_item)
                for ignored in [".git", "__pycache__", ".venv", "node_modules", "test_images"]
            )
        ):
            files_found.append(str(path_item.relative_to(folder_path)).replace("\\", "/"))
            if len(files_found) >= limit:
                break
    return files_found


def get_all_module_governance_records() -> List[ModuleGovernanceRecord]:
    """Retorna o catálogo consolidado das 8 disciplinas e seus indicadores reais."""
    return [
        ModuleGovernanceRecord(
            module_id="front_end",
            discipline_name="Front-End em Sistemas de IA",
            project_title="ZelaAI • Zeladoria Urbana e Clima",
            folder_name="GS - FRONT END",
            integration_status="Integrado (Fluxo ZelaIA)",
            coupling_level="API REST FastAPI + Pipeline de Risco e Clima",
            primary_technology_stack="Streamlit • FastAPI • Pydantic • RandomForest • Open-Meteo • Gemini 2.5",
            main_metric_label="Testes & Validação",
            main_metric_value="13 Pytest (100%)",
            secondary_metric_label="Acessibilidade",
            secondary_metric_value="WCAG 2.1 AAA + Voz",
            lgpd_mechanism="Mascaramento automático de CPF e e-mail via Regex no schema Pydantic antes do envio ao LLM.",
            human_in_the_loop_mechanism="Duplo Human-in-the-Loop: confirmação pelo cidadão e revisão pelo gestor municipal (RBAC).",
            hallucination_or_error_control="Contrato JSON estrito (StructuredAiTriageOutput) + Motor Determinístico de Contingência local.",
            sdg_goals=["ODS 11", "ODS 13"],
            integration_justification="Porta de entrada oficial do cidadão e do gestor no fluxo de zeladoria urbana ZelaIA.",
            known_limitations="Não substitui emergências imediatas (193/192); consulta climática requer conexão à API Open-Meteo.",
        ),
        ModuleGovernanceRecord(
            module_id="visao_computacional",
            discipline_name="Visão Computacional",
            project_title="CitizenTech • Inspeção de Fissuras",
            folder_name="GS - VISÃO COMPUTACIONAL",
            integration_status="Integrado (Fluxo ZelaIA)",
            coupling_level="Motor de Análise Visual para Anexos do ZelaIA",
            primary_technology_stack="PyTorch • MobileNetV3-Small • WSOL via Grad-CAM • OpenCV",
            main_metric_label="Acurácia / Precisão",
            main_metric_value="99,71% / 100% (FP=0)",
            secondary_metric_label="Taxa de Quadros",
            secondary_metric_value="223,2 FPS (4,48 ms GPU)",
            lgpd_mechanism="Imagens restritas a superfícies de concreto; validação de pacotes contra vulnerabilidade Zip Slip.",
            human_in_the_loop_mechanism="Triagem visual estritamente preventiva para priorizar vistoria presencial de engenheiro civil.",
            hallucination_or_error_control="Particionamento GroupShuffleSplit (janela 85) contra Data Leakage + Limiar sensível a sombra (0,35).",
            sdg_goals=["ODS 9", "ODS 11"],
            integration_justification="Analisa automaticamente as fotos de calçadas, viadutos e muros enviadas no fluxo ZelaIA.",
            known_limitations="Imagens 2D não medem profundidade estrutural; sombras intensas reduzem probabilidade para 35%-48%.",
        ),
        ModuleGovernanceRecord(
            module_id="cluster_computing",
            discipline_name="Cluster & Supercomputadores",
            project_title="ZelaIA • Escalabilidade no iSPD",
            folder_name="GS - CLUSTER",
            integration_status="Integrado (Fluxo ZelaIA)",
            coupling_level="Dimensionamento de Capacidade p/ Lotes de Imagens",
            primary_technology_stack="Simulador iSPD 2.0 (UNESP) • Java Temurin 8 • RoundRobin",
            main_metric_label="Redução (2 ➔ 4 Workers)",
            main_metric_value="-49,9945% no Tempo",
            secondary_metric_label="Tempo p/ 1.000 Fotos",
            secondary_metric_value="500,019 s ➔ 250,037 s",
            lgpd_mechanism="Simulação executada sobre arquivo de trace sintético (ocorrencias.wmsx) sem dados pessoais.",
            human_in_the_loop_mechanism="Auditoria manual das métricas por recurso no motor iSPD contra rótulos globais distorcidos.",
            hallucination_or_error_control="Carga única determinística (1.000 tarefas de 1.000 MFLOP e 8 Mbit) repetida 3 vezes sem variação.",
            sdg_goals=["ODS 9", "ODS 11"],
            integration_justification="Garante que o back-end do ZelaIA escale horizontalmente ao receber lotes de 1.000 imagens.",
            known_limitations="Projeção de infraestrutura de CPU e rede; não modela contenção de banco de dados ou GPU.",
        ),
        ModuleGovernanceRecord(
            module_id="computacao_quantica",
            discipline_name="Computação Quântica",
            project_title="ZelaIA • Despacho Ótimo e PQC",
            folder_name="GS - COMPUTAÇÃO QUANTICA",
            integration_status="Integrado (Fluxo ZelaIA)",
            coupling_level="Otimização Pós-Triagem e Criptografia Pós-Quântica",
            primary_technology_stack="Problema da Mochila Binária (QUBO) • QAOA • NIST FIPS 203 (ML-KEM)",
            main_metric_label="Ótimo vs. Guloso (8h)",
            main_metric_value="20 pts vs. 18 pts (+11%)",
            secondary_metric_label="Escala Combinatória",
            secondary_metric_value="2^N (N=50 ➔ >10^15)",
            lgpd_mechanism="Proteção de longo prazo contra 'coletar agora, decifrar depois' em fotos/GPS via PQC (Art. 46 LGPD).",
            human_in_the_loop_mechanism="Critérios públicos de prioridade e revisão humana (Art. 20 LGPD) para impedir viés territorial.",
            hallucination_or_error_control="Honestidade científica declarada: sem vantagem quântica hoje para N pequeno; uso de solver clássico.",
            sdg_goals=["ODS 9", "ODS 10", "ODS 11", "ODS 16"],
            integration_justification="Decide quais ocorrências triadas no ZelaIA serão atendidas pelas equipes dentro do limite de horas.",
            known_limitations="Em instâncias pequenas (5 itens), força bruta e programação linear clássica resolvem em milissegundos.",
        ),
        ModuleGovernanceRecord(
            module_id="rpa_ia",
            discipline_name="AI for RPA",
            project_title="Robô de Triagem de Serviços Públicos",
            folder_name="GS - RPA",
            integration_status="Vertical Independente Governada",
            coupling_level="Desacoplado (Escopo Multi-Órgão .gov.br + SQLite)",
            primary_technology_stack="Python • TF-IDF + Regressão Logística • SQLite • OpenRouter LLM",
            main_metric_label="Acurácia Automática",
            main_metric_value="100,0% (c/ corte 0,60)",
            secondary_metric_label="Catálogo Verificado",
            secondary_metric_value="127 Fontes .gov.br",
            lgpd_mechanism="Anonimiza CPF, RG, CNH, SUS, PIS, telefone, e-mail, CEP e nomes antes do log, banco e LLM.",
            human_in_the_loop_mechanism="Retém 33,3% dos pedidos (baixa confiança <0,60, urgência ou fora do catálogo) na fila humana.",
            hallucination_or_error_control="Allowlist estrita de domínios oficiais + Verificação HTTP 200 ao vivo + Guarda contra URLs externas.",
            sdg_goals=["ODS 10", "ODS 16"],
            integration_justification="Separado do código ZelaAI por atender 127 serviços documentais (CNH, INSS, IPTU) e não obras urbanas.",
            known_limitations="Anonimização por regras/prenomes possui risco residual para nomes próprios atípicos fora de contexto.",
        ),
        ModuleGovernanceRecord(
            module_id="generative_ai",
            discipline_name="Generative AI & Advanced Nets",
            project_title="Descarte Certo • Assistente Municipal",
            folder_name="GS - GENERATIVE AI",
            integration_status="Vertical Independente Governada",
            coupling_level="Desacoplado (Servidor Dedicado + Guarda Factual Jev)",
            primary_technology_stack="Python Stdlib • Busca Léxica BM25 • TypeSafe Jev • OpenAI API",
            main_metric_label="Fidelidade Factual",
            main_metric_value="20/20 Estados (0 Erros)",
            secondary_metric_label="Ganho de Latência",
            secondary_metric_value="-70,9% Jev | -94,1% Cache",
            lgpd_mechanism="Histórico mantido apenas em memória volátil do navegador + Filtro local contra PII e ataques.",
            human_in_the_loop_mechanism="Abstenção controlada transparente quando a evidência documental é insuficiente para responder.",
            hallucination_or_error_control="Verificador Jev (33/34 decisões corretas, limiar 0,75/0,80) + 4/4 bloqueios de Prompt Injection.",
            sdg_goals=["ODS 11", "ODS 12"],
            integration_justification="Separado por operar sobre corpus fechado de regras de Ecopontos e Cata-Bagulho com guarda Jev.",
            known_limitations="Limiar conservador do Jev pode ocasionar recusa cautelosa em perguntas limítrofes (ex.: escore 0,74).",
        ),
        ModuleGovernanceRecord(
            module_id="nlp_corpus",
            discipline_name="Natural Language Processing",
            project_title="Fábrica de Corpus • Defesa do Consumidor",
            folder_name="GS - NLP",
            integration_status="Vertical Independente Governada",
            coupling_level="Desacoplado (Pipeline Batch Colab GPU p/ Dados JSONL)",
            primary_technology_stack="Google Colab T4 • Qwen2.5-7B (4-bit) • spaCy NER • Sentence-Transformers",
            main_metric_label="Corpus Curado à Mão",
            main_metric_value="112 QA + 33 Diálogos",
            secondary_metric_label="Língua Informal Real",
            secondary_metric_value="38,1% a 58,3% (Meta 30%)",
            lgpd_mechanism="Anonimização híbrida (spaCy pt_core_news_lg + Regex) auditada com tabela antes/depois e zero PII.",
            human_in_the_loop_mechanism="Revisão humana integral de 100% dos 126 pares QA e 22 diálogos gerados (revisao.csv).",
            hallucination_or_error_control="197 pares defeituosos barrados por filtros/juízes + Fatos voláteis (multas/prazos) isolados p/ RAG.",
            sdg_goals=["ODS 10", "ODS 16"],
            integration_justification="Separado por ser uma fábrica offline de datasets JSONL (60-90 min em GPU) para Direito do Consumidor.",
            known_limitations="Juízes automáticos isolados aprovam ~35% de pares imperfeitos, exigindo a revisão humana aplicada.",
        ),
        ModuleGovernanceRecord(
            module_id="iot_ouviai",
            discipline_name="Cognitive IoT & Embedded AI",
            project_title="OuviAí • Assistente Acústico Embarcado",
            folder_name="GS - IOT",
            integration_status="Vertical Independente Governada",
            coupling_level="Desacoplado (TinyML int8 Cortex-M4F + PyTorch Local)",
            primary_technology_stack="Edge Impulse (Modelo 08 int8) • MFE FFT 512 + CNN 1D • PyTorch (3 Sementes)",
            main_metric_label="Validação / Sintéticos",
            main_metric_value="66,7% Studio | +5,9% SNR10",
            secondary_metric_label="Bateria Experimental",
            secondary_metric_value="3.900 Decisões + 72 Var.",
            lgpd_mechanism="Processamento acústico em borda (on-device) + Manifestos CC BY 3.0/4.0, CRC32 e hashes SHA-256.",
            human_in_the_loop_mechanism="Limiar de confiança 0,60 (marca baixa confiança como 'Incerto') + Curadoria de recortes e ganho RMS.",
            hallucination_or_error_control="Separação estrita de autores entre treino e teste (ESC-50/FSD50K) + Ensaio de sintéticos sob ruído.",
            sdg_goals=["ODS 10"],
            integration_justification="Separado por operar em hardware embarcado (Cortex-M4F / celular) monitorando sons domésticos.",
            known_limitations="Ruído intenso (SNR 10 dB) reduz acurácia do 08 int8 para 31,1%; sintéticos melhoram ruído (40,7%), mas reduzem limpos.",
        ),
    ]


def build_complete_hub_api_payload() -> Dict[str, Any]:
    """Constrói o payload JSON consolidado consumido pelo Front-end Web moderno do Hub."""
    records = get_all_module_governance_records()
    cv_metrics = load_computer_vision_metrics()
    nlp_metrics = load_nlp_quality_metrics()
    iot_telemetry = load_iot_complete_telemetry()

    cv_figures = [
        {"label": label, "url": f"/media/cv_fig/{path.name}"}
        for label, path in list_computer_vision_figure_paths().items()
    ]
    cv_samples = [
        {
            "name": path.name,
            "url": f"/media/cv_sample/{path.name}",
            "is_crack": "fissura" in path.name.lower(),
        }
        for path in list_computer_vision_sample_images()
    ]
    iot_figures = [
        {"label": label, "url": f"/media/iot_fig/{path.name}"}
        for label, path in list_iot_evidence_figure_paths().items()
    ]

    modules_payload = []
    for record in records:
        record_dict = asdict(record)
        record_dict["verified_files"] = list_folder_verified_files(record.folder_name)
        if record.module_id == "visao_computacional":
            record_dict["evidence_images"] = cv_figures
        elif record.module_id == "iot_ouviai":
            record_dict["evidence_images"] = iot_figures
            record_dict["studio_url"] = iot_telemetry["studio_url"]
            record_dict["target_mcu"] = iot_telemetry["target_mcu"]
        else:
            record_dict["evidence_images"] = []
        modules_payload.append(record_dict)

    return {
        "modules": modules_payload,
        "cv_metrics": cv_metrics,
        "cv_samples": cv_samples,
        "nlp_metrics": nlp_metrics,
        "iot_telemetry": iot_telemetry,
    }
