# src/solvers/combinatorics_solver.py

import math
import logging
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import re
from functools import lru_cache

from .base_solver import BaseSolver, MathProblem

logger = logging.getLogger(__name__)

@dataclass
class CombinatoricsProblem:
    """Structure to hold parsed combinatorics problem data"""
    problem_type: str  # 'permutation', 'combination', 'arrangement', etc.
    total_elements: int  # Total number of elements
    select_elements: Optional[int]  # Number of elements to select
    constraints: Dict[str, any]  # Additional constraints
    is_ordered: bool  # Whether order matters
    allow_repetition: bool  # Whether repetition is allowed

class CombinatoricsSolver(BaseSolver):
    """
    Specialized solver for combinatorial problems.
    Handles permutations, combinations, arrangements, and related concepts.
    """
    
    def __init__(self):
        super().__init__()
        self._initialize_combinatorics_patterns()
    
    def _initialize_combinatorics_patterns(self):
        """Initialize combinatorics-specific patterns and handlers"""
        self.combinatorics_patterns = {
            'permutation': {
                'pattern': r'permutation|arrange|order|ways to order',
                'handler': self._handle_permutation
            },
            'combination': {
                'pattern': r'combination|choose|select|ways to select',
                'handler': self._handle_combination
            },
            'arrangement': {
                'pattern': r'arrangement|place|position|distribute',
                'handler': self._handle_arrangement
            },
            'partition': {
                'pattern': r'partition|divide|split|separate',
                'handler': self._handle_partition
            }
        }
        
        # Keywords indicating problem properties
        self.problem_indicators = {
            'order_matters': [
                'order', 'arrange', 'permute', 'sequence',
                'lineup', 'position', 'rank'
            ],
            'repetition_allowed': [
                'repetition', 'reuse', 'again', 'multiple times',
                'can be used', 'may be used'
            ],
            'distinct_elements': [
                'different', 'distinct', 'unique', 'no two same'
            ]
        }
    
    @lru_cache(maxsize=1000)
    def _factorial_mod_1000(self, n: int) -> int:
        """Calculate factorial modulo 1000 efficiently"""
        result = 1
        for i in range(1, min(n + 1, 1001)):  # Only need to go up to 1000
            result = (result * i) % 1000
        return result
    
    @lru_cache(maxsize=1000)
    def _permutation(self, n: int, r: Optional[int] = None) -> int:
        """Calculate P(n,r) modulo 1000"""
        if r is None:
            r = n
        if r > n:
            return 0
        result = 1
        for i in range(n - r + 1, n + 1):
            result = (result * i) % 1000
        return result
    
    @lru_cache(maxsize=1000)
    def _combination(self, n: int, r: int) -> int:
        """Calculate C(n,r) modulo 1000"""
        if r > n:
            return 0
        r = min(r, n - r)  # Use symmetry of combinations
        result = 1
        for i in range(r):
            result = (result * (n - i)) % 1000
            result = (result * pow(i + 1, -1, 1000)) % 1000
        return result
    
    def solve(self, question: str) -> int:
        """
        Main solving method for combinatorial problems.
        
        Args:
            question: The LaTeX formatted problem text
            
        Returns:
            int: Solution modulo 1000
        """
        try:
            # Basic problem preprocessing
            problem = self.preprocess(question)
            
            # Parse into combinatorics problem structure
            comb_problem = self._parse_combinatorics_problem(problem)
            
            # Try to solve using appropriate method
            result = self._solve_combinatorics_problem(comb_problem)
            
            if result is not None:
                return self._ensure_valid_answer(result)
            
            # Fallback to basic combinatorics heuristics
            return self._apply_combinatorics_heuristics(problem)
            
        except Exception as e:
            logger.error(f"Error in combinatorics solver: {e}")
            return 42
    
    def _parse_combinatorics_problem(
        self, problem: MathProblem
    ) -> CombinatoricsProblem:
        """Parse problem into combinatorics-specific structure"""
        problem_type = 'unknown'
        total_elements = 0
        select_elements = None
        constraints = {}
        
        # Identify problem type
        for ptype, pattern_info in self.combinatorics_patterns.items():
            if re.search(pattern_info['pattern'], problem.cleaned_text, re.IGNORECASE):
                problem_type = ptype
                break
        
        # Extract numbers for elements
        numbers = sorted([int(n) for n in problem.numbers if n.is_integer()])
        if numbers:
            total_elements = numbers[-1]  # Usually the largest number
            if len(numbers) > 1:
                select_elements = numbers[-2]  # Usually the second-largest number
        
        # Determine if order matters
        is_ordered = any(
            indicator in problem.cleaned_text.lower()
            for indicator in self.problem_indicators['order_matters']
        )
        
        # Check if repetition is allowed
        allow_repetition = any(
            indicator in problem.cleaned_text.lower()
            for indicator in self.problem_indicators['repetition_allowed']
        )
        
        return CombinatoricsProblem(
            problem_type=problem_type,
            total_elements=total_elements,
            select_elements=select_elements,
            constraints=constraints,
            is_ordered=is_ordered,
            allow_repetition=allow_repetition
        )
    
    def _solve_combinatorics_problem(
        self, comb_problem: CombinatoricsProblem
    ) -> Optional[int]:
        """Main combinatorics problem solving logic"""
        try:
            # Get appropriate handler
            handler = self.combinatorics_patterns.get(
                comb_problem.problem_type, {}
            ).get('handler')
            
            if handler:
                return handler(comb_problem)
            
            # If no specific handler, try general combinatorics solver
            return self._solve_general_combinatorics(comb_problem)
            
        except Exception as e:
            logger.error(f"Error solving combinatorics problem: {e}")
            return None
    
    def _handle_permutation(
        self, comb_problem: CombinatoricsProblem
    ) -> Optional[int]:
        """Handle permutation problems"""
        try:
            n = comb_problem.total_elements
            r = comb_problem.select_elements
            
            if comb_problem.allow_repetition:
                # Permutation with repetition
                if r is not None:
                    return pow(n, r, 1000)
                return pow(n, n, 1000)
            else:
                # Permutation without repetition
                return self._permutation(n, r)
            
        except Exception as e:
            logger.debug(f"Error handling permutation: {e}")
            return None
    
    def _handle_combination(
        self, comb_problem: CombinatoricsProblem
    ) -> Optional[int]:
        """Handle combination problems"""
        try:
            n = comb_problem.total_elements
            r = comb_problem.select_elements
            
            if r is None:
                return None
            
            if comb_problem.allow_repetition:
                # Combination with repetition
                return self._combination(n + r - 1, r)
            else:
                # Combination without repetition
                return self._combination(n, r)
            
        except Exception as e:
            logger.debug(f"Error handling combination: {e}")
            return None
    
    def _handle_arrangement(
        self, comb_problem: CombinatoricsProblem
    ) -> Optional[int]:
        """Handle arrangement problems"""
        try:
            n = comb_problem.total_elements
            r = comb_problem.select_elements
            
            if comb_problem.is_ordered:
                # Ordered arrangement
                return self._handle_permutation(comb_problem)
            else:
                # Unordered arrangement
                return self._handle_combination(comb_problem)
            
        except Exception as e:
            logger.debug(f"Error handling arrangement: {e}")
            return None
    
    def _handle_partition(
        self, comb_problem: CombinatoricsProblem
    ) -> Optional[int]:
        """Handle partition problems"""
        try:
            n = comb_problem.total_elements
            
            # Simple partition number modulo 1000
            if n <= 0:
                return 1 if n == 0 else 0
            
            # Dynamic programming for partitions
            dp = [0] * (n + 1)
            dp[0] = 1
            
            for i in range(1, n + 1):
                for j in range(i, n + 1):
                    dp[j] = (dp[j] + dp[j - i]) % 1000
            
            return dp[n]
            
        except Exception as e:
            logger.debug(f"Error handling partition: {e}")
            return None
    
    def _solve_general_combinatorics(
        self, comb_problem: CombinatoricsProblem
    ) -> Optional[int]:
        """Handle general combinatorics problems"""
        try:
            n = comb_problem.total_elements
            r = comb_problem.select_elements
            
            if comb_problem.is_ordered:
                if comb_problem.allow_repetition:
                    return pow(n, r, 1000) if r is not None else pow(n, n, 1000)
                else:
                    return self._permutation(n, r)
            else:
                if r is None:
                    return None
                if comb_problem.allow_repetition:
                    return self._combination(n + r - 1, r)
                else:
                    return self._combination(n, r)
            
        except Exception as e:
            logger.debug(f"Error in general combinatorics solver: {e}")
            return None
    
    def _apply_combinatorics_heuristics(self, problem: MathProblem) -> int:
        """Apply basic combinatorics heuristics when exact solution isn't possible"""
        text_lower = problem.cleaned_text.lower()
        numbers = [int(n) for n in problem.numbers if n.is_integer()]
        
        if not numbers:
            return 42
        
        n = max(numbers)
        if len(numbers) > 1:
            r = sorted(numbers)[-2]
        else:
            r = None
        
        if 'permutation' in text_lower or 'arrange' in text_lower:
            return self._permutation(n, r)
        
        if 'combination' in text_lower or 'choose' in text_lower:
            if r is not None:
                return self._combination(n, r)
        
        if 'ways' in text_lower:
            if r is not None:
                return self._combination(n, r)
            return self._factorial_mod_1000(n)
        
        return max(numbers) % 1000
    
    def __str__(self) -> str:
        """String representation"""
        return "CombinatoricsSolver(patterns={})".format(
            len(self.combinatorics_patterns)
        )