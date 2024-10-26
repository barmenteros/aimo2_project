# src/utils/math_helpers.py

import math
from typing import List, Optional, Tuple, Set, Dict
from functools import reduce, lru_cache
import logging

logger = logging.getLogger(__name__)

# Number Theory Functions
@lru_cache(maxsize=1000)
def gcd(a: int, b: int) -> int:
    """
    Calculate Greatest Common Divisor using Euclidean algorithm.
    
    Args:
        a, b: Numbers to find GCD of
        
    Returns:
        int: Greatest Common Divisor
    """
    while b:
        a, b = b, a % b
    return abs(a)

def lcm(a: int, b: int) -> int:
    """
    Calculate Least Common Multiple.
    
    Args:
        a, b: Numbers to find LCM of
        
    Returns:
        int: Least Common Multiple
    """
    return abs(a * b) // gcd(a, b)

@lru_cache(maxsize=1000)
def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Number to check
        
    Returns:
        bool: True if prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    return all(n % i != 0 for i in range(3, int(math.sqrt(n)) + 1, 2))

def prime_factors(n: int) -> List[int]:
    """
    Get prime factorization of a number.
    
    Args:
        n: Number to factorize
        
    Returns:
        List[int]: List of prime factors
    """
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
        if d * d > n:
            if n > 1:
                factors.append(n)
            break
    return factors

@lru_cache(maxsize=1000)
def euler_totient(n: int) -> int:
    """
    Calculate Euler's totient function φ(n).
    
    Args:
        n: Number to calculate totient for
        
    Returns:
        int: Value of φ(n)
    """
    result = n
    for p in set(prime_factors(n)):
        result *= (1 - 1/p)
    return int(result)

# Modular Arithmetic Functions
def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Calculate modular multiplicative inverse.
    
    Args:
        a: Number to find inverse of
        m: Modulus
        
    Returns:
        Optional[int]: Modular multiplicative inverse if exists
    """
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return (x % m + m) % m

@lru_cache(maxsize=1000)
def chinese_remainder(remainders: Tuple[int, ...], moduli: Tuple[int, ...]) -> Optional[int]:
    """
    Solve system of congruences using Chinese Remainder Theorem.
    
    Args:
        remainders: Tuple of remainders
        moduli: Tuple of moduli
        
    Returns:
        Optional[int]: Solution if exists
    """
    total = 0
    product = reduce(lambda x, y: x * y, moduli)
    
    for remainder, modulus in zip(remainders, moduli):
        p = product // modulus
        total += remainder * p * mod_inverse(p, modulus)
    
    return total % product

# Sequence Functions
@lru_cache(maxsize=1000)
def fibonacci_mod(n: int, m: int = 1000) -> int:
    """
    Calculate nth Fibonacci number modulo m.
    
    Args:
        n: Index of Fibonacci number
        m: Modulus (default 1000)
        
    Returns:
        int: nth Fibonacci number modulo m
    """
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, (a + b) % m
    return b

@lru_cache(maxsize=1000)
def factorial_mod(n: int, m: int = 1000) -> int:
    """
    Calculate factorial modulo m.
    
    Args:
        n: Number to calculate factorial of
        m: Modulus (default 1000)
        
    Returns:
        int: n! modulo m
    """
    result = 1
    for i in range(1, min(n + 1, m + 1)):
        result = (result * i) % m
    return result

def binomial_mod(n: int, k: int, m: int = 1000) -> int:
    """
    Calculate binomial coefficient modulo m.
    
    Args:
        n, k: Parameters for binomial coefficient
        m: Modulus (default 1000)
        
    Returns:
        int: C(n,k) modulo m
    """
    if k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    k = min(k, n - k)
    result = 1
    
    for i in range(k):
        result = (result * (n - i)) % m
        inv = mod_inverse(i + 1, m)
        if inv is None:
            return 0
        result = (result * inv) % m
    
    return result

# Geometric Functions
def triangle_area(a: float, b: float, c: float) -> Optional[float]:
    """
    Calculate triangle area using Heron's formula.
    
    Args:
        a, b, c: Side lengths
        
    Returns:
        Optional[float]: Area if triangle is valid
    """
    if a + b <= c or b + c <= a or c + a <= b:
        return None
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))

def circle_area(radius: float) -> float:
    """
    Calculate circle area.
    
    Args:
        radius: Circle radius
        
    Returns:
        float: Circle area
    """
    return math.pi * radius * radius

# Statistics Functions
def mean_mod(numbers: List[int], m: int = 1000) -> int:
    """
    Calculate mean modulo m.
    
    Args:
        numbers: List of numbers
        m: Modulus (default 1000)
        
    Returns:
        int: Mean modulo m
    """
    if not numbers:
        return 0
    total = sum(x % m for x in numbers) % m
    inv = mod_inverse(len(numbers), m)
    if inv is None:
        return 0
    return (total * inv) % m

# String/Number Conversion
def digits_to_number(digits: List[int]) -> int:
    """
    Convert list of digits to number.
    
    Args:
        digits: List of digits
        
    Returns:
        int: Resulting number
    """
    return reduce(lambda x, y: x * 10 + y, digits, 0)

def number_to_digits(n: int) -> List[int]:
    """
    Convert number to list of digits.
    
    Args:
        n: Number to convert
        
    Returns:
        List[int]: List of digits
    """
    return [int(d) for d in str(abs(n))]

# Utility Functions
def is_perfect_square(n: int) -> bool:
    """
    Check if number is perfect square.
    
    Args:
        n: Number to check
        
    Returns:
        bool: True if perfect square
    """
    if n < 0:
        return False
    root = int(math.sqrt(n))
    return root * root == n

def is_perfect_cube(n: int) -> bool:
    """
    Check if number is perfect cube.
    
    Args:
        n: Number to check
        
    Returns:
        bool: True if perfect cube
    """
    root = round(pow(abs(n), 1/3))
    return root ** 3 == abs(n)

def divisors(n: int) -> Set[int]:
    """
    Find all divisors of a number.
    
    Args:
        n: Number to find divisors of
        
    Returns:
        Set[int]: Set of all divisors
    """
    divs = set()
    for i in range(1, int(math.sqrt(abs(n))) + 1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    return divs

# Error checking decorator
def check_math_error(func):
    """Decorator to handle mathematical errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Math error in {func.__name__}: {str(e)}")
            return None
    return wrapper