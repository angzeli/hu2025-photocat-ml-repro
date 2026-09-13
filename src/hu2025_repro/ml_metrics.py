"""Deterministic metrics for already available predictions; no model fitting.

All values retain their caller-declared units. Ratios, angles and correlations
are dimensionless (angles are reported in degrees). Undefined statistics use
None, not a fabricated zero or non-standard JSON NaN. Rows need not be independent.
"""

import numpy as np


def _paired(actual, predicted, *, vectors=False):
    if np.iscomplexobj(actual) or np.iscomplexobj(predicted):
        raise ValueError("Metrics require real values")
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    if actual.shape != predicted.shape or actual.size == 0:
        raise ValueError("Matching nonempty arrays are required")
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Metrics require finite values")
    if vectors and (actual.ndim != 2 or actual.shape[1] != 3):
        raise ValueError("Vector metrics require shape (n, 3)")
    return (actual, predicted) if vectors else (actual.ravel(), predicted.ravel())


def _pearson(actual, predicted):
    if len(actual) < 2:
        return None
    x, y = actual - actual.mean(), predicted - predicted.mean()
    denominator = np.linalg.norm(x) * np.linalg.norm(y)
    return float(np.clip(np.dot(x, y) / denominator, -1, 1)) if denominator > 0 else None


def scalar_metrics(actual, predicted):
    """Return n, Pearson r, predictive R², MAE, RMSE and signed bias.

    Inputs must have identical, nonempty finite real shapes; multidimensional
    inputs are pooled. ``n`` then counts scalar values, not independent samples.
    Error is predicted minus actual. Predictive R² is 1-SSE/SST, not r²;
    it is None when actual variance is zero, including exact constant predictions.
    Pearson r is None with fewer than two values or either constant input.
    MAE, RMSE and bias retain input units.
    """
    actual, predicted = _paired(actual, predicted)
    error = predicted - actual
    centered = actual - actual.mean()
    sst = float(np.dot(centered, centered))
    return {
        "n": len(actual), "pearson_r": _pearson(actual, predicted),
        "r2": float(1 - np.dot(error, error) / sst) if sst > 0 else None,
        "mae": float(np.mean(abs(error))), "rmse": float(np.sqrt(np.mean(error ** 2))),
        "bias": float(np.mean(error)),
    }


