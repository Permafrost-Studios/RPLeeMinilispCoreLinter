from enum import Enum, auto
import argparse

class LexerException(Exception):
    pass

class ParseException(Exception):
    pass
 
class State(Enum):
    START_OR_SPACE = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    SINGLE_CHARACTER_TOKEN = auto()
    ERROR = auto()

class TokenType(Enum):
    NUMBER = auto()
    IDENTIFIER = auto()
    PLUS = auto()
    MINUS = auto()
    MULT = auto()
    EQUALS = auto()
    CONDITIONAL = auto()
    LAMBDA = auto()
    LET = auto()
    LPAREN = auto()
    RPAREN = auto()


class Token:
    def __init__(self, tokenType, value):
        if tokenType is None:
            # For single character tokens - can only have one token type
            self.tokenType = self.getTokenTypeForSingleCharacterToken(value)
            self.value = value
        else:
            self.tokenType = tokenType
            self.value = value
            
    def __str__(self):
        strings = {
            TokenType.NUMBER: str(self.value),
            TokenType.IDENTIFIER: str(self.value),
            TokenType.PLUS: "+",
            TokenType.MINUS: "−",
            TokenType.MULT: "×",
            TokenType.EQUALS: "=",
            TokenType.CONDITIONAL: "?",
            TokenType.LAMBDA: "λ",
            TokenType.LET: "≜",
            TokenType.LPAREN: "(",
            TokenType.RPAREN: ")"
        }
        return strings.get(self.tokenType, None)
    
    def getTokenTypeForSingleCharacterToken(cls, character):
        mapping = {
            "+": TokenType.PLUS,
            "−": TokenType.MINUS,
            "×": TokenType.MULT,
            "=": TokenType.EQUALS,
            "?": TokenType.CONDITIONAL,
            "λ": TokenType.LAMBDA,
            "≜": TokenType.LET,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN
        }
        return mapping.get(character, None)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        elif self.tokenType != other.tokenType:
            return False
        elif self.tokenType == TokenType.NUMBER:
                return self.value == other.value
        elif self.tokenType == TokenType.IDENTIFIER:
                return self.value == other.value
        else:
             return True

    def __ne__(self, other):
        return not self == other


