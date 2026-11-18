"""Contratos de domínio imutáveis para o Hub de Governança em IA e Business Analytics."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ModuleGovernanceRecord:
    """Representa o diagnóstico arquitetural, analítico e de governança de uma disciplina."""

    module_id: str
    discipline_name: str
    project_title: str
    folder_name: str
    integration_status: str
    coupling_level: str
    primary_technology_stack: str
    main_metric_label: str
    main_metric_value: str
    secondary_metric_label: str
    secondary_metric_value: str
    lgpd_mechanism: str
    human_in_the_loop_mechanism: str
    hallucination_or_error_control: str
    sdg_goals: List[str]
    integration_justification: str
    known_limitations: str


@dataclass(frozen=True)
class KnapsackTaskItem:
    """Representa uma ocorrência urbana candidata à priorização combinatória."""

    task_code: str
    description: str
    priority_score: int
    estimated_hours: int
    category: str


@dataclass(frozen=True)
class OptimizationComparisonResult:
    """Resultado comparativo entre a heurística gulosa e a solução exata/quântica."""

    budget_hours: int
    greedy_selected_codes: List[str]
    greedy_total_priority: int
    greedy_total_hours: int
    optimal_selected_codes: List[str]
    optimal_total_priority: int
    optimal_total_hours: int
    priority_gain: int
    total_combinations_evaluated: int


@dataclass(frozen=True)
class SanitizationAuditResult:
    """Resultado auditável da camada de proteção de dados pessoais (LGPD)."""

    original_length: int
    sanitized_text: str
    masked_items_count: Dict[str, int]
    contains_residual_pii_warning: bool
