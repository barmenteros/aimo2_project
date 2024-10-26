# tests/data/reference_problems.py

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ReferenceProblem:
    """Structure to hold reference problem data and metadata"""
    id: str
    problem: str
    answer: int
    category: str
    key_concepts: List[str]
    special_features: List[str]

class ReferenceProblems:
    """Container for reference problems with metadata and utilities"""
    
    def __init__(self):
        self.problems: Dict[str, ReferenceProblem] = self._initialize_problems()
        
    def _initialize_problems(self) -> Dict[str, ReferenceProblem]:
        """Initialize the reference problems with metadata"""
        return {
            "057f8a": ReferenceProblem(
                id="057f8a",
                problem=("Three airline companies operate flights from Dodola island. "
                        "Each company has a different schedule of departures. The first "
                        "company departs every 100 days, the second every 120 days and "
                        "the third every 150 days. What is the greatest positive integer "
                        "$d$ for which it is true that there will be $d$ consecutive days "
                        "without a flight from Dodola island, regardless of the departure "
                        "times of the various airlines?"),
                answer=79,
                category="number_theory",
                key_concepts=["least common multiple", "chinese remainder theorem", "periodic sequences"],
                special_features=["multiple periods", "optimization problem"]
            ),
            
            "192e23": ReferenceProblem(
                id="192e23",
                problem=("Fred and George take part in a tennis tournament with $4046$ "
                        "other players. In each round, the players are paired into $2024$ "
                        "matches. How many ways are there to arrange the first round such "
                        "that Fred and George do not have to play each other? (Two "
                        "arrangements for the first round are \\textit{different} if there "
                        "is a player with a different opponent in the two arrangements.)"),
                answer=250,
                category="combinatorics",
                key_concepts=["pair matching", "permutations", "tournament arrangements"],
                special_features=["conditional counting", "large numbers"]
            ),
            
            "1acac0": ReferenceProblem(
                id="1acac0",
                problem=("Triangle $ABC$ has side length $AB = 120$ and circumradius "
                        "$R = 100$. Let $D$ be the foot of the perpendicular from $C$ "
                        "to the line $AB$. What is the greatest possible length of "
                        "segment $CD$?"),
                answer=180,
                category="geometry",
                key_concepts=["triangle geometry", "circumradius", "height", "optimization"],
                special_features=["geometric constraints", "maximum value"]
            ),
            
            "1fce4b": ReferenceProblem(
                id="1fce4b",
                problem=("Find the three-digit number $n$ such that writing any other "
                        "three-digit number $10^{2024}$ times in a row and $10^{2024}+2$ "
                        "times in a row results in two numbers divisible by $n$."),
                answer=143,
                category="number_theory",
                key_concepts=["divisibility", "number patterns", "modular arithmetic"],
                special_features=["large exponents", "pattern recognition"]
            ),
            
            "349493": ReferenceProblem(
                id="349493",
                problem=("We call a sequence $a_1, a_2, \\ldots$ of non-negative integers "
                        "\\textit{delightful} if there exists a positive integer $N$ such "
                        "that for all $n > N$, $a_n = 0$, and for all $i \\geq 1$, $a_i$ "
                        "counts the number of multiples of $i$ in $a_1, a_2, \\ldots, a_N$. "
                        "How many delightful sequences of non-negative integers are there?"),
                answer=3,
                category="sequence",
                key_concepts=["sequence properties", "self-referential sequences", "counting"],
                special_features=["recursion", "finite sequences"]
            ),
            
            "480182": ReferenceProblem(
                id="480182",
                problem=("Let $ABC$ be a triangle with $BC=108$, $CA=126$, and $AB=39$. "
                        "Point $X$ lies on segment $AC$ such that $BX$ bisects $\\angle CBA$. "
                        "Let $\\omega$ be the circumcircle of triangle $ABX$. Let $Y$ be a "
                        "point on $\\omega$ different from $X$ such that $CX=CY$. Line $XY$ "
                        "meets $BC$ at $E$. The length of the segment $BE$ can be written "
                        "as $\\frac{m}{n}$, where $m$ and $n$ are coprime positive integers. "
                        "Find $m+n$."),
                answer=751,
                category="geometry",
                key_concepts=["triangle geometry", "circle geometry", "angle bisector"],
                special_features=["complex construction", "fraction result"]
            ),
            
            "71beb6": ReferenceProblem(
                id="71beb6",
                problem=("For a positive integer $n$, let $S(n)$ denote the sum of the "
                        "digits of $n$ in base 10. Compute $S(S(1)+S(2)+\\cdots+S(N))$ "
                        "with $N=10^{100}-2$."),
                answer=891,
                category="number_theory",
                key_concepts=["digit sums", "modular arithmetic", "large numbers"],
                special_features=["nested operations", "very large numbers"]
            ),
            
            "88c219": ReferenceProblem(
                id="88c219",
                problem=("For positive integers $x_1,\\ldots, x_n$ define $G(x_1, \\ldots, x_n)$ "
                        "to be the sum of their $\\frac{n(n-1)}{2}$ pairwise greatest common "
                        "divisors. We say that an integer $n \\geq 2$ is \\emph{artificial} "
                        "if there exist $n$ different positive integers $a_1, ..., a_n$ "
                        "such that \n[a_1 + \\cdots + a_n = G(a_1, \\ldots, a_n) +1.\\]\n"
                        "Find the sum of all artificial integers $m$ in the range "
                        "$2 \\leq m \\leq 40$."),
                answer=810,
                category="number_theory",
                key_concepts=["greatest common divisor", "sequences", "summation"],
                special_features=["function definition", "property search"]
            ),
            
            "a1d40b": ReferenceProblem(
                id="a1d40b",
                problem=("The Fibonacci numbers are defined as follows: $F_0 = 0$, "
                        "$F_1 = 1$, and $F_{n+1} = F_n + F_{n-1}$ for $n \\geq 1$. "
                        "There are $N$ positive integers $n$ strictly less than "
                        "$10^{101}$ such that $n^2 + (n+1)^2$ is a multiple of 5 "
                        "but $F_{n-1}^2 + F_n^2$ is not. How many prime factors "
                        "does $N$ have, counted with multiplicity?"),
                answer=201,
                category="sequence",
                key_concepts=["fibonacci sequence", "modular arithmetic", "prime factorization"],
                special_features=["multiple conditions", "very large numbers"]
            ),
            
            "bbd91e": ReferenceProblem(
                id="bbd91e",
                problem=("Alice writes all positive integers from $1$ to $n$ on the "
                        "board for some positive integer $n \\geq 11$. Bob then erases "
                        "ten of them. The mean of the remaining numbers is $3000/37$. "
                        "The sum of the numbers Bob erased is $S$. What is the "
                        "remainder when $n \\times S$ is divided by $997$?"),
                answer=902,
                category="arithmetic",
                key_concepts=["arithmetic mean", "modular arithmetic", "summation"],
                special_features=["reverse calculation", "remainder"]
            )
        }
    
    def get_problem(self, problem_id: str) -> Optional[ReferenceProblem]:
        """Get a specific reference problem by ID"""
        return self.problems.get(problem_id)
    
    def get_problems_by_category(self, category: str) -> List[ReferenceProblem]:
        """Get all problems of a specific category"""
        return [p for p in self.problems.values() if p.category == category]
    
    def get_problem_categories(self) -> List[str]:
        """Get list of unique problem categories"""
        return list(set(p.category for p in self.problems.values()))
    
    def get_problems_with_feature(self, feature: str) -> List[ReferenceProblem]:
        """Get all problems containing a specific special feature"""
        return [p for p in self.problems.values() if feature in p.special_features]
    
    def get_problems_with_concept(self, concept: str) -> List[ReferenceProblem]:
        """Get all problems involving a specific key concept"""
        return [p for p in self.problems.values() if concept in p.key_concepts]

    @property
    def statistics(self) -> Dict[str, int]:
        """Get basic statistics about the reference problems"""
        categories = {}
        for problem in self.problems.values():
            categories[problem.category] = categories.get(problem.category, 0) + 1
        return {
            'total_problems': len(self.problems),
            'categories': categories,
            'max_answer': max(p.answer for p in self.problems.values()),
            'min_answer': min(p.answer for p in self.problems.values())
        }

# Example usage
if __name__ == "__main__":
    ref_problems = ReferenceProblems()
    
    # Print statistics
    print("Reference Problems Statistics:")
    print(ref_problems.statistics)
    
    # Print all problem categories
    print("\nProblem Categories:")
    for category in ref_problems.get_problem_categories():
        problems = ref_problems.get_problems_by_category(category)
        print(f"{category}: {len(problems)} problems")
        
    # Example of getting problems with specific features
    modular_problems = ref_problems.get_problems_with_feature("modular arithmetic")
    print(f"\nProblems involving modular arithmetic: {len(modular_problems)}")