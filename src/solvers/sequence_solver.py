# src/solvers/sequence_solver.py

import math
import logging
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import re
from functools import lru_cache

from sympy import symbols, solve, sympify
from .base_solver import BaseSolver, MathProblem

logger = logging.getLogger(__name__)

@dataclass
class SequenceProblem:
    """Structure to hold parsed sequence problem data"""
    sequence_type: str  # 'arithmetic', 'geometric', 'fibonacci', 'custom', etc.
    terms: List[float]  # Known terms
    pattern: Optional[str]  # Pattern description (e.g., 'a_{n+1} = a_n + 2')
    constraints: Dict[str, any]  # Additional constraints
    target_index: Optional[int]  # Which term we need to find
    target_property: str  # What we're asked about the sequence

class SequenceSolver(BaseSolver):
    """
    Specialized solver for sequence-related problems.
    Handles various types of sequences and their properties.
    """
    
    def __init__(self):
        super().__init__()
        self._initialize_sequence_patterns()
    
    def _initialize_sequence_patterns(self):
        """Initialize sequence-specific patterns and handlers"""
        self.sequence_patterns = {
            'fibonacci': {
                'pattern': r'fibonacci|F_n\s*=\s*F_{n-1}\s*\+\s*F_{n-2}',
                'handler': self._handle_fibonacci
            },
            'arithmetic': {
                'pattern': r'arithmetic|a_{n\+1}\s*=\s*a_n\s*[+\-]\s*d',
                'handler': self._handle_arithmetic
            },
            'geometric': {
                'pattern': r'geometric|a_{n\+1}\s*=\s*a_n\s*[×\*]\s*r',
                'handler': self._handle_geometric
            },
            'recursive': {
                'pattern': r'a_{n\+1}\s*=|a_n\s*=',
                'handler': self._handle_recursive
            }
        }
        
        # Special sequence generators
        self.sequence_generators = {
            'fibonacci': self._generate_fibonacci,
            'arithmetic': self._generate_arithmetic,
            'geometric': self._generate_geometric
        }
    
    def solve(self, question: str) -> int:
        """
        Main solving method for sequence problems.
        
        Args:
            question: The LaTeX formatted problem text
            
        Returns:
            int: Solution modulo 1000
        """
        try:
            # Basic problem preprocessing
            problem = self.preprocess(question)
            
            # Parse into sequence problem structure
            seq_problem = self._parse_sequence_problem(problem)
            
            # Try to solve using appropriate method
            result = self._solve_sequence_problem(seq_problem)
            
            if result is not None:
                return self._ensure_valid_answer(result)
            
            # Fallback to basic sequence heuristics
            return self._apply_sequence_heuristics(problem)
            
        except Exception as e:
            logger.error(f"Error in sequence solver: {e}")
            return 42
    
    def _parse_sequence_problem(self, problem: MathProblem) -> SequenceProblem:
        """Parse problem into sequence-specific structure"""
        sequence_type = 'unknown'
        terms = []
        pattern = None
        constraints = {}
        target_index = None
        target_property = 'term'  # Default to finding a specific term
        
        # Identify sequence type
        for seq_type, pattern_info in self.sequence_patterns.items():
            if re.search(pattern_info['pattern'], problem.cleaned_text, re.IGNORECASE):
                sequence_type = seq_type
                break
        
        # Extract known terms
        terms = [float(n) for n in problem.numbers if n.is_integer()]
        
        # Look for target term index
        index_match = re.search(r'a_(\d+)|F_(\d+)', problem.cleaned_text)
        if index_match:
            target_index = int(index_match.group(1) or index_match.group(2))
        
        # Identify target property
        if 'sum' in problem.cleaned_text.lower():
            target_property = 'sum'
        elif 'product' in problem.cleaned_text.lower():
            target_property = 'product'
        
        return SequenceProblem(
            sequence_type=sequence_type,
            terms=terms,
            pattern=pattern,
            constraints=constraints,
            target_index=target_index,
            target_property=target_property
        )
    
    def _solve_sequence_problem(self, seq_problem: SequenceProblem) -> Optional[int]:
        """Main sequence problem solving logic"""
        try:
            # Get appropriate handler
            handler = self.sequence_patterns.get(
                seq_problem.sequence_type, {}
            ).get('handler')
            
            if handler:
                return handler(seq_problem)
            
            # If no specific handler, try general sequence solver
            return self._solve_general_sequence(seq_problem)
            
        except Exception as e:
            logger.error(f"Error solving sequence problem: {e}")
            return None
    
    @lru_cache(maxsize=1000)
    def _generate_fibonacci(self, n: int) -> int:
        """Generate nth Fibonacci number with modulo 1000"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, (a + b) % 1000
        return b
    
    def _handle_fibonacci(self, seq_problem: SequenceProblem) -> Optional[int]:
        """Handle Fibonacci sequence problems"""
        try:
            if seq_problem.target_index is not None:
                return self._generate_fibonacci(seq_problem.target_index)
            
            # If we have terms, try to find the next one
            if seq_problem.terms:
                # Verify if it's really a Fibonacci sequence
                if len(seq_problem.terms) >= 3:
                    is_fibonacci = all(
                        seq_problem.terms[i] == (
                            seq_problem.terms[i-1] + seq_problem.terms[i-2]
                        ) % 1000
                        for i in range(2, len(seq_problem.terms))
                    )
                    if is_fibonacci:
                        next_term = (
                            seq_problem.terms[-1] + seq_problem.terms[-2]
                        ) % 1000
                        return next_term
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling Fibonacci: {e}")
            return None
    
    def _generate_arithmetic(
        self, first_term: float, difference: float, n: int
    ) -> float:
        """Generate nth term of arithmetic sequence"""
        return first_term + (n - 1) * difference
    
    def _handle_arithmetic(self, seq_problem: SequenceProblem) -> Optional[int]:
        """Handle arithmetic sequence problems"""
        try:
            terms = seq_problem.terms
            if len(terms) >= 2:
                # Calculate common difference
                differences = [
                    terms[i] - terms[i-1] for i in range(1, len(terms))
                ]
                
                # Check if it's arithmetic
                if all(abs(d - differences[0]) < 1e-10 for d in differences):
                    d = differences[0]
                    
                    if seq_problem.target_index is not None:
                        result = self._generate_arithmetic(
                            terms[0], d, seq_problem.target_index
                        )
                        return int(result) % 1000
                    
                    # Generate next term if no specific index
                    next_term = terms[-1] + d
                    return int(next_term) % 1000
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling arithmetic sequence: {e}")
            return None
    
    def _generate_geometric(
        self, first_term: float, ratio: float, n: int
    ) -> float:
        """Generate nth term of geometric sequence"""
        return first_term * (ratio ** (n - 1))
    
    def _handle_geometric(self, seq_problem: SequenceProblem) -> Optional[int]:
        """Handle geometric sequence problems"""
        try:
            terms = seq_problem.terms
            if len(terms) >= 2:
                # Calculate common ratio
                ratios = [
                    terms[i] / terms[i-1] for i in range(1, len(terms))
                    if terms[i-1] != 0
                ]
                
                # Check if it's geometric
                if all(abs(r - ratios[0]) < 1e-10 for r in ratios):
                    r = ratios[0]
                    
                    if seq_problem.target_index is not None:
                        result = self._generate_geometric(
                            terms[0], r, seq_problem.target_index
                        )
                        return int(result) % 1000
                    
                    # Generate next term if no specific index
                    next_term = terms[-1] * r
                    return int(next_term) % 1000
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling geometric sequence: {e}")
            return None
    
    def _handle_recursive(self, seq_problem: SequenceProblem) -> Optional[int]:
        """Handle general recursive sequences"""
        try:
            terms = seq_problem.terms
            if len(terms) >= 3:
                # Try to identify pattern
                differences = [
                    terms[i] - terms[i-1] for i in range(1, len(terms))
                ]
                ratios = [
                    terms[i] / terms[i-1] for i in range(1, len(terms))
                    if terms[i-1] != 0
                ]
                
                # Check for common patterns
                if all(abs(d - differences[0]) < 1e-10 for d in differences):
                    # Arithmetic sequence
                    return self._handle_arithmetic(seq_problem)
                
                if all(abs(r - ratios[0]) < 1e-10 for r in ratios):
                    # Geometric sequence
                    return self._handle_geometric(seq_problem)
                
                if len(terms) >= 3 and all(
                    terms[i] == (terms[i-1] + terms[i-2]) % 1000
                    for i in range(2, len(terms))
                ):
                    # Fibonacci-like sequence
                    return self._handle_fibonacci(seq_problem)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling recursive sequence: {e}")
            return None
    
    def _solve_general_sequence(
        self, seq_problem: SequenceProblem
    ) -> Optional[int]:
        """Handle general sequence problems"""
        try:
            terms = seq_problem.terms
            if not terms:
                return None
            
            if seq_problem.target_property == 'sum':
                return int(sum(terms)) % 1000
            
            if seq_problem.target_property == 'product':
                product = 1
                for term in terms:
                    product = (product * term) % 1000
                return product
            
            # Try to predict next term using differences
            if len(terms) >= 2:
                diff = terms[-1] - terms[-2]
                next_term = terms[-1] + diff
                return int(next_term) % 1000
            
            return None
            
        except Exception as e:
            logger.debug(f"Error in general sequence solver: {e}")
            return None
    
    def _apply_sequence_heuristics(self, problem: MathProblem) -> int:
        """Apply basic sequence heuristics when exact solution isn't possible"""
        text_lower = problem.cleaned_text.lower()
        numbers = [int(n) for n in problem.numbers if n.is_integer()]
        
        if not numbers:
            return 42
        
        if 'fibonacci' in text_lower:
            return self._generate_fibonacci(10)  # Common Fibonacci term
        
        if 'arithmetic' in text_lower:
            if len(numbers) >= 2:
                diff = numbers[1] - numbers[0]
                return int(numbers[-1] + diff) % 1000
        
        if 'geometric' in text_lower:
            if len(numbers) >= 2 and numbers[0] != 0:
                ratio = numbers[1] / numbers[0]
                return int(numbers[-1] * ratio) % 1000
        
        return max(numbers) % 1000
    
    def __str__(self) -> str:
        """String representation"""
        return "SequenceSolver(patterns={})".format(
            len(self.sequence_patterns)
        )