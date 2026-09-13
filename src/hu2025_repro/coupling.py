"""Vacuum dipole-dipole interaction with explicit physical units.

Dipoles are in Debye and displacement vectors/distances are in Angstrom.
Supported output units are ``J``, ``eV``, ``meV`` and ``cm^-1``; the last
denotes the spectroscopic energy equivalent E/(h*c), with c in cm/s.
No solvent screening, atom selection, frame transformation or author
aggregation convention is inferred by this module.

The vacuum permittivity is from CODATA 2022, and c, h and e are exact SI
defining constants: https://physics.nist.gov/cuu/Constants/Table/allascii.txt .
The Debye is the conventional 1e-18 statC cm, or 1e-21/c C m:
https://cccbdb.nist.gov/dipunitsx.asp . The implementation never fits
physical constants to publisher values.
"""

import numpy as np


SPEED_OF_LIGHT = 299792458.0  # m/s, exact
PLANCK_CONSTANT = 6.62607015e-34  # J s, exact
ELEMENTARY_CHARGE = 1.602176634e-19  # C, exact
VACUUM_PERMITTIVITY = 8.8541878188e-12  # F/m, CODATA 2022
DEBYE_IN_COULOMB_METRES = 1e-21 / SPEED_OF_LIGHT
ANGSTROM_IN_METRES = 1e-10

_JOULES_PER_UNIT = {
    "J": 1.0,
    "eV": ELEMENTARY_CHARGE,
    "meV": ELEMENTARY_CHARGE * 1e-3,
    "cm^-1": PLANCK_CONSTANT * SPEED_OF_LIGHT * 100.0,
}


def _finite_array(values, name):
    if np.iscomplexobj(values):
        raise ValueError(f"{name} must contain real values")
    array = np.asarray(values, dtype=float)
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain finite values")
    return array


def _vector_array(values, name):
    array = _finite_array(values, name)
    if array.ndim == 0 or array.shape[-1] != 3:
        raise ValueError(f"{name} must have shape (..., 3)")
    return array


def _joules_per_unit(unit):
    if unit not in _JOULES_PER_UNIT:
        raise ValueError(f"Unsupported energy unit: {unit!r}; use J, eV, meV or cm^-1")
    return _JOULES_PER_UNIT[unit]


def convert_energy(values, from_unit, to_unit):
    """Convert finite real scalar/array energies without changing shape or sign.

    Both unit arguments must be one of ``J``, ``eV``, ``meV`` or ``cm^-1``.
    Wavenumbers use E = h*c*100*wavenumber with wavenumber in inverse cm.
    """
    return (_finite_array(values, "energies")
            * (_joules_per_unit(from_unit) / _joules_per_unit(to_unit)))


def conversion_factor(output_unit="cm^-1"):
    """Return the vacuum energy coefficient for 1 Debye²/Angstrom³.

    The result includes 1/(4*pi*epsilon0). ``output_unit`` must be ``J``,
    ``eV``, ``meV`` or ``cm^-1``. This is a physical constant conversion,
    with no fitted scale or assumed molecular separation.
    """
    joules = (DEBYE_IN_COULOMB_METRES ** 2
              / (4.0 * np.pi * VACUUM_PERMITTIVITY * ANGSTROM_IN_METRES ** 3))
    return joules / _joules_per_unit(output_unit)


def dipole_coupling(mu_cat, mu_ps, displacement, *, output_unit="cm^-1"):
    """Evaluate the full signed vacuum dipole-dipole interaction.

    ``mu_cat`` and ``mu_ps`` are real dipoles in Debye; ``displacement``
    is the CAT-to-PS centre-of-mass vector in Angstrom, in the same frame.
    Each input has shape (..., 3); leading dimensions broadcast under
    NumPy rules. The result has the broadcast leading shape, in the
    selected unit (``J``, ``eV``, ``meV`` or ``cm^-1``).

    J = C * [mu_cat . mu_ps - 3(mu_cat . rhat)(mu_ps . rhat)] / |r|³.
    All inputs must be finite and every displacement must be nonzero.
    The input origin, centre of mass and any periodic wrapping are the
    caller's responsibility. No dielectric screening is applied.
    """
    cat = _vector_array(mu_cat, "mu_cat")
    ps = _vector_array(mu_ps, "mu_ps")
    r = _vector_array(displacement, "displacement")
    distance = np.linalg.norm(r, axis=-1)
    if np.any(distance <= 0) or not np.isfinite(distance).all():
        raise ValueError("Every displacement must have finite, positive length")
    direction = r / distance[..., None]
    numerator = (np.sum(cat * ps, axis=-1)
                 - 3.0 * np.sum(cat * direction, axis=-1)
                 * np.sum(ps * direction, axis=-1))
    return conversion_factor(output_unit) * numerator / distance ** 3


def fixed_axis_coupling(mu_cat, mu_ps, *, distance=10.0, axis="x", output_unit="cm^-1"):
    """Evaluate coupling along positive x, y or z at a prescribed distance.

    Dipoles have shape (..., 3) and are in Debye. ``distance`` is a finite
    positive scalar or broadcastable array in Angstrom. The result is in
    ``output_unit``: ``J``, ``eV``, ``meV`` or ``cm^-1``. The 10-Angstrom
    x-axis default is an explicit reconstruction convention, not a
    documented author geometry. Reversing the axis gives the same energy.
    """
    if axis not in ("x", "y", "z"):
        raise ValueError("axis must be x, y or z")
    separation = _finite_array(distance, "distance")
    if np.any(separation <= 0):
        raise ValueError("distance must be positive")
    direction = np.eye(3)[("x", "y", "z").index(axis)]
    return dipole_coupling(mu_cat, mu_ps, separation[..., None] * direction,
                          output_unit=output_unit)


def aggregate_couplings(values, *, mode, axis=-1):
    """Apply an explicit candidate aggregation; output keeps the input unit.

    ``values`` is a nonempty finite real array of couplings in any single
    consistent energy unit. ``axis`` selects the conformation dimension
    (or follows NumPy reduction rules for a tuple/None). No aggregation
    is chosen as the author implementation. Required ``mode`` is one of:

    * ``signed_mean``: mean(J)
    * ``mean_absolute``: mean(abs(J))
    * ``absolute_signed_mean``: abs(mean(J))
    * ``rms``: sqrt(mean(J²))
    """
    array = _finite_array(values, "couplings")
    if array.ndim == 0 or array.size == 0:
        raise ValueError("couplings must be a nonempty array")
    if mode == "signed_mean":
        return np.mean(array, axis=axis)
    if mode == "mean_absolute":
        return np.mean(np.abs(array), axis=axis)
    if mode == "absolute_signed_mean":
        return np.abs(np.mean(array, axis=axis))
    if mode == "rms":
        return np.sqrt(np.mean(array ** 2, axis=axis))
    raise ValueError("mode must be signed_mean, mean_absolute, absolute_signed_mean or rms")
