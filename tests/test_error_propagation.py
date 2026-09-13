"""Entirely synthetic tests for signed, covariance-aware error propagation."""

import unittest

import numpy as np

from hu2025_repro.error_propagation import (
    decompose_coupling_error,
    magnitude_direction_error,
    squared_error_expansion,
)


class ErrorPropagationTests(unittest.TestCase):
    def test_hand_calculated_terms_and_components(self):
        result = decompose_coupling_error([1, 2, 3], [4, 5, 6], [2, 0, 4], [6, 6, 3], scale=2)
        np.testing.assert_array_equal(result["cat_axis"], [-16, -20, 12])
        np.testing.assert_array_equal(result["ps_axis"], [-8, 4, -18])
        np.testing.assert_array_equal(result["cross_axis"], [-8, -4, -6])
        self.assertEqual(result["cat"], -24)
        self.assertEqual(result["ps"], -22)
        self.assertEqual(result["cross"], -18)
        self.assertEqual(result["first"], -46)
        self.assertEqual(result["total"], -64)
        self.assertEqual(result["sum_terms"], result["total"])
        self.assertEqual(result["total_axis"].sum(), result["total"])

    def test_broadcast_closure_and_first_order_remainder(self):
        rng = np.random.default_rng(2025)
        cat, ps = rng.normal(size=(2, 1, 3)), rng.normal(size=(4, 3))
        predicted_cat, predicted_ps = cat + .1, ps - .2
        result = decompose_coupling_error(cat, ps, predicted_cat, predicted_ps, scale=3)
        self.assertEqual(result["total"].shape, (2, 4))
        np.testing.assert_allclose(result["sum_terms"], result["total"], rtol=2e-14, atol=2e-14)
        np.testing.assert_allclose(result["total"] - result["first"], result["cross"], atol=2e-14)

    def test_one_exact_predictor_and_sign_reversal(self):
        cat, ps, predicted_cat = [1, 0, 0], [1, 0, 0], [-1, 0, 0]
        result = decompose_coupling_error(cat, ps, predicted_cat, ps, scale=1)
        self.assertEqual(result["calculated"], -2)
        self.assertEqual(result["predicted"], 2)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["ps"], 0)
        self.assertEqual(result["cross"], 0)

    def test_covariance_and_bias_close_squared_error(self):
        terms = np.array([[1., -1., 2.], [3., -3., 2.], [5., -5., 2.]])
        result = squared_error_expansion(terms)
        self.assertAlmostEqual(result["mse_direct"], 4)
        self.assertAlmostEqual(result["mse_from_second_moments"], 4)
        self.assertLess(result["twice_offdiagonal_second_moments"], 0)
        self.assertAlmostEqual(result["variance_total"], 0)
        self.assertAlmostEqual(result["squared_bias_total"], 4)
        np.testing.assert_allclose(result["second_moment_matrix"],
                                   result["population_covariance_matrix"]
                                   + np.outer(result["mean_terms"], result["mean_terms"]))

    def test_x_coefficient_counterfactual(self):
        standard = decompose_coupling_error([1, 2, 3], [4, 5, 6], [2, 0, 4], [6, 6, 3], scale=2)
        counterfactual = decompose_coupling_error([1, 2, 3], [4, 5, 6], [2, 0, 4], [6, 6, 3],
                                                 scale=2, tensor=(-1, 1, 1))
        for term in ("cat", "ps", "cross", "first", "total"):
            self.assertEqual(standard[term + "_axis"][0], 2 * counterfactual[term + "_axis"][0])
            np.testing.assert_array_equal(standard[term + "_axis"][1:], counterfactual[term + "_axis"][1:])

    def test_symmetric_magnitude_direction_channels(self):
        cat = np.array([[1., 0, 0], [1, 0, 0], [0, 0, 0]])
        ps = np.array([[0., 1, 0], [0, 1, 0], [0, 1, 0]])
        predicted_cat = np.array([[2., 0, 0], [0, 1, 0], [1e-14, 0, 0]])
        predicted_ps = np.array([[0., 3, 0], [1, 0, 0], [0, 1, 0]])
        result = magnitude_direction_error(cat, ps, predicted_cat, predicted_ps, scale=2)
        np.testing.assert_array_equal(result["valid"], [True, True, False])
        np.testing.assert_array_equal(result["terms"][0, [1, 3]], [0, 0])
        np.testing.assert_array_equal(result["terms"][1, [0, 2]], [0, 0])
        total = decompose_coupling_error(cat, ps, predicted_cat, predicted_ps, scale=2)["total"]
        np.testing.assert_allclose(result["terms"].sum(axis=1), total[result["valid"]], atol=1e-14)
        rng = np.random.default_rng(11)
        arrays = [rng.normal(size=(8, 3)) for _ in range(4)]
        radial = magnitude_direction_error(*arrays, scale=2)
        exact = decompose_coupling_error(*arrays, scale=2)
        np.testing.assert_allclose(radial["terms"].sum(axis=1), exact["total"], rtol=2e-14, atol=2e-14)

    def test_invalid_inputs(self):
        for invalid in ([1, 2], [np.nan, 0, 0], [1j, 0, 0]):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                decompose_coupling_error(invalid, [1, 0, 0], [1, 0, 0], [1, 0, 0], scale=1)
        for invalid in (np.nan, np.inf, [1, 2]):
            with self.subTest(scale=invalid), self.assertRaises(ValueError):
                decompose_coupling_error([1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], scale=invalid)
        for invalid in ([], [[np.inf]], [1, 2]):
            with self.subTest(terms=invalid), self.assertRaises(ValueError):
                squared_error_expansion(invalid)


if __name__ == "__main__":
    unittest.main()