class Lexer:
    def __init__(self):
        self.numbers = {"0","1","2","3","4","5","6","7","8","9"}

        self.lowerCaseIdentifiers = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"}
        self.identifiers = self.lowerCaseIdentifiers.union({x.upper() for x in self.lowerCaseIdentifiers})

        self.operators = {"+", "×", "=", "−", "?", "λ", "≜"}
        self.formattingCharacters = {"(", ")"}

        self.singleCharacterTokenCharacters = self.operators.union(self.formattingCharacters)

        self.whiteSpaceCharacters = {" ", "\t", "\n"}

        self.alphabet = self.numbers.union(self.identifiers).union(self.singleCharacterTokenCharacters).union(self.whiteSpaceCharacters)

    def createTransitionFunctions(self):
        allNonErrorStates = [State.START_OR_SPACE, State.NUMBER, State.IDENTIFIER, State.SINGLE_CHARACTER_TOKEN]

        transitions = {}

        ## Identifiers
        for letter in self.identifiers:
            transitions[(State.IDENTIFIER, letter)] = State.IDENTIFIER
            transitions[(State.NUMBER, letter)] = State.ERROR
            transitions[(State.START_OR_SPACE, letter)] = State.IDENTIFIER
            transitions[(State.SINGLE_CHARACTER_TOKEN, letter)] = State.IDENTIFIER

        # Numbers
        for digit in self.numbers:
            transitions[(State.NUMBER, digit)] = State.NUMBER
            transitions[(State.IDENTIFIER, digit)] = State.ERROR
            transitions[(State.START_OR_SPACE, digit)] = State.NUMBER
            transitions[(State.SINGLE_CHARACTER_TOKEN, digit)] = State.NUMBER

        # Single character tokens
        for character in self.singleCharacterTokenCharacters:
            transitions[(State.SINGLE_CHARACTER_TOKEN, character)] = State.SINGLE_CHARACTER_TOKEN
            transitions[(State.NUMBER, character)] = State.SINGLE_CHARACTER_TOKEN
            transitions[(State.IDENTIFIER, character)] = State.SINGLE_CHARACTER_TOKEN
            transitions[(State.START_OR_SPACE, character)] = State.SINGLE_CHARACTER_TOKEN

        for state in allNonErrorStates:
            for ws in {" ", "\t", "\n", "\r"}:
                transitions[(state, ws)] = State.START_OR_SPACE

        return transitions

    def GetTokensForString(self, input):
        if not input.strip():
            raise LexerException("Input is empty or contains only whitespace")

        transitionFunctionDictionary = self.createTransitionFunctions()

        allTokens = []

        numberBuffer = ""
        identifierBuffer = ""

        currentState = State.START_OR_SPACE

        for character in input:
            if character not in self.alphabet:
                raise LexerException(f"Character '{character}' is not in the alphabet")

            newState = transitionFunctionDictionary.get((currentState, character), State.ERROR)

            if newState == State.ERROR:
                raise LexerException(f"Transition ({currentState}, '{character}') is not valid")
            
            if (newState != currentState):
                if currentState == State.NUMBER:
                    allTokens.append(Token(TokenType.NUMBER, int(numberBuffer)))
                    numberBuffer = ""
                elif currentState == State.IDENTIFIER:
                    allTokens.append(Token(TokenType.IDENTIFIER, identifierBuffer))
                    identifierBuffer = ""

            currentState = newState

            if currentState == State.SINGLE_CHARACTER_TOKEN:
                allTokens.append(Token(None, character))
            elif currentState == State.NUMBER:
                numberBuffer += character
            elif currentState == State.IDENTIFIER:
                identifierBuffer += character

        if currentState == State.NUMBER:
            allTokens.append(Token(TokenType.NUMBER, int(numberBuffer)))
        elif currentState == State.IDENTIFIER:
            allTokens.append(Token(TokenType.IDENTIFIER, identifierBuffer))

        return allTokens
    
