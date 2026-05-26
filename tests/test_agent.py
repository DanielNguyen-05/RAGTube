"""
Tests for Agent module (agent.py)
"""

import pytest
from simpleeval import simple_eval, DEFAULT_FUNCTIONS, DEFAULT_NAMES


def test_safe_evaluator_arithmetic():
    """Test safe expression evaluator works correctly."""
    assert simple_eval("1500", names=DEFAULT_NAMES, functions=DEFAULT_FUNCTIONS) == 1500
    assert simple_eval("2 + 3", names=DEFAULT_NAMES, functions=DEFAULT_FUNCTIONS) == 5
    assert simple_eval("5 * 2", names=DEFAULT_NAMES, functions=DEFAULT_FUNCTIONS) == 10


def test_safe_evaluator_division():
    """Test division."""
    result = simple_eval("100 / 4", names=DEFAULT_NAMES, functions=DEFAULT_FUNCTIONS)
    assert result == 25.0


def test_safe_evaluator_floats():
    """Test floating point arithmetic."""
    result = simple_eval("1.5 * 2", names=DEFAULT_NAMES, functions=DEFAULT_FUNCTIONS)
    assert result == 3.0


def test_safe_evaluator_complex():
    """Test compound expressions."""
    result = simple_eval("(100 + 50) * 0.2", names=DEFAULT_NAMES, functions=DEFAULT_FUNCTIONS)
    assert result == 30.0


def test_safe_evaluator_blocks_injection():
    """Verify code injection is blocked by simpleeval."""
    dangerous_exprs = [
        "__import__('os')",
        "__builtins__",
        "open('/etc/passwd')",
        "exec('print(1)')",
    ]
    for expr in dangerous_exprs:
        with pytest.raises(Exception):
            simple_eval(expr, names=DEFAULT_NAMES, functions=DEFAULT_FUNCTIONS)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
