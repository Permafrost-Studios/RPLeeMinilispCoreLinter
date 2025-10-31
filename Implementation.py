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


class LexicalAnalyser:
    @classmethod
    def createTransitionFunctions(cls):
        numbers = ["0","1","2","3","4","5","6","7","8","9"]

        lowerCaseIdentifiers = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        identifiers = lowerCaseIdentifiers + [x.upper() for x in lowerCaseIdentifiers]

        operators = ["+", "×", "=", "−", "?", "λ", "≜"]
        formattingCharacters = ["(", ")"]

        singleCharacterTokenCharacters = operators + formattingCharacters

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
        AcceptingStates = [State.NUMBER, State.IDENTIFIER]

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
         
def main():
    print("test")

    
if __name__ == "__main__":
     # Basic expressions
     print(LexicalAnalyser.GetTokensForString("42"))
     print(LexicalAnalyser.GetTokensForString("x"))
     print(LexicalAnalyser.GetTokensForString("(+ 2 3)"))
     print(LexicalAnalyser.GetTokensForString("(× x 5)"))
     
     # Nested expressions
     print(LexicalAnalyser.GetTokensForString("(+ (× 2 3) 4)"))
     print(LexicalAnalyser.GetTokensForString("(? (= x 0) 1 0)"))
     
     # Function expressions
     print(LexicalAnalyser.GetTokensForString("(λ x x)"))
     print(LexicalAnalyser.GetTokensForString("(≜ y 10 y)"))
     print(LexicalAnalyser.GetTokensForString("((λ x (+ x 1)) 5)"))
     
     # More complex
     print(LexicalAnalyser.GetTokensForString("(× (+ 1 2) (− 5 3))"))
     print(LexicalAnalyser.GetTokensForString("(λ f (λ x (f x)))"))