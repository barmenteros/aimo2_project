# tests/utils/test_latex_parser.py

import pytest
from typing import List, Dict, Tuple
from src.utils.latex_parser import LatexParser, LatexExpression
from tests.data.reference_problems import ReferenceProblems

class TestLatexParser:
    """Test suite for LaTeX parser"""
    
    @pytest.fixture
    def parser(self):
        """Fixture to provide parser instance"""
        return LatexParser()
    
    @pytest.fixture
    def reference_problems(self):
        """Fixture to provide reference problems"""
        return ReferenceProblems()
    
    @pytest.fixture
    def test_expressions(self):
        """Fixture providing standard LaTeX test expressions"""
        return [
            (
                r"$x^2 + 2x + 1$",
                {
                    'variables': ['x'],
                    'has_equation': False,
                    'numbers': [2, 1]
                }
            ),
            (
                r"\[\frac{a+b}{c} = d\]",
                {
                    'variables': ['a', 'b', 'c', 'd'],
                    'has_equation': True,
                    'numbers': []
                }
            ),
            (
                r"$\triangle ABC$ where $AB = 5$",
                {
                    'variables': ['A', 'B', 'C'],
                    'has_equation': True,
                    'numbers': [5]
                }
            )
        ]
    
    def test_basic_parsing(self, parser, test_expressions):
        """Test basic LaTeX parsing functionality"""
        for latex, expected in test_expressions:
            expressions = parser.parse_problem(latex)
            assert expressions
            expr = expressions[0]
            assert set(expr.variables) == set(expected['variables'])
            assert expr.has_equation == expected['has_equation']
            assert all(n in expr.numbers for n in expected['numbers'])
    
    def test_math_mode_detection(self, parser):
        """Test detection of different math modes"""
        test_cases = [
            (
                r"Inline math $x + y$",
                "inline"
            ),
            (
                r"Display math \[x + y\]",
                "display"
            ),
            (
                r"Parentheses \(x + y\)",
                "inline"
            )
        ]
        
        for latex, expected_mode in test_cases:
            expressions = parser.parse_problem(latex)
            assert expressions[0].math_mode == expected_mode
    
    def test_command_extraction(self, parser):
        """Test LaTeX command extraction"""
        test_cases = [
            (
                r"$\sqrt{x}$",
                {'sqrt': ['x']}
            ),
            (
                r"$\frac{a}{b}$",
                {'frac': ['a', 'b']}
            ),
            (
                r"$\triangle ABC$",
                {'triangle': []}
            )
        ]
        
        for latex, expected_commands in test_cases:
            expressions = parser.parse_problem(latex)
            assert expressions[0].commands
            for cmd, args in expected_commands.items():
                assert cmd in expressions[0].commands
                if args:
                    assert expressions[0].commands[cmd] == args
    
    def test_number_extraction(self, parser):
        """Test numerical value extraction"""
        test_cases = [
            (
                r"$1.5x + 2$",
                [1.5, 2]
            ),
            (
                r"$\frac{3}{4}$",
                [3, 4, 0.75]
            ),
            (
                r"$-2.5$",
                [-2.5]
            )
        ]
        
        for latex, expected_numbers in test_cases:
            expressions = parser.parse_problem(latex)
            for num in expected_numbers:
                assert any(abs(n - num) < 1e-10 for n in expressions[0].numbers)
    
    def test_special_forms(self, parser):
        """Test identification of special mathematical forms"""
        test_cases = [
            (
                r"$ax^2 + bx + c = 0$",
                ['quadratic']
            ),
            (
                r"$a_n = a_{n-1} + a_{n-2}$",
                ['sequence']
            ),
            (
                r"$\sum_{i=1}^n i$",
                ['summation']
            )
        ]
        
        for latex, expected_forms in test_cases:
            forms = parser.identify_special_forms(latex)
            assert all(form in forms for form in expected_forms)
    
    def test_error_handling(self, parser):
        """Test error handling for invalid input"""
        edge_cases = [
            "",  # Empty string
            None,  # None input
            r"$\invalid{command}$",  # Invalid command
            r"Unmatched $formula",  # Unmatched delimiters
            r"$$"  # Empty math mode
        ]
        
        for case in edge_cases:
            # Should not raise exception
            result = parser.parse_problem(case)
            assert isinstance(result, list)
    
    def test_geometry_parsing(self, parser):
        """Test parsing of geometric elements"""
        test_cases = [
            (
                r"Triangle $\triangle ABC$ with $\angle ABC = 90^\circ$",
                {
                    'triangles': ['ABC'],
                    'angles': ['ABC']
                }
            ),
            (
                r"Points $A$, $B$, and $C$ form a line segment $AB$ of length 5",
                {
                    'points': ['A', 'B', 'C'],
                    'segments': ['AB']
                }
            )
        ]
        
        for latex, expected in test_cases:
            elements = parser.parse_geometry_elements(latex)
            for key, values in expected.items():
                assert all(val in elements[key] for val in values)
    
    @pytest.mark.parametrize("problem_id", ["1acac0", "480182"])
    def test_reference_geometry_problems(self, parser, reference_problems, problem_id):
        """Test parser with reference geometry problems"""
        problem = reference_problems.get_problem(problem_id)
        expressions = parser.parse_problem(problem.problem)
        assert expressions
        # Verify geometry-specific elements are detected
        geometry_elements = parser.parse_geometry_elements(problem.problem)
        assert geometry_elements['triangles'] or geometry_elements['angles']
    
    def test_equation_detection(self, parser):
        """Test equation detection in expressions"""
        test_cases = [
            (
                r"$x + 1 = 5$",
                True
            ),
            (
                r"$x + y$",
                False
            ),
            (
                r"$a \equiv b \pmod{5}$",
                True
            )
        ]
        
        for latex, should_be_equation in test_cases:
            expressions = parser.parse_problem(latex)
            assert expressions[0].has_equation == should_be_equation
    
    def test_nested_structures(self, parser):
        """Test parsing of nested LaTeX structures"""
        test_cases = [
            (
                r"$\sqrt{\frac{a}{b}}$",
                {'sqrt': True, 'frac': True}
            ),
            (
                r"$\sum_{i=1}^n \frac{1}{i^2}$",
                {'sum': True, 'frac': True}
            )
        ]
        
        for latex, expected_commands in test_cases:
            expressions = parser.parse_problem(latex)
            commands = expressions[0].commands
            for cmd, should_exist in expected_commands.items():
                assert (cmd in commands) == should_exist
    
    def test_expression_cleaning(self, parser):
        """Test LaTeX expression cleaning"""
        test_cases = [
            (
                r"$x  +  y$",
                "x + y"
            ),
            (
                r"$\,a\,b\,$",
                "a b"
            ),
            (
                r"$x\\y$",
                "x y"
            )
        ]
        
        for latex, expected_clean in test_cases:
            expressions = parser.parse_problem(latex)
            assert expressions[0].cleaned_text.replace(" ", "") == expected_clean.replace(" ", "")
    
    def test_multi_expression_parsing(self, parser):
        """Test parsing multiple expressions in one problem"""
        latex = r"""
        Find $x$ where $x^2 = 4$ and $x > 0$.
        Also calculate $\frac{x}{2}$.
        """
        
        expressions = parser.parse_problem(latex)
        assert len(expressions) >= 3
        # Check each expression is parsed correctly
        assert any(expr.has_equation for expr in expressions)
        assert any('frac' in expr.commands for expr in expressions)

if __name__ == '__main__':
    pytest.main([__file__])