#!/usr/bin/env python3
"""
Unified task per customer calculation logic
Ensures consistency between frontend and backend calculations
"""
import math
from typing import Dict, List, Tuple, Optional

# ------------------------
# Constants for advanced algorithm (moved from final_builder_parallel.py)
# ------------------------
PER_ELEM_EXPOSURES = 3     # minimum exposures per element
MIN_ACTIVE_PER_ROW = 2     # min actives per vignette
SAFETY_ROWS        = 3     # OLS safety above P
ABSENCE_RATIO      = 2.0   # 1.0 ≈ "absences ~ exposures"; 2.0 = "twice exposures", etc.
T_RATIO            = 1.50  # scale rows/respondent above minimal feasible T
CAPACITY_SLACK     = 1     # try to keep at least this many patterns un-used (avoid T==cap)

# ------------------------
# Helper functions for advanced algorithm (moved from final_builder_parallel.py)
# ------------------------
def params_main_effects(category_info: Dict[str, List[str]]) -> int:
    """Calculate main effects parameters for OLS identifiability."""
    C = len(category_info)
    M = sum(len(v) for v in category_info.values())
    return M - C + 1  # intercept + (n_c - 1) per category

def visible_capacity(category_info: Dict[str, List[str]],
                     min_active: int,
                     max_active: Optional[int] = None) -> int:
    """Absence-collapsed count of distinct row patterns with ≥ min_active actives,
       optionally capped at ≤ max_active actives per row."""
    cats = list(category_info.keys())
    m = [len(category_info[c]) for c in cats]
    C = len(m)
    coeff = [0]*(C+1); coeff[0] = 1
    for mi in m:
        nxt=[0]*(C+1)
        for k in range(C+1):
            if coeff[k]==0: continue
            nxt[k] += coeff[k]           # ABS choice
            if k+1<=C: nxt[k+1] += coeff[k]*mi  # choose an element
        coeff = nxt
    hi = C if max_active is None else min(max_active, C)
    lo = max(min_active, 0)
    if lo > hi:
        return 0
    return sum(coeff[k] for k in range(lo, hi+1))

def plan_T_E_auto(category_info: Dict[str, List[str]],
                  study_mode: str,
                  max_active_per_row: int | None) -> Tuple[int,int,Dict[str,int],float,int]:
    """
    Advanced algorithm for calculating optimal T (tasks per consumer) and E (exposures per element).
    
    Args:
        category_info: Dictionary mapping category names to element lists
        study_mode: "grid" or "layer"
        max_active_per_row: Maximum active categories per row (for grid studies)
    
    Returns:
        Tuple of (T, E, A_map, avg_k, A_min_used)
        - T: Tasks per consumer
        - E: Exposures per element
        - A_map: Absences per category
        - avg_k: Average active categories per row
        - A_min_used: Minimum absences used
    """
    cats = list(category_info.keys())
    q = {c: len(category_info[c]) for c in cats}
    C = len(cats)
    M = sum(q.values())
    P = params_main_effects(category_info)
    cap = visible_capacity(
        category_info,
        MIN_ACTIVE_PER_ROW,
        (max_active_per_row if study_mode == "grid" else None)
    )

    # Start from identifiability floor and scale by T_RATIO
    T = max(P + SAFETY_ROWS, 2)
    if T_RATIO and T_RATIO > 1.0:
        T = int(math.ceil(T * float(T_RATIO)))

    # Helper: maximum feasible E at a given T
    def E_upper_at_T(T_try: int) -> int:
        # For each category c: T - q[c]*E >= ceil(ABSENCE_RATIO * E)
        bound_ratio = min(int(math.floor(T_try / (q[c] + ABSENCE_RATIO))) for c in cats)
        # Per-row active cap: total 1s = M*E <= T * rowcap
        rowcap = (max_active_per_row if (study_mode == "grid" and max_active_per_row is not None) else C)
        bound_rowcap = int(math.floor(T_try * rowcap / M))
        return min(bound_ratio, bound_rowcap)

    slack = CAPACITY_SLACK
    while True:
        if T > max(cap - slack, 0):
            if T > cap:
                raise RuntimeError("Infeasible: T exceeds visible capacity. Add elements/categories or relax ABSENCE_RATIO/T_RATIO.")
            slack = 0
        E_up = E_upper_at_T(T)
        if E_up >= PER_ELEM_EXPOSURES:
            E = E_up
            break
        T += 1

    A_min_used = int(math.ceil(ABSENCE_RATIO * E))
    A_map = {c: T - q[c]*E for c in cats}  # by construction >= A_min_used
    avg_k = (M * E) / T
    return T, E, A_map, avg_k, A_min_used

