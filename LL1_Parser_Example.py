
"""
Example of a Table-Driven LL(1) Parser in Python

Grammar:
    E  -> T E'
    E' -> + T E' | ε
    T  -> F T'
    T' -> * F T' | ε
    F  -> ( E ) | id

This grammar parses simple arithmetic expressions like: id + id * id
"""

class LL1Parser:
    def __init__(self):
        # Define terminals and non-terminals
        self.terminals = {'+', '*', '(', ')', 'id', '$'}  # $ is end marker
        self.non_terminals = {'E', "E'", 'T', "T'", 'F'}
        
        # Define the LL(1) parsing table
        # Table[non_terminal][terminal] = production rule
        self.parsing_table = {
            'E': {
