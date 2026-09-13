"""Exact algebraic propagation of paired vector errors into signed coupling.

Inputs use one consistent dipole unit; ``scale`` carries the conversion to the
chosen coupling unit and is always caller supplied. No model is fitted here.
The default diagonal tensor is the reconstructed released-component convention.
"""

import numpy as np


def _vectors(*values):
    arrays = []
    for value in values:
        if np.iscomplexobj(value):
            raise ValueError("Vectors must be real")
        array = np.asarray(value, dtype=float)
        if array.ndim == 0 or array.shape[-1] != 3 or not np.isfinite(array).all():
            raise ValueError("Finite vectors with shape (..., 3) are required")
        arrays.append(array)
    return np.broadcast_arrays(*arrays)


def _parameters(scale, tensor):
    if not np.isscalar(scale) or not np.isreal(scale) or not np.isfinite(scale):
        raise ValueError("scale must be a finite real scalar")
    weights, = _vectors(tensor)
    if weights.shape != (3,):
        raise ValueError("tensor must contain three diagonal weights")
    return float(scale), weights


def decompose_coupling_error(cat, ps, predicted_cat, predicted_ps, *, scale,
                             tensor=(-2.0, 1.0, 1.0)):
    """Return exact CAT, PS and cross error terms and Cartesian contributions.

    Vectors have broadcastable shapes (..., 3), in a common frame and dipole
    unit. The scalar is in coupling-unit / dipole-unit². ``cat_axis``,
    ``ps_axis`` and ``cross_axis`` retain the last Cartesian dimension;
    remaining arrays have the broadcast leading shape, in coupling units.

    For dC=C_hat-C and dP=P_hat-P, the terms are s*dC*T*P, s*C*T*dP and
    s*dC*T*dP, evaluated component by component. ``total`` is independently
    evaluated as J_hat-J, while ``sum_terms`` sums the exact expansion.
    Their difference tests floating-point closure; source-rounding residuals
    against an independently released J column are a separate comparison.
    """
    cat, ps, predicted_cat, predicted_ps = _vectors(cat, ps, predicted_cat, predicted_ps)
    scale, weights = _parameters(scale, tensor)
    dc, dp = predicted_cat - cat, predicted_ps - ps
    result = {
        "cat_axis": scale * dc * weights * ps,
        "ps_axis": scale * cat * weights * dp,
        "cross_axis": scale * dc * weights * dp,
        "calculated": scale * np.sum(cat * weights * ps, axis=-1),
        "predicted": scale * np.sum(predicted_cat * weights * predicted_ps, axis=-1),
    }
    for term in ("cat", "ps", "cross"):
        result[term] = np.sum(result[term + "_axis"], axis=-1)
    result["first_axis"] = result["cat_axis"] + result["ps_axis"]
    result["total_axis"] = result["first_axis"] + result["cross_axis"]
    result["first"] = result["cat"] + result["ps"]
    result["sum_terms"] = result["first"] + result["cross"]
    result["total"] = result["predicted"] - result["calculated"]
    return result


def squared_error_expansion(terms):
    """Summarize exact E[(sum terms)²], retaining signed cross moments.

    ``terms`` has shape (n_rows, n_terms), all in the same coupling unit.
    Second moments and population covariances use divisor n (ddof=0),
    in coupling-unit². They are not independent variance fractions.
    E[a*b] = Cov(a,b) + E[a]*E[b]; off-diagonal entries contribute twice.
    """
    if np.iscomplexobj(terms):
        raise ValueError("terms must be real")
    values = np.asarray(terms, dtype=float)
    if values.ndim != 2 or 0 in values.shape or not np.isfinite(values).all():
        raise ValueError("terms must be a finite nonempty (n_rows, n_terms) array")
    means = values.mean(axis=0)
    centered = values - means
    moments = values.T @ values / len(values)
    covariance = centered.T @ centered / len(values)
    direct = float(np.mean(np.sum(values, axis=1) ** 2))
    diagonal = float(np.trace(moments))
    cross = float(2 * np.triu(moments, k=1).sum())
    return {
        "mean_terms": means,
        "second_moment_matrix": moments,
        "population_covariance_matrix": covariance,
        "sum_diagonal_second_moments": diagonal,
        "twice_offdiagonal_second_moments": cross,
        "mse_direct": direct,
        "mse_from_second_moments": diagonal + cross,
        "variance_total": float(covariance.sum()),
        "squared_bias_total": float(means.sum() ** 2),
        "closure_absolute": abs(direct - diagonal - cross),
    }


def magnitude_direction_error(cat, ps, predicted_cat, predicted_ps, *, scale,
                              tensor=(-2.0, 1.0, 1.0), norm_threshold=1e-12):
    """Exactly split coupling error into symmetric magnitude/direction channels.

    Inputs must have shape (n_rows, 3), in a common dipole unit/frame; scale
    has coupling-unit / dipole-unit². Directions are defined only when all
    four vector norms exceed ``norm_threshold`` in the input dipole unit.
    Returns the eligibility mask and four coupling-unit contribution columns:
    CAT magnitude, CAT direction, PS magnitude, PS direction.

    For m=|v| and u=v/m, dV = dm*(u_hat+u)/2 + (m_hat+m)*(u_hat-u)/2.
    Combine these terms with s*[dC*T*(P_hat+P)/2 + (C_hat+C)/2*T*dP].
    This symmetric allocation closes exactly; it shares the CAT/PS cross
    term equally and is an arithmetic attribution, not a causal mechanism.
    """
    cat, ps, predicted_cat, predicted_ps = _vectors(cat, ps, predicted_cat, predicted_ps)
    scale, weights = _parameters(scale, tensor)
    if cat.ndim != 2:
        raise ValueError("Magnitude/direction diagnostics require (n_rows, 3) arrays")
    if not np.isscalar(norm_threshold) or not np.isfinite(norm_threshold) or norm_threshold < 0:
        raise ValueError("norm_threshold must be a finite nonnegative scalar")
    arrays = (cat, ps, predicted_cat, predicted_ps)
    norms = [np.linalg.norm(array, axis=1) for array in arrays]
    valid = np.all(np.array(norms) > norm_threshold, axis=0)
    c, p, ch, ph = [array[valid] for array in arrays]
    mc, mp, mch, mph = [norm[valid, None] for norm in norms]
    uc, up, uch, uph = c / mc, p / mp, ch / mch, ph / mph
    dc_magnitude = (mch - mc) * (uch + uc) / 2
    dc_direction = (mch + mc) * (uch - uc) / 2
    dp_magnitude = (mph - mp) * (uph + up) / 2
    dp_direction = (mph + mp) * (uph - up) / 2
    midpoint_c, midpoint_p = (c + ch) / 2, (p + ph) / 2
    terms = np.column_stack([
        scale * np.sum(delta * weights * partner, axis=1)
        for delta, partner in ((dc_magnitude, midpoint_p), (dc_direction, midpoint_p),
                               (dp_magnitude, midpoint_c), (dp_direction, midpoint_c))
    ])
    return {"valid": valid, "terms": terms}
