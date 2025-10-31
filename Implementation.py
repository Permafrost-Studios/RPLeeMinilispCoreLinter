from enum import Enum, auto

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
            # Single character tokens can nly have oone token type
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
    @classmethod
    def createTransitionFunctions(cls):
        numbers = {"0","1","2","3","4","5","6","7","8","9"}

        lowerCaseIdentifiers = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"}
        identifiers = lowerCaseIdentifiers.union({x.upper() for x in lowerCaseIdentifiers})

        operators = {"+", "×", "=", "−", "?", "λ", "≜"}
        formattingCharacters = {"(", ")"}

        singleCharacterTokenCharacters = operators.union(formattingCharacters)

        #alphabet = numbers + identifiers + singleCharacterTokenCharacters

        allNonErrorStates = [State.START_OR_SPACE, State.NUMBER, State.IDENTIFIER, State.SINGLE_CHARACTER_TOKEN]

        transitions = {}

        for state in allNonErrorStates:
            for digit in numbers:
                transitions[(state, digit)] = State.NUMBER
            
            for letter in identifiers:
                transitions[(state, letter)] = State.IDENTIFIER

            for character in singleCharacterTokenCharacters:
                transitions[(state, character)] = State.SINGLE_CHARACTER_TOKEN
            
            transitions[(state, " ")] = State.START_OR_SPACE

        return transitions

    @classmethod
    def GetTokensForString(cls, input):
        transitionFunctionDictionary = cls.createTransitionFunctions()

        allTokens = []

        numberBuffer = ""
        identifierBuffer = ""

        currentState = State.START_OR_SPACE

        for character in input:
            newState = transitionFunctionDictionary.get((currentState, character), State.ERROR)

            # print("Number Buffer: '" + numberBuffer + "'")
            # print("Identifier Buffer: '" + identifierBuffer + "'")
            # print("Transitioning from " + str(currentState) + " to " + str(newState) + " on character '" + character + "'")

            if newState == State.ERROR:
                raise Exception("Lexical Error: Character is not in the valid alphabet: '" + character + "'")
            
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
                'LPAREN': ['LPAREN', '<parent-expr>', 'RPAREN']
            },
            '<parent-expr>': {
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
                'RPAREN': []  # (empty production)
            }
        }

        parseTreeStack = [[]]
        currentlyObservedParseTreeSublist = parseTreeStack[-1]

        terminals = {'NUMBER', 'IDENTIFIER', 'PLUS', 'MULT', 'EQUALS', 'MINUS', 'CONDITIONAL', 'LAMBDA', 'LET', 'LPAREN', 'RPAREN', '$'}
        nonTerminals = set(parsingTable.keys())

        stack = ['$', '<program>']

        inputTokensIndex = 0
        
        while len(stack) > 0:
            top = stack[-1]

            if top == '$':
                stack.pop()
            elif (top in terminals):
                currentTokenType = tokens[inputTokensIndex].tokenType.name
                if top == currentTokenType:
                    stack.pop()

                    if (currentTokenType == 'LPAREN'):
                        newParseTreeSublist = []
                        parseTreeStack.append(newParseTreeSublist)
                        currentlyObservedParseTreeSublist = newParseTreeSublist
                    elif (currentTokenType == 'RPAREN'):
                        completedParseTreeSublist = parseTreeStack.pop()
                        if len(parseTreeStack) > 0:
                            parseTreeStack[-1].append(completedParseTreeSublist)
                            currentlyObservedParseTreeSublist = parseTreeStack[-1]
                    else:
                        currentlyObservedParseTreeSublist.append(tokens[inputTokensIndex])
                    
                    inputTokensIndex += 1
                else:
                    raise Exception(f"Parse Error: Expected {top}, found {currentTokenType}")
                
            elif top in nonTerminals:
                currentTokenType = tokens[inputTokensIndex].tokenType.name

                productionRules = parsingTable.get(top, None).get(currentTokenType, None)
                if productionRules is not None:
                    stack.pop()
                    if len(productionRules) == 0:
                        pass
                    else:
                        for symbol in reversed(productionRules):
                            stack.append(symbol)
                else:
                    raise Exception(f"Parse Error: No production for {top} with input {currentTokenType}")

        result = parseTreeStack[0]
        return result[0] if len(result) == 1 else result
         
def main():
    print("test")

    
if __name__ == "__main__":
     # Basic expressions
     print("Test: 42")
     tokens1 = Lexer.GetTokensForString("42")
     print("Tokens:", tokens1)
     print("Parse:", Parser.Parse(tokens1))
     print()
     
     print("Test: x")
     tokens2 = Lexer.GetTokensForString("x")
     print("Tokens:", tokens2)
     print("Parse:", Parser.Parse(tokens2))
     print()
     
     print("Test: (+ 2 3)")
     tokens3 = Lexer.GetTokensForString("(+ 2 3)")
     print("Tokens:", tokens3)
     print("Parse:", Parser.Parse(tokens3))
     print()
     
     print("Test: (× x 5)")
     tokens4 = Lexer.GetTokensForString("(× x 5)")
     print("Tokens:", tokens4)
     print("Parse:", Parser.Parse(tokens4))
     print()
     
     # Nested expressions
     print("Test: (+ (× 2 3) 4)")
     tokens5 = Lexer.GetTokensForString("(+ (× 2 3) 4)")
     print("Tokens:", tokens5)
     print("Parse:", Parser.Parse(tokens5))
     print()
     
     print("Test: (? (= x 0) 1 0)")
     tokens6 = Lexer.GetTokensForString("(? (= x 0) 1 0)")
     print("Tokens:", tokens6)
     print("Parse:", Parser.Parse(tokens6))
     print()
     
     # Function expressions
     print("Test: (λ x x)")
     tokens7 = Lexer.GetTokensForString("(λ x x)")
     print("Tokens:", tokens7)
     print("Parse:", Parser.Parse(tokens7))
     print()
     
     print("Test: (≜ y 10 y)")
     tokens8 = Lexer.GetTokensForString("(≜ y 10 y)")
     print("Tokens:", tokens8)
     print("Parse:", Parser.Parse(tokens8))
     print()
     
     print("Test: ((λ x (+ x 1)) 5)")
     tokens9 = Lexer.GetTokensForString("((λ x (+ x 1)) 5)")
     print("Tokens:", tokens9)
     print("Parse:", Parser.Parse(tokens9))
     print()
     
     # More complex
     print("Test: (× (+ 1 2) (− 5 3))")
     tokens10 = Lexer.GetTokensForString("(× (+ 1 2) (− 5 3))")
     print("Tokens:", tokens10)
     print("Parse:", Parser.Parse(tokens10))
     print()
     
     print("Test: (λ f (λ x (f x)))")
     tokens11 = Lexer.GetTokensForString("(λ f (λ x (f x)))")
     print("Tokens:", tokens11)
     print("Parse:", Parser.Parse(tokens11))
     print()
