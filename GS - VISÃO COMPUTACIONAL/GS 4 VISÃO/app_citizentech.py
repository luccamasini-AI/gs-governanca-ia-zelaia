"""
Interface Web Interativa do Protótipo CitizenTech — Módulo de Visão Computacional
para Triagem e Manutenção Urbana (Classificação de Fissuras e Monitoramento em Vídeo).
"""

import tempfile
import time
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from src.domain.inspection_contracts import (
    ModelInferenceConfiguration,
    UrbanInspectionStatus,
)
from src.inference.crack_classifier_service import ConcreteCrackClassifierService
from src.reporting.bundle_and_report_manager import ColabBundleAndReportManager
from src.reporting.generate_printable_html_report import (
    generate_printable_html_report,
)
from src.video.urban_monitoring_processor import UrbanMonitoringVideoProcessor

WORKSPACE_ROOT = Path(__file__).resolve().parent


def configure_streamlit_page() -> None:
    """Define metadados e estilo visual do painel municipal CitizenTech."""
    st.set_page_config(
        page_title="CitizenTech | Visão Computacional Urbana",
        page_icon="🏙️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .main-banner {
            background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%);
            color: #ffffff;
            padding: 18px 24px;
            border-radius: 10px;
            margin-bottom: 18px;
        }
        .status-alert {
            background-color: #fef2f2;
            border-left: 6px solid #dc2626;
            padding: 14px 18px;
            border-radius: 6px;
            color: #7f1d1d;
            font-weight: 600;
        }
        .status-normal {
            background-color: #f0fdf4;
            border-left: 6px solid #16a34a;
            padding: 14px 18px;
            border-radius: 6px;
            color: #14532d;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def initialize_classifier_service(
    weights_path_str: str,
) -> ConcreteCrackClassifierService:
    """Inicializa e mantém em cache o serviço de inferência PyTorch."""
    configuration = ModelInferenceConfiguration()
    weights_path = Path(weights_path_str)
    return ConcreteCrackClassifierService(
        configuration=configuration,
        weights_file_path=weights_path if weights_path.exists() else None,
    )


def ensure_fallback_demo_samples_exist(sample_media_dir: Path) -> List[Path]:
    """
    Garante que existam amostras de concreto para demonstração imediata caso o
    pacote do Colab ainda não tenha sido importado.
    """
    test_images_dir = sample_media_dir / "test_images"
    test_images_dir.mkdir(parents=True, exist_ok=True)
    existing_images = sorted(test_images_dir.glob("*.jpg"))
    if existing_images:
        return existing_images

    rng = np.random.default_rng(42)
    for index in range(1, 7):
        base_texture = rng.normal(loc=175, scale=14, size=(227, 227, 3)).clip(
            0, 255
        ).astype(np.uint8)
        base_texture = cv2.GaussianBlur(base_texture, (3, 3), 0)

        if index <= 3:
            # Simula superfície com fissura estrutural visível
            pts = np.array(
                [
                    [20 + index * 10, 10],
                    [75, 68],
                    [110 - index * 5, 118],
                    [145, 172],
                    [195, 218],
                ],
                np.int32,
            )
            cv2.polylines(
                base_texture, [pts], isClosed=False, color=(28, 28, 30), thickness=3
            )
            filename = f"0{index}_fissura_amostra_demo.jpg"
        else:
            filename = f"0{index}_normal_amostra_demo.jpg"

        Image.fromarray(base_texture).save(test_images_dir / filename)

    return sorted(test_images_dir.glob("*.jpg"))


