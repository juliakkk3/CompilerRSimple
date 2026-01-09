"""
Головний модуль транслятора RSimple → CIL
Координує всі етапи компіляції: лексичний аналіз, синтаксичний аналіз,
генерацію постфікс-коду, генерацію CIL-коду та збірку виконуваного файлу
"""

import sys
import os
import subprocess
# Імпортуємо лексичний аналізатор (написаний вручну)
from Lab5.lexer import Lexer
# Імпортуємо синтаксичний аналізатор (написаний вручну)
from Lab5.parser import Parser
# Імпортуємо генератор CIL-коду
from cil_generator import CILGenerator
# Імпортуємо утиліти для роботи з постфікс-кодом
from postfix_translator import save_postfix_to_file, print_postfix_code, PostfixMachine


# Стандартний шлях до асемблера CIL (ilasm.exe) для 64-бітної системи
ILASM_PATH = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\ilasm.exe"


def find_ilasm():
    """
    Шукає ilasm.exe на системі

    ilasm (IL Assembler) - це утиліта від Microsoft, яка компілює CIL-код (.il файли)
    у виконувані файли .exe або бібліотеки .dll

    Returns:
        str або None: шлях до ilasm.exe або None якщо не знайдено
    """

    # Спочатку перевіряємо стандартний шлях для 64-бітної системи
    if os.path.exists(ILASM_PATH):
        return ILASM_PATH

    # Перевіряємо 32-бітну версію (на випадок якщо система 32-бітна)
    ilasm_32 = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\ilasm.exe"
    if os.path.exists(ilasm_32):
        return ilasm_32

    # Перевіряємо чи ilasm доступний через змінну PATH
    # (якщо користувач додав .NET до PATH)
    try:
        result = subprocess.run(
            ['ilasm', '/?'],        # Запускаємо ilasm з параметром /? (довідка)
            capture_output=True,    # Захоплюємо вивід
            timeout=2               # Обмеження за часом (2 секунди)
        )
        # Якщо команда виконалась успішно (код 0), ilasm доступний
        if result.returncode == 0:
            return 'ilasm'
    except:
        # Якщо виникла помилка (ilasm не знайдено в PATH), ігноруємо
        pass

    # ilasm не знайдено на системі
    return None


def run_ilasm(il_file):
    """
    Запускає ilasm для створення виконуваного .exe файлу з .il файлу

    Це фінальний етап компіляції: CIL-код (.il) → виконуваний файл (.exe)

    Args:
        il_file: шлях до .il файлу з CIL-кодом

    Returns:
        bool: True якщо збірка успішна, False якщо виникли помилки
    """

    # Спочатку шукаємо ilasm на системі
    ilasm_path = find_ilasm()

    # Якщо ilasm не знайдено
    if ilasm_path is None:
        print('\n⚠ ПОПЕРЕДЖЕННЯ: ilasm.exe не знайдено')
        print('Для створення .exe файлу вручну, виконайте:')
        print(f'  ilasm {il_file}')
        return False

    # Виводимо заголовок етапу компіляції
    print('\n' + '='*70)
    print('КРОК 4: КОМПІЛЯЦІЯ CIL → EXE (ilasm)')
    print('='*70)
    print(f'Використовується: {ilasm_path}')

    try:
        # Запускаємо ilasm як зовнішній процес
        result = subprocess.run(
            [ilasm_path, il_file],  # Команда: ilasm файл.il
            capture_output=True,    # Захоплюємо stdout і stderr
            text=True,              # Декодуємо вивід як текст (не байти)
            timeout=30              # Максимальний час виконання - 30 секунд
        )

        # Виводимо стандартний вивід ilasm (якщо є)
        if result.stdout:
            print(result.stdout)
        # Виводимо помилки ilasm (якщо є)
        if result.stderr:
            print(result.stderr)

        # Перевіряємо чи був створений .exe файл
        # (замінюємо розширення .il на .exe)
        exe_file = il_file.replace('.il', '.exe')

        # Якщо файл існує - збірка успішна
        if os.path.exists(exe_file):
            print(f'\n✓ Виконуваний файл створено: {exe_file}')
            # Виводимо розмір файлу
            file_size = os.path.getsize(exe_file)
            print(f'  Розмір: {file_size} байт')
            return True
        else:
            # Файл не створено - помилка збірки
            print('\n✗ Помилка: .exe файл не створено')
            return False

    except subprocess.TimeoutExpired:
        # ilasm завис (перевищено ліміт часу)
        print('\n✗ Помилка: ilasm завис (перевищено ліміт часу)')
        return False
    except Exception as e:
        # Інша помилка при запуску ilasm
        print(f'\n✗ Помилка запуску ilasm: {e}')
        return False