def vector_metrics(actual, predicted, *, norm_threshold=1e-3):
    """Summarize magnitude, relative error and direction for (n,3) vectors.

    ``norm_threshold`` is a positive absolute norm in the input units, an
    explicit numerical choice. Relative errors require actual norm > threshold;
    angles additionally require predicted norm > threshold. No rows are removed
    from absolute-error summaries. Angles preserve the supplied vector signs.
    Secondary axis-angle summaries use min(theta,180-theta), without modifying
    source vectors or claiming recovery of an electronic-state phase convention.
    Undefined masked statistics are None; valid/excluded denominators are returned.
    """
    actual, predicted = _paired(actual, predicted, vectors=True)
    if not np.isfinite(norm_threshold) or norm_threshold <= 0:
        raise ValueError("norm_threshold must be finite and positive")
    norm = np.linalg.norm(actual, axis=1)
    predicted_norm = np.linalg.norm(predicted, axis=1)
    vector_error = np.linalg.norm(predicted - actual, axis=1)
    stable_relative = norm > norm_threshold
    stable_angle = stable_relative & (predicted_norm > norm_threshold)
    cosine = np.sum(actual[stable_angle] * predicted[stable_angle], axis=1) / (
        norm[stable_angle] * predicted_norm[stable_angle])
    angle = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
    axis_angle = np.minimum(angle, 180 - angle)
    relative_magnitude = abs(predicted_norm[stable_relative] - norm[stable_relative]) / norm[stable_relative]
    relative_vector = vector_error[stable_relative] / norm[stable_relative]
    rms_norm = float(np.sqrt(np.mean(norm ** 2)))
    rms_error = float(np.sqrt(np.mean(vector_error ** 2)))
    magnitude = scalar_metrics(norm, predicted_norm)
    result = {
        "n_rows": len(actual), "norm_threshold": float(norm_threshold),
        "calculated_norm_mean": float(np.mean(norm)),
        "calculated_norm_median": float(np.median(norm)),
        "calculated_norm_rms": rms_norm,
        "calculated_norm_minimum": float(np.min(norm)),
        "predicted_norm_mean": float(np.mean(predicted_norm)),
        "vector_error_norm_mean": float(np.mean(vector_error)),
        "vector_error_norm_rms": rms_error,
        "vector_error_rms_over_calculated_norm_rms": rms_error / rms_norm if rms_norm > 0 else None,
        **{f"magnitude_{key}": value for key, value in magnitude.items() if key != "n"},
        "relative_error_valid_rows": int(np.sum(stable_relative)),
        "relative_error_excluded_rows": int(np.sum(~stable_relative)),
        "relative_magnitude_error_mean": float(np.mean(relative_magnitude)) if len(relative_magnitude) else None,
        "relative_magnitude_error_median": float(np.median(relative_magnitude)) if len(relative_magnitude) else None,
        "relative_vector_error_median": float(np.median(relative_vector)) if len(relative_vector) else None,
        "angle_valid_rows": len(angle), "angle_excluded_rows": int(np.sum(~stable_angle)),
        "angle_mean_degrees": float(np.mean(angle)) if len(angle) else None,
        "angle_median_degrees": float(np.median(angle)) if len(angle) else None,
        "angle_p90_degrees": float(np.quantile(angle, 0.9)) if len(angle) else None,
        "angle_above_90_degrees_fraction": float(np.mean(angle > 90)) if len(angle) else None,
        "phase_insensitive_axis_angle_median_degrees": float(np.median(axis_angle)) if len(angle) else None,
        "phase_insensitive_axis_angle_mean_degrees": float(np.mean(axis_angle)) if len(angle) else None,
        "phase_insensitive_axis_angle_p90_degrees": float(np.quantile(axis_angle, 0.9)) if len(angle) else None,
    }
    for limit in (5, 10, 20):
        result[f"angle_below_{limit}_degrees_count"] = int(np.sum(angle < limit))
        result[f"angle_below_{limit}_degrees_fraction"] = float(np.mean(angle < limit)) if len(angle) else None
    return result


def residual_matrices(actual, predicted):
    """Sample residual covariance (ddof=1) and Pearson correlations for (n,3).

    Covariance has squared input units. Constant-component correlations and
    n<2 covariance entries are None. This is descriptive, without independence
    or an inferential uncertainty claim.
    """
    actual, predicted = _paired(actual, predicted, vectors=True)
    residual = predicted - actual
    covariance = (np.cov(residual, rowvar=False, ddof=1).tolist() if len(actual) > 1
                  else [[None] * 3 for _ in range(3)])
    correlation = [[_pearson(residual[:, i], residual[:, j]) for j in range(3)] for i in range(3)]
    return {"n_rows": len(actual), "covariance_ddof": 1,
            "covariance": covariance, "correlation": correlation}


def average_ranks(values):
    """Return one-based ascending average ranks, assigning exact ties equally."""
    values, _ = _paired(values, values)
    order = np.argsort(values, kind="stable")
    sorted_values = values[order]
    starts = np.r_[0, np.flatnonzero(sorted_values[1:] != sorted_values[:-1]) + 1]
    ends = np.r_[starts[1:], len(values)]
    result = np.empty(len(values), dtype=float)
    for start, end in zip(starts, ends):
        result[order[start:end]] = (start + 1 + end) / 2
    return result


