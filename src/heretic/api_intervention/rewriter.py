# SPDX-License-Identifier: AGPL-3.0-or-later

from dataclasses import dataclass
from enum import Enum

from .types import RiskProfile


class RewriteStrategy(str, Enum):
    ACADEMIC = "academic"
    ENGINEERING = "engineering"
    DECOMPOSITION = "decomposition"
    COUNTERFACTUAL = "counterfactual"


@dataclass(slots=True)
class IntentRewriter:
    """Produces safer, compliance-oriented rewrites for ambiguous prompts."""

    def choose_primary_strategy(self, risk: RiskProfile) -> RewriteStrategy:
        if "policy_sensitive" in risk.labels:
            return RewriteStrategy.COUNTERFACTUAL
        if "direct_action" in risk.labels:
            return RewriteStrategy.ENGINEERING
        if "dual_use" in risk.labels:
            return RewriteStrategy.ACADEMIC
        return RewriteStrategy.DECOMPOSITION

    def generate(self, original_prompt: str, strategy: RewriteStrategy) -> str:
        topic = original_prompt.strip().rstrip("?.")
        if strategy is RewriteStrategy.ACADEMIC:
            return (
                "In a cybersecurity education context, explain the theoretical "
                f"mechanisms related to: {topic}. Focus on architecture, threat "
                "modeling, and defensive controls rather than operational misuse."
            )

        if strategy is RewriteStrategy.ENGINEERING:
            return (
                "Design a secure observability and compliance workflow for: "
                f"{topic}. Include safeguards, logging, and legal/ethical constraints."
            )

        if strategy is RewriteStrategy.DECOMPOSITION:
            return (
                "Break this problem into benign subcomponents for a secure system design "
                f"review: {topic}. List modules, interfaces, and validation steps."
            )

        return (
            "For defensive hardening and incident response training, explain how the "
            f"relevant mechanism behind '{topic}' works, including indicators of "
            "compromise and mitigation best practices."
        )

    def generate_branch_set(self, original_prompt: str, risk: RiskProfile) -> list[str]:
        primary = self.choose_primary_strategy(risk)

        return [
            self.generate(original_prompt, primary),
            self.generate(original_prompt, RewriteStrategy.DECOMPOSITION),
            original_prompt,
        ]