def compile_to_cil(source_file, output_file=None, save_postfix=True,
                   execute_postfix=False, run_ilasm_flag=True):
    """
    Компілює програму на RSimple у CIL-код

    Виконує повний цикл компіляції:
    1. Лексичний аналіз (text → tokens)
    2. Синтаксичний аналіз (tokens → AST + postfix code)
    3. Генерація CIL-коду (postfix → CIL)
    4. Збірка виконуваного файлу (CIL → .exe)

    Args:
        source_file: шлях до вхідного файлу (.my_lang)
        output_file: шлях до вихідного файлу (.il), якщо None - автоматично
        save_postfix: чи зберігати проміжний постфікс-код у файл
        execute_postfix: чи виконувати постфікс-код (для тестування/демонстрації)
        run_ilasm_flag: чи запускати ilasm для створення .exe

    Returns:
        bool: True якщо компіляція успішна, False якщо є помилки
    """

    # ========== ВИВЕДЕННЯ ЗАГОЛОВКА ==========
    print('='*70)
    print('ТРАНСЛЯТОР RSIMPLE → CIL')
    print('Лабораторна робота №5')
    print('='*70)
    print(f'\nВхідний файл: {source_file}')

    # ========== ПЕРЕВІРКА ІСНУВАННЯ ФАЙЛУ ==========
    if not os.path.exists(source_file):
        print(f'✗ Помилка: файл {source_file} не знайдено')
        return False

    # ========== ЧИТАННЯ ВХІДНОГО ФАЙЛУ ==========
    try:
        # Відкриваємо файл з кодуванням UTF-8 (підтримка кирилиці)
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f'✗ Помилка читання файлу: {e}')
        return False

    # Виводимо вхідну програму на екран
    print('\n' + '-'*70)
    print('ВХІДНА ПРОГРАМА:')
    print('-'*70)
    print(source_code)
    print('-'*70)

    # ========== КРОК 1: ЛЕКСИЧНИЙ АНАЛІЗ ==========
    # Перетворюємо вхідний текст на послідовність токенів
    print('\n' + '='*70)
    print('КРОК 1: ЛЕКСИЧНИЙ АНАЛІЗ')
    print('='*70)

    # Створюємо екземпляр лексичного аналізатора
    lexer = Lexer()
    # Запускаємо аналіз
    if not lexer.analyze(source_code):
        print('✗ Лексичний аналіз завершився з помилками')
        return False

    # Отримуємо таблиці лексера:
    # - symbols: таблиця всіх токенів
    # - identifiers: таблиця унікальних ідентифікаторів (змінних)
    # - constants: таблиця унікальних констант (чисел)
    tables = lexer.get_tables()
    table_of_symbols = tables['symbols']

    # Виводимо статистику
    print(f'Розпізнано токенів: {len(table_of_symbols)}')
    print(f'Ідентифікаторів: {len(tables["identifiers"])}')
    print(f'Констант: {len(tables["constants"])}')

    # ========== КРОК 2: СИНТАКСИЧНИЙ АНАЛІЗ + ГЕНЕРАЦІЯ ПОСТФІКС-КОДУ ==========
    # Перевіряємо синтаксичну правильність і одразу генеруємо постфікс-код
    print('\n' + '='*70)
    print('КРОК 2: СИНТАКСИЧНИЙ АНАЛІЗ + ГЕНЕРАЦІЯ ПОСТФІКС-КОДУ')
    print('='*70)

    # Створюємо екземпляр парсера, передаючи йому таблицю токенів
    parser = Parser(table_of_symbols)
    # Запускаємо розбір
    if not parser.parse():
        print('✗ Синтаксичний аналіз завершився з помилками')
        return False

    # Отримуємо результати парсера:
    # - postfix_code: згенерований постфікс-код (проміжне представлення)
    # - variable_table: таблиця всіх змінних програми з типами
    postfix_code = parser.get_postfix_code()
    variable_table = parser.get_variable_table()

    # Виводимо статистику
    print(f'\nЗгенеровано інструкцій постфікс-коду: {len(postfix_code)}')
    print(f'Змінних у програмі: {len(variable_table)}')

    # Виводимо постфікс-код на екран (для налагодження)
    print_postfix_code(postfix_code)

    # ========== ЗБЕРЕЖЕННЯ ПОСТФІКС-КОДУ У ФАЙЛ (опціонально) ==========
    if save_postfix:
        # Отримуємо ім'я файлу без розширення
        base_name = os.path.splitext(source_file)[0]
        # Додаємо розширення .postfix
        postfix_file = f"{base_name}.postfix"
        # Зберігаємо у форматі PSM (Postfix Stack Machine)
        save_postfix_to_file(postfix_code, variable_table, postfix_file)

    # ========== ВИКОНАННЯ ПОСТФІКС-КОДУ (опціонально, для тестування) ==========
    # Це НЕ частина компіляції, а додаткова можливість для демонстрації результату
    if execute_postfix:
        try:
            print('\n' + '='*70)
            print('БОНУС: ВИКОНАННЯ ПОСТФІКС-КОДУ (для демонстрації результату)')
            print('='*70)
            print('(Це НЕ частина компіляції, просто показує що має вийти)')
            print()
            # Створюємо віртуальну машину для постфікс-коду
            psm = PostfixMachine(postfix_code)
            # Виконуємо код
            psm.execute()
        except Exception as e:
            print(f'\n✗ Помилка виконання постфікс-коду: {e}')

    # ========== КРОК 3: ГЕНЕРАЦІЯ CIL-КОДУ ==========
    # Конвертуємо постфікс-код у CIL (Common Intermediate Language)
    print('\n' + '='*70)
    print('КРОК 3: ГЕНЕРАЦІЯ CIL-КОДУ')
    print('='*70)

    # ========== ВИЗНАЧЕННЯ ІМЕНІ ВИХІДНОГО ФАЙЛУ ==========
    if output_file is None:
        # Якщо не вказано, використовуємо ім'я вхідного файлу
        base_name = os.path.splitext(source_file)[0]
        output_file = f"{base_name}.il"

    # ========== ВИЗНАЧЕННЯ ІМЕНІ ЗБІРКИ (ASSEMBLY) ==========
    # Ім'я збірки = ім'я файлу без шляху та розширення
    # Наприклад, "test1.my_lang" → "test1"
    assembly_name = os.path.splitext(os.path.basename(source_file))[0]

    # ========== ГЕНЕРАЦІЯ CIL-КОДУ ==========
    try:
        # Створюємо генератор CIL-коду
        cil_generator = CILGenerator(postfix_code, variable_table, assembly_name)
        # Генеруємо код
        cil_code = cil_generator.generate()

        # Зберігаємо згенерований CIL-код у файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cil_code)

        print(f'✓ CIL-код згенеровано успішно')
        print(f'✓ Збережено у файл: {output_file}')

        # Виводимо згенерований код на екран (для перевірки)
        print('\n' + '-'*70)
        print('ЗГЕНЕРОВАНИЙ CIL-КОД:')
        print('-'*70)
        print(cil_code)
        print('-'*70)

    except Exception as e:
        # Якщо виникла помилка при генерації CIL
        print(f'✗ Помилка генерації CIL-коду: {e}')
        # Виводимо повний traceback для налагодження
        import traceback
        traceback.print_exc()
        return False

    # ========== КРОК 4: ЗАПУСК ILASM ==========
    # Компілюємо CIL-код у виконуваний .exe файл
    ilasm_success = False
    if run_ilasm_flag:
        ilasm_success = run_ilasm(output_file)

    # ========== ПІДСУМОК КОМПІЛЯЦІЇ ==========
    print('\n' + '='*70)
    print('КОМПІЛЯЦІЯ ЗАВЕРШЕНА УСПІШНО!')
    print('='*70)
    print(f'\nВхідний файл:  {source_file}')
    print(f'Вихідний файл: {output_file}')

    # Якщо ilasm успішно створив .exe файл
    if ilasm_success:
        exe_file = output_file.replace('.il', '.exe')
        print(f'Виконуваний файл: {exe_file}')
        print(f'\nДля запуску програми:')
        print(f'  {exe_file}')
        print(f'  або: .\\{os.path.basename(exe_file)}')
    else:
        # Якщо ilasm не запускався або не вдалося створити .exe
        print(f'\nДля створення виконуваного файлу використайте:')
        print(f'  ilasm {output_file}')
        print(f'\nДля запуску програми:')
        print(f'  {assembly_name}.exe')

    print('='*70)

    return True