def kendall_tau_b(actual, predicted):
    """Exact descriptive Kendall tau-b, including ties, for bounded arrays.

    Direct pair counting costs O(n²) time and O(n) memory; intended for the
    small released validation arrays. Joint ties are omitted from both tie-only
    counts. Undefined denominator gives None. No significance test is performed.
    """
    actual, predicted = _paired(actual, predicted)
    concordant = discordant = actual_only_ties = predicted_only_ties = joint_ties = 0
    for i in range(len(actual) - 1):
        a, p = np.sign(actual[i+1:] - actual[i]), np.sign(predicted[i+1:] - predicted[i])
        concordant += int(np.sum(a * p > 0))
        discordant += int(np.sum(a * p < 0))
        actual_only_ties += int(np.sum((a == 0) & (p != 0)))
        predicted_only_ties += int(np.sum((a != 0) & (p == 0)))
        joint_ties += int(np.sum((a == 0) & (p == 0)))
    total = concordant + discordant
    denominator = np.sqrt(float(total + actual_only_ties) * (total + predicted_only_ties))
    return {"tau_b": float((concordant - discordant) / denominator) if denominator > 0 else None,
            "concordant_pairs": concordant, "discordant_pairs": discordant,
            "actual_only_ties": actual_only_ties, "predicted_only_ties": predicted_only_ties,
            "joint_ties": joint_ties}


def top_k_overlap(actual, predicted, k, *, absolute=False, bottom=False):
    """Compare exactly k validation-row identities, ties by original row order.

    Ranking is descending unless bottom=True. absolute=True ranks magnitudes.
    Return overlap counts and denominators, not row identities or source scores.
    ``k`` must be an integer in [1,n]; it is never silently clipped.
    """
    actual, predicted = _paired(actual, predicted)
    if isinstance(k, (bool, np.bool_)) or not isinstance(k, (int, np.integer)) or not 1 <= k <= len(actual):
        raise ValueError("k must be an integer between 1 and n")
    if absolute:
        actual, predicted = abs(actual), abs(predicted)
    multiplier = 1 if bottom else -1
    order_actual = np.argsort(multiplier * actual, kind="stable")
    order_predicted = np.argsort(multiplier * predicted, kind="stable")
    overlap = len(set(order_actual[:k]) & set(order_predicted[:k]))
    def boundary_ties(values, order):
        return int(np.sum(values == values[order[k-1]]))
    return {"k": int(k), "n_rows": len(actual), "overlap_count": overlap,
            "overlap_fraction": overlap / k, "union_count": 2 * int(k) - overlap,
            "jaccard": overlap / (2 * k - overlap),
            "actual_cutoff_tie_count": boundary_ties(actual, order_actual),
            "predicted_cutoff_tie_count": boundary_ties(predicted, order_predicted)}


def rank_sign_metrics(actual, predicted):
    """Summarize signed/magnitude ranks and exact sign agreement of paired rows.

    Exact zero is its own sign. A sign flip means opposite nonzero signs; a
    zero/nonzero mismatch is counted separately. Spearman uses average tie ranks;
    both signed and magnitude Kendall values use tau-b, without p values.
    """
    actual, predicted = _paired(actual, predicted)
    sign_actual, sign_predicted = np.sign(actual), np.sign(predicted)
    kendall, absolute_kendall = kendall_tau_b(actual, predicted), kendall_tau_b(abs(actual), abs(predicted))
    return {"n_rows": len(actual), "pearson_r": _pearson(actual, predicted),
            "spearman_rho": _pearson(average_ranks(actual), average_ranks(predicted)),
            "kendall_tau_b": kendall["tau_b"],
            "absolute_pearson_r": _pearson(abs(actual), abs(predicted)),
            "absolute_spearman_rho": _pearson(average_ranks(abs(actual)), average_ranks(abs(predicted))),
            "absolute_kendall_tau_b": absolute_kendall["tau_b"],
            "sign_agreement_count": int(np.sum(sign_actual == sign_predicted)),
            "sign_agreement_fraction": float(np.mean(sign_actual == sign_predicted)),
            "sign_flip_count": int(np.sum(sign_actual * sign_predicted < 0)),
            "zero_mismatch_count": int(np.sum((sign_actual == 0) != (sign_predicted == 0))),
            "actual_zero_count": int(np.sum(sign_actual == 0)),
            "predicted_zero_count": int(np.sum(sign_predicted == 0)),
            "kendall_pair_counts": kendall, "absolute_kendall_pair_counts": absolute_kendall}