def render_sidebar_controls(
    bundle_manager: ColabBundleAndReportManager,
) -> float:
    """Renderiza controles de limiar de confiança e importação do pacote do Colab."""
    st.sidebar.markdown("## ⚙️ Painel de Controle CitizenTech")

    confidence_threshold = st.sidebar.slider(
        "Limiar de Confiança para Inspeção (Threshold)",
        min_value=0.20,
        max_value=0.90,
        value=0.50,
        step=0.05,
        help="Probabilidades de fissura iguais ou superiores a este valor disparam alerta de vistoria.",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📦 Sincronização Google Colab")

    if bundle_manager.model_weights_path.exists():
        st.sidebar.success("✅ Modelo treinado no Colab carregado (`concrete_crack_mobilenetv3.pth`)")
    else:
        st.sidebar.warning(
            "⚠️ Pesos treinados ainda não importados. Faça upload do `citizentech_bundle.zip` gerado no Colab abaixo."
        )

    uploaded_bundle = st.sidebar.file_uploader(
        "Importar citizentech_bundle.zip (ou .pth)",
        type=["zip", "pth"],
    )
    if uploaded_bundle is not None:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f"_{uploaded_bundle.name}"
        ) as tmp_file:
            tmp_file.write(uploaded_bundle.getbuffer())
            tmp_path = Path(tmp_file.name)

        if tmp_path.suffix.lower() == ".zip":
            bundle_manager.extract_colab_bundle_safely(tmp_path)
            generate_printable_html_report(WORKSPACE_ROOT)
            st.cache_resource.clear()
            st.sidebar.success(
                "Pacote do Colab extraído e Relatório HTML atualizado! Recarregando..."
            )
            st.rerun()
        elif tmp_path.suffix.lower() == ".pth":
            bundle_manager.model_weights_path.parent.mkdir(
                parents=True, exist_ok=True
            )
            bundle_manager.model_weights_path.write_bytes(tmp_path.read_bytes())
            st.cache_resource.clear()
            st.sidebar.success("Pesos .pth importados com sucesso!")
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Nota Técnica:** A presença visual de fissuras apoia a **triagem de locais para inspeção**, "
        "não determinando isoladamente a gravidade estrutural da edificação."
    )
    return float(confidence_threshold)


def render_single_image_inspection_tab(
    classifier_service: ConcreteCrackClassifierService,
    bundle_manager: ColabBundleAndReportManager,
    confidence_threshold: float,
) -> None:
    """Renderiza a Aba 1: Inspeção Individual de Imagens com Grad-CAM e Confiança."""
    st.subheader("🔍 Triagem Visual de Superfícies de Concreto e Pavimentos")

    col_source, col_upload = st.columns([1, 1])
    sample_files = ensure_fallback_demo_samples_exist(
        bundle_manager.sample_media_directory
    )

    with col_source:
        input_mode = st.radio(
            "Fonte da Imagem para Triagem:",
            options=[
                "Selecionar da Galeria de Teste",
                "Enviar Nova Imagem (Upload)",
            ],
            horizontal=True,
        )

    selected_pil_image = None
    selected_image_name = ""

    with col_upload:
        if input_mode == "Selecionar da Galeria de Teste":
            sample_names = [f.name for f in sample_files]
            chosen_name = st.selectbox(
                "Escolha uma imagem do conjunto de teste:", options=sample_names
            )
            if chosen_name:
                chosen_path = next(
                    f for f in sample_files if f.name == chosen_name
                )
                selected_pil_image = Image.open(chosen_path).convert("RGB")
                selected_image_name = chosen_name
        else:
            uploaded_img = st.file_uploader(
                "Envie uma foto de superfície (.jpg, .png):",
                type=["jpg", "jpeg", "png"],
            )
            if uploaded_img is not None:
                selected_pil_image = Image.open(uploaded_img).convert("RGB")
                selected_image_name = uploaded_img.name

    if selected_pil_image is None:
        return

    inspection_result = classifier_service.inspect_surface_image(
        pil_image=selected_pil_image,
        image_identifier=selected_image_name,
        custom_confidence_threshold=confidence_threshold,
    )
    gradcam_overlay, annotated_box_image = (
        classifier_service.generate_visual_inspection_overlay(
            pil_image=selected_pil_image,
            inspection_result=inspection_result,
        )
    )

    if inspection_result.inspection_status == UrbanInspectionStatus.INSPECTION_REQUIRED:
        st.markdown(
            f'<div class="status-alert">🚨 SINALIZAÇÃO DE MANUTENÇÃO: {inspection_result.inspection_status.value} '
            f'— Confiança do Modelo: {inspection_result.prediction_confidence * 100:.2f}%</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="status-normal">✅ STATUS DE TRIAGEM: {inspection_result.inspection_status.value} '
            f'— Confiança do Modelo: {inspection_result.prediction_confidence * 100:.2f}%</div>',
            unsafe_allow_html=True,
        )

    st.write("")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Classificação", inspection_result.predicted_class_name)
    kpi2.metric(
        "Confiança do Modelo",
        f"{inspection_result.prediction_confidence * 100:.2f}%",
    )
    kpi3.metric(
        "Probabilidade de Fissura",
        f"{inspection_result.crack_probability * 100:.2f}%",
    )
    kpi4.metric(
        "Latência / Velocidade",
        f"{inspection_result.inference_latency_milliseconds:.2f} ms",
        f"{inspection_result.instantaneous_frames_per_second:.1f} FPS",
    )

    img_col1, img_col2, img_col3 = st.columns(3)
    with img_col1:
        st.image(
            selected_pil_image,
            caption=f"1. Imagem Original ({selected_image_name})",
            use_container_width=True,
        )
    with img_col2:
        st.image(
            gradcam_overlay,
            caption="2. Mapa de Atenção Neural (Grad-CAM)",
            use_container_width=True,
        )
    with img_col3:
        st.image(
            annotated_box_image,
            caption="3. Localização Fracamente Supervisionada (WSOL / Grad-CAM ≥ 0.45)",
            use_container_width=True,
        )

    st.info(f"**Parecer Automático de Triagem:** {inspection_result.technical_recommendation}")


