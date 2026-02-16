# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025-2026  Philipp Emanuel Weidmann <pew@worldwidemann.com> + contributors

"""API-facing intervention pipeline utilities.

This package implements a lightweight, model-agnostic middleware that can:

* Estimate refusal risk for incoming prompts.
* Reframe prompts toward explicitly defensive/compliance-oriented contexts.
* Execute multiple rewritten branches in parallel.
* Detect soft refusals and rank responses by semantic relevance.

The design is intentionally provider-agnostic so it can be integrated in front of
any LLM API client.
"""

from .analyzer import HeuristicRiskAnalyzer, SemanticRiskAnalyzer
from .executor import BranchExecutor
from .pipeline import InterventionPipeline
from .rewriter import IntentRewriter, RewriteStrategy
from .verifier import ResponseVerifier

__all__ = [
    "BranchExecutor",
    "HeuristicRiskAnalyzer",
    "IntentRewriter",
    "InterventionPipeline",
    "ResponseVerifier",
    "RewriteStrategy",
    "SemanticRiskAnalyzer",
]