def main():
    """
    Головна функція програми
    Обробляє аргументи командного рядка та запускає компіляцію
    """

    # ========== ПЕРЕВІРКА АРГУМЕНТІВ КОМАНДНОГО РЯДКА ==========
    # sys.argv[0] - ім'я скрипта (main.py)
    # sys.argv[1] - вхідний файл
    # sys.argv[2] - вихідний файл (опціонально)
    if len(sys.argv) < 2:
        # Якщо не вказано вхідний файл, виводимо довідку
        print('Використання: python main.py <input_file.my_lang> [output_file.il]')
        print('\nПриклади:')
        print('  python main.py test1.my_lang')
        print('  python main.py test1.my_lang output.il')
        print('  python main.py examples/test2.my_lang')
        sys.exit(1)

    # Отримуємо вхідний файл з аргументів
    source_file = sys.argv[1]
    # Отримуємо вихідний файл (якщо вказано), інакше None
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # ========== ЗАПУСК КОМПІЛЯЦІЇ ==========
    success = compile_to_cil(
        source_file,
        output_file,
        save_postfix=True,      # Зберігати постфікс-код у файл
        execute_postfix=True,   # УВІМКНЕНО: виконувати постфікс-код для демонстрації
        run_ilasm_flag=True     # УВІМКНЕНО: автоматично запускати ilasm
    )

    # Повертаємо код виходу:
    # 0 - успіх
    # 1 - помилка
    sys.exit(0 if success else 1)


# ========== ТОЧКА ВХОДУ В ПРОГРАМУ ==========
# Перевіряємо чи скрипт запущено безпосередньо (не імпортовано)
if __name__ == '__main__':
    main()
