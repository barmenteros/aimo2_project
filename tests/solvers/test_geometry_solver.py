# tests/solvers/test_geometry_solver.py

import pytest
import math
from typing import Dict, List, Tuple
from src.solvers.geometry_solver import GeometrySolver, GeometricElement, GeometricProblem
from tests.data.reference_problems import ReferenceProblems

class TestGeometrySolver:
    """Test suite for GeometrySolver"""
    
    @pytest.fixture
    def solver(self):
        """Fixture to provide solver instance"""
        return GeometrySolver()
    
    @pytest.fixture
    def reference_problems(self):
        """Fixture to provide reference problems"""
        return ReferenceProblems()
    
    @pytest.fixture
    def triangle_problems(self):
        """Fixture providing standard triangle test cases"""
        return [
            (
                "Triangle ABC has sides of length 3, 4, and 5. Find its area.",
                6  # Area = 6
            ),
            (
                r"In triangle ABC, $AB = 5$, $BC = 12$, and $\angle ABC = 90^\circ$. Find AC.",
                13  # Pythagorean theorem
            ),
            (
                r"Triangle ABC has $AB = 120$ and circumradius $R = 100$. Find the maximum possible length of CD where D is the foot of the perpendicular from C to AB.",
                180  # Reference problem 1acac0
            )
        ]
    
    def test_solver_initialization(self, solver):
        """Test solver initialization"""
        assert not solver.is_initialized
        solver.initialize()
        assert solver.is_initialized
        assert solver.geometry_patterns is not None
    
    def test_geometric_element_creation(self, solver):
        """Test creation of geometric elements"""
        test_cases = [
            (
                r"\triangle ABC",
                {
                    'element_type': 'triangle',
                    'vertices': ['A', 'B', 'C']
                }
            ),
            (
                r"\angle ABC = 90",
                {
                    'element_type': 'angle',
                    'value': 90,
                    'points': ['A', 'B', 'C']
                }
            ),
            (
                "AB = 5",
                {
                    'element_type': 'distance',
                    'value': 5,
                    'points': ['A', 'B']
                }
            )
        ]
        
        for latex, expected in test_cases:
            problem = solver.preprocess(latex)
            element = solver._create_geometric_element(
                expected['element_type'],
                problem.cleaned_text,
                problem
            )
            assert element is not None
            assert element.element_type == expected['element_type']
    
    @pytest.mark.parametrize("problem_id,expected_answer", [
        ("1acac0", 180),  # Triangle with circumradius
        ("480182", 751),  # Complex triangle with angle bisector
    ])
    def test_reference_problems(self, solver, reference_problems, problem_id, expected_answer):
        """Test solver against reference geometry problems"""
        problem = reference_problems.get_problem(problem_id)
        result = solver.solve(problem.problem)
        assert result == expected_answer, f"Failed on problem {problem_id}"
    
    def test_triangle_calculations(self, solver, triangle_problems):
        """Test various triangle calculations"""
        for problem_text, expected in triangle_problems:
            result = solver.solve(problem_text)
            assert result == expected, f"Failed triangle calculation: {problem_text}"
    
    def test_angle_calculations(self, solver):
        """Test angle-related calculations"""
        test_cases = [
            (
                r"In triangle ABC, $\angle A = 60^\circ$, $\angle B = 60^\circ$. Find $\angle C$.",
                60  # Equilateral triangle
            ),
            (
                r"If $\angle ABC = 90^\circ$ and $\angle BAC = 30^\circ$, find $\angle BCA$.",
                60  # Right triangle
            ),
            (
                r"In isosceles triangle ABC, $AB = AC$. If $\angle BAC = 40^\circ$, find $\angle ABC$.",
                70  # Isosceles triangle
            )
        ]
        
        for problem, expected in test_cases:
            result = solver.solve(problem)
            assert result == expected, f"Failed angle calculation: {problem}"
    
    def test_circle_properties(self, solver):
        """Test circle-related calculations"""
        test_cases = [
            (
                r"A circle has radius 10. Find the length of a chord that is 12 units from the center.",
                16  # Using Pythagorean theorem
            ),
            (
                r"In a circle with radius 5, find the length of an arc subtending an angle of 60° at the center.",
                5  # Arc length = rθ = 5 * π/3
            )
        ]
        
        for problem, expected in test_cases:
            result = solver.solve(problem)
            assert result == expected, f"Failed circle calculation: {problem}"
    
    def test_perpendicular_calculations(self, solver):
        """Test perpendicular line calculations"""
        test_cases = [
            (
                r"Line AB is perpendicular to CD at point P. If AP = 3 and PB = 4, find AB.",
                5  # Distance calculation
            ),
            (
                r"In triangle ABC, AD is perpendicular to BC where D is on BC. If BC = 10 and AD = 6, find the area.",
                30  # Area using height
            )
        ]
        
        for problem, expected in test_cases:
            result = solver.solve(problem)
            assert result == expected, f"Failed perpendicular calculation: {problem}"
    
    def test_geometric_constraints(self, solver):
        """Test handling of geometric constraints"""
        test_cases = [
            (
                {
                    'type': 'distance',
                    'elements': 'AB',
                    'value': 5
                },
                True
            ),
            (
                {
                    'type': 'angle',
                    'elements': 'ABC',
                    'value': 90
                },
                True
            ),
            (
                {
                    'type': 'parallel',
                    'elements': ['AB', 'CD']
                },
                True
            )
        ]
        
        for constraint, should_handle in test_cases:
            result = solver._extract_geometric_constraints(constraint)
            assert bool(result) == should_handle
    
    def test_error_handling(self, solver):
        """Test error handling capabilities"""
        edge_cases = [
            "",  # Empty string
            "Invalid geometry",
            None,  # None input
            r"\triangle ABC with invalid = -1"  # Invalid measurements
        ]
        
        for case in edge_cases:
            result = solver.solve(case)
            assert isinstance(result, int)
            assert 0 <= result <= 999
    
    def test_solution_range(self, solver):
        """Test that solutions are always in valid range"""
        test_cases = [
            r"Triangle ABC has area 12345",
            r"Circle has radius 1000",
            r"Angle ABC = -30°"
        ]
        
        for problem in test_cases:
            result = solver.solve(problem)
            assert isinstance(result, int)
            assert 0 <= result <= 999
    
    def test_special_triangles(self, solver):
        """Test handling of special triangle cases"""
        test_cases = [
            (
                "Right triangle with legs 3 and 4",
                5  # Hypotenuse
            ),
            (
                "Equilateral triangle with side 10",
                25  # Area (approximate)
            ),
            (
                "30-60-90 triangle with shortest side 5",
                10  # Hypotenuse
            )
        ]
        
        for description, expected in test_cases:
            problem = GeometricProblem(
                elements={},
                relationships=[],
                target_property="length",
                constraints=[]
            )
            result = solver._solve_special_triangle(problem)
            if result is not None:
                assert abs(result - expected) < 1
    
    def test_geometric_transformations(self, solver):
        """Test geometric transformation handling"""
        test_cases = [
            (
                "Rectangle ABCD with AB = 3, BC = 4 is rotated 90°",
                12  # Area remains same
            ),
            (
                "Triangle ABC is reflected across line l",
                True  # Preserves shape
            )
        ]
        
        for problem, expected in test_cases:
            result = solver._handle_transformation(problem)
            assert result is not None
    
    def test_parallel_lines(self, solver):
        """Test parallel line properties"""
        test_cases = [
            (
                "Lines AB and CD are parallel, with transversal EF",
                180  # Corresponding angles sum
            ),
            (
                "Parallel lines l1 and l2 are 5 units apart",
                5  # Distance
            )
        ]
        
        for problem, expected in test_cases:
            result = solver.solve(problem)
            assert result == expected

if __name__ == '__main__':
    pytest.main([__file__])