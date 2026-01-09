"""
Синтаксичний та семантичний аналізатор + генератор постфікс-коду
"""


class Parser:
    """Синтаксичний аналізатор з генерацією постфікс-коду"""

    def __init__(self, table_of_symbols):
        self.tableOfSymb = table_of_symbols       # Таблиця символів (токенів) з лексера
        self.len_tableOfSymb = len(table_of_symbols)  # Кількість токенів
        self.numRow = 1                           # Номер поточного рядка в таблиці
        self.tableOfVar = {}                      # Таблиця змінних {ім'я: (індекс, тип, ініціалізована)}
        self.postfixCode = []                     # Постфікс-код (результат)
        self.labelCounter = 0                     # Лічильник міток для JMP/JF
        self.success = False                      # Прапорець успішності розбору

    # ============= ДОПОМІЖНІ МЕТОДИ =============

    def generateLabel(self):
        """Генерує унікальну мітку для переходів"""
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
        """Розбирає конкретний токен (перевіряє відповідність)"""
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
        """Додає змінну до таблиці або оновлює її тип"""
        if ident not in self.tableOfVar:
            index = len(self.tableOfVar) + 1
            self.tableOfVar[ident] = (index, varType, False)
            print(f'  ├─ Додано змінну: {ident}, тип: {varType}')
        else:
            index, oldType, initialized = self.tableOfVar[ident]
            self.tableOfVar[ident] = (index, varType, initialized)
            print(f'  ├─ Оновлено тип змінної {ident}: {oldType} → {varType}')

    def getVarType(self, ident):
        """Отримує тип змінної з таблиці"""
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
        """Головний метод розбору програми"""
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

        # Семантична перевірка типів
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

        # Розбір списку виразів через кому
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

        # Умова
        condType = self.parseExpression()
        self.parseToken(')', 'brackets_op')

        # Мітка для else або кінця if
        label_else = self.generateLabel()
        self.addToPostfix(label_else)
        self.addToPostfix('JF')  # Перехід на else, якщо умова хибна

        # Then-блок
        self.parseStatementBlock()

        # Перевірка наявності else
        numLine, lex, tok = self.getSymb()
        if lex == 'else':
            self.numRow += 1
            # Мітка для кінця всього if-else
            label_end = self.generateLabel()
            self.addToPostfix(label_end)
            self.addToPostfix('JMP')  # Пропустити else
            self.addToPostfix(f"{label_else}:")  # Початок else
            self.parseStatementBlock()
            self.addToPostfix(f"{label_end}:")  # Кінець if-else
        else:
            self.addToPostfix(f"{label_else}:")  # Кінець if

        return True

    # ============= ЦИКЛ =============

    def parseWhileStatement(self):
        """WhileStatement = while '(' Expression ')' StatementBlock"""
        print('  parseWhileStatement()')
        self.parseToken('while', 'keyword')
        self.parseToken('(', 'brackets_op')

        # Мітка початку циклу
        label_start = self.generateLabel()
        self.addToPostfix(f"{label_start}:")

        # Умова
        condType = self.parseExpression()
        self.parseToken(')', 'brackets_op')

        # Мітка виходу з циклу
        label_end = self.generateLabel()
        self.addToPostfix(label_end)
        self.addToPostfix('JF')  # Вихід з циклу, якщо умова хибна

        # Тіло циклу
        self.parseStatementBlock()

        # Повернення на початок циклу
        self.addToPostfix(label_start)
        self.addToPostfix('JMP')
        self.addToPostfix(f"{label_end}:")  # Кінець циклу

        return True

    def parseStatementBlock(self):
        """StatementBlock = '{' StatementList '}' | Statement"""
        print('  parseStatementBlock()')
        numLine, lex, tok = self.getSymb()

        if lex == '{':
            # Блок операторів у фігурних дужках
            self.numRow += 1
            while True:
                numLine, lex, tok = self.getSymb()
                if lex == '}':
                    self.numRow += 1
                    break
                self.parseStatement()
        else:
            # Один оператор без дужок
            self.parseStatement()

        return True

    # ============= ВИРАЗИ =============

    def parseExpression(self):
        """Expression = ArithmExpression [RelOp ArithmExpression] | BoolConst"""
        print('  parseExpression()')
        numLine, lex, tok = self.getSymb()

        # Булева константа (TRUE/FALSE)
        if lex in ('TRUE', 'FALSE'):
            self.numRow += 1
            self.addToPostfix(lex)
            return 'logical'

        # Арифметичний вираз (можливо з порівнянням)
        leftType = self.parseArithmExpression()

        # Перевірка на оператор відношення
        numLine, lex, tok = self.getSymb()
        if tok == 'rel_op':
            relOp = lex.strip()
            self.numRow += 1
            rightType = self.parseArithmExpression()

            # Семантична перевірка типів
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

        # Обробка додавання/віднімання
        while True:
            numLine, lex, tok = self.getSymb()
            if tok == 'add_op':
                op = lex
                self.numRow += 1
                rightType = self.parseTerm()

                # Семантична перевірка типів
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

        # Обробка множення/ділення
        while True:
            numLine, lex, tok = self.getSymb()
            if tok == 'mult_op':
                op = lex
                self.numRow += 1
                rightType = self.parsePower()

                # Семантична перевірка типів
                if leftType != rightType:
                    self.failSem('невідповідність типів',
                               (numLine, leftType, op, rightType))

                self.addToPostfix(op)
            else:
                break

        return leftType

    def parsePower(self):
        """Power = Factor ['^' Power] (правоасоціативна операція)"""
        print('  parsePower()')
        leftType = self.parseFactor()

        # Степінь (правоасоціативна)
        numLine, lex, tok = self.getSymb()
        if tok == 'power_op':
            self.numRow += 1
            rightType = self.parsePower()  # Рекурсивний виклик для правої асоціативності

            # Семантична перевірка типів
            if leftType != rightType:
                self.failSem('невідповідність типів',
                           (numLine, leftType, '^', rightType))

            self.addToPostfix('^')

        return leftType

    def parseFactor(self):
        """Factor = [Sign] Primary"""
        print('  parseFactor()')
        numLine, lex, tok = self.getSymb()

        # Перевірка на унарний мінус
        hasUnaryMinus = False
        if tok == 'add_op' and lex == '-':
            hasUnaryMinus = True
            self.numRow += 1
            numLine, lex, tok = self.getSymb()

        # Primary (базовий елемент)
        if tok in ('intnum', 'realnum'):
            # Числова константа
            self.addToPostfix(lex)
            self.numRow += 1
            if hasUnaryMinus:
                self.addToPostfix('unary-')
            return 'numeric'

        elif tok == 'boolval':
            # Булева константа
            self.addToPostfix(lex)
            self.numRow += 1
            return 'logical'

        elif tok == 'id':
            # Ідентифікатор (змінна)
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
            # Введення з клавіатури
            self.numRow += 1
            self.parseToken('(', 'brackets_op')
            self.parseToken(')', 'brackets_op')
            self.addToPostfix('scan')
            return 'numeric'

        elif lex == '(':
            # Вираз у дужках
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
        """Скидає стан парсера до початкового"""
        self.numRow = 1
        self.tableOfVar = {}
        self.postfixCode = []
        self.labelCounter = 0
        self.success = False