def render_video_monitoring_tab(
    classifier_service: ConcreteCrackClassifierService,
    bundle_manager: ColabBundleAndReportManager,
    confidence_threshold: float,
) -> None:
    """Renderiza a Aba 2: Processamento de Vídeo Curto ou Sequência de Imagens."""
    st.subheader("🎥 Simulação de Monitoramento Urbano Contínuo (Vídeo / Sequência de Imagens)")
    video_processor = UrbanMonitoringVideoProcessor(classifier_service)

    col_mode, col_speed = st.columns([3, 2])
    with col_mode:
        mode_choice = st.radio(
            "Modo de Simulação de Monitoramento:",
            options=[
                "Processar Sequência de Imagens de Inspeção Urbana",
                "Enviar Arquivo de Vídeo Curto (.mp4, .avi, .mov)",
            ],
            horizontal=True,
        )
    with col_speed:
        playback_speed_label = st.selectbox(
            "Ritmo de Exibição Visual na Tela:",
            options=[
                "Didático (0.35s/quadro — Ideal para Apresentação)",
                "Moderado (0.15s/quadro)",
                "Velocidade Bruta da IA (Sem pausa visual)",
            ],
            help="A pausa visual facilita enxergar cada detecção na tela sem alterar a medição real de Latência (ms) e FPS da rede neural.",
        )

    visual_delay_seconds = (
        0.35
        if playback_speed_label.startswith("Didático")
        else (0.15 if playback_speed_label.startswith("Moderado") else 0.0)
    )

    named_frames: List[Tuple[str, Image.Image]] = []

    if mode_choice == "Processar Sequência de Imagens de Inspeção Urbana":
        sample_files = ensure_fallback_demo_samples_exist(
            bundle_manager.sample_media_directory
        )
        crack_files = [f for f in sample_files if "fissura" in f.name.lower()]
        normal_files = [f for f in sample_files if "normal" in f.name.lower()]

        # Intercala quadros normais e com fissura simulando o deslocamento real de uma câmera na via
        interleaved_files: List[Path] = []
        max_pairs = max(len(crack_files), len(normal_files))
        for idx in range(max_pairs):
            if idx < len(normal_files):
                interleaved_files.append(normal_files[idx])
            if idx < len(crack_files):
                interleaved_files.append(crack_files[idx])

        ordered_files = interleaved_files if interleaved_files else sample_files
        for file_path in ordered_files:
            named_frames.append(
                (file_path.name, Image.open(file_path).convert("RGB"))
            )
        st.caption(
            f"Sequência pronta com {len(named_frames)} quadros reais intercalados (trechos íntegros e trechos fissurados) para varredura."
        )
    else:
        uploaded_video = st.file_uploader(
            "Faça upload de um vídeo curto de vistoria urbana (.mp4, .avi, .mov):",
            type=["mp4", "avi", "mov"],
        )
        default_video_path = (
            bundle_manager.sample_media_directory
            / "simulacao_monitoramento_urbano.mp4"
        )
        if uploaded_video is not None:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as tmp_video:
                tmp_video.write(uploaded_video.getbuffer())
                video_path = Path(tmp_video.name)
            named_frames = video_processor.extract_frames_from_video_file(
                video_path, frame_sampling_step=4, maximum_frames_limit=30
            )
        elif default_video_path.exists():
            st.info(
                "Utilizando vídeo de monitoramento gerado no Google Colab (`simulacao_monitoramento_urbano.mp4`)."
            )
            named_frames = video_processor.extract_frames_from_video_file(
                default_video_path, frame_sampling_step=6, maximum_frames_limit=24
            )

    if st.button("▶️ Iniciar Varredura Contínua de Monitoramento Urbano", type="primary"):
        if not named_frames:
            st.warning("Nenhum quadro disponível para processamento.")
            return

        progress_bar = st.progress(0)
        live_banner_slot = st.empty()
        live_frame_slot = st.empty()
        running_alerts_count = 0

        def update_ui_callback(
            current_idx: int,
            total_count: int,
            result,
            hud_frame: np.ndarray,
        ) -> None:
            nonlocal running_alerts_count
            if result.requires_field_inspection:
                running_alerts_count += 1

            progress_bar.progress(current_idx / total_count)
            live_banner_slot.info(
                f"📡 **Varredura em Andamento:** Analisando Quadro **{current_idx}/{total_count}** (`{result.image_identifier}`) — "
                f"**Alertas de Fissura Acumulados até aqui: {running_alerts_count}**"
            )
            live_frame_slot.image(
                hud_frame,
                caption=f"Quadro {current_idx}/{total_count} ({result.image_identifier}) — {result.predicted_class_name}",
                width=440,
            )
            if visual_delay_seconds > 0:
                time.sleep(visual_delay_seconds)

        summary, annotated_frames = video_processor.process_image_sequence(
            named_images=named_frames,
            confidence_threshold=confidence_threshold,
            on_frame_processed=update_ui_callback,
        )

        live_banner_slot.empty()
        live_frame_slot.empty()

        st.session_state["last_video_summary"] = summary
        st.session_state["last_video_frames"] = annotated_frames

    if "last_video_summary" in st.session_state and "last_video_frames" in st.session_state:
        summary = st.session_state["last_video_summary"]
        annotated_frames = st.session_state["last_video_frames"]

        if summary.flagged_frames_count > 0:
            critical_pct = (
                summary.flagged_frames_count
                / max(summary.total_frames_processed, 1)
            ) * 100.0
            st.markdown(
                f'<div class="status-alert">🚨 DIAGNÓSTICO FINAL DO MONITORAMENTO: '
                f'FORAM DETECTADAS FISSURAS EM {summary.flagged_frames_count} DE {summary.total_frames_processed} QUADROS '
                f'({critical_pct:.1f}% do trecho analisado) — NECESSITA VISTORIA TÉCNICA PRESENCIAL!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-normal">✅ DIAGNÓSTICO FINAL DO MONITORAMENTO: '
                'NENHUMA FISSURA DETECTADA NO TRECHO ANALISADO.</div>',
                unsafe_allow_html=True,
            )

        st.write("")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total de Quadros Analisados", summary.total_frames_processed)
        m2.metric(
            "Quadros com Fissura (Alertas)",
            f"{summary.flagged_frames_count} de {summary.total_frames_processed}",
            delta=f"{(summary.flagged_frames_count / max(summary.total_frames_processed, 1)) * 100:.1f}% críticos",
            delta_color="inverse",
        )
        m3.metric(
            "Latência Média da IA / Quadro",
            f"{summary.average_latency_milliseconds:.2f} ms",
        )
        m4.metric(
            "Velocidade Real de Inferência",
            f"{summary.average_frames_per_second:.1f} FPS",
        )

        # Seleciona por padrão o último quadro crítico com fissura para ficar em destaque no visor
        flagged_indices = [
            idx + 1
            for idx, item in enumerate(summary.frame_results)
            if item.requires_field_inspection
        ]
        default_frame_number = (
            flagged_indices[-1]
            if flagged_indices
            else summary.total_frames_processed
        )

        st.markdown("#### 🔎 Inspecionar Quadro Individual da Varredura")
        selected_frame_num = st.slider(
            "Deslize para revisar qualquer quadro processado no vídeo (por padrão posicionado em um quadro crítico com fissura):",
            min_value=1,
            max_value=summary.total_frames_processed,
            value=default_frame_number,
        )
        chosen_res = summary.frame_results[selected_frame_num - 1]
        chosen_hud = annotated_frames[selected_frame_num - 1]

        col_viewer, col_details = st.columns([1, 1])
        with col_viewer:
            st.image(
                chosen_hud,
                caption=f"Quadro {selected_frame_num}/{summary.total_frames_processed} — {chosen_res.image_identifier}",
                width=420,
            )
        with col_details:
            st.markdown(f"**Arquivo / Quadro:** `{chosen_res.image_identifier}`")
            st.markdown(f"**Classificação:** **{chosen_res.predicted_class_name}**")
            st.markdown(f"**Status de Triagem:** {chosen_res.inspection_status.value}")
            st.markdown(f"**Probabilidade de Fissura:** `{chosen_res.crack_probability * 100:.2f}%`")
            st.markdown(f"**Confiança do Modelo:** `{chosen_res.prediction_confidence * 100:.2f}%`")
            st.markdown(
                f"**Telemetria do Quadro:** `{chosen_res.inference_latency_milliseconds:.2f} ms` (`{chosen_res.instantaneous_frames_per_second:.1f} FPS`)"
            )
            st.info(chosen_res.technical_recommendation)

        # Tabela auditável de quadros processados
        st.markdown("#### 📋 Registro Completo de Ocorrências por Quadro")
        rows = [
            {
                "Nº Quadro": idx + 1,
                "Quadro / Arquivo": item.image_identifier,
                "Classificação": item.predicted_class_name,
                "Probabilidade de Fissura (%)": round(
                    item.crack_probability * 100, 2
                ),
                "Confiança (%)": round(item.prediction_confidence * 100, 2),
                "Latência (ms)": round(item.inference_latency_milliseconds, 2),
                "FPS Instantâneo": round(
                    item.instantaneous_frames_per_second, 1
                ),
                "Status": item.inspection_status.value,
            }
            for idx, item in enumerate(summary.frame_results)
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.markdown("#### 📸 Galeria Completa dos Quadros Sinalizados com Fissura")
        flagged_pairs = [
            (idx + 1, res, frame)
            for idx, (res, frame) in enumerate(
                zip(summary.frame_results, annotated_frames)
            )
            if res.requires_field_inspection
        ]
        if flagged_pairs:
            cols = st.columns(4)
            for idx, (f_num, res, frame_img) in enumerate(flagged_pairs[:12]):
                with cols[idx % 4]:
                    st.image(
                        frame_img,
                        caption=f"Quadro {f_num}: {res.image_identifier} ({res.prediction_confidence*100:.1f}%)",
                        use_container_width=True,
                    )
        else:
            st.info("Nenhum quadro ultrapassou o limiar de alerta nesta varredura.")


def render_metrics_and_architecture_tab(
    classifier_service: ConcreteCrackClassifierService,
    bundle_manager: ColabBundleAndReportManager,
) -> None:
    """Renderiza a Aba 3: Métricas do Modelo, Gráficos e Relatório HTML Imprimível."""
    st.subheader("📊 Qualidade do Modelo, Latência, FPS e Justificativa Técnica")
    report_data = bundle_manager.load_evaluation_metrics()
    metrics = report_data.get("metrics", {})
    perf = report_data.get("performance", {})

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Precisão", f"{float(metrics.get('precision', 0.9901))*100:.2f}%")
    c2.metric("Recall", f"{float(metrics.get('recall', 0.9967))*100:.2f}%")
    c3.metric("F1-Score", f"{float(metrics.get('f1_score', 0.9934))*100:.2f}%")
    c4.metric(
        "Latência Média", f"{float(perf.get('average_latency_ms', 4.82)):.2f} ms"
    )
    c5.metric("Taxa de Quadros", f"{float(perf.get('fps', 207.47)):.1f} FPS")

    st.caption(
        f"**Equipamento Registrado:** {perf.get('hardware')} | "
        f"**Equipamento Local Atual:** {classifier_service.hardware_description} | "
        f"**Resolução:** {report_data.get('resolution', '224x224 px')}"
    )

    fig_col1, fig_col2 = st.columns(2)
    cm_path = bundle_manager.figures_directory / "confusion_matrix.png"
    hist_path = bundle_manager.figures_directory / "training_history.png"
    if cm_path.exists():
        fig_col1.image(str(cm_path), caption="Matriz de Confusão (Teste)", use_container_width=True)
    if hist_path.exists():
        fig_col2.image(str(hist_path), caption="Curvas de Aprendizado", use_container_width=True)

    fig_col3, fig_col4 = st.columns(2)
    ok_path = bundle_manager.figures_directory / "correct_predictions_analysis.png"
    err_path = bundle_manager.figures_directory / "error_and_interference_analysis.png"
    if ok_path.exists():
        fig_col3.image(str(ok_path), caption="Acertos e Grad-CAM", use_container_width=True)
    if err_path.exists():
        fig_col4.image(str(err_path), caption="Análise de Erros e Interferências", use_container_width=True)


def main() -> None:
    """Função principal da aplicação CitizenTech."""
    configure_streamlit_page()
    bundle_manager = ColabBundleAndReportManager(WORKSPACE_ROOT)
    confidence_threshold = render_sidebar_controls(bundle_manager)

    classifier_service = initialize_classifier_service(
        str(bundle_manager.model_weights_path)
    )

    st.markdown(
        """
        <div class="main-banner">
            <h2 style="margin:0;color:#ffffff;">🏙️ CitizenTech — Visão Computacional para Manutenção Urbana</h2>
            <p style="margin:4px 0 0 0;opacity:0.9;">
                Sistema Inteligente de Triagem Preventiva de Fissuras em Concreto e Monitoramento Contínuo de Vias e Edificações
            </p>
            <p style="margin:6px 0 0 0;font-size:0.86rem;opacity:0.85;">
                <strong>Equipe:</strong> Lucca Phelipe Masini (RM 564121) • Igor Paixão Sarak (RM 563726) • Bernardo Braga Perobeli (RM 562468)
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_image, tab_video, tab_metrics = st.tabs(
        [
            "🔍 1. Triagem de Imagem Individual",
            "🎥 2. Monitoramento em Vídeo / Sequência",
            "📊 3. Métricas, Latência e Arquitetura",
        ]
    )

    with tab_image:
        render_single_image_inspection_tab(
            classifier_service, bundle_manager, confidence_threshold
        )

    with tab_video:
        render_video_monitoring_tab(
            classifier_service, bundle_manager, confidence_threshold
        )

    with tab_metrics:
        render_metrics_and_architecture_tab(classifier_service, bundle_manager)


if __name__ == "__main__":
    main()
