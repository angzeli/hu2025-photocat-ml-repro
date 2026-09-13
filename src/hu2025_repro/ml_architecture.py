"""Dependency-free description of the disclosed, untrained MLP family.

Evidence: Hu et al. 2025, DOI 10.1038/s41929-025-01291-z, article
PDF p. 8 (ML protocol); see forensics/reports/PAPER_METHODS_AUDIT.md.
This module creates no tensors, weights, optimizer or executable model. Its
caller-supplied values are reimplementation choices, never recovered author facts.
Phase-1 proposed training defaults are deliberately not imported here.
"""

from dataclasses import dataclass, fields
import math
from typing import ClassVar


@dataclass(frozen=True)
class ArchitectureSpec:
    """Published family plus explicit unknowns, with no training functionality.

    ``None`` denotes an undisclosed author setting. Populating a field records
    an explicit caller choice and does not establish what the authors used.
    Width choices must stay inside the disclosed two-hidden-layer family.
    Dimension and training counts are positive integers; a seed may be zero.
    L1 coefficient is finite and nonnegative, with its scope separately required
    for a complete penalty definition. The three outputs are x/y/z components
    of one dipole target, not a claim about the number of fitted models.
    """

    hidden_layer_count: ClassVar[int] = 2
    hidden_width_candidates: ClassVar[tuple[int, ...]] = (256, 512, 1024)
    hidden_activation: ClassVar[str] = "relu"
    regularizer_family: ClassVar[str] = "L1"
    output_dimension: ClassVar[int] = 3
    output_components: ClassVar[tuple[str, ...]] = ("x", "y", "z")
    optimizer: ClassVar[str] = "Adam"
    learning_rate: ClassVar[float] = 1e-4
    published_frameworks: ClassVar[tuple[str, ...]] = ("TensorFlow", "Keras")

    input_dimension: int | None = None
    selected_hidden_widths: tuple[int, int] | None = None
    model_count: int | None = None
    l1_coefficient: float | None = None
    l1_scope: str | None = None
    output_activation: str | None = None
    loss: str | None = None
    batch_size: int | None = None
    epochs: int | None = None
    early_stopping: str | None = None
    random_seed: int | None = None
    preprocessing: str | None = None

    def __post_init__(self):
        for name in ("input_dimension", "model_count", "batch_size", "epochs"):
            value = getattr(self, name)
            if value is not None and (type(value) is not int or value <= 0):
                raise ValueError(f"{name} must be a positive integer or None")
        if self.random_seed is not None and (
                type(self.random_seed) is not int or self.random_seed < 0):
            raise ValueError("random_seed must be a nonnegative integer or None")
        if self.selected_hidden_widths is not None:
            widths = self.selected_hidden_widths
            if (not isinstance(widths, tuple) or len(widths) != 2
                    or any(type(w) is not int or w not in self.hidden_width_candidates for w in widths)):
                raise ValueError("selected_hidden_widths must be two widths from 256/512/1024")
        if self.l1_coefficient is not None:
            coefficient = self.l1_coefficient
            if (isinstance(coefficient, bool) or not isinstance(coefficient, (int, float))
                    or not math.isfinite(coefficient) or coefficient < 0):
                raise ValueError("l1_coefficient must be finite and nonnegative or None")
        for name in ("l1_scope", "output_activation", "loss", "early_stopping", "preprocessing"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a nonempty description or None")

    @property
    def layer_dimensions(self):
        """Return input, hidden 1, hidden 2 and output sizes; unknowns stay None."""
        widths = self.selected_hidden_widths or (None, None)
        return (self.input_dimension, *widths, self.output_dimension)

    def as_dict(self):
        """Return provenance-separated, serializable specification metadata.

        Author settings remain unknown even when a caller supplies a choice;
        therefore their names stay in ``undisclosed_author_settings``.
        """
        choices = {field.name: getattr(self, field.name) for field in fields(self)
                   if getattr(self, field.name) is not None}
        return {
            "status": "specification_only_no_model_or_training",
            "paper_defined": {
                "hidden_layer_count": self.hidden_layer_count,
                "hidden_width_candidates": self.hidden_width_candidates,
                "hidden_activation": self.hidden_activation,
                "regularizer_family": self.regularizer_family,
                "output_dimension": self.output_dimension,
                "output_components": self.output_components,
                "optimizer": self.optimizer,
                "learning_rate": self.learning_rate,
                "published_frameworks": self.published_frameworks,
            },
            "undisclosed_author_settings": tuple(field.name for field in fields(self)),
            "explicit_reimplementation_choices": choices,
        }
