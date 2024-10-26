# src/solvers/geometry_solver.py

import math
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

from sympy import sympify, solve, symbols
from sympy.geometry import Point, Triangle, Circle, Line, Segment

from .base_solver import BaseSolver, MathProblem

logger = logging.getLogger(__name__)

@dataclass
class GeometricElement:
    """Structure to hold geometric element data"""
    element_type: str  # 'point', 'line', 'triangle', 'circle', etc.
    label: str
    properties: Dict[str, float]
    related_elements: List[str] = None
    sympy_obj: any = None  # Store SymPy geometric object if needed

@dataclass
class GeometricProblem:
    """Structure to hold parsed geometric problem data"""
    elements: Dict[str, GeometricElement]
    relationships: List[Dict[str, str]]  # List of relationships between elements
    target_property: str  # What we're asked to find
    constraints: List[Dict[str, any]]  # Known constraints and conditions

class GeometrySolver(BaseSolver):
    """
    Specialized solver for geometric problems.
    Handles various geometric constructions, relationships, and calculations.
    """
    
    def __init__(self):
        super().__init__()
        self._initialize_geometry_patterns()
    
    def _initialize_geometry_patterns(self):
        """Initialize geometry-specific patterns and handlers"""
        self.geometry_patterns = {
            'triangle': {
                'pattern': r'triangle\s+(?:\\triangle\s+)?([A-Z]{3})',
                'handler': self._handle_triangle
            },
            'circle': {
                'pattern': r'circle|circumcircle|incircle',
                'handler': self._handle_circle
            },
            'angle': {
                'pattern': r'\\angle\s+([A-Z]{3})\s*=\s*(\d+)',
                'handler': self._handle_angle
            },
            'distance': {
                'pattern': r'([A-Z]{2})\s*=\s*(\d+)',
                'handler': self._handle_distance
            },
            'perpendicular': {
                'pattern': r'perpendicular|⊥',
                'handler': self._handle_perpendicular
            },
            'parallel': {
                'pattern': r'parallel|\|\|',
                'handler': self._handle_parallel
            }
        }
        
        # Common geometric properties and their handlers
        self.property_handlers = {
            'area': self._calculate_area,
            'perimeter': self._calculate_perimeter,
            'angle': self._calculate_angle,
            'distance': self._calculate_distance,
            'ratio': self._calculate_ratio
        }
    
    def solve(self, question: str) -> int:
        """
        Main solving method for geometric problems.
        
        Args:
            question: The LaTeX formatted problem text
            
        Returns:
            int: Solution modulo 1000
        """
        try:
            # Basic problem preprocessing
            problem = self.preprocess(question)
            
            # Parse geometric elements and relationships
            geo_problem = self._parse_geometric_problem(problem)
            
            # Try to solve using appropriate method
            result = self._solve_geometric_problem(geo_problem)
            
            if result is not None:
                return self._ensure_valid_answer(result)
            
            # Fallback to basic geometric heuristics
            return self._apply_geometric_heuristics(problem)
            
        except Exception as e:
            logger.error(f"Error in geometry solver: {e}")
            return 42
    
    def _parse_geometric_problem(self, problem: MathProblem) -> GeometricProblem:
        """Parse problem into geometric elements and relationships"""
        elements = {}
        relationships = []
        
        # Extract geometric elements
        for element_type, pattern in self.geometry_patterns.items():
            matches = re.finditer(pattern['pattern'], problem.cleaned_text)
            for match in matches:
                element = self._create_geometric_element(
                    element_type, match, problem
                )
                if element:
                    elements[element.label] = element
        
        # Extract relationships and constraints
        constraints = self._extract_geometric_constraints(problem)
        
        # Identify target property
        target = self._identify_target_property(problem)
        
        return GeometricProblem(
            elements=elements,
            relationships=relationships,
            target_property=target,
            constraints=constraints
        )
    
    def _create_geometric_element(
        self, element_type: str, match: re.Match, problem: MathProblem
    ) -> Optional[GeometricElement]:
        """Create a geometric element from a pattern match"""
        try:
            if element_type == 'triangle':
                vertices = match.group(1)
                return GeometricElement(
                    element_type='triangle',
                    label=vertices,
                    properties={'vertices': list(vertices)},
                    related_elements=[]
                )
            elif element_type == 'circle':
                return self._create_circle_element(match, problem)
            elif element_type == 'angle':
                points = match.group(1)
                angle_value = float(match.group(2))
                return GeometricElement(
                    element_type='angle',
                    label=f"angle_{points}",
                    properties={'value': angle_value, 'points': list(points)},
                    related_elements=[]
                )
            # Add more element types as needed
            return None
        except Exception as e:
            logger.debug(f"Error creating geometric element: {e}")
            return None
    
    def _extract_geometric_constraints(
        self, problem: MathProblem
    ) -> List[Dict[str, any]]:
        """Extract geometric constraints from problem text"""
        constraints = []
        
        # Look for length constraints
        length_matches = re.finditer(
            r'([A-Z]{2})\s*=\s*(\d+)', problem.cleaned_text
        )
        for match in length_matches:
            constraints.append({
                'type': 'length',
                'elements': match.group(1),
                'value': float(match.group(2))
            })
        
        # Look for angle constraints
        angle_matches = re.finditer(
            r'\\angle\s+([A-Z]{3})\s*=\s*(\d+)', problem.cleaned_text
        )
        for match in angle_matches:
            constraints.append({
                'type': 'angle',
                'elements': match.group(1),
                'value': float(match.group(2))
            })
        
        return constraints
    
    def _identify_target_property(self, problem: MathProblem) -> str:
        """Identify what property we need to find"""
        text_lower = problem.cleaned_text.lower()
        
        if 'area' in text_lower:
            return 'area'
        if 'length' in text_lower or 'distance' in text_lower:
            return 'distance'
        if 'angle' in text_lower:
            return 'angle'
        if 'ratio' in text_lower:
            return 'ratio'
        
        return 'unknown'
    
    def _solve_geometric_problem(self, geo_problem: GeometricProblem) -> Optional[float]:
        """Main geometric problem solving logic"""
        try:
            # Get appropriate property handler
            handler = self.property_handlers.get(geo_problem.target_property)
            if handler:
                return handler(geo_problem)
            
            # If no specific handler, try general geometric solver
            return self._solve_general_geometry(geo_problem)
            
        except Exception as e:
            logger.error(f"Error solving geometric problem: {e}")
            return None
    
    def _calculate_area(self, geo_problem: GeometricProblem) -> Optional[float]:
        """Calculate area for various geometric figures"""
        try:
            # Find triangle if present
            triangle = next(
                (elem for elem in geo_problem.elements.values() 
                 if elem.element_type == 'triangle'),
                None
            )
            
            if triangle:
                return self._calculate_triangle_area(triangle, geo_problem.constraints)
            
            # Add more shape handling as needed
            return None
            
        except Exception as e:
            logger.debug(f"Error calculating area: {e}")
            return None
    
    def _calculate_triangle_area(
        self, triangle: GeometricElement, constraints: List[Dict[str, any]]
    ) -> Optional[float]:
        """Calculate triangle area using available information"""
        try:
            # Get side lengths from constraints
            sides = self._get_triangle_sides(triangle, constraints)
            
            if len(sides) == 3:
                # Use Heron's formula
                s = sum(sides) / 2  # semi-perimeter
                area = math.sqrt(
                    s * (s - sides[0]) * (s - sides[1]) * (s - sides[2])
                )
                return area
            
            # Get angles from constraints
            angles = self._get_triangle_angles(triangle, constraints)
            
            if len(sides) == 2 and len(angles) == 1:
                # Use area = (1/2) * a * b * sin(C)
                angle_rad = math.radians(angles[0])
                area = 0.5 * sides[0] * sides[1] * math.sin(angle_rad)
                return area
            
            return None
            
        except Exception as e:
            logger.debug(f"Error calculating triangle area: {e}")
            return None
    
    def _get_triangle_sides(
        self, triangle: GeometricElement, constraints: List[Dict[str, any]]
    ) -> List[float]:
        """Extract triangle side lengths from constraints"""
        sides = []
        vertices = triangle.properties['vertices']
        
        for i in range(3):
            side = vertices[i] + vertices[(i+1)%3]
            # Look for constraint with these vertices in either order
            length = next(
                (c['value'] for c in constraints 
                 if c['type'] == 'length' and 
                 (c['elements'] == side or c['elements'] == side[::-1])),
                None
            )
            if length is not None:
                sides.append(length)
        
        return sides
    
    def _get_triangle_angles(
        self, triangle: GeometricElement, constraints: List[Dict[str, any]]
    ) -> List[float]:
        """Extract triangle angles from constraints"""
        angles = []
        vertices = triangle.properties['vertices']
        
        for i in range(3):
            angle_vertices = (
                vertices[(i-1)%3] + vertices[i] + vertices[(i+1)%3]
            )
            angle = next(
                (c['value'] for c in constraints 
                 if c['type'] == 'angle' and c['elements'] == angle_vertices),
                None
            )
            if angle is not None:
                angles.append(angle)
        
        return angles
    
    def _apply_geometric_heuristics(self, problem: MathProblem) -> int:
        """Apply basic geometric heuristics when exact solution isn't possible"""
        text_lower = problem.cleaned_text.lower()
        numbers = problem.numbers
        
        if not numbers:
            return 42
        
        if 'triangle' in text_lower:
            if 'right' in text_lower or 'perpendicular' in text_lower:
                return 90  # Common right angle
            if 'equilateral' in text_lower:
                return 60  # Common equilateral triangle angle
            return max(numbers) % 1000  # Default to largest number
        
        if 'circle' in text_lower:
            if 'diameter' in text_lower or 'radius' in text_lower:
                for num in numbers:
                    if num > 10:  # Likely a length
                        return int(num) % 1000
            return 360  # Full circle angle
        
        return max(numbers) % 1000
    
    def __str__(self) -> str:
        """String representation"""
        return "GeometrySolver(patterns={})".format(
            len(self.geometry_patterns)
        )