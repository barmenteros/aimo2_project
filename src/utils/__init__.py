# src/utils/__init__.py

import math
import logging
from typing import Dict, Union, Any, List
from .latex_parser import LatexParser, LatexExpression
from . import math_helpers

# Version information
__version__ = "0.3.0"

# Export main utility classes and functions
LATEX_PARSER = LatexParser()

def parse_latex(text: str) -> List[LatexExpression]:
    """
    Convenience function to parse LaTeX text.
    
    Args:
        text: Raw LaTeX text
        
    Returns:
        List[LatexExpression]: Parsed expressions
    """
    return LATEX_PARSER.parse_problem(text)

# Common mathematical constants
MATH_CONSTANTS = {
    'pi': math.pi,
    'e': math.e,
    'phi': (1 + math.sqrt(5)) / 2,  # Golden ratio
}

# Common mathematical functions
def mod_1000(value: Union[int, float]) -> int:
    """
    Ensure a value is properly reduced modulo 1000.
    
    Args:
        value: Number to reduce
        
    Returns:
        int: Value modulo 1000 (0-999)
    """
    try:
        result = int(value) % 1000
        return result if result >= 0 else result + 1000
    except:
        return 0

def ensure_range(value: Union[int, float], min_val: int = 0, max_val: int = 999) -> int:
    """
    Ensure a value falls within the specified range.
    
    Args:
        value: Number to check
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        int: Value clamped to range
    """
    try:
        return max(min_val, min(max_val, int(value)))
    except:
        return min_val

# Package exports
__all__ = [
    'LatexParser',
    'LatexExpression',
    'parse_latex',
    'mod_1000',
    'ensure_range',
    'MATH_CONSTANTS',
    'math_helpers',
]

# Package metadata
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Utility functions for AIMO mathematical problem solving"

# Convenience re-exports from math_helpers
from .math_helpers import (
    gcd,
    lcm,
    is_prime,
    prime_factors,
    fibonacci_mod,
    factorial_mod,
    binomial_mod
)

# Error types
class LatexParseError(Exception):
    """Raised when LaTeX parsing fails"""
    pass

class MathError(Exception):
    """Raised when a mathematical operation fails"""
    pass

def setup_logging(level: str = 'INFO') -> None:
    """
    Set up logging configuration for utilities.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    import logging
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Configuration functions
def get_config() -> Dict[str, Any]:
    """Get current utility configuration"""
    return {
        'version': __version__,
        'latex_parser': LATEX_PARSER,
        'math_constants': MATH_CONSTANTS,
    }

def validate_latex_expression(expr: str) -> bool:
    """
    Validate if a LaTeX expression is properly formatted.
    
    Args:
        expr: LaTeX expression to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        LATEX_PARSER.parse_problem(expr)
        return True
    except:
        return False