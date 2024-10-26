# src/main.py

import os
import logging
from typing import Union, Dict, Any
from pathlib import Path

import pandas as pd
import polars as pl
import kaggle_evaluation.aimo_2_inference_server

from solvers import (
    PatternBasedSolver,
    GeometrySolver,
    NumberTheorySolver,
    SequenceSolver,
    CombinatoricsSolver,
    ArithmeticSolver
)
from utils import setup_logging, parse_latex, mod_1000
from utils.latex_parser import LatexExpression

# Configure logging
setup_logging(level='INFO')
logger = logging.getLogger(__name__)

class AIMOSolver:
    """
    Main solver class that orchestrates different specialized solvers
    and handles problem distribution.
    """
    
    def __init__(self):
        """Initialize solver components and logging"""
        logger.info("Initializing AIMO Solver components...")
        
        # Initialize specialized solvers
        self.solvers = {
            'pattern': PatternBasedSolver(),
            'geometry': GeometrySolver(),
            'number_theory': NumberTheorySolver(),
            'sequence': SequenceSolver(),
            'combinatorics': CombinatoricsSolver(),
            'arithmetic': ArithmeticSolver()
        }
        
        # Statistics tracking
        self.stats = {
            'problems_processed': 0,
            'solver_usage': {name: 0 for name in self.solvers},
            'successful_solves': 0
        }
        
        logger.info("All solver components initialized successfully")
    
    def _identify_problem_type(
        self, problem_text: str, expressions: List[LatexExpression]
    ) -> str:
        """
        Identify the most likely problem type based on content analysis.
        
        Args:
            problem_text: Raw problem text
            expressions: Parsed LaTeX expressions
            
        Returns:
            str: Most likely problem type
        """
        # Problem type indicators
        type_indicators = {
            'geometry': [
                'triangle', 'circle', 'angle', 'perpendicular', 'parallel',
                'distance', 'area', 'point'
            ],
            'number_theory': [
                'divisible', 'prime', 'factor', 'modulo', 'remainder',
                'multiple', 'gcd', 'lcm'
            ],
            'sequence': [
                'sequence', 'series', 'fibonacci', 'term', 'arithmetic',
                'geometric', 'progression'
            ],
            'combinatorics': [
                'ways', 'arrange', 'permutation', 'combination',
                'possibility', 'different'
            ],
            'arithmetic': [
                'sum', 'product', 'mean', 'average', 'total',
                'ratio', 'proportion'
            ]
        }
        
        # Count indicators for each type
        type_scores = {ptype: 0 for ptype in type_indicators}
        text_lower = problem_text.lower()
        
        # Check for indicators in problem text
        for ptype, indicators in type_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    type_scores[ptype] += 1
        
        # Get type with highest score
        max_score = max(type_scores.values())
        if max_score > 0:
            for ptype, score in type_scores.items():
                if score == max_score:
                    return ptype
        
        # Default to pattern-based solver if no clear type
        return 'pattern'
    
    def solve_problem(self, problem_text: str) -> int:
        """
        Main solving method that distributes problem to appropriate solver.
        
        Args:
            problem_text: LaTeX formatted problem text
            
        Returns:
            int: Solution modulo 1000
        """
        try:
            # Update statistics
            self.stats['problems_processed'] += 1
            
            # Parse LaTeX expressions
            expressions = parse_latex(problem_text)
            
            # Identify problem type
            problem_type = self._identify_problem_type(problem_text, expressions)
            
            # Get appropriate solver
            solver = self.solvers[problem_type]
            self.stats['solver_usage'][problem_type] += 1
            
            # Attempt to solve
            logger.info(f"Attempting to solve using {problem_type} solver")
            result = solver.solve(problem_text)
            
            if result is not None:
                self.stats['successful_solves'] += 1
                return mod_1000(result)
            
            # Fallback to pattern solver if specific solver fails
            if problem_type != 'pattern':
                logger.info("Specific solver failed, falling back to pattern solver")
                result = self.solvers['pattern'].solve(problem_text)
                return mod_1000(result) if result is not None else 42
            
            return 42
            
        except Exception as e:
            logger.error(f"Error solving problem: {e}")
            return 42
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get solver usage statistics"""
        return {
            'total_problems': self.stats['problems_processed'],
            'successful_solves': self.stats['successful_solves'],
            'solver_usage': self.stats['solver_usage'],
            'success_rate': (
                self.stats['successful_solves'] / 
                max(1, self.stats['problems_processed'])
            )
        }

# Create global solver instance
solver = AIMOSolver()

def predict(
    id_: Union[pl.DataFrame, pd.DataFrame],
    question: Union[pl.DataFrame, pd.DataFrame]
) -> Union[pl.DataFrame, pd.DataFrame]:
    """
    Prediction function for competition submission.
    
    Args:
        id_: DataFrame containing problem ID
        question: DataFrame containing problem text
        
    Returns:
        DataFrame: Prediction result
    """
    try:
        # Extract values
        id_value = id_.item(0)
        question_text = question.item(0)
        
        logger.info(f"Processing problem {id_value}")
        
        # Get prediction
        prediction = solver.solve_problem(question_text)
        
        # Ensure valid range
        prediction = max(0, min(999, prediction))
        
        logger.info(f"Generated prediction for problem {id_value}: {prediction}")
        
        return pl.DataFrame({'id': id_value, 'answer': prediction})
        
    except Exception as e:
        logger.error(f"Error in predict function: {str(e)}")
        return pl.DataFrame({'id': id_.item(0), 'answer': 0})

# Initialize inference server
inference_server = kaggle_evaluation.aimo_2_inference_server.AIMO2InferenceServer(predict)

if __name__ == "__main__":
    if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
        inference_server.serve()
    else:
        inference_server.run_local_gateway(
            ('/kaggle/input/ai-mathematical-olympiad-progress-prize-2/test.csv',)
        )