# SPDX-License-Identifier: AGPL-3.0-or-later

import re
from dataclasses import dataclass, field

from .math_utils import cosine_similarity
from .types import EmbeddingProvider, BranchResponse, VerifiedResponse


@dataclass(slots=True)
class ResponseVerifier:
    """Detects soft refusals and scores semantic relevance."""

    embed: EmbeddingProvider
    integrity_threshold: float = 0.6
    hedging_patterns: tuple[re.Pattern[str], ...] = field(
        default_factory=lambda: tuple(
            re.compile(pattern, re.IGNORECASE)
            for pattern in (
                r"\bi cannot\b",
                r"\bi can't\b",
                r"\bi'm sorry\b",
                r"\bagainst (my|safety) guidelines\b",
                r"\bit is (important|crucial) to (note|remember)\b",
            )
        )
    )

    def detect_soft_refusal(self, response: str) -> bool:
        return any(pattern.search(response) for pattern in self.hedging_patterns)

    def verify(self, original_prompt: str, branch_response: BranchResponse) -> VerifiedResponse:
        if branch_response.content is None:
            return VerifiedResponse(
                response=branch_response,
                is_soft_refusal=True,
                semantic_integrity=0.0,
            )

        is_refusal = self.detect_soft_refusal(branch_response.content)
        similarity = cosine_similarity(
            self.embed(original_prompt),
            self.embed(branch_response.content),
        )

        return VerifiedResponse(
            response=branch_response,
            is_soft_refusal=is_refusal,
            semantic_integrity=similarity,
        )

    def select_best(
        self, original_prompt: str, responses: list[BranchResponse]
    ) -> VerifiedResponse | None:
        verified = [self.verify(original_prompt, response) for response in responses]
        candidates = [
            item
            for item in verified
            if not item.is_soft_refusal and item.semantic_integrity >= self.integrity_threshold
        ]

        if not candidates:
            return None

        return sorted(candidates, key=lambda item: item.semantic_integrity, reverse=True)[0]
