# src/solvers/__init__.py

from typing import Dict, Type
from .base_solver import BaseSolver
from .pattern_solver import PatternBasedSolver
from .geometry_solver import GeometrySolver
from .number_theory_solver import NumberTheorySolver
from .sequence_solver import SequenceSolver
from .combinatorics_solver import CombinatoricsSolver
from .arithmetic_solver import ArithmeticSolver

# Version information
__version__ = "0.3.0"

# Available solver mapping
AVAILABLE_SOLVERS: Dict[str, Type[BaseSolver]] = {
    "pattern": PatternBasedSolver,
    "geometry": GeometrySolver,
    "number_theory": NumberTheorySolver,
    "sequence": SequenceSolver,
    "combinatorics": CombinatoricsSolver,
    "arithmetic": ArithmeticSolver
}

def get_solver(solver_type: str = "pattern") -> BaseSolver:
    """
    Factory function to get a solver instance.
    
    Args:
        solver_type: Type of solver to instantiate
        
    Returns:
        BaseSolver: Instance of requested solver
        
    Raises:
        ValueError: If solver_type is not recognized
    """
    if solver_type not in AVAILABLE_SOLVERS:
        raise ValueError(
            f"Unknown solver type: {solver_type}. "
            f"Available types: {list(AVAILABLE_SOLVERS.keys())}"
        )
    return AVAILABLE_SOLVERS[solver_type]()

# Expose key classes and functions
__all__ = [
    "BaseSolver",
    "PatternBasedSolver",
    "GeometrySolver",
    "NumberTheorySolver",
    "SequenceSolver",
    "CombinatoricsSolver",
    "ArithmeticSolver",
    "get_solver",
    "AVAILABLE_SOLVERS",
    "__version__"
]

# Package metadata
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Specialized solvers for AIMO mathematical problems"