class Parser:
    @classmethod
    def Parse(cls, tokens):
        parsingTable = {
            '<program>': {
                'NUMBER': ['<expr>'],
                'IDENTIFIER': ['<expr>'],
                'LPAREN': ['<expr>']
            },
            '<expr>': {
                'NUMBER': ['NUMBER'],
                'IDENTIFIER': ['IDENTIFIER'],
                'LPAREN': ['LPAREN', '<paren-expr>', 'RPAREN']
            },
            '<paren-expr>': {
                'PLUS': ['PLUS', '<expr>', '<expr>'],
                'MULT': ['MULT', '<expr>', '<expr>'],
                'EQUALS': ['EQUALS', '<expr>', '<expr>'],
                'MINUS': ['MINUS', '<expr>', '<expr>'],
                'CONDITIONAL': ['CONDITIONAL', '<expr>', '<expr>', '<expr>'],
                'LAMBDA': ['LAMBDA', 'IDENTIFIER', '<expr>'],
                'LET': ['LET', 'IDENTIFIER', '<expr>', '<expr>'],
                'NUMBER': ['<expr>', '<expr>*'],
                'IDENTIFIER': ['<expr>', '<expr>*'],
                'LPAREN': ['<expr>', '<expr>*']
            },
            '<expr>*': {
                'NUMBER': ['<expr>', '<expr>*'],
                'IDENTIFIER': ['<expr>', '<expr>*'],
                'LPAREN': ['<expr>', '<expr>*'],
                'RPAREN': []
            }
        }

        parseTreeStack = [[]] ## Initial nested list is needed so that "parseTreeStack[-1]" can always be used to the get the latest parse tree container in the stack

        terminals = {'NUMBER', 'IDENTIFIER', 'PLUS', 'MULT', 'EQUALS', 'MINUS', 'CONDITIONAL', 'LAMBDA', 'LET', 'LPAREN', 'RPAREN', '$'}
        nonTerminals = set(parsingTable.keys())

        stack = ['$', '<program>']

        inputTokensIndex = 0
        parenthesisDepth = 0
        
        while len(stack) > 0:
            top = stack[-1]
            currentTokenType = tokens[inputTokensIndex].tokenType.name if inputTokensIndex < len(tokens) else '$'


            if top == '$' or currentTokenType == '$':
                stack.pop()
                if parenthesisDepth > 0:
                    raise ParseException(f"Missing {parenthesisDepth} closing parentheses")
            elif (top in terminals):
                if top == currentTokenType:
                    stack.pop()

                    # Since the only situation where a non-terminal is expanded to more than one terminal is when expanding the non terminal <paren-expr>, 
                    # and <paren-expr> can ONLY appear when surrounded by parentheses, we can safely use the parenthesis to manage the parse tree depth/structure. 
                    if (currentTokenType == 'LPAREN'):
                        parenthesisDepth += 1

                        # Add new parse tree container to the stack - will be put into its 'parent' tree container when RPAREN is encountered
                        newParseTreeSublist = []
                        parseTreeStack.append(newParseTreeSublist)
                    elif (currentTokenType == 'RPAREN'):
                        parenthesisDepth -= 1
                        if parenthesisDepth < 0:
                            raise ParseException(f"Unmatched closing parenthesis at position: {inputTokensIndex}")
                        
                        # Removes the current parse tree container from the stack and appends it to the 'parent' parse tree container
                        completedParseTreeSublist = parseTreeStack.pop()
                        parseTreeStack[-1].append(completedParseTreeSublist)
                    else:
                        parseTreeStack[-1].append(tokens[inputTokensIndex])
                    
                    inputTokensIndex += 1
                else:
                    if currentTokenType == '$':
                        raise ParseException(f"Unexpected end of input. Expected: {top}")
                    elif top == 'RPAREN':
                        raise ParseException(f"Expected closing parenthesis, but found: {currentTokenType}. Wrong number of arguments")
                    else:
                        raise ParseException(f"Expected {top}, found: {currentTokenType}")
                
            elif top in nonTerminals:
                productionRules = parsingTable.get(top, None).get(currentTokenType, None)
                if productionRules is not None:
                    stack.pop()
                    if len(productionRules) == 0: # Only case is: ('<expr>*', ')') -> [] 
                        pass
                    else:
                        for symbol in reversed(productionRules):
                            stack.append(symbol)
                else:
                    if currentTokenType == '$':
                            raise ParseException(f"Unexpected end of input while parsing: {top}")
                    elif top == '<paren-expr>':
                        raise ParseException(f"Invalid expression inside parentheses: {currentTokenType}")
                    else:
                        raise ParseException(f"Unexpected {currentTokenType} while parsing: {top}")

        result = parseTreeStack[0]
        return result[0] if len(result) == 1 else result
    
class MiniLispAnalyser:
    @classmethod
    def Analyse(cls, input):
        lexer = Lexer()

        tokens = lexer.GetTokensForString(input)
        parseTree = Parser.Parse(tokens)
        return parseTree
         
def main():
    parser = argparse.ArgumentParser(description='MiniLisp Lexer and Parser')
    parser.add_argument('mode', choices = ['Lexer', 'Analyser'], help = 'Mode to run: Lexer (lexer only), Analyser (full analysis)')
    parser.add_argument('input', help = 'MiniLisp expression to process')
    
    args = parser.parse_args()
    
    if args.mode == 'Lexer':
        tokens = Lexer.GetTokensForString(args.input)
        print("Tokens:", tokens)
    elif args.mode == 'Analyser':
        parseTree = MiniLispAnalyser.Analyse(args.input)
        print("Parse Tree:", parseTree)

if __name__ == "__main__":
    main()