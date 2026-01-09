"""
Visitor для генерації постфікс-коду з AST (Abstract Syntax Tree)
Використовується з ANTLR4 парсером
"""

from RSimpleVisitor import RSimpleVisitor
from RSimpleParser import RSimpleParser


class RSimpleCompilerVisitor(RSimpleVisitor):
    """Visitor для генерації постфікс-коду з AST"""

    def __init__(self):
        self.postfix_code = []        # Згенерований постфікс-код
        self.variable_table = {}      # Таблиця змінних {ім'я: (індекс, тип, ініціалізована)}
        self.label_counter = 0        # Лічильник міток для JMP/JF

    def generate_label(self):
        """Генерує унікальну мітку для переходів"""
        self.label_counter += 1
        return f"m{self.label_counter}"

    def add_to_postfix(self, item):
        """Додає елемент до постфікс-коду"""
        self.postfix_code.append(item)
        print(f"  POSTFIX: {item}")

    def add_variable(self, name, var_type='numeric'):
        """Додає змінну до таблиці"""
        if name not in self.variable_table:
            index = len(self.variable_table) + 1
            self.variable_table[name] = (index, var_type, True)

    # ========== ОПЕРАТОРИ (STATEMENTS) ==========

    def visitAssignment(self, ctx: RSimpleParser.AssignmentContext):
        """Обробляє присвоювання: x <- 5 або x = 5"""
        ident = ctx.ID().getText()
        # Спочатку обробляємо вираз (праву частину)
        expr_type = self.visit(ctx.expression())
        # Додаємо змінну до таблиці
        self.add_variable(ident, expr_type)
        # Генеруємо інструкцію присвоювання
        self.add_to_postfix(f'={ident}')
        return None

    def visitOutputStatement(self, ctx: RSimpleParser.OutputStatementContext):
        """Обробляє вивід: print(x, y, z)"""
        expr_list = ctx.expressionList()
        # Обробляємо кожен вираз у списку
        for expr in expr_list.expression():
            self.visit(expr)
            self.add_to_postfix('print')
        return None

    def visitIfStatement(self, ctx: RSimpleParser.IfStatementContext):
        """Обробляє умовний оператор if-else"""
        # Обробка умови
        self.visit(ctx.expression())

        # Мітка для else або кінця if
        label_else = self.generate_label()
        self.add_to_postfix(label_else)
        self.add_to_postfix('JF')  # Jump if False (перехід якщо умова хибна)

        # Then-блок (перший блок)
        self.visit(ctx.statementBlock(0))

        # Перевірка наявності else
        if ctx.statementBlock(1):
            # Є else блок
            label_end = self.generate_label()
            self.add_to_postfix(label_end)
            self.add_to_postfix('JMP')  # Безумовний перехід (пропустити else)
            self.add_to_postfix(f"{label_else}:")  # Мітка початку else
            self.visit(ctx.statementBlock(1))
            self.add_to_postfix(f"{label_end}:")  # Мітка кінця if-else
        else:
            # Немає else
            self.add_to_postfix(f"{label_else}:")  # Мітка кінця if

        return None

    def visitWhileStatement(self, ctx: RSimpleParser.WhileStatementContext):
        """Обробляє цикл while"""
        # Мітка початку циклу (для повернення назад)
        label_start = self.generate_label()
        self.add_to_postfix(f"{label_start}:")

        # Обробка умови
        self.visit(ctx.expression())

        # Мітка виходу з циклу
        label_end = self.generate_label()
        self.add_to_postfix(label_end)
        self.add_to_postfix('JF')  # Вихід з циклу, якщо умова хибна

        # Тіло циклу
        self.visit(ctx.statementBlock())

        # Повернення на початок циклу
        self.add_to_postfix(label_start)
        self.add_to_postfix('JMP')  # Безумовний перехід на початок
        self.add_to_postfix(f"{label_end}:")  # Мітка кінця циклу

        return None

    # ========== ВИРАЗИ (EXPRESSIONS) ==========

    def visitExpression(self, ctx: RSimpleParser.ExpressionContext):
        """Обробляє вирази (булеві або арифметичні з порівнянням)"""
        # Перевірка на булеву константу (TRUE/FALSE)
        if ctx.boolConst():
            value = ctx.boolConst().getText()
            self.add_to_postfix(value)
            return 'logical'

        # Арифметичний вираз (можливо з оператором відношення)
        left_type = self.visit(ctx.arithmExpression(0))

        # Перевірка на оператор відношення (<, >, ==, !=, <=, >=)
        if ctx.relOp():
            op = ctx.relOp().getText()
            self.visit(ctx.arithmExpression(1))
            self.add_to_postfix(op)
            return 'logical'

        return left_type

    def visitArithmExpression(self, ctx: RSimpleParser.ArithmExpressionContext):
        """Обробляє арифметичні вирази: a + b - c"""
        # Перший терм
        self.visit(ctx.term(0))

        # Обробка всіх операцій додавання/віднімання
        for i in range(1, len(ctx.term())):
            op = ctx.getChild(2*i - 1).getText()  # Оператор + або -
            self.visit(ctx.term(i))
            self.add_to_postfix(op)

        return 'numeric'

    def visitTerm(self, ctx: RSimpleParser.TermContext):
        """Обробляє терми (множення/ділення): a * b / c"""
        # Перший power
        self.visit(ctx.power(0))

        # Обробка всіх операцій множення/ділення
        for i in range(1, len(ctx.power())):
            op = ctx.getChild(2*i - 1).getText()  # Оператор * або /
            self.visit(ctx.power(i))
            self.add_to_postfix(op)

        return 'numeric'

    def visitPower(self, ctx: RSimpleParser.PowerContext):
        """Обробляє степінь (правоасоціативна): a ^ b ^ c = a ^ (b ^ c)"""
        # Базис (лівий операнд)
        self.visit(ctx.factor())

        # Перевірка на оператор степеня
        if ctx.power():
            # Рекурсивний виклик для правої асоціативності
            self.visit(ctx.power())
            self.add_to_postfix('^')

        return 'numeric'

    def visitFactor(self, ctx: RSimpleParser.FactorContext):
        """Обробляє фактор з можливим унарним мінусом: -x або x"""
        # Перевірка на унарний мінус
        has_minus = ctx.getChildCount() > 1 and ctx.getChild(0).getText() == '-'

        # Обробка базового елемента (primary)
        self.visit(ctx.primary())

        # Якщо був унарний мінус, додаємо відповідну операцію
        if has_minus:
            self.add_to_postfix('unary-')

        return 'numeric'

    def visitPrimary(self, ctx: RSimpleParser.PrimaryContext):
        """Обробляє базові елементи: змінні, числа, scan(), вирази в дужках"""
        if ctx.ID():
            # Ідентифікатор (змінна)
            self.add_to_postfix(ctx.ID().getText())
        elif ctx.INT():
            # Ціле число
            self.add_to_postfix(ctx.INT().getText())
        elif ctx.FLOAT():
            # Дробове число
            self.add_to_postfix(ctx.FLOAT().getText())
        elif ctx.getText().startswith('scan'):
            # Введення з клавіатури
            self.add_to_postfix('scan')
        elif ctx.arithmExpression():
            # Вираз у дужках
            self.visit(ctx.arithmExpression())

        return 'numeric'
