# src/utils/latex_parser.py

import re
import logging
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass
from sympy.parsing.latex import parse_latex
from sympy import sympify, SympifyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class LatexExpression:
    """Structure to hold parsed LaTeX expression data"""
    raw_text: str
    cleaned_text: str
    math_mode: str  # inline ($...$) or display (\[...\])
    variables: List[str]
    commands: Dict[str, List[str]]
    numbers: List[float]
    has_equation: bool = False

class LatexParser:
    """Parser for LaTeX mathematical expressions"""
    
    def __init__(self):
        # LaTeX command patterns
        self.patterns = {
            'math_inline': r'\$(.*?)\$',
            'math_display': r'\\\[(.*?)\\\]|\\\((.*?)\\\)',
            'command': r'\\([a-zA-Z]+)(?:\{([^}]*)\})*',
            'variable': r'(?<![a-zA-Z])([a-zA-Z])(?![a-zA-Z])',
            'number': r'-?\d*\.?\d+',
            'fraction': r'\\frac\{([^}]*)\}\{([^}]*)\}',
            'binomial': r'\\binom\{([^}]*)\}\{([^}]*)\}',
            'root': r'\\sqrt(?:\[([^]]*)\])?\{([^}]*)\}',
            'subscript': r'_\{([^}]*)\}|_([a-zA-Z0-9])',
            'superscript': r'\^\{([^}]*)\}|\^([a-zA-Z0-9])',
        }
        
        # Common mathematical environments
        self.environments = {
            'equation': r'\\begin\{equation\}(.*?)\\end\{equation\}',
            'align': r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}',
            'gather': r'\\begin\{gather\*?\}(.*?)\\end\{gather\*?\}',
        }
        
        # Mathematical operators
        self.operators = {
            '+': 'add',
            '-': 'subtract',
            '*': 'multiply',
            '/': 'divide',
            '^': 'power',
            '\\cdot': 'multiply',
            '\\times': 'multiply',
            '\\div': 'divide'
        }

    def parse_problem(self, text: str) -> List[LatexExpression]:
        """
        Parse a complete problem text and extract all LaTeX expressions.
        
        Args:
            text: Raw problem text containing LaTeX
            
        Returns:
            List[LatexExpression]: List of parsed expressions
        """
        expressions = []
        
        try:
            # Find all math mode expressions
            inline_math = self._find_inline_math(text)
            display_math = self._find_display_math(text)
            
            # Process each expression
            for expr, mode in inline_math + display_math:
                parsed = self._parse_expression(expr, mode)
                if parsed:
                    expressions.append(parsed)
            
            return expressions
        except Exception as e:
            logger.error(f"Error parsing problem: {e}")
            return []

    def _find_inline_math(self, text: str) -> List[Tuple[str, str]]:
        """Find all inline math expressions ($...$)"""
        matches = re.findall(self.patterns['math_inline'], text)
        return [(m, 'inline') for m in matches]

    def _find_display_math(self, text: str) -> List[Tuple[str, str]]:
        """Find all display math expressions (\[...\])"""
        matches = re.findall(self.patterns['math_display'], text)
        return [(m[0] or m[1], 'display') for m in matches if m[0] or m[1]]

    def _parse_expression(self, expr: str, mode: str) -> Optional[LatexExpression]:
        """Parse a single LaTeX expression"""
        try:
            # Clean the expression
            cleaned = self._clean_expression(expr)
            
            # Extract components
            variables = self._extract_variables(cleaned)
            commands = self._extract_commands(cleaned)
            numbers = self._extract_numbers(cleaned)
            
            # Check if it's an equation
            has_equation = '=' in cleaned or '\\eq' in cleaned
            
            return LatexExpression(
                raw_text=expr,
                cleaned_text=cleaned,
                math_mode=mode,
                variables=variables,
                commands=commands,
                numbers=numbers,
                has_equation=has_equation
            )
        except Exception as e:
            logger.error(f"Error parsing expression '{expr}': {e}")
            return None

    def _clean_expression(self, expr: str) -> str:
        """Clean and normalize LaTeX expression"""
        # Remove unnecessary whitespace
        expr = re.sub(r'\s+', ' ', expr.strip())
        # Normalize multiplication
        expr = expr.replace('\\cdot', '*').replace('\\times', '*')
        return expr

    def _extract_variables(self, expr: str) -> List[str]:
        """Extract variable names from expression"""
        variables = re.findall(self.patterns['variable'], expr)
        return list(set(variables))  # Remove duplicates

    def _extract_commands(self, expr: str) -> Dict[str, List[str]]:
        """Extract LaTeX commands and their arguments"""
        commands = {}
        for cmd, *args in re.findall(self.patterns['command'], expr):
            if cmd not in commands:
                commands[cmd] = []
            if args:
                commands[cmd].extend(arg for arg in args if arg)
        return commands

    def _extract_numbers(self, expr: str) -> List[float]:
        """Extract numerical values from expression"""
        numbers = []
        
        # Regular numbers
        numbers.extend(float(x) for x in re.findall(self.patterns['number'], expr))
        
        # Fractions
        fractions = re.findall(self.patterns['fraction'], expr)
        for num, den in fractions:
            try:
                numbers.append(float(sympify(num)) / float(sympify(den)))
            except (SympifyError, ValueError, ZeroDivisionError):
                continue
        
        return numbers

    def try_evaluate(self, expr: str) -> Optional[float]:
        """
        Attempt to evaluate a LaTeX expression numerically.
        
        Args:
            expr: LaTeX expression
            
        Returns:
            Optional[float]: Numerical result if evaluation successful
        """
        try:
            # Parse LaTeX to SymPy expression
            sympy_expr = parse_latex(expr)
            # Try to evaluate numerically
            result = float(sympy_expr.evalf())
            return result
        except Exception as e:
            logger.debug(f"Could not evaluate expression '{expr}': {e}")
            return None

    def extract_equations(self, text: str) -> List[str]:
        """Extract equation environments from text"""
        equations = []
        for env_pattern in self.environments.values():
            equations.extend(re.findall(env_pattern, text, re.DOTALL))
        return equations

    def identify_special_forms(self, expr: str) -> List[str]:
        """
        Identify special mathematical forms in the expression
        (e.g., quadratic equations, arithmetic sequences)
        """
        special_forms = []
        # Look for quadratic pattern: ax^2 + bx + c = 0
        if re.search(r'[a-zA-Z]\^{2}|[a-zA-Z]\^2', expr):
            special_forms.append('quadratic')
        # Look for arithmetic sequence pattern: a_n or a_{n+1}
        if re.search(r'a_\{?n\+?\d*\}?', expr):
            special_forms.append('sequence')
        return special_forms

    def parse_geometry_elements(self, text: str) -> Dict[str, List[str]]:
        """
        Parse geometric elements from text
        (e.g., triangles, angles, lines)
        """
        elements = {
            'triangles': re.findall(r'\\triangle\s*([A-Z]{3})', text),
            'angles': re.findall(r'\\angle\s*([A-Z]{3})', text),
            'segments': re.findall(r'([A-Z]{2})', text),
            'points': list(set(re.findall(r'point\s*([A-Z])', text)))
        }
        return elements

if __name__ == "__main__":
    # Example usage
    parser = LatexParser()
    test_text = r"""
    Let $x^2 + 3x + 2 = 0$ be a quadratic equation.
    Consider triangle $\triangle ABC$ where $\angle ABC = 60^\circ$.
    The sequence $a_n$ is defined by $a_{n+1} = a_n + \frac{1}{n}$.
    """
    expressions = parser.parse_problem(test_text)
    for expr in expressions:
        print(f"Found expression: {expr}")