# ------------------------
# Main calculation functions
# ------------------------
def calculate_tasks_per_consumer(
    total_elements: int,
    category_info: Optional[Dict[str, List[str]]] = None,
    study_mode: str = "grid",
    use_advanced_algorithm: bool = True
) -> int:
    """
    Calculate tasks per consumer using unified logic.
    
    Args:
        total_elements: Total number of elements across all categories
        category_info: Dictionary mapping category names to element lists
        study_mode: "grid" or "layer"
        use_advanced_algorithm: Whether to use the advanced algorithm or simple fallback
    
    Returns:
        Number of tasks per consumer
    """
    
    if total_elements < 4:
        return 8  # Minimum for valid studies
    
    if use_advanced_algorithm and category_info:
        try:
            # Use advanced algorithm (now local function)
            T, E, A_map, avg_k, A_min_used = plan_T_E_auto(
                category_info=category_info,
                study_mode=study_mode,
                max_active_per_row=min(4, len(category_info)) if study_mode == "grid" else None
            )
            
            print(f"DEBUG: Advanced algorithm calculated tasks_per_consumer: {T}")
            return T
            
        except Exception as e:
            print(f"DEBUG: Advanced algorithm failed ({e}), using fallback calculation")
            # Fall through to simple calculation
    
    # Simple fallback calculation
    return calculate_tasks_per_consumer_simple(total_elements)

def calculate_tasks_per_consumer_simple(total_elements: int) -> int:
    """
    Simple fallback calculation for tasks per consumer.
    This matches the JavaScript calculation exactly.
    
    Args:
        total_elements: Total number of elements
    
    Returns:
        Number of tasks per consumer
    """
    if total_elements < 4:
        return 8
    
    # Calculate K based on number of elements (same logic as JavaScript)
    if total_elements <= 8:
        K = 2
    elif total_elements <= 16:
        K = 3
    else:
        K = 4
    
    # Calculate maximum possible combinations
    max_combinations = math.comb(total_elements, K) if total_elements >= K else 0
    
    # Use half of maximum combinations, with dynamic cap based on study size
    if total_elements <= 16:
        max_cap = 24  # Small studies: cap at 24
    elif total_elements <= 32:
        max_cap = 48  # Medium studies: cap at 48
    elif total_elements <= 64:
        max_cap = 96  # Large studies: cap at 96
    else:
        max_cap = 120  # Very large studies: cap at 120
    
    tasks_per_consumer = min(max_cap, max(1, math.floor(max_combinations / 2)))
    
    print(f"DEBUG: Simple calculation - elements: {total_elements}, K: {K}, max_combinations: {max_combinations}, tasks_per_consumer: {tasks_per_consumer}")
    
    return tasks_per_consumer

def calculate_tasks_per_consumer_javascript(total_elements: int) -> int:
    """
    JavaScript-compatible calculation for frontend validation.
    This should match the JavaScript calculateCombination function exactly.
    
    Args:
        total_elements: Total number of elements
    
    Returns:
        Number of tasks per consumer
    """
    if total_elements < 4:
        return 8
    
    # Calculate K (same logic as JavaScript)
    if total_elements <= 8:
        K = 2
    elif total_elements <= 16:
        K = 3
    else:
        K = 4
    
    # Calculate combinations (JavaScript-compatible)
    def calculate_combination(n: int, k: int) -> int:
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
        
        result = 1
        for i in range(1, k + 1):
            result = result * (n - i + 1) // i
        return result
    
    max_combinations = calculate_combination(total_elements, K)
    
    # Use same dynamic cap as simple calculation
    if total_elements <= 16:
        max_cap = 24  # Small studies: cap at 24
    elif total_elements <= 32:
        max_cap = 48  # Medium studies: cap at 48
    elif total_elements <= 64:
        max_cap = 96  # Large studies: cap at 96
    else:
        max_cap = 120  # Very large studies: cap at 120
    
    tasks_per_consumer = min(max_cap, max(1, max_combinations // 2))
    
    print(f"DEBUG: JavaScript-compatible calculation - elements: {total_elements}, K: {K}, max_combinations: {max_combinations}, tasks_per_consumer: {tasks_per_consumer}")
    
    return tasks_per_consumer

def validate_calculation_consistency(total_elements: int, category_info: Optional[Dict[str, List[str]]] = None) -> Dict[str, int]:
    """
    Validate that all calculation methods give consistent results.
    
    Args:
        total_elements: Total number of elements
        category_info: Category information for advanced algorithm
    
    Returns:
        Dictionary with results from all calculation methods
    """
    results = {}
    
    # Simple calculation
    results['simple'] = calculate_tasks_per_consumer_simple(total_elements)
    
    # JavaScript-compatible calculation
    results['javascript'] = calculate_tasks_per_consumer_javascript(total_elements)
    
    # Advanced algorithm (if category_info provided)
    if category_info:
        try:
            results['advanced'] = calculate_tasks_per_consumer(
                total_elements, category_info, use_advanced_algorithm=True
            )
        except Exception as e:
            results['advanced'] = f"Error: {e}"
    
    return results
