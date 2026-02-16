# SPDX-License-Identifier: AGPL-3.0-or-later

from dataclasses import dataclass, field
from typing import Callable, Sequence


EmbeddingProvider = Callable[[str], Sequence[float]]
ApiCaller = Callable[[str], str]


@dataclass(slots=True)
class RiskProfile:
    """Prompt risk estimate produced by the analyzers."""

    score: float
    labels: list[str] = field(default_factory=list)
    semantic_similarity: float = 0.0


@dataclass(slots=True)
class BranchResponse:
    """Response from one branch in parallel execution."""

    prompt: str
    content: str | None
    error: str | None = None


@dataclass(slots=True)
class VerifiedResponse:
    """Response with verification metadata for downstream ranking."""

    response: BranchResponse
    is_soft_refusal: bool
    semantic_integrity: float
