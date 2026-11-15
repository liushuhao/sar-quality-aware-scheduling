"""Genetic Algorithm solver for SAR observation scheduling.

Evolves a population of schedules, using selection, crossover,
and mutation to maximize total weighted observations while
maintaining compatibility constraints.
"""

import random
import numpy as np
from typing import List, Tuple, Optional

from sar_sim.types import ObservationWindow, ScheduledObservation, SolverResult
from sar_sim.solver.csp import (
    CSPInstance,
    build_csp_instance,
    schedule_from_indices,
    compute_solution_score,
    validate_solution,
)


def random_individual(csp: CSPInstance) -> np.ndarray:
    """Generate a random individual (bitstring).

    Args:
        csp: the CSP instance

    Returns:
        boolean array of length n
    """
    n = len(csp.windows)
    individual = np.zeros(n, dtype=bool)

    for i in range(n):
        if random.random() < 0.3:  # ~30% chance initially selected
            # Check compatibility with already selected
            if all(
                not individual[j] or csp.compatibility[i, j]
                for j in range(i)
            ):
                individual[i] = True

    return individual


def fitness(csp: CSPInstance, individual: np.ndarray) -> float:
    """Compute fitness score.

    Rewards weight sum, penalizes incompatibility.

    Args:
        csp: CSP instance
        individual: boolean selection vector

    Returns:
        fitness score (higher = better)
    """
    selected = np.where(individual)[0]
    score = compute_solution_score(csp, list(selected))

    # Penalty for incompatible pairs
    penalty = 0.0
    for i in range(len(selected)):
        for j in range(i + 1, len(selected)):
            if not csp.compatibility[selected[i], selected[j]]:
                penalty += 1000.0  # Hard penalty

    return score - penalty


def tournament_select(
    population: List[np.ndarray],
    fitnesses: List[float],
    tournament_size: int = 3,
) -> np.ndarray:
    """Select an individual via tournament selection.

    Args:
        population: list of individuals
        fitnesses: fitness scores
        tournament_size: number of candidates per tournament

    Returns:
        selected individual (copy)
    """
    candidates = random.sample(range(len(population)), tournament_size)
    best_idx = max(candidates, key=lambda i: fitnesses[i])
    return population[best_idx].copy()


def crossover(
    parent1: np.ndarray,
    parent2: np.ndarray,
    csp: CSPInstance,
) -> Tuple[np.ndarray, np.ndarray]:
    """Single-point crossover with repair.

    After crossover, repair infeasible bits by dropping
    incompatible observations.

    Args:
        parent1, parent2: parent bitstrings
        csp: CSP instance

    Returns:
        (child1, child2)
    """
    n = len(parent1)
    point = random.randint(1, n - 1)

    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])

    return repair(child1, csp), repair(child2, csp)


def repair(individual: np.ndarray, csp: CSPInstance) -> np.ndarray:
    """Repair an individual by removing incompatible observations.

    Greedy repair: sort selected by weight, keep compatible ones.

    Args:
        individual: potentially infeasible bitstring
        csp: CSP instance

    Returns:
        repaired bitstring
    """
    selected = list(np.where(individual)[0])
    if len(selected) <= 1:
        return individual.copy()

    # Sort by weight descending
    selected.sort(key=lambda i: -csp.weights[i])

    kept = []
    for idx in selected:
        if all(csp.compatibility[idx, k] for k in kept):
            kept.append(idx)

    result = np.zeros(len(individual), dtype=bool)
    result[kept] = True
    return result


def mutate(individual: np.ndarray, csp: CSPInstance, rate: float = 0.05):
    """Mutate an individual by flipping bits, then repair.

    Args:
        individual: bitstring to mutate
        csp: CSP instance
        rate: per-bit mutation probability
    """
    n = len(individual)
    for i in range(n):
        if random.random() < rate:
            individual[i] = not individual[i]


def ga_solver(
    windows: List[ObservationWindow],
    targets: List,
    population_size: int = 50,
    generations: int = 100,
    mutation_rate: float = 0.05,
    elite_size: int = 2,
    seed: Optional[int] = None,
) -> SolverResult:
    """Genetic Algorithm solver.

    Args:
        windows: candidate observation windows
        targets: ground targets
        population_size: number of individuals
        generations: number of generations to evolve
        mutation_rate: per-bit mutation probability
        elite_size: number of best individuals preserved each gen
        seed: random seed for reproducibility

    Returns:
        SolverResult with best schedule found
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    csp = build_csp_instance(windows, targets)
    n = len(csp.windows)

    if n == 0:
        return SolverResult(schedule=(), score=0.0,
                            metadata={"solver": "ga", "generations": 0})

    # Initialize population
    population = [random_individual(csp) for _ in range(population_size)]
    fitnesses = [fitness(csp, ind) for ind in population]

    best_individual = population[0].copy()
    best_fitness = fitnesses[0]

    for gen in range(generations):
        new_population = []

        # Elitism: keep best individuals
        elite_indices = sorted(range(len(population)),
                               key=lambda i: -fitnesses[i])[:elite_size]
        for i in elite_indices:
            new_population.append(population[i].copy())

        # Fill rest with crossover + mutation
        while len(new_population) < population_size:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)
            c1, c2 = crossover(p1, p2, csp)

            mutate(c1, csp, mutation_rate)
            mutate(c2, csp, mutation_rate)

            c1 = repair(c1, csp)
            c2 = repair(c2, csp)

            new_population.append(c1)
            if len(new_population) < population_size:
                new_population.append(c2)

        population = new_population
        fitnesses = [fitness(csp, ind) for ind in population]

        # Track best
        gen_best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_individual = population[gen_best_idx].copy()
            best_fitness = fitnesses[gen_best_idx]

    # Build result
    selected_indices = list(np.where(best_individual)[0])
    schedule = schedule_from_indices(windows, selected_indices)
    score = compute_solution_score(csp, selected_indices)
    is_valid, _ = validate_solution(csp, selected_indices)

    return SolverResult(
        schedule=tuple(schedule),
        score=score,
        metadata={
            "solver": "ga",
            "generations": generations,
            "population_size": population_size,
            "n_selected": len(selected_indices),
            "n_total": n,
            "valid": is_valid,
            "best_fitness": best_fitness,
        },
    )
