"""
Синтаксичний та семантичний аналізатор + генератор постфікс-коду
"""


class Parser:
    """Синтаксичний аналізатор з генерацією постфікс-коду"""

    def __init__(self, table_of_symbols):
        self.tableOfSymb = table_of_symbols
        self.len_tableOfSymb = len(table_of_symbols)
        self.numRow = 1
        self.tableOfVar = {}
        self.postfixCode = []
        self.labelCounter = 0
        self.success = False

    # ============= ДОПОМІЖНІ МЕТОДИ =============

    def generateLabel(self):
        """Генерує унікальну мітку"""
        self.labelCounter += 1
        return f"m{self.labelCounter}"

    def addToPostfix(self, item):
        """Додає елемент до постфікс-коду"""
        self.postfixCode.append(item)
        print(f"  POSTFIX: {item}")

    def getSymb(self):
        """Отримує поточний символ з таблиці"""
        if self.numRow > self.len_tableOfSymb:
            return None, None, None
        numLine, lexeme, token, _ = self.tableOfSymb[self.numRow]
        return numLine, lexeme, token

    def parseToken(self, lexeme, token):
        """Розбирає конкретний токен"""
        if self.numRow > self.len_tableOfSymb:
            self.failParse('неочікуваний кінець програми', (lexeme, token, self.numRow))

        numLine, lex, tok = self.getSymb()
        self.numRow += 1

        if (lex, tok) == (lexeme, token):
            print(f'  parseToken: В рядку {numLine} токен ({lexeme}, {token})')
            return True
        else:
            self.failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
            return False

    # ============= ОБРОБКА ПОМИЛОК =============

    def failParse(self, msg, data):
        """Обробляє синтаксичні помилки"""
        if msg == 'неочікуваний кінець програми':
            lexeme, token, numRow = data
            print(f'\n✗ PARSER ERROR: неочікуваний кінець програми')
            print(f'  В таблиці символів немає запису з номером {numRow}')
            print(f'  Очікувалось: ({lexeme}, {token})')
            raise SystemExit(1001)

        elif msg == 'невідповідність токенів':
            numLine, lex, tok, expected_lex, expected_tok = data
            print(f'\n✗ PARSER ERROR: невідповідність токенів')
            print(f'  В рядку {numLine} неочікуваний елемент ({lex}, {tok})')
            print(f'  Очікувався - ({expected_lex}, {expected_tok})')
            raise SystemExit(1002)

        elif msg == 'невідповідність у Factor':
            numLine, lex, tok = data
            print(f'\n✗ PARSER ERROR: невідповідність у Factor')
            print(f'  В рядку {numLine} неочікуваний елемент ({lex}, {tok})')
            raise SystemExit(1003)

    def failSem(self, msg, data):
        """Обробляє семантичні помилки"""
        if msg == 'використання неоголошеної змінної':
            numLine, ident = data
            print(f'\n✗ SEMANTIC ERROR: використання неоголошеної змінної')
            print(f'  В рядку {numLine}, змінна: {ident}')
            raise SystemExit(2001)

        elif msg == 'невідповідність типів при присвоюванні':
            numLine, ident, varType, exprType = data
            print(f'\n✗ SEMANTIC ERROR: невідповідність типів при присвоюванні')
            print(f'  В рядку {numLine}, змінна {ident} має тип {varType},')
            print(f'  але їй присвоюється значення типу {exprType}')
            raise SystemExit(2002)

        elif msg == 'невідповідність типів':
            numLine, leftType, op, rightType = data
            print(f'\n✗ SEMANTIC ERROR: невідповідність типів у виразі')
            print(f'  В рядку {numLine}: {leftType} {op} {rightType}')
            raise SystemExit(2003)

        elif msg == 'використання неініціалізованої змінної':
            numLine, ident = data
            print(f'\n✗ SEMANTIC ERROR: використання неініціалізованої змінної')
            print(f'  В рядку {numLine}, змінна: {ident}')
            raise SystemExit(2004)

    # ============= РОБОТА З ТАБЛИЦЕЮ ЗМІННИХ =============

    def addVarToTable(self, ident, varType):
        """Додає змінну до таблиці"""
        if ident not in self.tableOfVar:
            index = len(self.tableOfVar) + 1
            self.tableOfVar[ident] = (index, varType, False)
            print(f'  ├─ Додано змінну: {ident}, тип: {varType}')
        else:
            index, oldType, initialized = self.tableOfVar[ident]
            self.tableOfVar[ident] = (index, varType, initialized)
            print(f'  ├─ Оновлено тип змінної {ident}: {oldType} → {varType}')

    def getVarType(self, ident):
        """Отримує тип змінної"""
        if ident not in self.tableOfVar:
            return 'undeclared'
        return self.tableOfVar[ident][1]

    def setVarInitialized(self, ident):
        """Позначає змінну як ініціалізовану"""
        if ident in self.tableOfVar:
            index, varType, _ = self.tableOfVar[ident]
            self.tableOfVar[ident] = (index, varType, True)
            print(f'  └─ Змінна {ident} ініціалізована')

    def isVarInitialized(self, ident):
        """Перевіряє, чи ініціалізована змінна"""
        if ident not in self.tableOfVar:
            return False
        return self.tableOfVar[ident][2]

    # ============= РОЗБІР ПРОГРАМИ =============

    def parse(self):
        """Головний метод розбору"""
        try:
            print('parseProgram()')
            self.parseStatementList()
            print('\n✓ Parser: Синтаксичний аналіз завершився успішно')
            print('\nТАБЛИЦЯ ЗМІННИХ:')
            for ident, (index, varType, initialized) in self.tableOfVar.items():
                init_status = 'initialized' if initialized else 'uninitialized'
                print(f'  {ident}: (index={index}, type={varType}, {init_status})')
            self.success = True
            return True

        except SystemExit as e:
            print(f'\n✗ Parser: Аварійне завершення програми з кодом {e.code}')
            self.success = False
            return False

    def parseStatementList(self):
        """StatementList = {Statement}"""
        print('  parseStatementList()')
        while self.numRow <= self.len_tableOfSymb:
            numLine, lex, tok = self.getSymb()
            if lex is None:
                break
            result = self.parseStatement()
            if not result:
                break

    def parseStatement(self):
        """Statement = Assign | Output | IfStatement | WhileStatement"""
        print('  parseStatement()')
        if self.numRow > self.len_tableOfSymb:
            return False

        numLine, lex, tok = self.getSymb()

        if tok == 'id':
            self.parseAssign()
            return True
        elif lex == 'print':
            self.parseOutput()
            return True
        elif lex == 'if':
            self.parseIfStatement()
            return True
        elif lex == 'while':
            self.parseWhileStatement()
            return True
        else:
            return False

    # ============= ПРИСВОЮВАННЯ =============

    def parseAssign(self):
        """Assign = Ident ('<-' | '=') Expression"""
        print('  parseAssign()')
        numLine, lex, tok = self.getSymb()
        ident = lex
        self.numRow += 1

        # Оператор присвоювання
        numLine, lex, tok = self.getSymb()
        if tok != 'assign_op':
            self.failParse('невідповідність токенів',
                          (numLine, lex, tok, '<- або =', 'assign_op'))
        self.numRow += 1

        # Вираз
        exprType = self.parseExpression()

        # Семантика
        if ident not in self.tableOfVar:
            self.addVarToTable(ident, exprType)
        else:
            varType = self.getVarType(ident)
            if varType != exprType:
                self.failSem('невідповідність типів при присвоюванні',
                           (numLine, ident, varType, exprType))

        self.setVarInitialized(ident)
        self.addToPostfix(f'={ident}')
        return True

    # ============= ВВЕДЕННЯ-ВИВЕДЕННЯ =============

    def parseOutput(self):
        """Output = print '(' ExprList ')'"""
        print('  parseOutput()')
        self.parseToken('print', 'keyword')
        self.parseToken('(', 'brackets_op')

        while True:
            exprType = self.parseExpression()
            self.addToPostfix('print')

            numLine, lex, tok = self.getSymb()
            if lex == ',':
                self.numRow += 1
            else:
                break

        self.parseToken(')', 'brackets_op')
        return True

    # ============= УМОВНИЙ ОПЕРАТОР =============

    def parseIfStatement(self):
        """IfStatement = if '(' Expression ')' StatementBlock [else StatementBlock]"""
        print('  parseIfStatement()')
        self.parseToken('if', 'keyword')
        self.parseToken('(', 'brackets_op')

        condType = self.parseExpression()
        self.parseToken(')', 'brackets_op')

        label_else = self.generateLabel()
        self.addToPostfix(label_else)
        self.addToPostfix('JF')

        self.parseStatementBlock()

        numLine, lex, tok = self.getSymb()
        if lex == 'else':
            self.numRow += 1
            label_end = self.generateLabel()
            self.addToPostfix(label_end)
            self.addToPostfix('JMP')
            self.addToPostfix(f"{label_else}:")
            self.parseStatementBlock()
            self.addToPostfix(f"{label_end}:")
        else:
            self.addToPostfix(f"{label_else}:")

        return True

    # ============= ЦИКЛ =============

    def parseWhileStatement(self):
        """WhileStatement = while '(' Expression ')' StatementBlock"""
        print('  parseWhileStatement()')
        self.parseToken('while', 'keyword')
        self.parseToken('(', 'brackets_op')

        label_start = self.generateLabel()
        self.addToPostfix(f"{label_start}:")

        condType = self.parseExpression()
        self.parseToken(')', 'brackets_op')

        label_end = self.generateLabel()
        self.addToPostfix(label_end)
        self.addToPostfix('JF')

        self.parseStatementBlock()

        self.addToPostfix(label_start)
        self.addToPostfix('JMP')
        self.addToPostfix(f"{label_end}:")

        return True

    def parseStatementBlock(self):
        """StatementBlock = '{' StatementList '}' | Statement"""
        print('  parseStatementBlock()')
        numLine, lex, tok = self.getSymb()

        if lex == '{':
            self.numRow += 1
            while True:
                numLine, lex, tok = self.getSymb()
                if lex == '}':
                    self.numRow += 1
                    break
                self.parseStatement()
        else:
            self.parseStatement()

        return True

    # ============= ВИРАЗИ =============

    def parseExpression(self):
        """Expression = ArithmExpression [RelOp ArithmExpression] | BoolConst"""
        print('  parseExpression()')
        numLine, lex, tok = self.getSymb()

        if lex in ('TRUE', 'FALSE'):
            self.numRow += 1
            self.addToPostfix(lex)
            return 'logical'

        leftType = self.parseArithmExpression()

        numLine, lex, tok = self.getSymb()
        if tok == 'rel_op':
            relOp = lex.strip()
            self.numRow += 1
            rightType = self.parseArithmExpression()

            if leftType != rightType:
                self.failSem('невідповідність типів',
                           (numLine, leftType, relOp, rightType))

            self.addToPostfix(relOp)
            return 'logical'

        return leftType

    def parseArithmExpression(self):
        """ArithmExpression = Term {('+' | '-') Term}"""
        print('  parseArithmExpression()')
        leftType = self.parseTerm()

        while True:
            numLine, lex, tok = self.getSymb()
            if tok == 'add_op':
                op = lex
                self.numRow += 1
                rightType = self.parseTerm()

                if leftType != rightType:
                    self.failSem('невідповідність типів',
                               (numLine, leftType, op, rightType))

                self.addToPostfix(op)
            else:
                break

        return leftType

    def parseTerm(self):
        """Term = Power {('*' | '/') Power}"""
        print('  parseTerm()')
        leftType = self.parsePower()

        while True:
            numLine, lex, tok = self.getSymb()
            if tok == 'mult_op':
                op = lex
                self.numRow += 1
                rightType = self.parsePower()

                if leftType != rightType:
                    self.failSem('невідповідність типів',
                               (numLine, leftType, op, rightType))

                self.addToPostfix(op)
            else:
                break

        return leftType

    def parsePower(self):
        """Power = Factor ['^' Power]"""
        print('  parsePower()')
        leftType = self.parseFactor()

        numLine, lex, tok = self.getSymb()
        if tok == 'power_op':
            self.numRow += 1
            rightType = self.parsePower()

            if leftType != rightType:
                self.failSem('невідповідність типів',
                           (numLine, leftType, '^', rightType))

            self.addToPostfix('^')

        return leftType

    def parseFactor(self):
        """Factor = [Sign] Primary"""
        print('  parseFactor()')
        numLine, lex, tok = self.getSymb()

        hasUnaryMinus = False
        if tok == 'add_op' and lex == '-':
            hasUnaryMinus = True
            self.numRow += 1
            numLine, lex, tok = self.getSymb()

        # Primary
        if tok in ('intnum', 'realnum'):
            self.addToPostfix(lex)
            self.numRow += 1
            if hasUnaryMinus:
                self.addToPostfix('unary-')
            return 'numeric'

        elif tok == 'boolval':
            self.addToPostfix(lex)
            self.numRow += 1
            return 'logical'

        elif tok == 'id':
            if lex not in self.tableOfVar:
                self.failSem('використання неоголошеної змінної', (numLine, lex))
            if not self.isVarInitialized(lex):
                self.failSem('використання неініціалізованої змінної', (numLine, lex))

            varType = self.getVarType(lex)
            self.addToPostfix(lex)
            self.numRow += 1

            if hasUnaryMinus:
                self.addToPostfix('unary-')

            return varType

        elif lex == 'scan':
            self.numRow += 1
            self.parseToken('(', 'brackets_op')
            self.parseToken(')', 'brackets_op')
            self.addToPostfix('scan')
            return 'numeric'

        elif lex == '(':
            self.numRow += 1
            exprType = self.parseArithmExpression()
            self.parseToken(')', 'brackets_op')

            if hasUnaryMinus:
                self.addToPostfix('unary-')

            return exprType

        else:
            self.failParse('невідповідність у Factor', (numLine, lex, tok))

    # ============= ОТРИМАННЯ РЕЗУЛЬТАТІВ =============

    def get_postfix_code(self):
        """Повертає згенерований постфікс-код"""
        return self.postfixCode

    def get_variable_table(self):
        """Повертає таблицю змінних"""
        return self.tableOfVar

    def reset(self):
        """Скидає стан парсера"""
        self.numRow = 1
        self.tableOfVar = {}
        self.postfixCode = []
        self.labelCounter = 0
        self.success = False
