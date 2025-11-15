"""Test suite for evaluation-first RAG development."""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from loguru import logger
from pydantic import BaseModel

from ..models import Query, QueryType, Answer
from .metrics import (
    EvaluationMetrics,
    calculate_faithfulness,
    calculate_answer_relevance,
    calculate_context_precision,
    calculate_hallucination_rate,
)


class TestCase(BaseModel):
    """Individual test case for evaluation."""
    id: UUID = uuid4()
    query: str
    query_type: QueryType
    expected_answer: Optional[str] = None
    expected_entities: List[str] = field(default_factory=list)
    expected_modalities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class EvaluationResult(BaseModel):
    """Result of evaluating a single test case."""
    test_case_id: UUID
    query: str
    answer: str
    metrics: Dict[str, Any]
    passed: bool
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True


class TestSuite:
    """Test suite for RAG system evaluation."""
    
    def __init__(
        self,
        test_cases: Optional[List[TestCase]] = None,
        min_pass_rate: float = 0.8,
        min_faithfulness: float = 0.7,
        min_relevance: float = 0.7,
        max_hallucination_rate: float = 0.3,
        max_latency_ms: float = 5000.0,
    ):
        """Initialize test suite.
        
        Args:
            test_cases: List of test cases
            min_pass_rate: Minimum pass rate for suite to pass
            min_faithfulness: Minimum faithfulness score
            min_relevance: Minimum relevance score
            max_hallucination_rate: Maximum acceptable hallucination rate
            max_latency_ms: Maximum acceptable latency in milliseconds
        """
        self.test_cases = test_cases or []
        self.min_pass_rate = min_pass_rate
        self.min_faithfulness = min_faithfulness
        self.min_relevance = min_relevance
        self.max_hallucination_rate = max_hallucination_rate
        self.max_latency_ms = max_latency_ms
        self.results: List[EvaluationResult] = []
    
    @classmethod
    def from_json(cls, file_path: str) -> "TestSuite":
        """Load test suite from JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            TestSuite instance
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Test suite file not found: {file_path}")
            return cls()
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        test_cases = [TestCase(**tc) for tc in data.get('test_cases', [])]
        config = data.get('config', {})
        
        return cls(
            test_cases=test_cases,
            min_pass_rate=config.get('min_pass_rate', 0.8),
            min_faithfulness=config.get('min_faithfulness', 0.7),
            min_relevance=config.get('min_relevance', 0.7),
            max_hallucination_rate=config.get('max_hallucination_rate', 0.3),
            max_latency_ms=config.get('max_latency_ms', 5000.0),
        )
    
    def add_test_case(self, test_case: TestCase) -> None:
        """Add a test case to the suite."""
        self.test_cases.append(test_case)
    
    def evaluate_answer(
        self,
        test_case: TestCase,
        answer: Answer,
        contexts: List[str],
    ) -> EvaluationResult:
        """Evaluate a single answer against a test case.
        
        Args:
            test_case: Test case
            answer: Generated answer
            contexts: Retrieved contexts
            
        Returns:
            Evaluation result
        """
        errors = []
        metrics_dict = {}
        
        try:
            # Calculate faithfulness
            faithfulness = calculate_faithfulness(
                answer.text,
                contexts
            )
            metrics_dict['faithfulness'] = faithfulness
            
            # Calculate answer relevance
            relevance = calculate_answer_relevance(
                test_case.query,
                answer.text
            )
            metrics_dict['answer_relevance'] = relevance
            
            # Calculate context precision if expected answer provided
            if test_case.expected_answer:
                precision = calculate_context_precision(
                    test_case.query,
                    answer.text,
                    contexts,
                    test_case.expected_answer
                )
                metrics_dict['context_precision'] = precision
            
            # Calculate hallucination rate
            hallucination = calculate_hallucination_rate(
                answer.text,
                contexts
            )
            metrics_dict['hallucination_rate'] = hallucination
            
            # Add latency
            if answer.latency_ms:
                metrics_dict['latency_ms'] = answer.latency_ms
            
            # Determine if test passed
            passed = True
            
            if faithfulness < self.min_faithfulness:
                passed = False
                errors.append(f"Faithfulness {faithfulness:.2f} below threshold {self.min_faithfulness}")
            
            if relevance < self.min_relevance:
                passed = False
                errors.append(f"Relevance {relevance:.2f} below threshold {self.min_relevance}")
            
            if hallucination > self.max_hallucination_rate:
                passed = False
                errors.append(f"Hallucination rate {hallucination:.2f} above threshold {self.max_hallucination_rate}")
            
            if answer.latency_ms and answer.latency_ms > self.max_latency_ms:
                passed = False
                errors.append(f"Latency {answer.latency_ms:.0f}ms above threshold {self.max_latency_ms}ms")
        
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            passed = False
            errors.append(str(e))
        
        return EvaluationResult(
            test_case_id=test_case.id,
            query=test_case.query,
            answer=answer.text,
            metrics=metrics_dict,
            passed=passed,
            errors=errors
        )
    
    def get_pass_rate(self) -> float:
        """Calculate pass rate of evaluated test cases."""
        if not self.results:
            return 0.0
        
        passed = sum(1 for r in self.results if r.passed)
        return passed / len(self.results)
    
    def save_results(self, output_path: str) -> None:
        """Save evaluation results to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        results_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'failed': sum(1 for r in self.results if not r.passed),
            'pass_rate': self.get_pass_rate(),
            'results': [r.dict() for r in self.results]
        }
        
        with open(path, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        logger.info(f"Saved evaluation results to {output_path}")

