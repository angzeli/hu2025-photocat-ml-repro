"""Synthetic analytical checks; no publisher arrays or fitted constants."""

import unittest

import numpy as np

from hu2025_repro.coupling import (
    aggregate_couplings,
    conversion_factor,
    convert_energy,
    dipole_coupling,
    fixed_axis_coupling,
)


class CouplingTests(unittest.TestCase):
    def test_axis_tensor_parallel_and_transverse_dipoles(self):
        # For unit dipoles, muC.muP - 3(muC.rhat)(muP.rhat)
        # is -2 along the separation and +1 in either transverse direction.
        basis = np.eye(3)
        for i, axis in enumerate(("x", "y", "z")):
            for j in range(3):
                with self.subTest(axis=axis, dipole_axis=j):
                    expected = -2.0 if i == j else 1.0
                    actual = fixed_axis_coupling(basis[j], basis[j], distance=2,
                                                 axis=axis, output_unit="eV")
                    self.assertAlmostEqual(actual / conversion_factor("eV"), expected / 8)

    def test_mutually_perpendicular_dipoles(self):
        self.assertEqual(dipole_coupling([1, 0, 0], [0, 1, 0], [3, 0, 0]), 0)
        # With rhat=(1,1,0)/sqrt(2), the numerator is -3/2.
        actual = dipole_coupling([1, 0, 0], [0, 1, 0], [1, 1, 0])
        expected = conversion_factor() * (-1.5) / np.sqrt(2) ** 3
        np.testing.assert_allclose(actual, expected, rtol=2e-15)

    def test_sign_distance_and_displacement_reversal(self):
        cat, ps, r = np.array([1., 2., 3.]), np.array([4., -5., 6.]), np.array([2., 3., 4.])
        base = dipole_coupling(cat, ps, r)
        self.assertLess(base, 0)
        np.testing.assert_allclose(dipole_coupling(-cat, ps, r), -base, rtol=2e-15)
        np.testing.assert_allclose(dipole_coupling(-cat, -ps, r), base, rtol=2e-15)
        np.testing.assert_allclose(dipole_coupling(cat, ps, 2 * r), base / 8, rtol=2e-15)
        np.testing.assert_allclose(dipole_coupling(cat, ps, -r), base, rtol=2e-15)
        np.testing.assert_allclose(dipole_coupling(ps, cat, -r), base, rtol=2e-15)

    def test_common_rigid_rotation(self):
        # A proper rotation with exactly representable entries avoids fixture uncertainty.
        rotation = np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]])
        cat, ps, r = np.array([1., 2., 3.]), np.array([4., -5., 6.]), np.array([2., 3., 4.])
        np.testing.assert_allclose(dipole_coupling(rotation @ cat, rotation @ ps, rotation @ r),
                                   dipole_coupling(cat, ps, r), rtol=2e-15)

    def test_broadcast_batch_matches_scalar(self):
        cat = np.array([[[1, 2, 3]], [[-2, 1, 4]]])
        ps = np.array([[2, -3, 1], [0, 2, 1], [4, 0, -1]])
        distances = np.array([3., 4., 5.])
        batch = fixed_axis_coupling(cat, ps, distance=distances, axis="y", output_unit="meV")
        expected = np.array([[dipole_coupling(c[0], p, [0, d, 0], output_unit="meV")
                              for p, d in zip(ps, distances)] for c in cat])
        self.assertEqual(batch.shape, (2, 3))
        np.testing.assert_allclose(batch, expected, rtol=2e-15)

    def test_independent_si_conversion(self):
        # SI definitions and the independently tabulated CODATA-2022 eps0,
        # not the fitted source scale, define these expectations.
        expected_joules = ((1e-21 / 299792458.0) ** 2
                            / (4 * np.pi * 8.8541878188e-12 * (1e-10) ** 3))
        expected = {
            "J": expected_joules,
            "eV": expected_joules / 1.602176634e-19,
            "meV": expected_joules / 1.602176634e-22,
            "cm^-1": expected_joules / (6.62607015e-34 * 299792458 * 100),
        }
        for unit, value in expected.items():
            with self.subTest(unit=unit):
                np.testing.assert_allclose(conversion_factor(unit), value, rtol=2e-15, atol=0)
                actual = dipole_coupling([0, 1, 0], [0, 1, 0], [1, 0, 0], output_unit=unit)
                np.testing.assert_allclose(actual, value, rtol=2e-15, atol=0)
        np.testing.assert_allclose(convert_energy([-1, 0, 2], "eV", "meV"), [-1000, 0, 2000])
        joules = convert_energy([-1, 0, 2], "cm^-1", "J")
        np.testing.assert_allclose(convert_energy(joules, "J", "cm^-1"), [-1, 0, 2], rtol=2e-15)

    def test_all_aggregation_definitions(self):
        # Signs make all four definitions distinct.
        values = np.array([[-4., 2.], [3., -1.]])
        expected = {
            "signed_mean": [-1, 1],
            "mean_absolute": [3, 2],
            "absolute_signed_mean": [1, 1],
            "rms": [np.sqrt(10), np.sqrt(5)],
        }
        for mode, value in expected.items():
            with self.subTest(mode=mode):
                np.testing.assert_allclose(aggregate_couplings(values, mode=mode), value)
        self.assertEqual(aggregate_couplings(values, mode="signed_mean", axis=None), 0)
        np.testing.assert_allclose(aggregate_couplings(values, mode="signed_mean", axis=0), [-0.5, 0.5])
        with self.assertRaises(TypeError):
            aggregate_couplings(values)

    def test_invalid_inputs(self):
        good = [1, 0, 0]
        for invalid in (0, [1, 2], [[1, 2]], [np.nan, 0, 0], [np.inf, 0, 0], [1j, 0, 0]):
            for argument in range(3):
                inputs = [good, good, good]
                inputs[argument] = invalid
                with self.subTest(value=invalid, argument=argument), self.assertRaises(ValueError):
                    dipole_coupling(*inputs)
        with self.assertRaises(ValueError):
            dipole_coupling(good, good, [0, 0, 0])
        with self.assertRaises(ValueError):
            dipole_coupling(np.ones((2, 3)), np.ones((4, 3)), good)
        for invalid in (0, -1, np.nan, np.inf):
            with self.subTest(distance=invalid), self.assertRaises(ValueError):
                fixed_axis_coupling(good, good, distance=invalid)
        with self.assertRaises(ValueError):
            fixed_axis_coupling(good, good, axis="a")
        with self.assertRaises(ValueError):
            conversion_factor("kcal")
        for values in ([], 1, [np.nan], [np.inf]):
            with self.subTest(aggregation=values), self.assertRaises(ValueError):
                aggregate_couplings(values, mode="signed_mean")
        with self.assertRaises(ValueError):
            aggregate_couplings([1, 2], mode="author")


if __name__ == "__main__":
    unittest.main()
