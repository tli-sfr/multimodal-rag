"""Evaluation framework for the RAG system."""

from .metrics import (
    EvaluationMetrics,
    calculate_faithfulness,
    calculate_answer_relevance,
    calculate_context_precision,
    calculate_hallucination_rate,
)
from .test_suite import TestSuite, TestCase, EvaluationResult

__all__ = [
    "EvaluationMetrics",
    "calculate_faithfulness",
    "calculate_answer_relevance",
    "calculate_context_precision",
    "calculate_hallucination_rate",
    "TestSuite",
    "TestCase",
    "EvaluationResult",
]

