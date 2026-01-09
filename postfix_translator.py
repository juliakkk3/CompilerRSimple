"""
Утиліти для роботи з постфікс-кодом
Містить функції для збереження постфікс-коду у файл та віртуальну машину для його виконання
"""


def save_postfix_to_file(postfix_code, variable_table, filename):
    """
    Зберігає постфікс-код у файл у форматі PSM (Postfix Stack Machine) v0.3

    Формат PSM - це текстовий формат для збереження постфікс-коду з секціями:
    - .target і .version - метадані
    - .vars - оголошення змінних
    - .labels - таблиця міток для переходів
    - .code - послідовність інструкцій

    Args:
        postfix_code: список постфікс-інструкцій
        variable_table: таблиця змінних {ident: (index, type, initialized)}
        filename: ім'я файлу для збереження
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # ========== ЗАГОЛОВОК ФАЙЛУ ==========
        f.write('.target: Postfix Machine\n')
        f.write('.version: 0.3\n')

        # ========== СЕКЦІЯ ЗМІННИХ ==========
        # Формат: ім'я_змінної    тип
        f.write('.vars(\n')
        for ident, (index, varType, initialized) in variable_table.items():
            # Конвертуємо типи RSimple → PSM
            if varType == 'numeric':
                psm_type = 'int'  # Числовий тип
            elif varType == 'logical':
                psm_type = 'bool'  # Логічний тип
            else:
                psm_type = varType  # Інші типи без змін
            f.write(f'\t{ident}\t{psm_type}\n')
        f.write(')\n')

        # ========== ЗБІР МІТОК ==========
        # Проходимо по коду і знаходимо всі мітки (рядки що закінчуються на ':')
        labels_dict = {}
        for i, item in enumerate(postfix_code):
            if isinstance(item, str) and item.endswith(':'):
                label_name = item[:-1]  # Видаляємо ':' з кінця
                labels_dict[label_name] = i + 1  # Зберігаємо позицію

        # ========== СЕКЦІЯ МІТОК ==========
        # Формат: ім'я_мітки    позиція
        if labels_dict:
            f.write('.labels(\n')
            for label, value in sorted(labels_dict.items()):
                f.write(f'\t{label}\t{value}\n')
            f.write(')\n')

        # ========== СЕКЦІЯ КОДУ ==========
        # Формат: інструкція    тип_інструкції
        f.write('.code(\n')
        for item in postfix_code:
            if isinstance(item, str):
                # Визначаємо тип інструкції та записуємо у відповідному форматі

                if item.endswith(':'):
                    # Мітка (наприклад, "m1:")
                    label_name = item[:-1]
                    f.write(f'\t{label_name}\tlabel\n')
                    f.write(f'\t:\tcolon\n')

                elif item.startswith('='):
                    # Присвоювання (наприклад, "=x")
                    var_name = item[1:]
                    f.write(f'\t={var_name}\tassign_op\n')

                elif item == 'print':
                    # Виведення
                    f.write(f'\tOUT\tout_op\n')

                elif item == 'scan':
                    # Введення
                    f.write(f'\tINP\tinp_op\n')

                elif item == 'JF':
                    # Умовний перехід (Jump if False)
                    f.write(f'\tJF\tjf\n')

                elif item == 'JMP':
                    # Безумовний перехід
                    f.write(f'\tJUMP\tjump\n')

                elif item == 'unary-':
                    # Унарний мінус
                    f.write(f'\tNEG\tmath_op\n')

                elif item in ('+', '-', '*', '/', '^'):
                    # Арифметичні операції
                    f.write(f'\t{item}\tmath_op\n')

                elif item in ('<', '<=', '>', '>=', '==', '!='):
                    # Оператори порівняння
                    f.write(f'\t{item}\trel_op\n')

                elif item in ('TRUE', 'FALSE'):
                    # Булеві константи
                    f.write(f'\t{item}\tbool\n')

                elif item in variable_table:
                    # Завантаження значення змінної
                    f.write(f'\t{item}\tr-val\n')

                else:
                    # Спробуємо визначити чи це числова константа
                    try:
                        if '.' in item:
                            # Дробове число
                            float(item)
                            f.write(f'\t{item}\tfloat\n')
                        else:
                            # Ціле число
                            int(item)
                            f.write(f'\t{item}\tint\n')
                    except:
                        # Невідомий елемент - записуємо як є
                        f.write(f'\t{item}\n')
        f.write(')\n')

    print(f"✓ Постфікс-код збережено у файл (формат PSM): {filename}")


class PostfixMachine:
    """
    Віртуальна стекова машина для виконання постфікс-коду

    Постфікс-код (зворотна польська нотація) виконується за допомогою стеку:
    - Операнди кладуться на стек
    - Оператори беруть потрібну кількість операндів зі стеку і кладуть результат назад

    Приклад: "3 4 +" виконується як:
    1. Push 3 → стек: [3]
    2. Push 4 → стек: [3, 4]
    3. ADD   → pop 4 і 3, push 7 → стек: [7]
    """

    def __init__(self, code):
        """
        Ініціалізація віртуальної машини

        Args:
            code: список постфікс-інструкцій
        """
        self.code = code              # Постфікс-код для виконання
        self.stack = []               # Стек для обчислень
        self.variables = {}           # Змінні програми {ім'я: значення}
        self.pc = 0                   # Program Counter (лічильник команд)
        self.labels = {}              # Таблиця міток {ім'я: позиція}

        # ========== ПОБУДОВА ТАБЛИЦІ МІТОК ==========
        # Проходимо по коду і запам'ятовуємо позиції всіх міток
        for i, item in enumerate(code):
            if isinstance(item, str) and item.endswith(':'):
                label_name = item[:-1]  # Видаляємо ':' з кінця
                self.labels[label_name] = i  # Зберігаємо позицію мітки

    def execute(self):
        """
        Виконує весь постфікс-код від початку до кінця
        Це головний цикл виконання програми
        """
        print("\n" + "="*70)
        print("ВИКОНАННЯ ПОСТФІКС-КОДУ")
        print("="*70)

        # ========== ГОЛОВНИЙ ЦИКЛ ВИКОНАННЯ ==========
        # Виконуємо інструкції поки не дійдемо до кінця коду
        while self.pc < len(self.code):
            item = self.code[self.pc]

            # Пропускаємо мітки (вони не виконуються, лише позначають позиції)
            if isinstance(item, str) and item.endswith(':'):
                self.pc += 1
                continue

            # Виконуємо інструкцію
            self.execute_instruction(item)
            self.pc += 1  # Переходимо до наступної інструкції

        # ========== ВИВЕДЕННЯ РЕЗУЛЬТАТІВ ==========
        print("\n✓ Виконання завершено успішно")
        print("\nЗНАЧЕННЯ ЗМІННИХ:")
        for var, val in self.variables.items():
            print(f"  {var} = {val}")

    def execute_instruction(self, instr):
        """
        Виконує одну інструкцію постфікс-коду

        Args:
            instr: інструкція для виконання (число, оператор, команда тощо)
        """

        # ========== ЧИСЛОВІ КОНСТАНТИ ==========
        if self.is_number(instr):
            # Кладемо число на стек
            self.stack.append(float(instr))

        # ========== ЛОГІЧНІ КОНСТАНТИ ==========
        elif instr in ('TRUE', 'FALSE'):
            # TRUE → True, FALSE → False
            self.stack.append(instr == 'TRUE')

        # ========== ІДЕНТИФІКАТОРИ (ЗМІННІ ТА МІТКИ) ==========
        elif self.is_identifier(instr):
            # Якщо це мітка (наприклад, "m1", "m2")
            if instr.startswith('m') and instr[1:].isdigit():
                self.stack.append(instr)
            # Якщо це змінна
            elif instr in self.variables:
                # Завантажуємо значення змінної на стек
                self.stack.append(self.variables[instr])
            else:
                # Змінна не ініціалізована
                raise RuntimeError(f"Змінна {instr} не ініціалізована")

        # ========== АРИФМЕТИЧНІ ОПЕРАЦІЇ ==========
        # Бінарні операції: беруть 2 операнди зі стеку, кладуть результат

        elif instr == '+':
            # Додавання: a + b
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)

        elif instr == '-':
            # Віднімання: a - b
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)

        elif instr == '*':
            # Множення: a * b
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)

        elif instr == '/':
            # Ділення: a / b
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a / b)

        elif instr == '^':
            # Піднесення до степеня: a ^ b
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a ** b)

        elif instr == 'unary-':
            # Унарний мінус: -a (змінює знак)
            a = self.stack.pop()
            self.stack.append(-a)

        # ========== ОПЕРАТОРИ ПОРІВНЯННЯ ==========
        # Беруть 2 операнди, повертають True або False

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

        # ========== ПРИСВОЮВАННЯ ==========
        elif isinstance(instr, str) and instr.startswith('='):
            # Формат: "=x" означає присвоїти значення зі стеку змінній x
            var_name = instr[1:]  # Отримуємо ім'я змінної (видаляємо '=')
            value = self.stack.pop()  # Беремо значення зі стеку
            self.variables[var_name] = value  # Зберігаємо у змінній

        # ========== ВВЕДЕННЯ ==========
        elif instr == 'scan':
            # Читаємо число з клавіатури і кладемо на стек
            value = float(input("Введіть число: "))
            self.stack.append(value)

        # ========== ВИВЕДЕННЯ ==========
        elif instr == 'print':
            # Беремо значення зі стеку і виводимо на екран
            value = self.stack.pop()
            print(f"OUTPUT: {value}")

        # ========== ПЕРЕХОДИ (JUMPS) ==========

        elif instr == 'JMP':
            # Безумовний перехід на мітку
            label = self.stack.pop()  # Мітка на стеку (наприклад, "m1")
            if label in self.labels:
                # Встановлюємо PC на позицію мітки (-1 бо після виконання буде +1)
                self.pc = self.labels[label] - 1
            else:
                raise RuntimeError(f"Мітка {label} не знайдена")

        elif instr == 'JF':
            # Умовний перехід (Jump if False)
            label = self.stack.pop()      # Мітка
            condition = self.stack.pop()  # Умова
            # Якщо умова хибна (False) - переходимо
            if not condition:
                if label in self.labels:
                    self.pc = self.labels[label] - 1
                else:
                    raise RuntimeError(f"Мітка {label} не знайдена")

    def is_number(self, s):
        """
        Перевіряє чи є рядок числом

        Args:
            s: рядок для перевірки

        Returns:
            bool: True якщо s - число, False інакше
        """
        try:
            float(s)
            return True
        except:
            return False

    def is_identifier(self, s):
        """
        Перевіряє чи є рядок ідентифікатором (змінною або міткою)

        Ідентифікатор - це:
        - Змінна (починається з літери, містить літери, цифри, '_', '.')
        - Мітка для переходів (формат: m1, m2, m3, ...)

        Args:
            s: рядок для перевірки

        Returns:
            bool: True якщо s - ідентифікатор, False інакше
        """
        if not isinstance(s, str):
            return False

        # Список зарезервованих слів (не можуть бути ідентифікаторами)
        reserved = ['=', '+', '-', '*', '/', '^', 'unary-',
                   '<', '<=', '>', '>=', '==', '!=',
                   'print', 'scan', 'JMP', 'JF', 'TRUE', 'FALSE']

        # Перевіряємо чи не є рядок зарезервованим словом
        if s in reserved or s.endswith(':') or s.startswith('='):
            return False

        # Перевіряємо чи це мітка (формат: m1, m2, ...)
        if s.startswith('m') and len(s) > 1 and s[1:].isdigit():
            return True

        # Перевіряємо чи це правильний ідентифікатор змінної
        if not s[0].isalpha():  # Повинен починатися з літери
            return False

        # Всі символи після першого повинні бути літерами, цифрами, '_' або '.'
        for char in s[1:]:
            if not (char.isalnum() or char in ('_', '.')):
                return False

        return True


def print_postfix_code(postfix_code):
    """
    Виводить постфікс-код на екран у зручному форматі

    Args:
        postfix_code: список постфікс-інструкцій
    """
    print("\n" + "="*70)
    print("ПОСТФІКС-КОД:")
    print("-"*70)
    for item in postfix_code:
        print(item)
    print("="*70)
