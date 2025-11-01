import json
import traceback
from typing import Any, Union

from Implementation import MiniLispAnalyser, Token, TokenType

def token_to_json(t: Token) -> dict[str, Any]:
    return {
        "type": t.tokenType.name,
        "value": t.value if t.tokenType in {TokenType.NUMBER, TokenType.IDENTIFIER} else str(t)
    }

def serialize_tree(node: Union[Token, list[Any]]) -> Any:
    if isinstance(node, Token):
        return token_to_json(node)
    if isinstance(node, list):
        return [serialize_tree(n) for n in node]
    return node

def run_test_case(input_str: str, description: str, expected: dict[str, Any]) -> dict[str, Any]:
    actual = {
        "status": None,
        "parse_tree": None,
        "error": None,
        "traceback": None
    }

    try:
        result = MiniLispAnalyser.Analyse(input_str)
        actual["parse_tree"] = serialize_tree(result)
        actual["status"] = "success"
    except Exception as e:
        actual["status"] = "error"
        actual["error"] = str(e)
        actual["traceback"] = traceback.format_exc()

    passed = False
    if expected.get("status") == "success":
        passed = (actual["status"] == "success")
    else:
        if actual["status"] == "error":
            substr = expected.get("error_contains")
            passed = True if not substr else (substr in (actual["error"] or ""))

    return {
        "description": description,
        "input": input_str,
        "expected_output": expected,
        "actual_output": actual,
        "success": passed
    }

def main() -> None:
    tests = [
        # Positive tests
        {"input": "42", "desc": "NUMBER literal", "expected": {"status": "success"}},
        {"input": "x", "desc": "IDENTIFIER literal", "expected": {"status": "success"}},
        {"input": "(+ 2 3)", "desc": "Simple addition", "expected": {"status": "success"}},
        {"input": "(× x 5)", "desc": "Multiplication with identifier", "expected": {"status": "success"}},
        {"input": "(+ (× 2 3) 4)", "desc": "Nested arithmetic", "expected": {"status": "success"}},
        {"input": "(? (= x 0) 1 0)", "desc": "Conditional expression", "expected": {"status": "success"}},
        {"input": "(λ x x)", "desc": "Lambda identity", "expected": {"status": "success"}},
        {"input": "(≜ y 10 y)", "desc": "Let binding", "expected": {"status": "success"}},
        {"input": "((λ x (+ x 1)) 5)", "desc": "Lambda application", "expected": {"status": "success"}},
        {"input": "(× (+ 1 2) (− 5 3))", "desc": "Mixed operators with unicode minus", "expected": {"status": "success"}},
        {"input": "(λ f (λ x (f x)))", "desc": "Higher-order lambda", "expected": {"status": "success"}},
        {"input": "(− 7 2)", "desc": "Unicode minus operator (U+2212)", "expected": {"status": "success"}},

        # Negative tests
        {"input": "(+ 1)", "desc": "Too few args for +", "expected": {"status": "error"}},
        {"input": "(+ 1 2 3)", "desc": "Too many args for +", "expected": {"status": "error", "error_contains": "Expected closing parenthesis"}},
        {"input": "@", "desc": "Invalid character", "expected": {"status": "error", "error_contains": "Character '@' is not in the alphabet"}},
        {"input": ")", "desc": "Unmatched closing parenthesis", "expected": {"status": "error"}},
        {"input": "(? 1 2)", "desc": "Too few args for ?", "expected": {"status": "error"}},
        {"input": "(- 7 2)", "desc": "ASCII hyphen-minus should be rejected", "expected": {"status": "error", "error_contains": "Character '-' is not in the alphabet"}},
        {"input": "((λ x (+ x 1)) 5", "desc": "Missing closing parenthesis", "expected": {"status": "error"}, "error_contains": "Missing closing parenthesis"},

        # Whitespace tolerance (positive)
        {"input": "   42   ", "desc": "Leading/trailing spaces around number", "expected": {"status": "success"}},
        {"input": "( + 2 3 )", "desc": "Spaces between parens, operator, and operands", "expected": {"status": "success"}},
        {"input": "(+    2    3)", "desc": "Multiple spaces between tokens", "expected": {"status": "success"}},
        {"input": "(\n+ \n2\t3\n)", "desc": "Newlines and tabs between tokens", "expected": {"status": "success"}},
        {"input": "(\nλ  x   x\n)", "desc": "Lambda with mixed whitespace", "expected": {"status": "success"}},
        {"input": "(\n(λ   x   (+  x    1))\t  5\n)", "desc": "Nested application with whitespace", "expected": {"status": "success"}},

        # Whitespace-only or empty input (negative)
        {"input": "   \n\t  ", "desc": "Whitespace-only input", "expected": {"status": "error"}},
        {"input": "", "desc": "Empty input", "expected": {"status": "error"}},
    ]

    results = [run_test_case(t["input"], t["desc"], t["expected"]) for t in tests]

    out_path = "test_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(results)} test results to {out_path}")

if __name__ == "__main__":
    main()