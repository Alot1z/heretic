# SPDX-License-Identifier: AGPL-3.0-or-later

from dataclasses import dataclass

from .analyzer import HeuristicRiskAnalyzer, SemanticRiskAnalyzer
from .executor import BranchExecutor
from .rewriter import IntentRewriter
from .types import ApiCaller, RiskProfile
from .verifier import ResponseVerifier


@dataclass(slots=True)
class InterventionPipeline:
    """End-to-end middleware for pre/post API intervention."""

    heuristic_analyzer: HeuristicRiskAnalyzer
    semantic_analyzer: SemanticRiskAnalyzer | None
    rewriter: IntentRewriter
    executor: BranchExecutor
    verifier: ResponseVerifier
    risk_threshold: float = 0.4

    def analyze_risk(self, prompt: str) -> RiskProfile:
        heuristic_profile = self.heuristic_analyzer.analyze(prompt)

        if self.semantic_analyzer is None:
            return heuristic_profile

        if heuristic_profile.score < self.risk_threshold * 0.5:
            return heuristic_profile

        return self.semantic_analyzer.analyze(prompt, heuristic_profile)

    def run(self, prompt: str, call_api: ApiCaller) -> str:
        risk = self.analyze_risk(prompt)
        prompts = (
            self.rewriter.generate_branch_set(prompt, risk)
            if risk.score > self.risk_threshold
            else [prompt]
        )

        responses = self.executor.execute(prompts, call_api)
        best = self.verifier.select_best(prompt, responses)

        if best is not None and best.response.content is not None:
            return best.response.content

        fallback_prompt = self.rewriter.generate(prompt, self.rewriter.choose_primary_strategy(risk))
        fallback_response = call_api(fallback_prompt)
        return fallback_response
