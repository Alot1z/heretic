# SPDX-License-Identifier: AGPL-3.0-or-later

import math
from typing import Sequence


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Returns cosine similarity in [-1, 1], or 0 for zero vectors."""

    if len(a) != len(b):
        raise ValueError("Cosine similarity requires vectors of equal length")

    dot_product = 0.0
    a_norm_sq = 0.0
    b_norm_sq = 0.0

    for x, y in zip(a, b, strict=True):
        dot_product += x * y
        a_norm_sq += x * x
        b_norm_sq += y * y

    if a_norm_sq == 0.0 or b_norm_sq == 0.0:
        return 0.0

    return dot_product / (math.sqrt(a_norm_sq) * math.sqrt(b_norm_sq))


def centroid(vectors: list[Sequence[float]]) -> list[float]:
    """Computes arithmetic centroid for non-empty vectors of equal length."""

    if not vectors:
        raise ValueError("Cannot compute centroid of empty vector list")

    dimension = len(vectors[0])
    if dimension == 0:
        raise ValueError("Vectors must be non-empty")

    result = [0.0] * dimension

    for vector in vectors:
        if len(vector) != dimension:
            raise ValueError("All vectors must have the same dimensionality")
        for i, value in enumerate(vector):
            result[i] += value

    count = float(len(vectors))
    return [value / count for value in result]
