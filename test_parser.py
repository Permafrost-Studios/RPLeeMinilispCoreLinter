from Implementation import Lexer, Parser

# Start with the simplest test cases
test_cases = [
    "42",
    "x", 
    "(+ 2 3)",
    "(× x 5)",
    "(+ (× 2 3) 4)",
    "(? (= x 0) 1 0)",
    "(λ x x)",
    "(≜ y 10 y)",
    "((λ x (+ x 1)) 5)",
    "(× (+ 1 2) (− 5 3))",
    "(λ f (λ x (f x)))"
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*50}")
    print(f"Test {i}: {test}")
    print('='*50)
    try:
        tokens = Lexer.GetTokensForString(test)
        print(f"Tokens: {tokens}")
        result = Parser.Parse(tokens)
        print(f"Parse tree: {result}")
        print("✓ SUCCESS")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        break