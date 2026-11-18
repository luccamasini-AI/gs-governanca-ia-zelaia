"""Motor de simulação de governança, dimensionamento de cluster e otimização combinatória."""

import re
from typing import Dict, List

from governanca_hub.domain_contracts import (
    KnapsackTaskItem,
    OptimizationComparisonResult,
    SanitizationAuditResult,
)

CPF_PATTERN = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b")


def sanitize_citizen_input_lgpd(raw_text: str) -> SanitizationAuditResult:
    """Aplica anonimização de dados pessoais sensíveis conforme diretrizes LGPD do ecossistema."""
    if not raw_text or not raw_text.strip():
        return SanitizationAuditResult(
            original_length=0,
            sanitized_text="",
            masked_items_count={"CPF": 0, "EMAIL": 0, "TELEFONE": 0},
            contains_residual_pii_warning=False,
        )

    cpf_matches = len(CPF_PATTERN.findall(raw_text))
    email_matches = len(EMAIL_PATTERN.findall(raw_text))
    phone_matches = len(PHONE_PATTERN.findall(raw_text))

    sanitized = CPF_PATTERN.sub("[CPF PROTEGIDO - LGPD]", raw_text)
    sanitized = EMAIL_PATTERN.sub("[EMAIL PROTEGIDO - LGPD]", sanitized)
    sanitized = PHONE_PATTERN.sub("[TELEFONE PROTEGIDO - LGPD]", sanitized)

    total_masked = cpf_matches + email_matches + phone_matches
    return SanitizationAuditResult(
        original_length=len(raw_text),
        sanitized_text=sanitized,
        masked_items_count={
            "CPF": cpf_matches,
            "EMAIL": email_matches,
            "TELEFONE": phone_matches,
        },
        contains_residual_pii_warning=(total_masked > 0),
    )


def simulate_ispd_cluster_scaling(task_count: int) -> Dict[str, float]:
    """Calcula o tempo simulado de processamento no cluster iSPD para 2 e 4 workers."""
    safe_task_count = max(1, min(task_count, 100000))
    scale_factor = safe_task_count / 1000.0

    # Calibrado exatamente sobre os resultados do iSPD 2.0 (1.000 tarefas = 500,019 s e 250,037 s)
    simulated_time_2_workers = 500.019000976563 * scale_factor
    simulated_time_4_workers = 250.037000976563 * scale_factor
    reduction_percentage = (
        (simulated_time_2_workers - simulated_time_4_workers)
        / simulated_time_2_workers
        * 100.0
    )

    return {
        "task_count": float(safe_task_count),
        "total_mflop": float(safe_task_count * 1000),
        "total_network_mbit": float(safe_task_count * 8),
        "time_2_workers_seconds": round(simulated_time_2_workers, 3),
        "time_4_workers_seconds": round(simulated_time_4_workers, 3),
        "time_saved_seconds": round(
            simulated_time_2_workers - simulated_time_4_workers, 3
        ),
        "reduction_percent": round(reduction_percentage, 4),
        "throughput_2_workers": round(safe_task_count / simulated_time_2_workers, 4),
        "throughput_4_workers": round(safe_task_count / simulated_time_4_workers, 4),
    }


def get_default_zelaia_dispatch_tasks() -> List[KnapsackTaskItem]:
    """Retorna as 5 ocorrências de referência do estudo de Computação Quântica do ZelaIA."""
    return [
        KnapsackTaskItem(
            task_code="A",
            description="Buraco em via principal",
            priority_score=8,
            estimated_hours=3,
            category="Pavimentação e Vias",
        ),
        KnapsackTaskItem(
            task_code="B",
            description="Vazamento de água",
            priority_score=9,
            estimated_hours=4,
            category="Saneamento e Drenagem",
        ),
        KnapsackTaskItem(
            task_code="C",
            description="Lâmpada queimada",
            priority_score=3,
            estimated_hours=1,
            category="Iluminação Pública",
        ),
        KnapsackTaskItem(
            task_code="D",
            description="Árvore caída",
            priority_score=7,
            estimated_hours=3,
            category="Manejo Arbóreo e Risco",
        ),
        KnapsackTaskItem(
            task_code="E",
            description="Entulho em calçada",
            priority_score=4,
            estimated_hours=2,
            category="Acessibilidade e Limpeza",
        ),
    ]


def compare_greedy_vs_optimal_dispatch(
    tasks: List[KnapsackTaskItem], budget_hours: int
) -> OptimizationComparisonResult:
    """Compara a heurística gulosa clássica (prioridade/hora) com a otimização combinatória exata."""
    if not tasks or budget_hours <= 0:
        return OptimizationComparisonResult(
            budget_hours=max(0, budget_hours),
            greedy_selected_codes=[],
            greedy_total_priority=0,
            greedy_total_hours=0,
            optimal_selected_codes=[],
            optimal_total_priority=0,
            optimal_total_hours=0,
            priority_gain=0,
            total_combinations_evaluated=1,
        )

    # 1. Heurística gulosa clássica: ordena por razão (prioridade / tempo) decrescente
    sorted_by_density = sorted(
        tasks,
        key=lambda item: (item.priority_score / item.estimated_hours, item.priority_score),
        reverse=True,
    )
    greedy_codes: List[str] = []
    greedy_priority = 0
    greedy_hours = 0
    for task in sorted_by_density:
        if greedy_hours + task.estimated_hours <= budget_hours:
            greedy_codes.append(task.task_code)
            greedy_priority += task.priority_score
            greedy_hours += task.estimated_hours

    # 2. Otimização combinatória exata / formulação binária QUBO (avalia as 2^N combinações)
    num_tasks = len(tasks)
    total_combinations = 1 << num_tasks
    best_priority = -1
    best_hours = 0
    best_codes: List[str] = []

    for bitmask in range(total_combinations):
        current_priority = 0
        current_hours = 0
        current_codes: List[str] = []
        for index in range(num_tasks):
            if (bitmask >> index) & 1:
                current_priority += tasks[index].priority_score
                current_hours += tasks[index].estimated_hours
                current_codes.append(tasks[index].task_code)

        if current_hours <= budget_hours:
            if current_priority > best_priority or (
                current_priority == best_priority and current_hours < best_hours
            ):
                best_priority = current_priority
                best_hours = current_hours
                best_codes = current_codes

    return OptimizationComparisonResult(
        budget_hours=budget_hours,
        greedy_selected_codes=greedy_codes,
        greedy_total_priority=greedy_priority,
        greedy_total_hours=greedy_hours,
        optimal_selected_codes=best_codes,
        optimal_total_priority=best_priority,
        optimal_total_hours=best_hours,
        priority_gain=best_priority - greedy_priority,
        total_combinations_evaluated=total_combinations,
    )
