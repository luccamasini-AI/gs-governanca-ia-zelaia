"""
Contratos de domínio e estruturas de dados para o módulo de Visão Computacional
do protótipo CitizenTech (Manutenção Urbana).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class UrbanInspectionStatus(Enum):
    """Classificação semântica de triagem para apoio à manutenção urbana."""

    INSPECTION_REQUIRED = "Necessita Inspeção Técnica (Fissura Detectada)"
    NORMAL_CONDITION = "Condição Visual Normal (Sem Fissura Aparente)"


@dataclass(frozen=True)
class ModelInferenceConfiguration:
    """Configurações de pré-processamento e inferência do classificador."""

    input_image_width: int = 224
    input_image_height: int = 224
    confidence_threshold: float = 0.50
    imagenet_normalization_mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    imagenet_normalization_standard_deviation: tuple[float, float, float] = (
        0.229,
        0.224,
        0.225,
    )
    architecture_name: str = "MobileNetV3-Small (Transfer Learning - ImageNet1K)"


@dataclass(frozen=True)
class SingleImageInspectionResult:
    """Resultado completo da análise de uma imagem de superfície urbana."""

    image_identifier: str
    predicted_class_name: str
    inspection_status: UrbanInspectionStatus
    crack_probability: float
    prediction_confidence: float
    requires_field_inspection: bool
    inference_latency_milliseconds: float
    instantaneous_frames_per_second: float
    technical_recommendation: str


@dataclass(frozen=True)
class VideoMonitoringSummary:
    """Resumo consolidado do processamento contínuo de vídeo ou sequência de quadros."""

    total_frames_processed: int
    flagged_frames_count: int
    normal_frames_count: int
    average_latency_milliseconds: float
    average_frames_per_second: float
    peak_crack_probability: float
    hardware_description: str
    resolution_evaluated: str
    frame_results: List[SingleImageInspectionResult] = field(default_factory=list)


@dataclass(frozen=True)
class EvaluationMetricsReport:
    """Relatório consolidado das métricas de qualidade e desempenho do modelo."""

    accuracy_score: float
    precision_score: float
    recall_score: float
    f1_score: float
    roc_auc_score: float
    confusion_matrix_values: Dict[str, int]
    average_latency_milliseconds: float
    latency_standard_deviation_milliseconds: float
    frames_per_second: float
    hardware_environment: str
    image_resolution: str
    confidence_threshold_used: float
    total_training_samples: int
    total_validation_samples: int
    total_testing_samples: int
    additional_notes: Optional[str] = None
