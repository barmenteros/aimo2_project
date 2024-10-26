# src/solvers/base_solver.py

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MathProblem:
    """Structure to hold parsed mathematical problem data"""
    id: str
    raw_text: str
    cleaned_text: str
    expressions: List[str]
    numbers: List[float]
    problem_type: str = "unknown"
    latex_commands: Dict[str, List[str]] = None
    metadata: Dict[str, Any] = None

class BaseSolver(ABC):
    """
    Abstract base class for mathematics problem solvers.
    Provides common functionality and enforces implementation of key methods.
    """
    
    def __init__(self):
        self.is_initialized = False
        # Common LaTeX patterns
        self.latex_patterns = {
            'math_mode': r'\$(.*?)\$|\\\[(.*?)\\\]|\\\((.*?)\\\)',
            'commands': r'\\[a-zA-Z]+',
            'numbers': r'-?\d*\.?\d+',
            'fractions': r'\\frac\{([^}]*)\}\{([^}]*)\}',
            'exponents': r'\^{([^}]*)}|\^(\d+)',
        }
        # Mathematical operators and their priorities
        self.operators = {
            '+': 1, '-': 1,
            '*': 2, '/': 2,
            '^': 3
        }
    
    @abstractmethod
    def solve(self, problem_text: str) -> int:
        """
        Main solving method to be implemented by concrete solver classes.
        
        Args:
            problem_text: The raw problem text in LaTeX format
            
        Returns:
            int: Solution modulo 1000
        """
        pass
    
    def initialize(self) -> None:
        """Initialize solver resources"""
        if not self.is_initialized:
            logger.info(f"Initializing {self.__class__.__name__}")
            try:
                self._setup_resources()
                self.is_initialized = True
                logger.info(f"{self.__class__.__name__} initialization complete")
            except Exception as e:
                logger.error(f"Initialization error: {e}")
                raise
    
    def _setup_resources(self) -> None:
        """Setup any resources needed by the solver"""
        pass
    
    def preprocess(self, problem_text: str) -> MathProblem:
        """
        Process raw LaTeX problem text into structured format.
        
        Args:
            problem_text: Raw LaTeX formatted problem text
            
        Returns:
            MathProblem: Structured problem data
        """
        try:
            # Basic cleanup
            cleaned_text = self._clean_text(problem_text)
            
            # Extract components
            expressions = self._extract_math_expressions(cleaned_text)
            numbers = self._extract_numbers(cleaned_text)
            latex_commands = self._extract_latex_commands(cleaned_text)
            
            # Identify problem type
            problem_type = self._identify_problem_type(cleaned_text)
            
            return MathProblem(
                id=str(hash(problem_text)),
                raw_text=problem_text,
                cleaned_text=cleaned_text,
                expressions=expressions,
                numbers=numbers,
                problem_type=problem_type,
                latex_commands=latex_commands,
                metadata={}
            )
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize LaTeX text"""
        text = text.replace('\\\\', ' ')
        text = text.replace('\\,', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_math_expressions(self, text: str) -> List[str]:
        """Extract mathematical expressions from text"""
        expressions = []
        for pattern in [r'\$(.*?)\$', r'\\\[(.*?)\\\]', r'\\\((.*?)\\\)']:
            expressions.extend(re.findall(pattern, text))
        return [expr for expr in expressions if expr]
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numerical values from text"""
        numbers = []
        # Extract regular numbers
        numbers.extend(float(x) for x in re.findall(r'-?\d*\.?\d+', text))
        # Extract fractions
        fractions = re.findall(r'\\frac\{(\d+)\}\{(\d+)\}', text)
        numbers.extend(float(n)/float(d) for n, d in fractions)
        return numbers
    
    def _extract_latex_commands(self, text: str) -> Dict[str, List[str]]:
        """Extract LaTeX commands and their arguments"""
        commands = {}
        # Find all LaTeX commands
        for cmd in re.findall(r'\\([a-zA-Z]+)(?:\{([^}]*)\})?', text):
            command, args = cmd
            if command not in commands:
                commands[command] = []
            if args:
                commands[command].append(args)
        return commands
    
    def _identify_problem_type(self, text: str) -> str:
        """Identify the type of mathematical problem"""
        keywords = {
            'geometry': ['triangle', 'angle', 'circle', 'square', 'rectangle'],
            'algebra': ['solve', 'equation', 'polynomial', 'factor'],
            'number_theory': ['prime', 'factor', 'modulo', 'divisor'],
            'combinatorics': ['permutation', 'combination', 'ways'],
            'sequence': ['sequence', 'series', 'fibonacci', 'arithmetic']
        }
        
        text_lower = text.lower()
        for ptype, words in keywords.items():
            if any(word in text_lower for word in words):
                return ptype
        return "unknown"
    
    def _ensure_valid_answer(self, result: Any) -> int:
        """Ensure the answer is a valid integer modulo 1000"""
        try:
            if result is None:
                return 0
            # Convert to integer and take modulo 1000
            answer = int(float(result)) % 1000
            # Handle negative numbers
            return answer if answer >= 0 else answer + 1000
        except Exception as e:
            logger.error(f"Error in answer validation: {e}")
            return 0
    
    def __str__(self) -> str:
        """String representation of the solver"""
        return f"{self.__class__.__name__}(initialized={self.is_initialized})"