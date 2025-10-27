from enum import Enum, auto

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
        self.value = value
        self.tokenType = tokenType
            
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
        return strings.get(self.type, None)

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


if __name__ == "__main__":
     print("This is something")