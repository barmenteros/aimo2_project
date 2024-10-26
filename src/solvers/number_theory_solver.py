# src/solvers/number_theory_solver.py

import math
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from functools import reduce
import re

from sympy import isprime, primefactors, gcd, lcm
from .base_solver import BaseSolver, MathProblem

logger = logging.getLogger(__name__)

@dataclass
class NumberTheoryProblem:
    """Structure to hold parsed number theory problem data"""
    problem_type: str  # 'divisibility', 'modulo', 'prime', etc.
    numbers: List[int]
    operations: List[str]
    constraints: Dict[str, any]
    target_type: str  # What kind of answer we're looking for

class NumberTheorySolver(BaseSolver):
    """
    Specialized solver for number theory problems.
    Handles divisibility, modular arithmetic, prime numbers, and related concepts.
    """
    
    def __init__(self):
        super().__init__()
        self._initialize_number_patterns()
    
    def _initialize_number_patterns(self):
        """Initialize number theory specific patterns and handlers"""
        self.number_patterns = {
            'divisibility': {
                'pattern': r'divisible|divides|factor',
                'handler': self._handle_divisibility
            },
            'modulo': {
                'pattern': r'modulo\s+(\d+)|mod\s+(\d+)',
                'handler': self._handle_modulo
            },
            'prime': {
                'pattern': r'prime|factor',
                'handler': self._handle_prime
            },
            'gcd': {
                'pattern': r'greatest\s+common\s+divisor|GCD|highest\s+common\s+factor',
                'handler': self._handle_gcd
            },
            'lcm': {
                'pattern': r'least\s+common\s+multiple|LCM',
                'handler': self._handle_lcm
            }
        }
        
        # Common number theory operations
        self.operations = {
            'mod': lambda x, y: x % y,
            'gcd': math.gcd,
            'lcm': lambda x, y: abs(x * y) // math.gcd(x, y),
            'phi': self._euler_totient,
            'sigma': self._sum_of_divisors
        }
    
    def solve(self, question: str) -> int:
        """
        Main solving method for number theory problems.
        
        Args:
            question: The LaTeX formatted problem text
            
        Returns:
            int: Solution modulo 1000
        """
        try:
            # Basic problem preprocessing
            problem = self.preprocess(question)
            
            # Parse into number theory problem structure
            nt_problem = self._parse_number_theory_problem(problem)
            
            # Try to solve using appropriate method
            result = self._solve_number_theory_problem(nt_problem)
            
            if result is not None:
                return self._ensure_valid_answer(result)
            
            # Fallback to basic number theory heuristics
            return self._apply_number_theory_heuristics(problem)
            
        except Exception as e:
            logger.error(f"Error in number theory solver: {e}")
            return 42
    
    def _parse_number_theory_problem(self, problem: MathProblem) -> NumberTheoryProblem:
        """Parse problem into number theory specific structure"""
        numbers = []
        operations = []
        constraints = {}
        
        # Extract numbers
        numbers.extend(int(n) for n in problem.numbers if n.is_integer())
        
        # Identify problem type and target
        problem_type = 'unknown'
        target_type = 'unknown'
        
        for pattern_type, pattern_info in self.number_patterns.items():
            if re.search(pattern_info['pattern'], problem.cleaned_text, re.IGNORECASE):
                problem_type = pattern_type
                break
        
        # Identify target type
        if 'remainder' in problem.cleaned_text.lower():
            target_type = 'remainder'
        elif 'factor' in problem.cleaned_text.lower():
            target_type = 'factor'
        elif 'multiple' in problem.cleaned_text.lower():
            target_type = 'multiple'
        
        return NumberTheoryProblem(
            problem_type=problem_type,
            numbers=numbers,
            operations=operations,
            constraints=constraints,
            target_type=target_type
        )
    
    def _solve_number_theory_problem(
        self, nt_problem: NumberTheoryProblem
    ) -> Optional[int]:
        """Main number theory problem solving logic"""
        try:
            # Get appropriate handler
            handler = self.number_patterns.get(nt_problem.problem_type, {}).get('handler')
            if handler:
                return handler(nt_problem)
            
            # If no specific handler, try general number theory solver
            return self._solve_general_number_theory(nt_problem)
            
        except Exception as e:
            logger.error(f"Error solving number theory problem: {e}")
            return None
    
    def _handle_divisibility(
        self, nt_problem: NumberTheoryProblem
    ) -> Optional[int]:
        """Handle divisibility-related problems"""
        try:
            numbers = nt_problem.numbers
            if len(numbers) >= 2:
                # Try common divisibility operations
                operations = [
                    lambda x, y: math.gcd(x, y),
                    lambda x, y: lcm(x, y) % 1000,
                    lambda x, y: (x % y) if y != 0 else 0
                ]
                
                for op in operations:
                    try:
                        result = op(numbers[0], numbers[1])
                        if 0 <= result <= 999:
                            return result
                    except:
                        continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling divisibility: {e}")
            return None
    
    def _handle_modulo(
        self, nt_problem: NumberTheoryProblem
    ) -> Optional[int]:
        """Handle modulo operation problems"""
        try:
            numbers = nt_problem.numbers
            if len(numbers) >= 2:
                # Find potential modulus (usually the last number)
                modulus = numbers[-1]
                value = numbers[0]
                
                return value % modulus
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling modulo: {e}")
            return None
    
    def _handle_prime(
        self, nt_problem: NumberTheoryProblem
    ) -> Optional[int]:
        """Handle prime number related problems"""
        try:
            numbers = nt_problem.numbers
            if not numbers:
                return None
            
            # Try common prime-related operations
            operations = [
                lambda x: len(primefactors(x)) % 1000,  # Number of prime factors
                lambda x: max(primefactors(x)) % 1000,  # Largest prime factor
                lambda x: sum(primefactors(x)) % 1000   # Sum of prime factors
            ]
            
            for op in operations:
                try:
                    result = op(max(numbers))
                    if 0 <= result <= 999:
                        return result
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling prime: {e}")
            return None
    
    def _handle_gcd(
        self, nt_problem: NumberTheoryProblem
    ) -> Optional[int]:
        """Handle greatest common divisor problems"""
        try:
            numbers = nt_problem.numbers
            if len(numbers) >= 2:
                # Calculate GCD of all numbers
                result = reduce(math.gcd, numbers)
                return result % 1000
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling GCD: {e}")
            return None
    
    def _handle_lcm(
        self, nt_problem: NumberTheoryProblem
    ) -> Optional[int]:
        """Handle least common multiple problems"""
        try:
            numbers = nt_problem.numbers
            if len(numbers) >= 2:
                # Calculate LCM of all numbers
                result = reduce(lcm, numbers)
                return result % 1000
            
            return None
            
        except Exception as e:
            logger.debug(f"Error handling LCM: {e}")
            return None
    
    def _euler_totient(self, n: int) -> int:
        """Calculate Euler's totient function φ(n)"""
        result = n
        p = 2
        while p * p <= n:
            if n % p == 0:
                while n % p == 0:
                    n //= p
                result *= (1.0 - (1.0 / float(p)))
            p += 1
        if n > 1:
            result *= (1.0 - (1.0 / float(n)))
        return int(result)
    
    def _sum_of_divisors(self, n: int) -> int:
        """Calculate sum of divisors σ(n)"""
        result = 0
        for i in range(1, int(math.sqrt(n)) + 1):
            if n % i == 0:
                result += i
                if i != n // i:
                    result += n // i
        return result
    
    def _find_primitive_root(self, n: int) -> Optional[int]:
        """Find smallest primitive root modulo n"""
        def is_primitive_root(a: int, n: int, factors: List[int]) -> bool:
            phi = self._euler_totient(n)
            for factor in factors:
                if pow(a, phi // factor, n) == 1:
                    return False
            return True
        
        if n <= 1:
            return None
            
        phi = self._euler_totient(n)
        factors = primefactors(phi)
        
        for a in range(2, n):
            if is_primitive_root(a, n, factors):
                return a
        
        return None
    
    def _apply_number_theory_heuristics(self, problem: MathProblem) -> int:
        """Apply basic number theory heuristics when exact solution isn't possible"""
        text_lower = problem.cleaned_text.lower()
        numbers = [int(n) for n in problem.numbers if n.is_integer()]
        
        if not numbers:
            return 42
        
        if 'prime' in text_lower:
            # Try prime-related calculations
            n = max(numbers)
            if isprime(n):
                return n % 1000
            return len(primefactors(n)) % 1000
        
        if 'modulo' in text_lower or 'remainder' in text_lower:
            # Try modulo operations
            if len(numbers) >= 2:
                return numbers[0] % numbers[-1]
        
        if 'divisor' in text_lower or 'factor' in text_lower:
            # Try divisor-related calculations
            n = max(numbers)
            return self._sum_of_divisors(n) % 1000
        
        # Default to largest number modulo 1000
        return max(numbers) % 1000
    
    def __str__(self) -> str:
        """String representation"""
        return "NumberTheorySolver(patterns={})".format(
            len(self.number_patterns)
        )