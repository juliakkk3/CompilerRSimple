"""
Main module of the RSimple → CIL translator
"""

import sys
import os
import subprocess
from Lab5.lexer import Lexer
from Lab5.parser import Parser
from cil_generator import CILGenerator
from postfix_translator import save_postfix_to_file, print_postfix_code, PostfixMachine


ILASM_PATH = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\ilasm.exe"


def find_ilasm():
    """Finds ilasm.exe on the system"""

    # First, check the standard path
    if os.path.exists(ILASM_PATH):
        return ILASM_PATH

    # Check the 32-bit version
    ilasm_32 = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\ilasm.exe"
    if os.path.exists(ilasm_32):
        return ilasm_32

    # Check if ilasm is available in PATH
    try:
        result = subprocess.run(['ilasm', '/?'],
                              capture_output=True,
                              timeout=2)
        if result.returncode == 0:
            return 'ilasm'
    except:
        pass

    return None


def run_ilasm(il_file):
    """
    Runs ilasm to create a .exe file

    Args:
        il_file: path to the .il file

    Returns:
        bool: True if successful, False otherwise
    """

    ilasm_path = find_ilasm()

    if ilasm_path is None:
        print('\n⚠ WARNING: ilasm.exe not found')
        print('To create the .exe file manually, run:')
        print(f'  ilasm {il_file}')
        return False

    print('\n' + '='*70)
    print('STEP 4: COMPILE CIL → EXE (ilasm)')
    print('='*70)
    print(f'Using: {ilasm_path}')

    try:
        # Run ilasm
        result = subprocess.run(
            [ilasm_path, il_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Print the result
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        # Check if the .exe file was created
        exe_file = il_file.replace('.il', '.exe')

        if os.path.exists(exe_file):
            print(f'\n✓ Executable created: {exe_file}')
            file_size = os.path.getsize(exe_file)
            print(f'  Size: {file_size} bytes')
            return True
        else:
            print('\n✗ Error: .exe file not created')
            return False

    except subprocess.TimeoutExpired:
        print('\n✗ Error: ilasm hung (timeout)')
        return False
    except Exception as e:
        print(f'\n✗ Error running ilasm: {e}')
        return False


def compile_to_cil(source_file, output_file=None, save_postfix=True, execute_postfix=False, run_ilasm_flag=True):
    """
    Compiles an RSimple program into CIL code

    Args:
        source_file: path to the input file (.my_lang)
        output_file: path to the output file (.il), if None - automatic
        save_postfix: whether to save the intermediate postfix code
        execute_postfix: whether to execute the postfix code (for testing)
        run_ilasm_flag: whether to run ilasm to create a .exe

    Returns:
        bool: True if compilation is successful, False otherwise
    """

    print('='*70)
    print('RSIMPLE → CIL TRANSLATOR')
    print('Lab work №5')
    print('='*70)
    print(f'\nInput file: {source_file}')

    # Check if file exists
    if not os.path.exists(source_file):
        print(f'✗ Error: file {source_file} not found')
        return False

    # Read the input code
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f'✗ Error reading file: {e}')
        return False

    print('\n' + '-'*70)
    print('ВХІДНА ПРОГРАМА:')
    print('-'*70)
    print(source_code)
    print('-'*70)

    # ========== КРОК 1: ЛЕКСИЧНИЙ АНАЛІЗ ==========
    print('\n' + '='*70)
    print('КРОК 1: ЛЕКСИЧНИЙ АНАЛІЗ')
    print('='*70)

    lexer = Lexer()
    if not lexer.analyze(source_code):
        print('✗ Лексичний аналіз завершився з помилками')
        return False

    tables = lexer.get_tables()
    table_of_symbols = tables['symbols']

    print(f'Розпізнано токенів: {len(table_of_symbols)}')
    print(f'Ідентифікаторів: {len(tables["identifiers"])}')
    print(f'Констант: {len(tables["constants"])}')

    # ========== КРОК 2: СИНТАКСИЧНИЙ АНАЛІЗ + ГЕНЕРАЦІЯ ПОСТФІКС-КОДУ ==========
    print('\n' + '='*70)
    print('КРОК 2: СИНТАКСИЧНИЙ АНАЛІЗ + ГЕНЕРАЦІЯ ПОСТФІКС-КОДУ')
    print('='*70)

    parser = Parser(table_of_symbols)
    if not parser.parse():
        print('✗ Синтаксичний аналіз завершився з помилками')
        return False

    postfix_code = parser.get_postfix_code()
    variable_table = parser.get_variable_table()

    print(f'\nЗгенеровано інструкцій постфікс-коду: {len(postfix_code)}')
    print(f'Змінних у програмі: {len(variable_table)}')

    # Виведення постфікс-коду
    print_postfix_code(postfix_code)

    # Збереження постфікс-коду у файл (опціонально)
    if save_postfix:
        base_name = os.path.splitext(source_file)[0]
        postfix_file = f"{base_name}.postfix"
        save_postfix_to_file(postfix_code, variable_table, postfix_file)

    # Виконання постфікс-коду (опціонально, для тестування)
    if execute_postfix:
        try:
            print('\n' + '='*70)
            print('БОНУС: ВИКОНАННЯ ПОСТФІКС-КОДУ (для демонстрації результату)')
            print('='*70)
            print('(Це НЕ частина компіляції, просто показує що має вийти)')
            print()
            psm = PostfixMachine(postfix_code)
            psm.execute()
        except Exception as e:
            print(f'\n✗ Помилка виконання постфікс-коду: {e}')

    # ========== КРОК 3: ГЕНЕРАЦІЯ CIL-КОДУ ==========
    print('\n' + '='*70)
    print('КРОК 3: ГЕНЕРАЦІЯ CIL-КОДУ')
    print('='*70)

    # Визначення імені вихідного файлу
    if output_file is None:
        base_name = os.path.splitext(source_file)[0]
        output_file = f"{base_name}.il"

    # Визначення імені збірки
    assembly_name = os.path.splitext(os.path.basename(source_file))[0]

    # Генерація CIL-коду
    try:
        cil_generator = CILGenerator(postfix_code, variable_table, assembly_name)
        cil_code = cil_generator.generate()

        # Збереження у файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cil_code)

        print(f'✓ CIL-код згенеровано успішно')
        print(f'✓ Збережено у файл: {output_file}')

        # Виведення згенерованого коду
        print('\n' + '-'*70)
        print('ЗГЕНЕРОВАНИЙ CIL-КОД:')
        print('-'*70)
        print(cil_code)
        print('-'*70)

    except Exception as e:
        print(f'✗ Помилка генерації CIL-коду: {e}')
        import traceback
        traceback.print_exc()
        return False

    # ========== КРОК 4: ЗАПУСК ILASM ==========
    ilasm_success = False
    if run_ilasm_flag:
        ilasm_success = run_ilasm(output_file)

    # ========== ПІДСУМОК ==========
    print('\n' + '='*70)
    print('КОМПІЛЯЦІЯ ЗАВЕРШЕНА УСПІШНО!')
    print('='*70)
    print(f'\nВхідний файл:  {source_file}')
    print(f'Вихідний файл: {output_file}')

    if ilasm_success:
        exe_file = output_file.replace('.il', '.exe')
        print(f'Виконуваний файл: {exe_file}')
        print(f'\nДля запуску програми:')
        print(f'  {exe_file}')
        print(f'  або: .\\{os.path.basename(exe_file)}')
    else:
        print(f'\nДля створення виконуваного файлу використайте:')
        print(f'  ilasm {output_file}')
        print(f'\nДля запуску програми:')
        print(f'  {assembly_name}.exe')

    print('='*70)

    return True


def main():
    """Головна функція"""

    # Перевірка аргументів командного рядка
    if len(sys.argv) < 2:
        print('Використання: python main.py <input_file.my_lang> [output_file.il]')
        print('\nПриклади:')
        print('  python main.py test1.my_lang')
        print('  python main.py test1.my_lang output.il')
        print('  python main.py examples/test2.my_lang')
        sys.exit(1)

    source_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Компіляція
    success = compile_to_cil(
        source_file,
        output_file,
        save_postfix=True,      # Зберігати постфікс-код
        execute_postfix=True,   # УВІМКНЕНО: виконувати постфікс-код для демонстрації
        run_ilasm_flag=True     # УВІМКНЕНО: автоматично запускати ilasm
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
