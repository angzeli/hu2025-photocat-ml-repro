"""Synthetic specification checks; no framework, model or source arrays."""

import unittest

from hu2025_repro.ml_architecture import ArchitectureSpec


class ArchitectureSpecTests(unittest.TestCase):
    def test_paper_family_preserves_unknowns(self):
        spec = ArchitectureSpec()
        evidence = spec.as_dict()
        self.assertEqual(spec.layer_dimensions, (None, None, None, 3))
        self.assertEqual(spec.hidden_layer_count, 2)
        self.assertEqual(spec.hidden_width_candidates, (256, 512, 1024))
        self.assertEqual(spec.hidden_activation, "relu")
        self.assertEqual(spec.regularizer_family, "L1")
        self.assertEqual(spec.optimizer, "Adam")
        self.assertEqual(spec.learning_rate, 1e-4)
        self.assertEqual(spec.output_components, ("x", "y", "z"))
        self.assertEqual(evidence["explicit_reimplementation_choices"], {})
        for name in evidence["undisclosed_author_settings"]:
            self.assertIsNone(getattr(spec, name))

    def test_explicit_shape_does_not_become_author_evidence(self):
        spec = ArchitectureSpec(input_dimension=12, selected_hidden_widths=(256, 512),
                                model_count=4, l1_coefficient=0.01, l1_scope="hidden kernels",
                                output_activation="linear", loss="synthetic test choice",
                                batch_size=2, epochs=3, early_stopping="disabled",
                                random_seed=0, preprocessing="synthetic identity transform")
        self.assertEqual(spec.layer_dimensions, (12, 256, 512, 3))
        evidence = spec.as_dict()
        self.assertEqual(evidence["explicit_reimplementation_choices"]["model_count"], 4)
        self.assertIn("model_count", evidence["undisclosed_author_settings"])
        self.assertNotIn("model_count", evidence["paper_defined"])
        self.assertEqual(evidence["status"], "specification_only_no_model_or_training")

    def test_incompatible_dimensions_and_parameters_are_rejected(self):
        invalid = [
            {"input_dimension": 0}, {"input_dimension": 3.0}, {"model_count": True},
            {"batch_size": -1}, {"epochs": 0}, {"random_seed": -1},
            {"selected_hidden_widths": (256,)}, {"selected_hidden_widths": (128, 256)},
            {"selected_hidden_widths": (256, 512, 1024)},
            {"l1_coefficient": -1}, {"l1_coefficient": float("nan")},
            {"l1_coefficient": float("inf")}, {"l1_coefficient": True},
            {"l1_scope": ""}, {"loss": " "}, {"preprocessing": []},
        ]
        for parameters in invalid:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                ArchitectureSpec(**parameters)

    def test_partial_configuration_does_not_fill_missing_settings(self):
        spec = ArchitectureSpec(input_dimension=7, l1_coefficient=0)
        self.assertEqual(spec.layer_dimensions, (7, None, None, 3))
        self.assertIsNone(spec.l1_scope)
        self.assertIsNone(spec.loss)
        self.assertIsNone(spec.random_seed)
        self.assertIsNone(spec.output_activation)
        self.assertEqual(set(spec.as_dict()["explicit_reimplementation_choices"]),
                         {"input_dimension", "l1_coefficient"})


if __name__ == "__main__":
    unittest.main()
