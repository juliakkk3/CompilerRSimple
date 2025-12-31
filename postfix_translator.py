"""
Утиліти для роботи з постфікс-кодом
"""


def save_postfix_to_file(postfix_code, variable_table, filename):
    """
    Зберігає постфікс-код у файл у форматі PSM v0.3

    Args:
        postfix_code: список постфікс-інструкцій
        variable_table: таблиця змінних {ident: (index, type, initialized)}
        filename: ім'я файлу для збереження
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # Заголовок
        f.write('.target: Postfix Machine\n')
        f.write('.version: 0.3\n')

        # Секція змінних
        f.write('.vars(\n')
        for ident, (index, varType, initialized) in variable_table.items():
            # Конвертуємо типи RSimple → PSM
            if varType == 'numeric':
                psm_type = 'int'
            elif varType == 'logical':
                psm_type = 'bool'
            else:
                psm_type = varType
            f.write(f'\t{ident}\t{psm_type}\n')
        f.write(')\n')

        # Збираємо мітки
        labels_dict = {}
        for i, item in enumerate(postfix_code):
            if isinstance(item, str) and item.endswith(':'):
                label_name = item[:-1]
                labels_dict[label_name] = i + 1

        # Записуємо мітки
        if labels_dict:
            f.write('.labels(\n')
            for label, value in sorted(labels_dict.items()):
                f.write(f'\t{label}\t{value}\n')
            f.write(')\n')

        # Секція коду
        f.write('.code(\n')
        for item in postfix_code:
            if isinstance(item, str):
                # Визначаємо тип інструкції
                if item.endswith(':'):
                    label_name = item[:-1]
                    f.write(f'\t{label_name}\tlabel\n')
                    f.write(f'\t:\tcolon\n')
                elif item.startswith('='):
                    var_name = item[1:]
                    f.write(f'\t={var_name}\tassign_op\n')
                elif item == 'print':
                    f.write(f'\tOUT\tout_op\n')
                elif item == 'scan':
                    f.write(f'\tINP\tinp_op\n')
                elif item == 'JF':
                    f.write(f'\tJF\tjf\n')
                elif item == 'JMP':
                    f.write(f'\tJUMP\tjump\n')
                elif item == 'unary-':
                    f.write(f'\tNEG\tmath_op\n')
                elif item in ('+', '-', '*', '/', '^'):
                    f.write(f'\t{item}\tmath_op\n')
                elif item in ('<', '<=', '>', '>=', '==', '!='):
                    f.write(f'\t{item}\trel_op\n')
                elif item in ('TRUE', 'FALSE'):
                    f.write(f'\t{item}\tbool\n')
                elif item in variable_table:
                    f.write(f'\t{item}\tr-val\n')
                else:
                    # Спробуємо визначити чи це число
                    try:
                        if '.' in item:
                            float(item)
                            f.write(f'\t{item}\tfloat\n')
                        else:
                            int(item)
                            f.write(f'\t{item}\tint\n')
                    except:
                        f.write(f'\t{item}\n')
        f.write(')\n')

    print(f"✓ Постфікс-код збережено у файл (формат PSM): {filename}")


class PostfixMachine:
    """Віртуальна машина для виконання постфікс-коду"""

    def __init__(self, code):
        self.code = code
        self.stack = []
        self.variables = {}
        self.pc = 0  # Program Counter
        self.labels = {}  # Таблиця міток

        # Будуємо таблицю міток
        for i, item in enumerate(code):
            if isinstance(item, str) and item.endswith(':'):
                label_name = item[:-1]
                self.labels[label_name] = i

    def execute(self):
        """Виконує постфікс-код"""
        print("\n" + "="*70)
        print("ВИКОНАННЯ ПОСТФІКС-КОДУ")
        print("="*70)

        while self.pc < len(self.code):
            item = self.code[self.pc]

            # Пропускаємо мітки
            if isinstance(item, str) and item.endswith(':'):
                self.pc += 1
                continue

            # Виконуємо інструкцію
            self.execute_instruction(item)
            self.pc += 1

        print("\n✓ Виконання завершено успішно")
        print("\nЗНАЧЕННЯ ЗМІННИХ:")
        for var, val in self.variables.items():
            print(f"  {var} = {val}")

    def execute_instruction(self, instr):
        """Виконує одну інструкцію"""

        # Числові константи
        if self.is_number(instr):
            self.stack.append(float(instr))

        # Логічні константи
        elif instr in ('TRUE', 'FALSE'):
            self.stack.append(instr == 'TRUE')

        # Ідентифікатори (завантажити значення)
        elif self.is_identifier(instr):
            if instr.startswith('m') and instr[1:].isdigit():
                self.stack.append(instr)
            elif instr in self.variables:
                self.stack.append(self.variables[instr])
            else:
                raise RuntimeError(f"Змінна {instr} не ініціалізована")

        # Арифметичні операції
        elif instr == '+':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        elif instr == '-':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)
        elif instr == '*':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)
        elif instr == '/':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a / b)
        elif instr == '^':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a ** b)
        elif instr == 'unary-':
            a = self.stack.pop()
            self.stack.append(-a)

        # Оператори відношення
        elif instr == '<':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a < b)
        elif instr == '<=':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a <= b)
        elif instr == '>':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a > b)
        elif instr == '>=':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a >= b)
        elif instr == '==':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a == b)
        elif instr == '!=':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a != b)

        # Присвоєння
        elif isinstance(instr, str) and instr.startswith('='):
            var_name = instr[1:]
            value = self.stack.pop()
            self.variables[var_name] = value

        # Введення
        elif instr == 'scan':
            value = float(input("Введіть число: "))
            self.stack.append(value)

        # Виведення
        elif instr == 'print':
            value = self.stack.pop()
            print(f"OUTPUT: {value}")

        # Переходи
        elif instr == 'JMP':
            label = self.stack.pop()
            if label in self.labels:
                self.pc = self.labels[label] - 1
            else:
                raise RuntimeError(f"Мітка {label} не знайдена")

        elif instr == 'JF':
            label = self.stack.pop()
            condition = self.stack.pop()
            if not condition:
                if label in self.labels:
                    self.pc = self.labels[label] - 1
                else:
                    raise RuntimeError(f"Мітка {label} не знайдена")

    def is_number(self, s):
        """Перевіряє, чи є рядок числом"""
        try:
            float(s)
            return True
        except:
            return False

    def is_identifier(self, s):
        """Перевіряє, чи є рядок ідентифікатором"""
        if not isinstance(s, str):
            return False

        reserved = ['=', '+', '-', '*', '/', '^', 'unary-',
                   '<', '<=', '>', '>=', '==', '!=',
                   'print', 'scan', 'JMP', 'JF', 'TRUE', 'FALSE']

        if s in reserved or s.endswith(':') or s.startswith('='):
            return False

        if s.startswith('m') and len(s) > 1 and s[1:].isdigit():
            return True

        if not s[0].isalpha():
            return False

        for char in s[1:]:
            if not (char.isalnum() or char in ('_', '.')):
                return False

        return True


def print_postfix_code(postfix_code):
    """Виводить постфікс-код на екран"""
    print("\n" + "="*70)
    print("ПОСТФІКС-КОД:")
    print("-"*70)
    for item in postfix_code:
        print(item)
    print("="*70)
