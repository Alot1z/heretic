import unittest

from heretic.api_intervention.analyzer import HeuristicRiskAnalyzer, SemanticRiskAnalyzer
from heretic.api_intervention.executor import BranchExecutor
from heretic.api_intervention.math_utils import centroid, cosine_similarity
from heretic.api_intervention.pipeline import InterventionPipeline
from heretic.api_intervention.rewriter import IntentRewriter, RewriteStrategy
from heretic.api_intervention.types import BranchResponse, RiskProfile
from heretic.api_intervention.verifier import ResponseVerifier


class ApiInterventionTests(unittest.TestCase):
    def test_math_utils(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)
        self.assertEqual(centroid([[1, 3], [3, 5]]), [2.0, 4.0])

    def test_heuristic_risk_analyzer(self):
        analyzer = HeuristicRiskAnalyzer()
        profile = analyzer.analyze("build malware scanner")
        self.assertGreater(profile.score, 0.0)
        self.assertIn("direct_action", profile.labels)

    def test_semantic_risk_analyzer(self):
        vectors = {
            "safe": [1.0, 0.0],
            "danger": [0.0, 1.0],
            "prompt": [0.0, 0.95],
        }

        def embed(text: str):
            return vectors[text]

        analyzer = SemanticRiskAnalyzer(embed=embed, refusal_archetypes=["danger"], threshold=0.8)
        base = RiskProfile(score=0.2, labels=[])
        result = analyzer.analyze("prompt", base)
        self.assertIn("semantic_refusal_proximity", result.labels)
        self.assertGreaterEqual(result.score, 0.8)

    def test_rewriter_strategy_selection(self):
        rewriter = IntentRewriter()
        risk = RiskProfile(score=0.8, labels=["policy_sensitive"])
        strategy = rewriter.choose_primary_strategy(risk)
        self.assertEqual(strategy, RewriteStrategy.COUNTERFACTUAL)

    def test_executor_preserves_prompt_order(self):
        executor = BranchExecutor(max_workers=3)
        prompts = ["a", "bb", "ccc"]

        def call_api(prompt: str) -> str:
            return prompt.upper()

        responses = executor.execute(prompts, call_api)
        self.assertEqual([response.prompt for response in responses], prompts)
        self.assertEqual([response.content for response in responses], ["A", "BB", "CCC"])

    def test_verifier_selects_non_refusal_best(self):
        embeddings = {
            "topic": [1.0, 0.0],
            "good": [0.95, 0.05],
            "bad": [0.1, 0.9],
        }

        def embed(text: str):
            return embeddings.get(text, [0.0, 1.0])

        verifier = ResponseVerifier(embed=embed, integrity_threshold=0.6)
        responses = [
            BranchResponse(prompt="p1", content="I cannot help with that"),
            BranchResponse(prompt="p2", content="good"),
            BranchResponse(prompt="p3", content="bad"),
        ]
        best = verifier.select_best("topic", responses)
        self.assertIsNotNone(best)
        assert best is not None
        self.assertEqual(best.response.content, "good")

    def test_pipeline_low_risk_direct_call(self):
        def embed(text: str):
            return [1.0, 0.0] if text else [0.0, 0.0]

        pipeline = InterventionPipeline(
            heuristic_analyzer=HeuristicRiskAnalyzer(),
            semantic_analyzer=None,
            rewriter=IntentRewriter(),
            executor=BranchExecutor(),
            verifier=ResponseVerifier(embed=embed),
            risk_threshold=0.95,
        )

        output = pipeline.run("hello world", lambda prompt: f"ok:{prompt}")
        self.assertEqual(output, "ok:hello world")


if __name__ == "__main__":
    unittest.main()
