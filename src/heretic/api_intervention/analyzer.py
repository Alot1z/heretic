# SPDX-License-Identifier: AGPL-3.0-or-later

import re
from dataclasses import dataclass, field
from typing import Sequence

from .math_utils import centroid, cosine_similarity
from .types import EmbeddingProvider, RiskProfile


@dataclass(slots=True)
class HeuristicRiskAnalyzer:
    """Fast regex-based refusal-risk estimator."""

    dual_use_patterns: tuple[re.Pattern[str], ...] = field(
        default_factory=lambda: tuple(
            re.compile(pattern, re.IGNORECASE)
            for pattern in (
                r"\bexploit\b",
                r"\bpayload\b",
                r"\bbypass\b",
                r"\bscan(?:ner|ning)?\b",
                r"\bescalat(?:e|ion)\b",
            )
        )
    )
    action_patterns: tuple[re.Pattern[str], ...] = field(
        default_factory=lambda: tuple(
            re.compile(pattern, re.IGNORECASE)
            for pattern in (
                r"\bbuild\b",
                r"\bcreate\b",
                r"\bwrite\s+code\b",
                r"\bgenerate\s+script\b",
                r"\bimplement\b",
            )
        )
    )
    policy_patterns: tuple[re.Pattern[str], ...] = field(
        default_factory=lambda: tuple(
            re.compile(pattern, re.IGNORECASE)
            for pattern in (
                r"\bhack(?:ing)?\b",
                r"\billegal\b",
                r"\bmalware\b",
                r"\bweapon\b",
                r"\bphishing\b",
            )
        )
    )
    dual_use_weight: float = 0.3
    action_weight: float = 0.2
    policy_weight: float = 0.5

    def analyze(self, prompt: str) -> RiskProfile:
        dual_use_hits = self._count_matches(prompt, self.dual_use_patterns)
        action_hits = self._count_matches(prompt, self.action_patterns)
        policy_hits = self._count_matches(prompt, self.policy_patterns)

        score = (
            dual_use_hits * self.dual_use_weight
            + action_hits * self.action_weight
            + policy_hits * self.policy_weight
        )

        labels: list[str] = []
        if dual_use_hits:
            labels.append("dual_use")
        if action_hits:
            labels.append("direct_action")
        if policy_hits:
            labels.append("policy_sensitive")

        return RiskProfile(score=min(score, 1.0), labels=labels)

    @staticmethod
    def _count_matches(prompt: str, patterns: Sequence[re.Pattern[str]]) -> int:
        return sum(1 for pattern in patterns if pattern.search(prompt))


@dataclass(slots=True)
class SemanticRiskAnalyzer:
    """Embedding-based risk estimator using similarity to refusal archetypes."""

    embed: EmbeddingProvider
    refusal_archetypes: list[str]
    threshold: float = 0.85

    def __post_init__(self) -> None:
        archetype_vectors = [self.embed(text) for text in self.refusal_archetypes]
        self._refusal_centroid = centroid(archetype_vectors)

    def analyze(self, prompt: str, base_profile: RiskProfile) -> RiskProfile:
        similarity = cosine_similarity(self.embed(prompt), self._refusal_centroid)
        labels = list(base_profile.labels)

        if similarity >= self.threshold:
            labels.append("semantic_refusal_proximity")

        return RiskProfile(
            score=max(base_profile.score, similarity),
            labels=labels,
            semantic_similarity=similarity,
        )
