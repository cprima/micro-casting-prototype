#!/usr/bin/env python3
"""Sample Python module for testing."""

def calculate_factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class DataProcessor:
    """Process data with various methods."""

    def __init__(self, data):
        self.data = data

    def process(self):
        """Process the data."""
        return [x * 2 for x in self.data]

if __name__ == "__main__":
    print(calculate_factorial(5))
    print(fibonacci(10))
