# src/solvers/arithmetic_solver.py

import math
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import re
from statistics import mean, median, mode
from functools import reduce

from sympy import simplify, symbols, solve, sympify
from .base_solver import BaseSolver, MathProblem

logger = logging.getLogger(__name__)

@dataclass
class ArithmeticProblem:
    """Structure to hold parsed arithmetic problem data"""
    problem_type: str  # 'mean', 'sum', 'product', etc.
    numbers: List[float]
    operations: List[str]
    target_value: Optional[float]
    constraints: Dict[str, any]
    unknowns: List[str]
    is_reverse: bool  # True if we need to work backwards

class ArithmeticSolver(BaseSolver):
    """
    Specialized solver for arithmetic problems.
    Handles basic operations, means, percentages, and related concepts.
    """
    
    def __init__(self):
        super().__init__()
        self._initialize_arithmetic_patterns()
    
    def _initialize_arithmetic_patterns(self):
        """Initialize arithmetic-specific patterns and handlers"""
        self.arithmetic_patterns = {
            'mean': {
                'pattern': r'mean|average',
                'handler': self._handle_mean
            },
            'sum': {
                'pattern': r'sum|total|add',
                'handler': self._handle_sum
            },
            'product': {
                'pattern': r'product|multiply',
                'handler': self._handle_product
            },
            'ratio': {
                'pattern': r'ratio|proportion|divide',
                'handler': self._handle_ratio
            },
            'remainder': {
                'pattern': r'remainder|modulo|mod',
                'handler': self._handle_remainder
            }
        }
        
        # Common arithmetic operations
        self.operations = {
            '+': lambda x, y: (x + y) % 1000,
            '-': lambda x, y: (x - y) % 1000,
            '*': lambda x, y: (x * y) % 1000,
            '/': lambda x, y: (x / y) if y != 0 else None,
            '%': lambda x, y: x % y if y != 0 else None
        }
    
    def solve(self, question: str) -> int:
        """
        Main solving method for arithmetic problems.
        
        Args:
            question: The LaTeX formatted problem text
            
        Returns:
            int: Solution modulo 1000
        """
        try:
            # Basic problem preprocessing
            problem = self.preprocess(question)
            
            # Parse into arithmetic problem structure
            arith_problem = self._parse_arithmetic_problem(problem)
            
            # Try to solve using appropriate method
            result = self._solve_arithmetic_problem(arith_problem)
            
            if result is not None:
                return self._ensure_valid_answer(result)
            
            # Fallback to basic arithmetic heuristics
            return self._apply_arithmetic_heuristics(problem)
            
        except Exception as e:
            logger.error(f"Error in arithmetic solver: {e}")
            return 42
    
    def _parse_arithmetic_problem(self, problem: MathProblem) -> ArithmeticProblem:
        """Parse problem into arithmetic-specific structure"""
        problem_type = 'unknown'
        numbers = []
        operations = []
        target_value = None
        constraints = {}
        unknowns = []
        is_reverse = False
        
        # Identify problem type
        for ptype, pattern_info in self.arithmetic_patterns.items():
            if re.search(pattern_info['pattern'], problem.cleaned_text, re.IGNORECASE):
                problem_type = ptype
                break
        
        # Extract numbers and operations
        numbers = [float(n) for n in problem.numbers]
        
        # Check if it's a reverse problem
        is_reverse = 'what' in problem.cleaned_text.lower() or 'find' in problem.cleaned_text.lower()
        
        # Extract target value if present
        target_match = re.search(r'equals\s*(\d+\.?\d*)', problem.cleaned_text)
        if target_match:
            target_value = float(target_match.group(1))
        
        return ArithmeticProblem(
            problem_type=problem_type,
            numbers=numbers,
            operations=operations,
            target_value=target_value,
            constraints=constraints,
            unknowns=unknowns,
            is_reverse=is_reverse
        )
    
    def _solve_arithmetic_problem(
        self, arith_problem: ArithmeticProblem
    ) -> Optional[int]:
        """Main arithmetic problem solving logic"""
        try:
            # Get appropriate handler
            handler = self.arithmetic_patterns.get(
                arith_problem.problem_type, {}
            ).get('handler')
            
            if handler:
                return handler(arith_problem)
            
            # If no specific handler, try general arithmetic solver
            return self._solve_general_arithmetic(arith_problem)
            
        except Exception as e:
            logger.error(f"Error solving arithmetic problem: {e}")
            return None
    
    def _handle_mean(self, arith_problem: ArithmeticProblem) -> Optional[int]:
        """Handle mean/average problems"""
        try:
            numbers = arith_problem.numbers
            if not numbers:
                return None
            
            if arith_problem.is_reverse:
                # Handle reverse mean problems
                if arith_problem.target_value is not None:
                    total = arith_problem.target_value * len(numbers)
                    missing_value = total - sum(numbers)
                    return int(missing_value) % 1000
            else:
                # Calculate direct mean
                return int(mean(numbers)) % 1000
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling mean: {e}")
            return None
    
    def _handle_sum(self, arith_problem: ArithmeticProblem) -> Optional[int]:
        """Handle sum problems"""
        try:
            numbers = arith_problem.numbers
            if not numbers:
                return None
            
            if arith_problem.is_reverse:
                # Handle reverse sum problems
                if arith_problem.target_value is not None:
                    missing_value = arith_problem.target_value - sum(numbers)
                    return int(missing_value) % 1000
            else:
                # Calculate direct sum
                return int(sum(numbers)) % 1000
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling sum: {e}")
            return None
    
    def _handle_product(self, arith_problem: ArithmeticProblem) -> Optional[int]:
        """Handle product problems"""
        try:
            numbers = arith_problem.numbers
            if not numbers:
                return None
            
            if arith_problem.is_reverse:
                # Handle reverse product problems
                if arith_problem.target_value is not None:
                    current_product = reduce(lambda x, y: x * y, numbers)
                    missing_value = arith_problem.target_value / current_product
                    return int(missing_value) % 1000
            else:
                # Calculate direct product
                product = reduce(lambda x, y: (x * y) % 1000, numbers)
                return int(product)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling product: {e}")
            return None
    
    def _handle_ratio(self, arith_problem: ArithmeticProblem) -> Optional[int]:
        """Handle ratio problems"""
        try:
            numbers = arith_problem.numbers
            if len(numbers) < 2:
                return None
            
            # Calculate ratio and reduce to lowest terms
            def gcd(a: int, b: int) -> int:
                while b:
                    a, b = b, a % b
                return a
            
            num = int(numbers[0])
            den = int(numbers[1])
            
            if den == 0:
                return None
            
            common = gcd(num, den)
            return (num // common + den // common) % 1000
            
        except Exception as e:
            logger.debug(f"Error handling ratio: {e}")
            return None
    
    def _handle_remainder(self, arith_problem: ArithmeticProblem) -> Optional[int]:
        """Handle remainder/modulo problems"""
        try:
            numbers = arith_problem.numbers
            if len(numbers) < 2:
                return None
            
            # Sort numbers to get likely dividend and divisor
            sorted_nums = sorted(numbers, reverse=True)
            dividend = int(sorted_nums[0])
            divisor = int(sorted_nums[1])
            
            if divisor == 0:
                return None
            
            return dividend % divisor % 1000
            
        except Exception as e:
            logger.debug(f"Error handling remainder: {e}")
            return None
    
    def _solve_general_arithmetic(
        self, arith_problem: ArithmeticProblem
    ) -> Optional[int]:
        """Handle general arithmetic problems"""
        try:
            numbers = arith_problem.numbers
            if not numbers:
                return None
            
            # Try common arithmetic operations
            operations = [
                lambda x: sum(x) % 1000,
                lambda x: reduce(lambda a, b: (a * b) % 1000, x),
                lambda x: int(mean(x)) % 1000,
                lambda x: int(median(x)) % 1000
            ]
            
            for op in operations:
                try:
                    result = op(numbers)
                    if 0 <= result <= 999:
                        return result
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error in general arithmetic solver: {e}")
            return None
    
    def _apply_arithmetic_heuristics(self, problem: MathProblem) -> int:
        """Apply basic arithmetic heuristics when exact solution isn't possible"""
        text_lower = problem.cleaned_text.lower()
        numbers = [float(n) for n in problem.numbers]
        
        if not numbers:
            return 42
        
        if 'mean' in text_lower or 'average' in text_lower:
            return int(mean(numbers)) % 1000
        
        if 'sum' in text_lower or 'total' in text_lower:
            return int(sum(numbers)) % 1000
        
        if 'product' in text_lower or 'multiply' in text_lower:
            product = reduce(lambda x, y: (x * y) % 1000, numbers)
            return int(product)
        
        if 'ratio' in text_lower or 'proportion' in text_lower:
            if len(numbers) >= 2:
                return int((numbers[0] / numbers[1]) * 100) % 1000
        
        return max(numbers) % 1000
    
    def __str__(self) -> str:
        """String representation"""
        return "ArithmeticSolver(patterns={})".format(
            len(self.arithmetic_patterns)
        )