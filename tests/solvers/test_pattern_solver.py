# tests/solvers/test_pattern_solver.py

import pytest
from typing import Dict, List
import math
from src.solvers.pattern_solver import PatternBasedSolver
from src.utils.latex_parser import LatexExpression
from tests.data.reference_problems import ReferenceProblems

class TestPatternBasedSolver:
    """Test suite for PatternBasedSolver"""
    
    @pytest.fixture
    def solver(self):
        """Fixture to provide solver instance"""
        return PatternBasedSolver()
    
    @pytest.fixture
    def reference_problems(self):
        """Fixture to provide reference problems"""
        return ReferenceProblems()

    def test_solver_initialization(self, solver):
        """Test solver initialization"""
        assert not solver.is_initialized
        solver.initialize()
        assert solver.is_initialized
        assert solver.pattern_matchers is not None
    
    def test_basic_number_extraction(self, solver):
        """Test extraction of numbers from LaTeX"""
        test_cases = [
            (
                r"Find $x$ where $2x + 3 = 15$",
                [2, 3, 15]
            ),
            (
                r"Calculate $\frac{24}{6}$",
                [24, 6]
            ),
            (
                r"Solve for $x$ in $x^2 = 100$",
                [2, 100]
            )
        ]
        
        for latex, expected in test_cases:
            problem = solver.preprocess(latex)
            assert all(n in problem.numbers for n in expected)
    
    def test_pattern_recognition(self, solver):
        """Test pattern recognition capabilities"""
        test_cases = [
            (
                r"Find the remainder when $1234$ is divided by $5$",
                'modulo'
            ),
            (
                r"Calculate $6!$",
                'factorial'
            ),
            (
                r"Find $\sqrt{144}$",
                'square_root'
            )
        ]
        
        for latex, expected_pattern in test_cases:
            problem = solver.preprocess(latex)
            matches = solver._find_patterns(problem)
            assert any(m.pattern_type == expected_pattern for m in matches)
    
    @pytest.mark.parametrize("problem_id,expected_answer", [
        ("057f8a", 79),  # Airline schedules (LCM problem)
        ("1fce4b", 143),  # Number divisibility
        ("71beb6", 891),  # Digit sums
    ])
    def test_reference_problems(self, solver, reference_problems, problem_id, expected_answer):
        """Test solver against reference problems"""
        problem = reference_problems.get_problem(problem_id)
        result = solver.solve(problem.problem)
        assert result == expected_answer, f"Failed on problem {problem_id}"
    
    def test_modulo_handling(self, solver):
        """Test handling of modulo operations"""
        test_cases = [
            (
                "What is $2024$ modulo $1000$?",
                24
            ),
            (
                "Calculate $5^4$ modulo $1000$",
                625
            ),
            (
                "Find $999999$ modulo $1000$",
                999
            )
        ]
        
        for question, expected in test_cases:
            result = solver.solve(question)
            assert result == expected, f"Failed modulo test: {question}"
    
    def test_factorial_calculation(self, solver):
        """Test factorial calculations"""
        test_cases = [
            ("Calculate $5!$", 120),
            ("What is $3!$?", 6),
            ("Find $7!$ modulo $1000$", 40)  # 7! = 5040 ≡ 40 (mod 1000)
        ]
        
        for question, expected in test_cases:
            result = solver.solve(question)
            assert result == expected, f"Failed factorial test: {question}"
    
    def test_error_handling(self, solver):
        """Test error handling capabilities"""
        edge_cases = [
            "",  # Empty string
            "Invalid LaTeX $\\unknown{command}$",
            None,  # None input
            "$\\frac{1}{0}$"  # Division by zero
        ]
        
        for case in edge_cases:
            result = solver.solve(case)
            assert isinstance(result, int)
            assert 0 <= result <= 999
    
    def test_pattern_confidence_scoring(self, solver):
        """Test pattern confidence scoring"""
        test_cases = [
            (
                r"Find the sum of $1, 2, 3$",
                ['sum'],
                0.7  # High confidence for simple arithmetic
            ),
            (
                r"Complex equation $ax^2 + bx + c = 0$",
                ['equation'],
                0.5  # Medium confidence for equations
            ),
            (
                r"Random text without clear pattern",
                [],
                0.3  # Low confidence when no clear pattern
            )
        ]
        
        for latex, patterns, min_confidence in test_cases:
            problem = solver.preprocess(latex)
            matches = solver._find_patterns(problem)
            if patterns:
                relevant_matches = [m for m in matches if any(
                    p in m.pattern_type for p in patterns
                )]
                assert any(
                    m.confidence >= min_confidence for m in relevant_matches
                ), f"Confidence too low for {latex}"
    
    def test_expression_parsing(self, solver):
        """Test mathematical expression parsing"""
        test_cases = [
            (
                r"Solve $2x + 3 = 15$",
                ['2x + 3 = 15']
            ),
            (
                r"Calculate $\frac{a+b}{c}$ where $a=1, b=2, c=3$",
                [r'\frac{a+b}{c}', 'a=1', 'b=2', 'c=3']
            )
        ]
        
        for latex, expected_expressions in test_cases:
            problem = solver.preprocess(latex)
            assert len(problem.expressions) == len(expected_expressions)
    
    def test_problem_type_identification(self, solver):
        """Test problem type identification"""
        test_cases = [
            (
                "Find the area of triangle ABC",
                "geometry"
            ),
            (
                "Calculate the sum of first 10 numbers",
                "arithmetic"
            ),
            (
                "How many ways to arrange 5 books?",
                "combinatorics"
            )
        ]
        
        for question, expected_type in test_cases:
            problem = solver.preprocess(question)
            assert problem.problem_type == expected_type
    
    def test_solution_range(self, solver):
        """Test that solutions are always in valid range"""
        test_cases = [
            "Calculate $12345$",
            "Find $-500$",
            "What is $1.5 * 1000$"
        ]
        
        for question in test_cases:
            result = solver.solve(question)
            assert isinstance(result, int)
            assert 0 <= result <= 999

if __name__ == '__main__':
    pytest.main([__file__])