from RSimpleVisitor import RSimpleVisitor
from RSimpleParser import RSimpleParser


class RSimpleCompilerVisitor(RSimpleVisitor):
    """Visitor для генерації постфікс-коду з AST"""

    def __init__(self):
        self.postfix_code = []
        self.variable_table = {}
        self.label_counter = 0

    def generate_label(self):
        """Генерує унікальну мітку"""
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

    # ========== STATEMENTS ==========

    def visitAssignment(self, ctx: RSimpleParser.AssignmentContext):
        """Обробляє присвоювання: x <- 5"""
        ident = ctx.ID().getText()
        expr_type = self.visit(ctx.expression())
        self.add_variable(ident, expr_type)
        self.add_to_postfix(f'={ident}')
        return None

    def visitOutputStatement(self, ctx: RSimpleParser.OutputStatementContext):
        """Обробляє вивід: print(x, y)"""
        expr_list = ctx.expressionList()
        for expr in expr_list.expression():
            self.visit(expr)
            self.add_to_postfix('print')
        return None

    def visitIfStatement(self, ctx: RSimpleParser.IfStatementContext):
        """Обробляє if-else"""
        # Умова
        self.visit(ctx.expression())

        label_else = self.generate_label()
        self.add_to_postfix(label_else)
        self.add_to_postfix('JF')

        # Then блок
        self.visit(ctx.statementBlock(0))

        # Else блок (якщо є)
        if ctx.statementBlock(1):
            label_end = self.generate_label()
            self.add_to_postfix(label_end)
            self.add_to_postfix('JMP')
            self.add_to_postfix(f"{label_else}:")
            self.visit(ctx.statementBlock(1))
            self.add_to_postfix(f"{label_end}:")
        else:
            self.add_to_postfix(f"{label_else}:")

        return None

    def visitWhileStatement(self, ctx: RSimpleParser.WhileStatementContext):
        """Обробляє while цикл"""
        label_start = self.generate_label()
        self.add_to_postfix(f"{label_start}:")

        # Умова
        self.visit(ctx.expression())

        label_end = self.generate_label()
        self.add_to_postfix(label_end)
        self.add_to_postfix('JF')

        # Тіло циклу
        self.visit(ctx.statementBlock())

        self.add_to_postfix(label_start)
        self.add_to_postfix('JMP')
        self.add_to_postfix(f"{label_end}:")

        return None

    # ========== EXPRESSIONS ==========

    def visitExpression(self, ctx: RSimpleParser.ExpressionContext):
        """Обробляє вирази"""
        if ctx.boolConst():
            value = ctx.boolConst().getText()
            self.add_to_postfix(value)
            return 'logical'

        # Arithmetic expression
        left_type = self.visit(ctx.arithmExpression(0))

        if ctx.relOp():
            op = ctx.relOp().getText()
            self.visit(ctx.arithmExpression(1))
            self.add_to_postfix(op)
            return 'logical'

        return left_type

    def visitArithmExpression(self, ctx: RSimpleParser.ArithmExpressionContext):
        """Обробляє арифметичні вирази: a + b - c"""
        self.visit(ctx.term(0))

        for i in range(1, len(ctx.term())):
            op = ctx.getChild(2*i - 1).getText()  # +/-
            self.visit(ctx.term(i))
            self.add_to_postfix(op)

        return 'numeric'

    def visitTerm(self, ctx: RSimpleParser.TermContext):
        """Обробляє терми: a * b / c"""
        self.visit(ctx.power(0))

        for i in range(1, len(ctx.power())):
            op = ctx.getChild(2*i - 1).getText()  # *//
            self.visit(ctx.power(i))
            self.add_to_postfix(op)

        return 'numeric'

    def visitPower(self, ctx: RSimpleParser.PowerContext):
        """Обробляє степінь: a ^ b"""
        self.visit(ctx.factor())

        if ctx.power():
            self.visit(ctx.power())
            self.add_to_postfix('^')

        return 'numeric'

    def visitFactor(self, ctx: RSimpleParser.FactorContext):
        """Обробляє фактор з можливим унарним мінусом"""
        has_minus = ctx.getChildCount() > 1 and ctx.getChild(0).getText() == '-'

        self.visit(ctx.primary())

        if has_minus:
            self.add_to_postfix('unary-')

        return 'numeric'

    def visitPrimary(self, ctx: RSimpleParser.PrimaryContext):
        """Обробляє базові елементи: змінні, числа, scan()"""
        if ctx.ID():
            self.add_to_postfix(ctx.ID().getText())
        elif ctx.INT():
            self.add_to_postfix(ctx.INT().getText())
        elif ctx.FLOAT():
            self.add_to_postfix(ctx.FLOAT().getText())
        elif ctx.getText().startswith('scan'):
            self.add_to_postfix('scan')
        elif ctx.arithmExpression():
            self.visit(ctx.arithmExpression())

        return 'numeric'
