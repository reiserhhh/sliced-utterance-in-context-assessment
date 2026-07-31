"""Target-aligned creation-law diagnostics for M4-C.3.4."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.special import expit

from .m4_chart_ecology_estimator import (
    _feedback_derivative,
    _fit_logistic,
    _flatten_events,
    _hazard_design,
    _hazard_logloss,
    _hazard_probability,
)
from .m4_creation_information import fisher_spectrum_from_design
from .m4_fisher_wiener_creation import (
    M4FixedHazardRoute,
    M4FixedHazardView,
    fisher_wiener_feedback,
    fit_fixed_hazard_route,
    split_opportunity_occasions,
)
from .m4_opportunity_contracts import (
    M4OpportunityObserved,
    M4OpportunityPanel,
)


@dataclass(frozen=True)
class M4CreationAttributionView:
    """One creation-law cell evaluated in an independent path view."""

    creation: np.ndarray
    evaluation_loss: np.ndarray
    comparable_hazard_loss: np.ndarray
    joint_information_minimum: np.ndarray
    joint_information_full_rank: np.ndarray
    source_at_risk_valid: np.ndarray


@dataclass(frozen=True)
class M4CreationAttributionRoute:
    """Train/test cell plus its observable source-routing declaration."""

    train: M4CreationAttributionView
    test: M4CreationAttributionView
    source_route_used: bool


@dataclass(frozen=True)
class M4CreationAttributionGrid:
    """Current/stratified x pooled/local target-aligned creation grid."""

    current_pooled: M4CreationAttributionRoute
    current_local: M4CreationAttributionRoute
    complete_pooled: M4CreationAttributionRoute
    complete_local: M4CreationAttributionRoute


@dataclass(frozen=True)
class _StratifiedView:
    coefficients: dict[str, np.ndarray]
    names: tuple[str, ...]
    creation: np.ndarray
    evaluation_loss: np.ndarray
    information_minimum: np.ndarray
    information_full_rank: np.ndarray
    source_valid: np.ndarray


@dataclass(frozen=True)
class _StratifiedRoute:
    train: _StratifiedView
    test: _StratifiedView
    source_route: bool


def dynamic_indices(
    names: tuple[str, ...],
    *,
    include_gate: bool,
) -> np.ndarray:
    """Return response-feedback columns, optionally including gate interactions."""
    prefixes = ("feedback_", "gate_") if include_gate else ("feedback_",)
    indices = np.asarray(
        [
            index
            for index, name in enumerate(names)
            if name.startswith(prefixes)
        ],
        dtype=int,
    )
    if len(indices) == 0:
        raise ValueError("hazard model has no requested dynamic block")
    return indices


def _binary_loss(probability: np.ndarray, target: np.ndarray) -> float:
    p = np.clip(np.asarray(probability, dtype=float), 1e-10, 1.0 - 1e-10)
    y = np.asarray(target, dtype=float)
    return -float(np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))


def _event_gate(rows: dict[str, np.ndarray]) -> np.ndarray:
    return rows["history"][:, 0] > 0.0


def _risk_target(rows: dict[str, np.ndarray]) -> np.ndarray:
    return np.logical_or(
        rows["external_next"],
        rows["generated_next"],
    )


def _source_partition_diagnostics(
    observed: M4OpportunityObserved,
    *,
    maximum_overlap_rate: float,
) -> tuple[bool, np.ndarray]:
    """Detect mutually exclusive, nondegenerate source-allocation data."""
    valid_by_author = []
    overlap_count = 0
    risk_count = 0
    for author in range(observed.train_calibration.menu.shape[0]):
        generated_values = []
        external_values = []
        gate_values = []
        for role in ("calibration", "selection"):
            rows = _flatten_events(
                getattr(observed, f"train_{role}"),
                author,
            )
            generated_values.append(rows["generated_next"].reshape(-1))
            external_values.append(rows["external_next"].reshape(-1))
            gate_values.append(
                np.repeat(
                    _event_gate(rows),
                    rows["generated_next"].shape[1],
                )
            )
        generated = np.concatenate(generated_values).astype(bool)
        external = np.concatenate(external_values).astype(bool)
        gate = np.concatenate(gate_values)
        risk = np.logical_or(generated, external)
        overlap_count += int(np.sum(generated & external))
        risk_count += int(np.sum(risk))
        gate0_risk = risk & ~gate
        gate0_generated = generated[gate0_risk]
        gate0_risk_target = risk[~gate]
        valid_by_author.append(
            len(gate0_generated) >= 32
            and np.any(gate0_generated)
            and np.any(~gate0_generated)
            and len(gate0_risk_target) >= 32
            and np.any(gate0_risk_target)
            and np.any(~gate0_risk_target)
        )
    overlap_rate = overlap_count / max(risk_count, 1)
    valid = np.asarray(valid_by_author, dtype=bool)
    return (
        overlap_rate <= maximum_overlap_rate
        and float(np.mean(valid)) >= 0.80,
        valid,
    )


def _block_definitions(
    source_route: bool,
) -> tuple[tuple[str, str, int, bool], ...]:
    if source_route:
        return (
            ("risk_g0", "risk", 0, False),
            ("risk_g1", "risk", 1, False),
            ("allocation_g0", "generated", 0, True),
            ("allocation_g1", "generated", 1, True),
        )
    return (
        ("generated_g0", "generated", 0, False),
        ("generated_g1", "generated", 1, False),
    )


def _block_arrays(
    rows: dict[str, np.ndarray],
    basis: np.ndarray,
    *,
    target_name: str,
    gate_value: int,
    at_risk: bool,
) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    design, names = _hazard_design(rows, basis, model="feedback")
    categories = rows["generated_next"].shape[1]
    gate = np.repeat(_event_gate(rows), categories)
    mask = gate == bool(gate_value)
    risk = _risk_target(rows).reshape(-1)
    if at_risk:
        mask &= risk
    target = (
        risk.astype(float)
        if target_name == "risk"
        else rows["generated_next"].reshape(-1).astype(float)
    )
    return design[mask], target[mask], names


def _fit_stratified_view(
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    evaluation: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    *,
    source_route: bool,
    ridge: float,
    iterations: int,
) -> _StratifiedView:
    definitions = _block_definitions(source_route)
    fitted: dict[str, list[np.ndarray]] = {
        name: [] for name, _, _, _ in definitions
    }
    valid_by_block: dict[str, list[bool]] = {
        name: [] for name, _, _, _ in definitions
    }
    names: tuple[str, ...] | None = None
    for author in range(calibration.menu.shape[0]):
        for block, target_name, gate_value, at_risk in definitions:
            designs = []
            targets = []
            for panel, role in (
                (calibration, "calibration"),
                (selection, "selection"),
            ):
                rows = _flatten_events(panel, author)
                design, target, current_names = _block_arrays(
                    rows,
                    basis[role],
                    target_name=target_name,
                    gate_value=gate_value,
                    at_risk=at_risk,
                )
                designs.append(design)
                targets.append(target)
                names = current_names
            target = np.concatenate(targets)
            valid_by_block[block].append(
                len(target) >= 32
                and np.any(target > 0.5)
                and np.any(target < 0.5)
            )
            fitted[block].append(
                _fit_logistic(
                    np.vstack(designs),
                    target,
                    ridge=ridge,
                    iterations=iterations,
                )
            )
    coefficients = {
        block: np.stack(values)
        for block, values in fitted.items()
    }
    valid = {
        block: np.asarray(values, dtype=bool)
        for block, values in valid_by_block.items()
    }
    return _assemble_stratified_view(
        coefficients,
        names or (),
        valid,
        calibration,
        selection,
        evaluation,
        basis,
        source_route=source_route,
    )


def _fit_stratified_route(
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    *,
    source_route: bool,
    ridge: float,
    iterations: int,
) -> _StratifiedRoute:
    parameters = {
        "source_route": source_route,
        "ridge": ridge,
        "iterations": iterations,
    }
    return _StratifiedRoute(
        train=_fit_stratified_view(
            observed.train_calibration,
            observed.train_selection,
            observed.train_evaluation,
            basis,
            **parameters,
        ),
        test=_fit_stratified_view(
            observed.test_calibration,
            observed.test_selection,
            observed.test_evaluation,
            basis,
            **parameters,
        ),
        source_route=source_route,
    )


def _block_probability(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis: np.ndarray,
    rows: dict[str, np.ndarray],
) -> np.ndarray:
    design, _ = _hazard_design(rows, basis, model="feedback")
    return expit(np.clip(design @ coefficient, -20.0, 20.0))


def _stratified_evaluation_loss(
    coefficients: dict[str, np.ndarray],
    names: tuple[str, ...],
    evaluation: M4OpportunityPanel,
    basis: np.ndarray,
    *,
    source_route: bool,
) -> np.ndarray:
    losses = []
    for author in range(evaluation.menu.shape[0]):
        rows = _flatten_events(evaluation, author)
        categories = rows["generated_next"].shape[1]
        gate = np.repeat(_event_gate(rows), categories)
        if source_route:
            risk0 = _block_probability(
                coefficients["risk_g0"][author],
                names,
                basis,
                rows,
            )
            risk1 = _block_probability(
                coefficients["risk_g1"][author],
                names,
                basis,
                rows,
            )
            allocation0 = _block_probability(
                coefficients["allocation_g0"][author],
                names,
                basis,
                rows,
            )
            allocation1 = _block_probability(
                coefficients["allocation_g1"][author],
                names,
                basis,
                rows,
            )
            probability = np.where(gate, risk1 * allocation1, risk0 * allocation0)
        else:
            probability0 = _block_probability(
                coefficients["generated_g0"][author],
                names,
                basis,
                rows,
            )
            probability1 = _block_probability(
                coefficients["generated_g1"][author],
                names,
                basis,
                rows,
            )
            probability = np.where(gate, probability1, probability0)
        losses.append(
            _binary_loss(
                probability,
                rows["generated_next"].reshape(-1),
            )
        )
    return np.asarray(losses, dtype=float)


def _baseline_probability(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis: np.ndarray,
    dimensions: int,
) -> np.ndarray:
    return _hazard_probability(
        coefficient,
        names,
        basis,
        np.zeros((1, dimensions)),
        np.zeros(1),
    )[0]


def _stratified_creation(
    coefficients: dict[str, np.ndarray],
    names: tuple[str, ...],
    evaluation_basis: np.ndarray,
    dimensions: int,
    *,
    source_route: bool,
) -> np.ndarray:
    output = []
    authors = len(next(iter(coefficients.values())))
    for author in range(authors):
        if not source_route:
            output.append(
                _feedback_derivative(
                    coefficients["generated_g0"][author],
                    names,
                    evaluation_basis,
                    dimensions,
                )
            )
            continue
        risk_coefficient = coefficients["risk_g0"][author]
        allocation_coefficient = coefficients["allocation_g0"][author]
        risk_probability = _baseline_probability(
            risk_coefficient,
            names,
            evaluation_basis,
            dimensions,
        )
        allocation_probability = _baseline_probability(
            allocation_coefficient,
            names,
            evaluation_basis,
            dimensions,
        )
        risk_derivative = _feedback_derivative(
            risk_coefficient,
            names,
            evaluation_basis,
            dimensions,
        )
        allocation_derivative = _feedback_derivative(
            allocation_coefficient,
            names,
            evaluation_basis,
            dimensions,
        )
        output.append(
            allocation_probability[:, None] * risk_derivative
            + risk_probability[:, None] * allocation_derivative
        )
    return np.stack(output)


def _block_information(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    datasets: tuple[
        tuple[dict[str, np.ndarray], np.ndarray],
        ...,
    ],
    *,
    target_name: str,
    gate_value: int,
    at_risk: bool,
) -> tuple[float, bool]:
    designs = []
    for rows, basis in datasets:
        design, _, _ = _block_arrays(
            rows,
            basis,
            target_name=target_name,
            gate_value=gate_value,
            at_risk=at_risk,
        )
        designs.append(design)
    matrix = np.vstack(designs)
    columns = dynamic_indices(names, include_gate=False)
    spectrum = fisher_spectrum_from_design(
        matrix,
        coefficient,
        columns,
    )
    probability = expit(np.clip(matrix @ coefficient, -20.0, 20.0))
    weight = np.clip(probability * (1.0 - probability), 1e-12, None)
    dynamic = matrix[:, columns]
    information = dynamic.T @ (weight[:, None] * dynamic)
    eigenvalues = np.linalg.eigvalsh(0.5 * (information + information.T))
    maximum = max(float(np.max(eigenvalues)), 1e-12)
    rank = int(np.sum(eigenvalues > 1e-10 * maximum))
    return float(spectrum[0]), rank == len(columns)


def _stratified_information(
    coefficients: dict[str, np.ndarray],
    names: tuple[str, ...],
    valid: dict[str, np.ndarray],
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    *,
    source_route: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    definitions = _block_definitions(source_route)
    minimum = []
    full_rank = []
    source_valid = []
    for author in range(calibration.menu.shape[0]):
        datasets = (
            (_flatten_events(calibration, author), basis["calibration"]),
            (_flatten_events(selection, author), basis["selection"]),
        )
        block_results = []
        for block, target_name, gate_value, at_risk in definitions:
            block_results.append(
                _block_information(
                    coefficients[block][author],
                    names,
                    datasets,
                    target_name=target_name,
                    gate_value=gate_value,
                    at_risk=at_risk,
                )
            )
        minimum.append(min(value[0] for value in block_results))
        full_rank.append(all(value[1] for value in block_results))
        if source_route:
            source_valid.append(
                bool(valid["risk_g0"][author])
                and bool(valid["allocation_g0"][author])
            )
        else:
            source_valid.append(True)
    return (
        np.asarray(minimum, dtype=float),
        np.asarray(full_rank, dtype=bool),
        np.asarray(source_valid, dtype=bool),
    )


def _assemble_stratified_view(
    coefficients: dict[str, np.ndarray],
    names: tuple[str, ...],
    valid: dict[str, np.ndarray],
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    evaluation: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    *,
    source_route: bool,
) -> _StratifiedView:
    minimum, full_rank, source_valid = _stratified_information(
        coefficients,
        names,
        valid,
        calibration,
        selection,
        basis,
        source_route=source_route,
    )
    return _StratifiedView(
        coefficients=coefficients,
        names=names,
        creation=_stratified_creation(
            coefficients,
            names,
            basis["evaluation"],
            calibration.response.shape[-1],
            source_route=source_route,
        ),
        evaluation_loss=_stratified_evaluation_loss(
            coefficients,
            names,
            evaluation,
            basis["evaluation"],
            source_route=source_route,
        ),
        information_minimum=minimum,
        information_full_rank=full_rank,
        source_valid=source_valid,
    )


def _pool_stratified_route(
    full: _StratifiedRoute,
    first: _StratifiedRoute,
    second: _StratifiedRoute,
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    *,
    epsilon_scale: float,
    second_permutation: np.ndarray | None,
) -> _StratifiedRoute:
    primary_blocks = (
        ("risk_g0", "allocation_g0")
        if full.source_route
        else ("generated_g0",)
    )
    indices = dynamic_indices(full.train.names, include_gate=False)
    views: dict[str, _StratifiedView] = {}
    for view_name in ("train", "test"):
        current = getattr(full, view_name)
        coefficients = {
            name: values.copy()
            for name, values in current.coefficients.items()
        }
        for block in primary_blocks:
            coefficients[block][:, indices] = fisher_wiener_feedback(
                first.train.coefficients[block][:, indices],
                second.train.coefficients[block][:, indices],
                current.coefficients[block][:, indices],
                epsilon_scale=epsilon_scale,
                second_permutation=second_permutation,
            )
        calibration = getattr(observed, f"{view_name}_calibration")
        selection = getattr(observed, f"{view_name}_selection")
        evaluation = getattr(observed, f"{view_name}_evaluation")
        valid = {
            block: np.ones(len(values), dtype=bool)
            for block, values in coefficients.items()
        }
        if full.source_route:
            valid["risk_g0"] = current.source_valid.copy()
            valid["allocation_g0"] = current.source_valid.copy()
        views[view_name] = _assemble_stratified_view(
            coefficients,
            current.names,
            valid,
            calibration,
            selection,
            evaluation,
            basis,
            source_route=full.source_route,
        )
    return _StratifiedRoute(
        train=views["train"],
        test=views["test"],
        source_route=full.source_route,
    )


def _replace_dynamic(
    full: M4FixedHazardRoute,
    first: M4FixedHazardRoute,
    second: M4FixedHazardRoute,
    *,
    epsilon_scale: float,
    second_permutation: np.ndarray | None,
) -> M4FixedHazardRoute:
    indices = dynamic_indices(full.train.names, include_gate=False)
    views: dict[str, M4FixedHazardView] = {}
    for view_name in ("train", "test"):
        current = getattr(full, view_name)
        coefficients = current.coefficient.copy()
        coefficients[:, indices] = fisher_wiener_feedback(
            first.train.coefficient[:, indices],
            second.train.coefficient[:, indices],
            current.coefficient[:, indices],
            epsilon_scale=epsilon_scale,
            second_permutation=second_permutation,
        )
        views[view_name] = M4FixedHazardView(
            coefficient=coefficients,
            names=current.names,
            creation=current.creation,
            evaluation_loss=current.evaluation_loss,
        )
    return M4FixedHazardRoute(
        model=full.model,
        train=views["train"],
        test=views["test"],
    )


def _current_information(
    coefficients: np.ndarray,
    names: tuple[str, ...],
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    columns = dynamic_indices(names, include_gate=True)
    minimum = []
    full_rank = []
    for author, coefficient in enumerate(coefficients):
        designs = []
        for panel, role in (
            (calibration, "calibration"),
            (selection, "selection"),
        ):
            rows = _flatten_events(panel, author)
            design, _ = _hazard_design(
                rows,
                basis[role],
                model="gate",
            )
            designs.append(design)
        matrix = np.vstack(designs)
        spectrum = fisher_spectrum_from_design(
            matrix,
            coefficient,
            columns,
        )
        probability = expit(np.clip(matrix @ coefficient, -20.0, 20.0))
        weight = np.clip(probability * (1.0 - probability), 1e-12, None)
        dynamic = matrix[:, columns]
        information = dynamic.T @ (weight[:, None] * dynamic)
        eigenvalues = np.linalg.eigvalsh(
            0.5 * (information + information.T)
        )
        maximum = max(float(np.max(eigenvalues)), 1e-12)
        rank = int(np.sum(eigenvalues > 1e-10 * maximum))
        minimum.append(spectrum[0])
        full_rank.append(rank == len(columns))
    return np.asarray(minimum), np.asarray(full_rank, dtype=bool)


def _current_attribution_route(
    route: M4FixedHazardRoute,
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
) -> M4CreationAttributionRoute:
    views: dict[str, M4CreationAttributionView] = {}
    for view_name in ("train", "test"):
        current = getattr(route, view_name)
        calibration = getattr(observed, f"{view_name}_calibration")
        selection = getattr(observed, f"{view_name}_selection")
        evaluation = getattr(observed, f"{view_name}_evaluation")
        creation = np.stack([
            _feedback_derivative(
                coefficient,
                current.names,
                basis["evaluation"],
                evaluation.response.shape[-1],
            )
            for coefficient in current.coefficient
        ])
        losses = []
        for author, coefficient in enumerate(current.coefficient):
            rows = _flatten_events(evaluation, author)
            design, _ = _hazard_design(
                rows,
                basis["evaluation"],
                model="gate",
            )
            losses.append(
                _hazard_logloss(
                    coefficient,
                    design,
                    rows["generated_next"],
                )
            )
        minimum, full_rank = _current_information(
            current.coefficient,
            current.names,
            calibration,
            selection,
            basis,
        )
        loss = np.asarray(losses, dtype=float)
        views[view_name] = M4CreationAttributionView(
            creation=creation,
            evaluation_loss=loss,
            comparable_hazard_loss=loss,
            joint_information_minimum=minimum,
            joint_information_full_rank=full_rank,
            source_at_risk_valid=np.ones(len(loss), dtype=bool),
        )
    return M4CreationAttributionRoute(
        train=views["train"],
        test=views["test"],
        source_route_used=False,
    )


def _stratified_attribution_route(
    route: _StratifiedRoute,
) -> M4CreationAttributionRoute:
    def convert(view: _StratifiedView) -> M4CreationAttributionView:
        return M4CreationAttributionView(
            creation=view.creation,
            evaluation_loss=view.evaluation_loss,
            comparable_hazard_loss=view.evaluation_loss,
            joint_information_minimum=view.information_minimum,
            joint_information_full_rank=view.information_full_rank,
            source_at_risk_valid=view.source_valid,
        )

    return M4CreationAttributionRoute(
        train=convert(route.train),
        test=convert(route.test),
        source_route_used=route.source_route,
    )


def build_creation_attribution_grid(
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    *,
    model: str = "gate",
    ridge: float = 0.005,
    iterations: int = 30,
    epsilon_scale: float = 1e-6,
    maximum_source_overlap_rate: float = 0.01,
    second_permutation: np.ndarray | None = None,
) -> M4CreationAttributionGrid:
    """Fit a target-aligned current/stratified x pooled/local grid."""
    direct_parameters: dict[str, Any] = {
        "model": model,
        "ridge": ridge,
        "iterations": iterations,
    }
    direct_full = fit_fixed_hazard_route(
        observed,
        basis,
        **direct_parameters,
    )
    first_observed, second_observed = split_opportunity_occasions(observed)
    direct_first = fit_fixed_hazard_route(
        first_observed,
        basis,
        **direct_parameters,
    )
    direct_second = fit_fixed_hazard_route(
        second_observed,
        basis,
        **direct_parameters,
    )
    direct_pooled = _replace_dynamic(
        direct_full,
        direct_first,
        direct_second,
        epsilon_scale=epsilon_scale,
        second_permutation=second_permutation,
    )

    source_route, _ = _source_partition_diagnostics(
        observed,
        maximum_overlap_rate=maximum_source_overlap_rate,
    )
    stratified_parameters = {
        "source_route": source_route,
        "ridge": ridge,
        "iterations": iterations,
    }
    stratified_full = _fit_stratified_route(
        observed,
        basis,
        **stratified_parameters,
    )
    stratified_first = _fit_stratified_route(
        first_observed,
        basis,
        **stratified_parameters,
    )
    stratified_second = _fit_stratified_route(
        second_observed,
        basis,
        **stratified_parameters,
    )
    stratified_pooled = _pool_stratified_route(
        stratified_full,
        stratified_first,
        stratified_second,
        observed,
        basis,
        epsilon_scale=epsilon_scale,
        second_permutation=second_permutation,
    )
    return M4CreationAttributionGrid(
        current_pooled=_current_attribution_route(
            direct_pooled,
            observed,
            basis,
        ),
        current_local=_current_attribution_route(
            direct_full,
            observed,
            basis,
        ),
        complete_pooled=_stratified_attribution_route(
            stratified_pooled,
        ),
        complete_local=_stratified_attribution_route(
            stratified_full,
        ),
    )


def mobius_effects(values: dict[tuple[int, int, int], float]) -> dict[str, float]:
    """Return all nonempty Möbius effects for a complete binary cube."""
    expected = {
        (c, s, p)
        for c in (0, 1)
        for s in (0, 1)
        for p in (0, 1)
    }
    if set(values) != expected:
        raise ValueError("Möbius decomposition requires all eight cells")
    labels = ("C", "S", "P")
    effects: dict[str, float] = {}
    for mask in range(1, 8):
        subset = tuple(index for index in range(3) if mask & (1 << index))
        total = 0.0
        for submask in range(mask + 1):
            if submask & ~mask:
                continue
            bits = tuple(
                int(bool(submask & (1 << index)))
                for index in range(3)
            )
            total += (
                (-1.0) ** (len(subset) - sum(bits))
                * values[bits]
            )
        effects["".join(labels[index] for index in subset)] = float(total)
    return effects


def shapley_effects(values: dict[tuple[int, int, int], float]) -> dict[str, float]:
    """Allocate the 000-to-111 geometry change across three factors."""
    expected = {
        (c, s, p)
        for c in (0, 1)
        for s in (0, 1)
        for p in (0, 1)
    }
    if set(values) != expected:
        raise ValueError("Shapley decomposition requires all eight cells")
    labels = ("C", "S", "P")
    output: dict[str, float] = {}
    for factor in range(3):
        total = 0.0
        others = [index for index in range(3) if index != factor]
        for mask in range(4):
            subset = [
                others[index]
                for index in range(2)
                if mask & (1 << index)
            ]
            size = len(subset)
            weight = (1.0 / 3.0) if size in {0, 2} else (1.0 / 6.0)
            low = [0, 0, 0]
            for index in subset:
                low[index] = 1
            high = low.copy()
            high[factor] = 1
            total += weight * (
                values[tuple(high)] - values[tuple(low)]
            )
        output[labels[factor]] = float(total)
    return output
