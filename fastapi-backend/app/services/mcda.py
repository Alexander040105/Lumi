"""MCDA module for LUMI — AHP weight validation and PROMETHEE ranking.

Provides:
- AHP consistency check for user-defined weight matrices
- Score aggregation using weighted sum
- PROMETHEE II outranking for multi-criteria comparison
"""
from __future__ import annotations

import math
from typing import Any

from app.services.mcda_weights_service import get_weights


def ahp_consistency_ratio(matrix: list[list[float]]) -> dict[str, Any]:
    """Check AHP pairwise comparison matrix consistency.

    Args:
        matrix: NxN pairwise comparison matrix (Saaty scale 1-9)

    Returns:
        Dict with consistency_ratio, is_consistent, lambda_max, n
    """
    n = len(matrix)
    if n < 2:
        return {"consistency_ratio": 0.0, "is_consistent": True, "lambda_max": float(n), "n": n}

    # Calculate priority vector (eigenvector approximation)
    col_sums = [sum(matrix[i][j] for i in range(n)) for j in range(n)]
    normalized = [
        [matrix[i][j] / col_sums[j] if col_sums[j] > 0 else 0 for j in range(n)]
        for i in range(n)
    ]
    priority = [sum(normalized[i]) / n for i in range(n)]

    # Calculate lambda_max
    weighted_sums = [
        sum(matrix[i][j] * priority[j] for j in range(n))
        for i in range(n)
    ]
    lambda_max = sum(weighted_sums[i] / priority[i] for i in range(n) if priority[i] > 0) / n

    # Consistency index
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0

    # Random consistency index (Saaty)
    rci_table = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    rci = rci_table.get(n, 1.49)

    cr = ci / rci if rci > 0 else 0.0

    return {
        "consistency_ratio": round(cr, 4),
        "is_consistent": cr < 0.10,
        "lambda_max": round(lambda_max, 4),
        "consistency_index": round(ci, 4),
        "n": n,
        "priority_vector": [round(p, 4) for p in priority],
    }


def aggregate_score(
    criteria_scores: dict[str, float],
    weights: dict[str, float] | None = None,
    energy_type: str = "",
    client=None,
) -> dict[str, Any]:
    """Aggregate criteria scores into a single suitability score using weighted sum.

    Args:
        criteria_scores: Dict mapping criterion name to score (0-100)
        weights: Optional weight dict. If None, loads from DB/defaults.
        energy_type: Energy type for loading default weights
        client: Optional Supabase client

    Returns:
        Dict with aggregated_score, classification, weights_used, contributions
    """
    if weights is None:
        weights = get_weights(energy_type, client) if energy_type else {}

    if not weights:
        # Equal weights fallback
        keys = list(criteria_scores.keys())
        weights = {k: 1.0 / len(keys) for k in keys} if keys else {}

    # Normalize weights to sum to 1
    total_weight = sum(weights.values())
    if total_weight > 0:
        norm_weights = {k: v / total_weight for k, v in weights.items()}
    else:
        norm_weights = weights

    # Calculate weighted score
    contributions = {}
    weighted_sum = 0.0
    for criterion, score in criteria_scores.items():
        w = norm_weights.get(criterion, 0.0)
        contribution = score * w
        contributions[criterion] = round(contribution, 2)
        weighted_sum += contribution

    score = round(min(max(weighted_sum, 0), 100), 2)

    # Classification
    if score >= 81:
        classification = "Very High"
    elif score >= 61:
        classification = "High"
    elif score >= 41:
        classification = "Moderate"
    elif score >= 21:
        classification = "Low"
    else:
        classification = "Very Low"

    return {
        "aggregated_score": score,
        "classification": classification,
        "weights_used": norm_weights,
        "contributions": contributions,
    }


def promethee_ii(
    alternatives: list[dict[str, Any]],
    criteria: list[str],
    weights: dict[str, float],
    preference_thresholds: dict[str, float] | None = None,
    maximize: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """PROMETHEE II outranking method for multi-criteria comparison.

    Args:
        alternatives: List of dicts with criteria values
        criteria: List of criterion names
        weights: Criterion weights (will be normalized)
        preference_thresholds: Per-criterion preference threshold (q). Default: 10% of range.
        maximize: Dict of criterion -> True if higher is better. Default: all True.

    Returns:
        Dict with rankings, net_outranking_flows, positive_flows, negative_flows
    """
    n = len(alternatives)
    if n == 0:
        return {"rankings": [], "net_outranking_flows": [], "positive_flows": [], "negative_flows": []}

    # Defaults
    if maximize is None:
        maximize = {c: True for c in criteria}
    if preference_thresholds is None:
        preference_thresholds = {}
        for c in criteria:
            values = [a.get(c, 0) for a in alternatives]
            if values:
                preference_thresholds[c] = 0.1 * (max(values) - min(values))
            else:
                preference_thresholds[c] = 1.0

    # Normalize weights
    total_w = sum(weights.get(c, 0) for c in criteria)
    norm_w = {c: weights.get(c, 0) / total_w for c in criteria} if total_w > 0 else {c: 1.0 / len(criteria) for c in criteria}

    # Pairwise preference function (Type 5 — linear with indifference)
    def preference(a_val: float, b_val: float, criterion: str) -> float:
        diff = a_val - b_val if maximize.get(criterion, True) else b_val - a_val
        q = preference_thresholds.get(criterion, 1.0)
        if diff <= 0:
            return 0.0
        if diff <= q:
            return diff / q
        return 1.0

    # Calculate pairwise preference indices
    pi = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            total = 0.0
            for c in criteria:
                total += norm_w[c] * preference(alternatives[i].get(c, 0), alternatives[j].get(c, 0), c)
            pi[i][j] = total

    # Positive and negative outranking flows
    positive = [sum(pi[i]) / (n - 1) for i in range(n)]
    negative = [sum(pi[j][i]) / (n - 1) for j in range(n) for i in [i]]  # fix
    negative = [sum(pi[j][i] for j in range(n) if j != i) / (n - 1) for i in range(n)]

    # Net outranking flow
    net = [positive[i] - negative[i] for i in range(n)]

    # Rank alternatives
    ranked_indices = sorted(range(n), key=lambda i: net[i], reverse=True)

    rankings = []
    for rank, idx in enumerate(ranked_indices, 1):
        rankings.append({
            "rank": rank,
            "alternative_index": idx,
            "name": alternatives[idx].get("name", f"Option {idx+1}"),
            "net_flow": round(net[idx], 4),
            "positive_flow": round(positive[idx], 4),
            "negative_flow": round(negative[idx], 4),
        })

    return {
        "rankings": rankings,
        "net_outranking_flows": [round(x, 4) for x in net],
        "positive_flows": [round(x, 4) for x in positive],
        "negative_flows": [round(x, 4) for x in negative],
    }
