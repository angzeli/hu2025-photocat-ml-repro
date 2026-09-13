"""Small synthetic metric checks; no publisher data or trained models."""

import json
import unittest

import numpy as np

from hu2025_repro.ml_metrics import (
    average_ranks, kendall_tau_b, rank_sign_metrics, residual_matrices,
    scalar_metrics, top_k_overlap, vector_metrics,
)


class MLMetricsTests(unittest.TestCase):
    def test_scalar_predictive_r2_and_bias(self):
        result = scalar_metrics([1, 2, 3], [2, 3, 4])
        self.assertEqual(result["n"], 3)
        self.assertAlmostEqual(result["pearson_r"], 1)
        self.assertAlmostEqual(result["r2"], -0.5)
        self.assertEqual(result["mae"], 1)
        self.assertEqual(result["rmse"], 1)
        self.assertEqual(result["bias"], 1)
        self.assertEqual(scalar_metrics([[1, 2], [3, 4]], [[1, 2], [3, 4]])["n"], 4)

    def test_constant_and_insufficient_values_are_undefined(self):
        result = scalar_metrics([2, 2], [2, 2])
        self.assertIsNone(result["pearson_r"])
        self.assertIsNone(result["r2"])
        self.assertEqual(result["rmse"], 0)
        self.assertIsNone(scalar_metrics([1], [2])["pearson_r"])
        self.assertIsNone(rank_sign_metrics([1, 1], [2, 2])["spearman_rho"])
        json.dumps(result, allow_nan=False)

    def test_vector_magnitude_and_signed_direction(self):
        actual = np.diag([1., 2., 3.])
        predicted = np.diag([2., 1., -3.])
        result = vector_metrics(actual, predicted)
        self.assertAlmostEqual(result["magnitude_mae"], 2 / 3)
        self.assertAlmostEqual(result["magnitude_rmse"], np.sqrt(2 / 3))
        self.assertAlmostEqual(result["magnitude_bias"], 0)
        self.assertEqual(result["angle_median_degrees"], 0)
        self.assertEqual(result["angle_mean_degrees"], 60)
        self.assertEqual(result["phase_insensitive_axis_angle_mean_degrees"], 0)
        self.assertAlmostEqual(result["angle_p90_degrees"], 144)
        self.assertEqual(result["angle_below_5_degrees_count"], 2)
        self.assertAlmostEqual(result["relative_magnitude_error_mean"], 0.5)
        self.assertAlmostEqual(result["vector_error_rms_over_calculated_norm_rms"], np.sqrt(38 / 14))
        orthogonal = vector_metrics([[1, 0, 0]], [[0, 1, 0]])
        self.assertEqual(orthogonal["angle_mean_degrees"], 90)

    def test_near_zero_masks_and_threshold_sensitivity(self):
        actual = [[0, 0, 0], [1e-4, 0, 0], [1, 0, 0], [1, 0, 0]]
        predicted = [[1, 0, 0], [0, 1e-4, 0], [0, 0, 0], [1, 0, 0]]
        result = vector_metrics(actual, predicted, norm_threshold=1e-3)
        self.assertEqual(result["n_rows"], 4)
        self.assertEqual(result["relative_error_valid_rows"], 2)
        self.assertEqual(result["angle_valid_rows"], 1)
        self.assertEqual(result["angle_excluded_rows"], 3)
        self.assertEqual(result["angle_mean_degrees"], 0)
        lower = vector_metrics(actual, predicted, norm_threshold=1e-5)
        self.assertEqual(lower["angle_valid_rows"], 2)
        self.assertEqual(lower["angle_mean_degrees"], 45)
        empty_angles = vector_metrics([[0, 0, 0]], [[0, 0, 0]])
        self.assertIsNone(empty_angles["angle_mean_degrees"])
        self.assertIsNone(empty_angles["relative_magnitude_error_mean"])
        json.dumps(empty_angles, allow_nan=False)

    def test_residual_covariance_and_constant_component(self):
        result = residual_matrices(np.zeros((3, 3)), [[1, 2, 0], [2, 4, 0], [3, 6, 0]])
        np.testing.assert_allclose(result["covariance"], [[1, 2, 0], [2, 4, 0], [0, 0, 0]])
        self.assertAlmostEqual(result["correlation"][0][1], 1)
        self.assertIsNone(result["correlation"][2][2])
        json.dumps(result, allow_nan=False)

    def test_average_tie_ranks_and_kendall_tau_b(self):
        np.testing.assert_array_equal(average_ranks([3, 1, 1, 2]), [4, 1.5, 1.5, 3])
        result = kendall_tau_b([1, 1, 2, 3], [1, 2, 2, 3])
        self.assertEqual(result["concordant_pairs"], 4)
        self.assertEqual(result["actual_only_ties"], 1)
        self.assertEqual(result["predicted_only_ties"], 1)
        self.assertEqual(result["tau_b"], 0.8)
        self.assertEqual(kendall_tau_b([1, 2, 3], [3, 2, 1])["tau_b"], -1)
        self.assertIsNone(kendall_tau_b([1, 1], [1, 1])["tau_b"])
        self.assertEqual(kendall_tau_b([1, 1, 2], [1, 1, 2])["joint_ties"], 1)

    def test_sign_zeros_and_signed_versus_absolute_ranking(self):
        result = rank_sign_metrics([-2, 0, 3, 4], [2, 1, 3, -4])
        self.assertEqual(result["sign_flip_count"], 2)
        self.assertEqual(result["zero_mismatch_count"], 1)
        self.assertEqual(result["sign_agreement_fraction"], 0.25)
        self.assertAlmostEqual(result["absolute_spearman_rho"], 1)
        self.assertAlmostEqual(result["absolute_kendall_tau_b"], 1)

    def test_top_k_deterministic_ties_and_magnitude(self):
        # Actual top-2 is indices 0,1, with index 1 winning the boundary tie.
        result = top_k_overlap([4, 3, 3, 1], [3, 4, 2, 1], 2)
        self.assertEqual(result["overlap_count"], 2)
        self.assertEqual(result["actual_cutoff_tie_count"], 2)
        self.assertEqual(result["jaccard"], 1)
        self.assertEqual(top_k_overlap([-5, 2, 3], [4, 2, 3], 1)["overlap_count"], 0)
        self.assertEqual(top_k_overlap([-5, 2, 3], [4, 2, 3], 1, absolute=True)["overlap_count"], 1)
        self.assertEqual(top_k_overlap([-5, 2, 3], [4, 2, 3], 1, bottom=True)["overlap_count"], 0)

    def test_invalid_data_and_parameters(self):
        for actual, predicted in (([], []), ([1], [1, 2]), ([np.nan], [0]), ([1j], [0])):
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                scalar_metrics(actual, predicted)
        for value in (0, -1, np.nan):
            with self.assertRaises(ValueError):
                vector_metrics([[1, 0, 0]], [[1, 0, 0]], norm_threshold=value)
        with self.assertRaises(ValueError):
            vector_metrics([1, 2, 3], [1, 2, 3])
        for k in (0, 4, 1.5, True):
            with self.assertRaises(ValueError):
                top_k_overlap([1, 2, 3], [1, 2, 3], k)


if __name__ == "__main__":
    unittest.main()
