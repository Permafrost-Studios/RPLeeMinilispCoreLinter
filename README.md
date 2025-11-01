# How to run our parser
## Implementation
The implementation python file takes a few arguments to run, in sequential order:
- Mode: Lexer or Analyser mode. Lexer mode runs only the lexer and returns tokens while Analyser mode runs both the lexer and parser and returns the parse tree.
- Input: The MiniLisp string to lex or parse

Example commands:
python Implementation.py Lexer "(+ x y)"
python Implementation.py Analyser "(+ x y)"

## Test Cases
To run the existing test cases, run the test cases python file without arguments.

New test cases can be testing manually using the implementation python file or added to the test case list in the test case python file, which just runs the implementation.