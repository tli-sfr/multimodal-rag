"""Evaluation metrics for RAG system quality assessment."""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase
from loguru import logger

from ..models import Answer, SearchResult, Query


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    faithfulness: Optional[float] = None
    answer_relevance: Optional[float] = None
    context_precision: Optional[float] = None
    context_recall: Optional[float] = None
    hallucination_rate: Optional[float] = None
    latency_ms: Optional[float] = None
    retrieval_precision_at_k: Optional[float] = None
    retrieval_recall_at_k: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "faithfulness": self.faithfulness,
            "answer_relevance": self.answer_relevance,
            "context_precision": self.context_precision,
            "context_recall": self.context_recall,
            "hallucination_rate": self.hallucination_rate,
            "latency_ms": self.latency_ms,
            "retrieval_precision_at_k": self.retrieval_precision_at_k,
            "retrieval_recall_at_k": self.retrieval_recall_at_k,
        }
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score."""
        scores = []
        weights = []
        
        if self.faithfulness is not None:
            scores.append(self.faithfulness)
            weights.append(0.3)
        
        if self.answer_relevance is not None:
            scores.append(self.answer_relevance)
            weights.append(0.3)
        
        if self.context_precision is not None:
            scores.append(self.context_precision)
            weights.append(0.2)
        
        if self.hallucination_rate is not None:
            scores.append(1.0 - self.hallucination_rate)  # Invert hallucination
            weights.append(0.2)
        
        if not scores:
            return 0.0
        
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0


def calculate_faithfulness(
    answer: str,
    contexts: List[str],
    model: str = "gpt-4-turbo-preview"
) -> float:
    """Calculate faithfulness score (factual consistency with context).
    
    Args:
        answer: Generated answer
        contexts: Retrieved context chunks
        model: LLM model for evaluation
        
    Returns:
        Faithfulness score (0-1)
    """
    try:
        metric = FaithfulnessMetric(
            threshold=0.7,
            model=model,
            include_reason=False
        )
        
        test_case = LLMTestCase(
            input="",  # Not needed for faithfulness
            actual_output=answer,
            retrieval_context=contexts
        )
        
        metric.measure(test_case)
        return metric.score
    
    except Exception as e:
        logger.error(f"Error calculating faithfulness: {e}")
        return 0.0


def calculate_answer_relevance(
    query: str,
    answer: str,
    model: str = "gpt-4-turbo-preview"
) -> float:
    """Calculate answer relevance score.
    
    Args:
        query: User query
        answer: Generated answer
        model: LLM model for evaluation
        
    Returns:
        Relevance score (0-1)
    """
    try:
        metric = AnswerRelevancyMetric(
            threshold=0.7,
            model=model,
            include_reason=False
        )
        
        test_case = LLMTestCase(
            input=query,
            actual_output=answer
        )
        
        metric.measure(test_case)
        return metric.score
    
    except Exception as e:
        logger.error(f"Error calculating answer relevance: {e}")
        return 0.0


def calculate_context_precision(
    query: str,
    answer: str,
    contexts: List[str],
    expected_answer: Optional[str] = None,
    model: str = "gpt-4-turbo-preview"
) -> float:
    """Calculate context precision score.
    
    Args:
        query: User query
        answer: Generated answer
        contexts: Retrieved context chunks
        expected_answer: Ground truth answer (if available)
        model: LLM model for evaluation
        
    Returns:
        Context precision score (0-1)
    """
    try:
        metric = ContextualPrecisionMetric(
            threshold=0.7,
            model=model,
            include_reason=False
        )
        
        test_case = LLMTestCase(
            input=query,
            actual_output=answer,
            expected_output=expected_answer,
            retrieval_context=contexts
        )
        
        metric.measure(test_case)
        return metric.score
    
    except Exception as e:
        logger.error(f"Error calculating context precision: {e}")
        return 0.0


def calculate_hallucination_rate(
    answer: str,
    contexts: List[str],
    model: str = "gpt-4-turbo-preview"
) -> float:
    """Calculate hallucination rate (inverse of faithfulness).
    
    Args:
        answer: Generated answer
        contexts: Retrieved context chunks
        model: LLM model for evaluation
        
    Returns:
        Hallucination rate (0-1, lower is better)
    """
    faithfulness = calculate_faithfulness(answer, contexts, model)
    return 1.0 - faithfulness

