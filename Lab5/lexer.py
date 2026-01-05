"""
Lexical analyzer for the RSimple language
"""

# Token table
tokenTable = {
    'if': 'keyword',
    'else': 'keyword',
    'while': 'keyword',
    'function': 'keyword',
    'print': 'keyword',
    'scan': 'keyword',
    'TRUE': 'boolval',
    'FALSE': 'boolval',
    '<-': 'assign_op',
    '=': 'assign_op',
    '+': 'add_op',
    '-': 'add_op',
    '*': 'mult_op',
    '/': 'mult_op',
    '^': 'power_op',
    '<': 'rel_op',
    '<=': 'rel_op',
    '==': 'rel_op',
    '>=': 'rel_op',
    '>': 'rel_op',
    '!=': 'rel_op',
    '(': 'brackets_op',
    ')': 'brackets_op',
    '{': 'brackets_op',
    '}': 'brackets_op',
    ',': 'punct'
}

# State to token type mapping table
tokStateTable = {
    2: 'id',
    6: 'realnum',
    9: 'intnum'
}

# State transition table
stf = {
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, '_'): 1,
    (1, 'dot'): 1, (1, 'other'): 2,
    (0, 'Digit'): 4, (4, 'Digit'): 4,
    (4, 'dot'): 5, (5, 'Digit'): 5, (5, 'other'): 6,
    (4, 'other'): 9,
    (0, 'dot'): 3, (3, 'Digit'): 5,
    (0, '<'): 11, (11, '-'): 12, (11, '='): 13, (11, 'other'): 14,
    (0, '>'): 15, (15, '='): 16, (15, 'other'): 17,
    (0, '='): 18, (18, '='): 19, (18, 'other'): 102,
    (0, '!'): 20, (20, '='): 21, (20, 'other'): 102,
    (0, '#'): 22, (22, 'eol'): 23, (22, 'other'): 22,
    (0, 'ws'): 0, (0, 'eol'): 23,
    (0, '+'): 24, (0, '-'): 24, (0, '*'): 24, (0, '/'): 24, (0, '^'): 24,
    (0, '('): 24, (0, ')'): 24, (0, '{'): 24, (0, '}'): 24,
    (0, ','): 24,
    (0, 'other'): 101
}

# Initial state
initState = 0

# Final states
F = {2, 6, 9, 12, 13, 14, 16, 17, 19, 21, 23, 24, 101, 102}

# Final states with character return
Fstar = {2, 6, 9, 14, 17}

# Error states
Ferror = {101, 102}


class Lexer:
    """Lexical analyzer"""

    def __init__(self):
        self.tableOfId = {}
        self.tableOfConst = {}
        self.tableOfSymb = {}
        self.sourceCode = ''
        self.lenCode = 0
        self.numLine = 1
        self.numChar = -1
        self.char = ''
        self.lexeme = ''
        self.state = initState
        self.success = None

    def classOfChar(self, char):
        """Determines the character class"""
        if char == '.':
            return "dot"
        elif char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            return "Letter"
        elif char in "0123456789":
            return "Digit"
        elif char in " \t":
            return "ws"
        elif char in "\n\r":
            return "eol"
        elif char == '_':
            return "_"
        elif char == '#':
            return "#"
        elif char in "<>=!+-*/^(){},:;":
            return char
        else:
            return 'other'

    def nextChar(self):
        """Returns the next character"""
        self.numChar += 1
        if self.numChar < self.lenCode:
            return self.sourceCode[self.numChar]
        return ''

    def putCharBack(self):
        """Pushes the character back"""
        self.numChar -= 1

    def nextState(self, state, classCh):
        """Determines the next state"""
        try:
            return stf[(state, classCh)]
        except KeyError:
            return stf.get((state, 'other'), state)

    def is_final(self, state):
        """Checks if the state is final"""
        return state in F

    def getToken(self, state, lexeme):
        """Determines the token type"""
        if state == 2:
            return tokenTable.get(lexeme, 'id')
        elif state in tokStateTable:
            return tokStateTable[state]
        elif state in (14, 17):
            return 'rel_op'
        elif lexeme in tokenTable:
            return tokenTable[lexeme]
        return 'unknown'

    def indexIdConst(self, state, lexeme):
        """Adds an identifier or constant to the table"""
        if state == 2:
            token = self.getToken(state, lexeme)
            if token == 'id':
                if lexeme not in self.tableOfId:
                    self.tableOfId[lexeme] = len(self.tableOfId) + 1
                return self.tableOfId[lexeme]
            else:
                return ''
        elif state in (6, 9):
            if lexeme not in self.tableOfConst:
                token = tokStateTable[state]
                self.tableOfConst[lexeme] = (token, len(self.tableOfConst) + 1)
            return self.tableOfConst[lexeme][1]
        return ''

    def fail(self):
        """Handles errors"""
        if self.state == 101:
            print(f'!!! Lexer: unexpected character "{self.char}" at line {self.numLine}')
        elif self.state == 102:
            print(f'!!! Lexer: incomplete operator "{self.lexeme}{self.char}" at line {self.numLine}')

    def processing(self):
        """Processes the recognized token"""
        if self.state == 23:
            self.numLine += 1
            self.state = initState
            self.lexeme = ''
            return

        if self.state in (2, 6, 9):
            token = self.getToken(self.state, self.lexeme)
            if token == 'id' or token in ('intnum', 'realnum'):
                index = self.indexIdConst(self.state, self.lexeme)
                self.tableOfSymb[len(self.tableOfSymb) + 1] = (
                    self.numLine, self.lexeme, token, index
                )
            else:
                self.tableOfSymb[len(self.tableOfSymb) + 1] = (
                    self.numLine, self.lexeme, token, ''
                )
            self.lexeme = ''
            self.putCharBack()
            self.state = initState

        elif self.state in (12, 13, 14, 16, 17, 19, 21, 24):
            self.lexeme += self.char
            token = self.getToken(self.state, self.lexeme)
            self.tableOfSymb[len(self.tableOfSymb) + 1] = (
                self.numLine, self.lexeme.strip(), token, ''
            )
            self.lexeme = ''
            if self.state in Fstar:
                self.putCharBack()
            self.state = initState

        elif self.state in Ferror:
            self.fail()
            raise SystemExit(self.state)

    def analyze(self, source_code):
        """Performs lexical analysis"""
        self.sourceCode = source_code + ' '
        self.lenCode = len(self.sourceCode) - 1

        try:
            while self.numChar < self.lenCode - 1:
                self.char = self.nextChar()
                classCh = self.classOfChar(self.char)
                self.state = self.nextState(self.state, classCh)

                if self.is_final(self.state):
                    self.processing()
                elif self.state == initState:
                    self.lexeme = ''
                else:
                    self.lexeme += self.char

            print('✓ Lexer: Lexical analysis completed successfully\n')
            self.success = True
            return True

        except SystemExit as e:
            print(f'✗ Lexer: Program terminated abruptly with code {e.code}')
            self.success = False
            return False

    def reset(self):
        """Resets the lexer state"""
        self.tableOfId = {}
        self.tableOfConst = {}
        self.tableOfSymb = {}
        self.sourceCode = ''
        self.lenCode = 0
        self.numLine = 1
        self.numChar = -1
        self.char = ''
        self.lexeme = ''
        self.state = initState
        self.success = None

    def get_tables(self):
        """Returns the tables"""
        return {
            'symbols': self.tableOfSymb,
            'identifiers': self.tableOfId,
            'constants': self.tableOfConst
        }
