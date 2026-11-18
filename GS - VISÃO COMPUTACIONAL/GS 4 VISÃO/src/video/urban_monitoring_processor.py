"""
Processador de vídeo curto e sequência de imagens para simulação de
monitoramento urbano contínuo no protótipo CitizenTech.
"""

from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

import cv2
import numpy as np
from PIL import Image

from src.domain.inspection_contracts import (
    SingleImageInspectionResult,
    VideoMonitoringSummary,
)
from src.inference.crack_classifier_service import ConcreteCrackClassifierService


class UrbanMonitoringVideoProcessor:
    """
    Orquestra a análise quadro a quadro de vídeos ou sequências de imagens
    de vias e edificações, consolidando métricas de FPS, latência e alertas,
    além de destacar visualmente a região da fissura em cada quadro crítico.
    """

    def __init__(self, classifier_service: ConcreteCrackClassifierService) -> None:
        self._classifier_service = classifier_service

    def process_image_sequence(
        self,
        named_images: Sequence[Tuple[str, Image.Image]],
        confidence_threshold: float = 0.50,
        on_frame_processed: Optional[
            Callable[[int, int, SingleImageInspectionResult, np.ndarray], None]
        ] = None,
    ) -> Tuple[VideoMonitoringSummary, List[np.ndarray]]:
        """
        Processa uma sequência ordenada de imagens simulando uma varredura
        urbana contínua e retorna o sumário estatístico junto aos quadros anotados.
        """
        if not named_images:
            raise ValueError(
                "A sequência de imagens para monitoramento não pode estar vazia."
            )

        frame_results: List[SingleImageInspectionResult] = []
        annotated_frames: List[np.ndarray] = []
        total_frames = len(named_images)

        for index, (frame_name, pil_image) in enumerate(named_images):
            inspection_result = self._classifier_service.inspect_surface_image(
                pil_image=pil_image,
                image_identifier=frame_name,
                custom_confidence_threshold=confidence_threshold,
            )
            frame_results.append(inspection_result)

            hud_frame = self._render_monitoring_hud_frame(
                pil_image=pil_image,
                inspection_result=inspection_result,
                frame_number=index + 1,
                total_frames=total_frames,
            )
            annotated_frames.append(hud_frame)

            if on_frame_processed is not None:
                on_frame_processed(
                    index + 1, total_frames, inspection_result, hud_frame
                )

        summary = self._compile_monitoring_summary(frame_results)
        return summary, annotated_frames

    def extract_frames_from_video_file(
        self,
        video_file_path: Path,
        frame_sampling_step: int = 6,
        maximum_frames_limit: int = 40,
    ) -> List[Tuple[str, Image.Image]]:
        """
        Extrai quadros representativos de um arquivo de vídeo (.mp4, .avi, .mov)
        para inspeção automatizada.
        """
        if not video_file_path.exists():
            raise FileNotFoundError(
                f"Arquivo de vídeo não encontrado: {video_file_path}"
            )
        if frame_sampling_step < 1:
            raise ValueError("O passo de amostragem de quadros deve ser >= 1.")

        video_capture = cv2.VideoCapture(str(video_file_path))
        if not video_capture.isOpened():
            raise RuntimeError(
                f"Não foi possível abrir o arquivo de vídeo: {video_file_path}"
            )

        extracted_frames: List[Tuple[str, Image.Image]] = []
        current_frame_index = 0

        try:
            while len(extracted_frames) < maximum_frames_limit:
                has_frame, frame_bgr = video_capture.read()
                if not has_frame:
                    break

                if current_frame_index % frame_sampling_step == 0:
                    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                    pil_frame = Image.fromarray(frame_rgb)
                    frame_identifier = f"frame_{current_frame_index:04d}.jpg"
                    extracted_frames.append((frame_identifier, pil_frame))

                current_frame_index += 1
        finally:
            video_capture.release()

        return extracted_frames

    def _compile_monitoring_summary(
        self, frame_results: Sequence[SingleImageInspectionResult]
    ) -> VideoMonitoringSummary:
        """Calcula estatísticas agregadas de latência, FPS e ocorrências sinalizadas."""
        total_processed = len(frame_results)
        flagged_count = sum(
            1 for item in frame_results if item.requires_field_inspection
        )
        normal_count = total_processed - flagged_count

        latencies = [item.inference_latency_milliseconds for item in frame_results]
        average_latency_ms = float(np.mean(latencies)) if latencies else 0.0
        average_fps = 1000.0 / average_latency_ms if average_latency_ms > 0 else 0.0
        peak_probability = (
            max(item.crack_probability for item in frame_results)
            if frame_results
            else 0.0
        )

        return VideoMonitoringSummary(
            total_frames_processed=total_processed,
            flagged_frames_count=flagged_count,
            normal_frames_count=normal_count,
            average_latency_milliseconds=average_latency_ms,
            average_frames_per_second=average_fps,
            peak_crack_probability=peak_probability,
            hardware_description=self._classifier_service.hardware_description,
            resolution_evaluated="224x224 px",
            frame_results=list(frame_results),
        )

    def _render_monitoring_hud_frame(
        self,
        pil_image: Image.Image,
        inspection_result: SingleImageInspectionResult,
        frame_number: int,
        total_frames: int,
    ) -> np.ndarray:
        """
        Renderiza um painel visual (HUD) sobre o quadro de vídeo com o status
        de manutenção, caixa delimitadora da fissura (quando detectada),
        confiança do modelo e telemetria de FPS/latência.
        """
        if inspection_result.requires_field_inspection:
            _gradcam_img, annotated_base = (
                self._classifier_service.generate_visual_inspection_overlay(
                    pil_image=pil_image,
                    inspection_result=inspection_result,
                )
            )
            base_pil = Image.fromarray(annotated_base)
        else:
            base_pil = pil_image.convert("RGB")

        resized_rgb = np.array(base_pil.resize((420, 420)))
        canvas = resized_rgb.copy()

        banner_color = (
            (220, 38, 38)
            if inspection_result.requires_field_inspection
            else (22, 163, 74)
        )
        status_headline = (
            "ALERTA: INSPECIONAR FISSURA"
            if inspection_result.requires_field_inspection
            else "NORMAL: SEM DANO APARENTE"
        )

        cv2.rectangle(canvas, (0, 0), (420, 56), banner_color, -1)
        cv2.putText(
            canvas,
            status_headline,
            (12, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        confidence_pct = inspection_result.prediction_confidence * 100.0
        probability_pct = inspection_result.crack_probability * 100.0
        sub_headline = (
            f"Confianca: {confidence_pct:.1f}% | Prob. Fissura: {probability_pct:.1f}%"
        )
        cv2.putText(
            canvas,
            sub_headline,
            (12, 46),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.44,
            (245, 245, 245),
            1,
            cv2.LINE_AA,
        )

        cv2.rectangle(canvas, (0, 382), (420, 420), (15, 23, 42), -1)
        telemetry_text = (
            f"Quadro {frame_number}/{total_frames} | "
            f"Latencia: {inspection_result.inference_latency_milliseconds:.1f} ms | "
            f"FPS: {inspection_result.instantaneous_frames_per_second:.1f}"
        )
        cv2.putText(
            canvas,
            telemetry_text,
            (12, 405),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (226, 232, 240),
            1,
            cv2.LINE_AA,
        )

        return canvas
